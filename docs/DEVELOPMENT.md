# Development Guidelines

This document provides development guidelines for contributing to the UNHCR IATI MCP Server.

## Project Structure

```
unhcr_iati_mcp/
├── src/
│   └── unhcr_iati_mcp/
│       ├── __init__.py                 # Package initialization
│       ├── server.py                   # FastMCP server entry point
│       ├── client.py                   # IATI API client with retry logic
│       ├── config.py                   # Pydantic settings configuration
│       │
│       ├── models/                     # Pydantic data models
│       │   ├── __init__.py
│       │   ├── activity.py              # Activity model
│       │   ├── budget.py                # Budget model
│       │   ├── transaction.py           # Transaction model
│       │   ├── donor.py                 # Donor model
│       │   ├── country.py               # Country model
│       │   ├── sector.py                # Sector model
│       │   ├── result.py                # Result framework model
│       │   ├── pagination.py            # Pagination utilities
│       │   ├── responses.py             # API response wrappers
│       │   ├── errors.py                # Error response models
│       │   └── generated/               # Auto-generated models
│       │
│       ├── tools/                      # MCP tools
│       │   ├── __init__.py
│       │   ├── activities.py            # Activity query tools
│       │   ├── transactions.py          # Transaction query tools
│       │   ├── budgets.py               # Budget query tools
│       │   ├── donors.py                # Donor analysis tools
│       │   ├── countries.py             # Country analysis tools
│       │   ├── sectors.py               # Sector analysis tools
│       │   ├── analytics.py             # Portfolio analytics tools
│       │   ├── export.py                # Data export tools
│       │   └── health.py                # Health check tools
│       │
│       ├── resources/                  # MCP resources (static reference data)
│       │   ├── __init__.py
│       │   ├── donors.py                # Donor code to name mapping
│       │   ├── countries.py             # Country reference data
│       │   ├── sectors.py               # Sector reference data and vocabulary management
│       │   ├── results.py               # Result framework and indicator resources
│       │   ├── sdgs.py                  # SDG reference data
│       │   ├── glossary.py              # IATI terminology glossary
│       │   ├── portfolio.py             # UNHCR portfolio metadata
│       │   ├── schemas.py               # Data schema definitions
│       │   └── code_tables.py           # All 41 IATI code lookup tables
│       │
│       └── observability/              # Monitoring and observability
│           ├── __init__.py
│           ├── logging.py               # Structured logging (structlog with JSON)
│           └── metrics.py               # Prometheus metrics
│
├── scripts/
│   └── generate_models.py              # Model generation script
│
├── tests/
│   └── test_smoke.py                   # Basic test suite
│
├── docs/
│   ├── ARCHITECTURE.md                 # Architecture documentation
│   ├── API_REFERENCE.md                # API reference
│   ├── DATA_MODELS.md                  # Data models documentation
│   ├── DEPLOYMENT.md                   # Deployment guide
│   ├── TROUBLESHOOTING.md               # Troubleshooting guide
│   ├── BEST_PRACTICES.md               # Best practices
│   └── DEVELOPMENT.md                  # Development guidelines (this file)
│
├── Dockerfile                         # Container image definition
├── docker-compose.yml                 # Development stack
├── pyproject.toml                     # Python project configuration
├── .env.example                       # Environment variables template
└── README.md                          # Project overview
```

## Coding Standards

### 1. Imports

- **Avoid circular imports** by using a context module for shared state
- **Group imports** by standard library, third-party, and local imports
- **Use absolute imports** for clarity
- **Import only what you need** (avoid `import *`)

```python
# Good
from typing import Optional, List, Dict
from pydantic import BaseModel
from unhcr_iati_mcp.models.activity import Activity

# Bad
from typing import *
import pydantic
from models import *
```

### 2. Naming Conventions

- **Variables and functions**: Use `snake_case`
- **Classes**: Use `PascalCase`
- **Constants**: Use `UPPER_SNAKE_CASE`
- **Private members**: Prefix with `_`
- **Protected members**: Prefix with `_` (Python convention)

```python
# Good
class ActivityModel(BaseModel):
    def get_sector_info(self) -> List[SectorInfo]:
        pass

# Bad
class activityModel(BaseModel):
    def GetSectorInfo(self) -> List[SectorInfo]:
        pass
```

### 3. Type Hints

- **Always include type hints** for public functions and methods
- **Use `Optional`** for parameters that can be None
- **Use `-> None`** for functions that don't return anything
- **Use type aliases** for complex types

```python
# Good
from typing import Optional, List, Dict

def get_activity(iati_identifier: str) -> Optional[Activity]:
    pass

async def query_activities(
    rows: int = 100,
    start: int = 0,
    fl: Optional[str] = None
) -> Dict[str, Any]:
    pass

# Bad
def get_activity(iati_identifier):
    pass
```

### 4. Error Handling

- **Always wrap external calls** in try/except blocks
- **Use custom exceptions** for domain-specific errors
- **Provide meaningful error messages**
- **Log errors** with context

```python
# Good
try:
    response = await self._client.get(
        url,
        headers=headers,
        params=params,
        timeout=self._timeout
    )
    response.raise_for_status()
    return response.json()
except httpx.TimeoutException as e:
    logger.error("Request timeout", url=url, timeout=self._timeout)
    raise IATITimeoutError(f"Request to {url} timed out after {self._timeout}s") from e
except httpx.HTTPStatusError as e:
    logger.error("HTTP error", url=url, status_code=e.response.status_code)
    raise IATIHTTPError(f"HTTP {e.response.status_code}: {e.response.text}") from e

# Bad
try:
    response = await self._client.get(url)
    return response.json()
except:
    pass  # Silent failure!
```

### 5. Logging

- **Use structured logging** with context
- **Include relevant information** in log messages
- **Use appropriate log levels**
- **Don't log sensitive information**

```python
# Good
logger = get_logger(__name__)
logger.info("Processing request", 
            request_id=request_id,
            collection=collection,
            start=start,
            rows=rows)
logger.error("API error", 
              error=str(error),
              collection=collection,
              retry_count=retry_count)

# Bad
print("Processing request...")
print(f"Error: {error}")
```

### 6. Testing

- **Add tests** for all new functionality
- **Test edge cases** and error conditions
- **Use pytest** for testing
- **Test with real data** when possible

```python
# Good
import pytest
from unhcr_iati_mcp.models.activity import Activity

@pytest.mark.asyncio
async def test_activity_model():
    data = {"iati_identifier": "XM-DAC-41121-ACT-001"}
    activity = Activity(**data)
    assert activity.iati_identifier == "XM-DAC-41121-ACT-001"

# Bad
# No tests!
```

### 7. Documentation

- **Update README and docstrings** for new features
- **Use Google-style docstrings**
- **Include examples** in documentation
- **Document return types** and exceptions

```python
# Good
def get_sector_info(self) -> List[SectorInfo]:
    """
    Get structured sector data from activity.
    
    Returns:
        List[SectorInfo]: List of sector information objects with
            code, narrative, vocabulary, and percentage.
    
    Example:
        >>> activity = Activity(**data)
        >>> sectors = activity.get_sector_info()
        >>> for sector in sectors:
        ...     print(f"{sector.sector_code}: {sector.sector_narrative}")
    """
    pass

# Bad
def get_sector_info(self):
    # Gets sector info
    pass
```

## Development Workflow

### Before Committing

- [ ] Run `pytest` to ensure all tests pass
- [ ] Run `python -m unhcr_iati_mcp.server` to verify server starts
- [ ] Test at least one tool manually
- [ ] Check for import errors
- [ ] Verify type hints are correct
- [ ] Update documentation if needed

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes
# Add tests
# Update documentation

# Run tests
pytest tests/

# Commit with descriptive message
git add .
git commit -m "feat: add your feature description

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>"

# Push and create PR
git push origin feature/your-feature
```

### Branch Naming Conventions

- `feature/your-feature`: New features
- `fix/your-fix`: Bug fixes
- `docs/your-docs`: Documentation updates
- `refactor/your-refactor`: Code refactoring
- `chore/your-chore`: Maintenance tasks

### Commit Message Format

Use conventional commits format:

```
type(scope): subject

body

footer
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(activities): add filter by year tool

Adds a new tool 'unhcr_activity_by_year' that filters
activities by a specific year.

Generated by Mistral Vibe.
Co-Authored-By: Mistral Vibe <vibe@mistral.ai>
```

## Code Review Process

### Before Requesting Review

1. **Run all tests** and ensure they pass
2. **Verify the server starts** and basic functionality works
3. **Check for linting issues**
4. **Update documentation**
5. **Squash commits** if there are many small commits

### During Review

1. **Address all feedback** promptly
2. **Explain changes** if requested
3. **Update tests** if logic changes
4. **Keep PRs small** and focused

### After Approval

1. **Merge with squash** if the PR has many commits
2. **Delete the branch** after merging
3. **Update changelog** if applicable

## Adding New Features

### Adding a New Tool

1. **Create a new file** in `src/unhcr_iati_mcp/tools/` or add to existing file
2. **Implement the tool function** with proper type hints
3. **Add error handling** and logging
4. **Add tests** for the new tool
5. **Update documentation** in `docs/TOOLS.md`

```python
# Example: New tool in tools/activities.py
from typing import Optional
from unhcr_iati_mcp.client import IATIClient
from unhcr_iati_mcp.observability.logging import get_logger

logger = get_logger(__name__)

async def unhcr_new_tool(param1: str, param2: Optional[int] = None) -> dict:
    """
    Description of what the tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
    
    Returns:
        dict: Description of return value
    
    Raises:
        ValueError: If parameters are invalid
        IATIError: If IATI API request fails
    """
    logger.info("Executing new tool", param1=param1, param2=param2)
    
    # Validate parameters
    if not param1:
        raise ValueError("param1 is required")
    
    # Use client to query IATI
    client = IATIClient()
    data = await client.query(
        collection="activity",
        q=f'some_query:{param1}'
    )
    
    # Process and return data
    return {"results": data}
```

### Adding a New Resource

1. **Create a new file** in `src/unhcr_iati_mcp/resources/` or add to existing file
2. **Implement the resource** with proper metadata
3. **Register the resource** in the server
4. **Add tests** for the new resource

```python
# Example: New resource in resources/custom.py
from typing import Any, Dict
from mcp.server import Resource

CUSTOM_DATA: Dict[str, Any] = {
    "key1": "value1",
    "key2": "value2"
}

custom_resource = Resource(
    uri="unhcr://custom",
    name="Custom Data",
    description="Description of custom data",
    data=CUSTOM_DATA,
    mime_type="application/json"
)
```

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Use mocking for external dependencies
- Test both success and error cases

```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
async def test_query_tool():
    with patch("unhcr_iati_mcp.client.IATIClient.query") as mock_query:
        mock_query.return_value = {"response": {"docs": []}}
        
        result = await query_activities(rows=10)
        
        assert "response" in result
        mock_query.assert_called_once()
```

### Integration Tests

- Test interactions between components
- Use real data when possible
- Test the full request/response cycle

```python
@pytest.mark.asyncio
async def test_server_startup():
    # This requires the server to be running
    client = Client("http://localhost:8000")
    
    # Test health check
    health = await client.call_tool("health_check", {})
    assert health["status"] == "healthy"
```

### Test Organization

- Place tests in the `tests/` directory
- Mirror the source code structure
- Use descriptive test names
- Group related tests together

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_client.py       # Client tests
├── test_models.py       # Model tests
├── test_tools/          # Tool tests
│   ├── __init__.py
│   ├── test_activities.py
│   └── test_analytics.py
└── test_resources.py    # Resource tests
```

## Performance Considerations

### Query Optimization

- **Always use pagination** for large datasets
- **Select specific fields** to reduce data transfer
- **Use filters** to limit result sets
- **Cache results** when appropriate

### Memory Management

- **Limit cache sizes**
- **Use generators** for large datasets
- **Clear unused data**
- **Monitor memory usage**

### Async/Await

- **Use async/await** for I/O-bound operations
- **Avoid blocking calls**
- **Use async libraries** (httpx, aiofiles, etc.)

```python
# Good
import httpx

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Bad
import requests

def fetch_data():
    response = requests.get(url)  # Blocking!
    return response.json()
```

## Security Considerations

- **Never hardcode secrets** (use environment variables or secrets manager)
- **Validate all inputs**
- **Sanitize outputs**
- **Use HTTPS** for all external communications
- **Keep dependencies updated**
- **Use secure defaults**

## Documentation Updates

When adding new features:

1. **Update README.md** if it's a major feature
2. **Add to appropriate docs file** (API_REFERENCE.md, etc.)
3. **Add docstrings** to all public functions
4. **Include examples** in documentation
5. **Update type hints**

## Version Management

- **Use semantic versioning** (MAJOR.MINOR.PATCH)
- **Update pyproject.toml** with new version
- **Tag releases** in Git
- **Generate changelog** for releases

## Dependency Management

- **Use Poetry** for dependency management
- **Pin versions** for production dependencies
- **Use development dependencies** for testing and development tools
- **Regularly update dependencies**

```bash
# Update a dependency
poetry update package-name

# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name
```

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- **Tests**: Run on every push and PR
- **Build**: Build Docker image on main branch
- **Deploy**: Deploy to production on tagged releases

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Update documentation**
6. **Submit a pull request**

We welcome contributions! Please follow the development guidelines and code of conduct.
