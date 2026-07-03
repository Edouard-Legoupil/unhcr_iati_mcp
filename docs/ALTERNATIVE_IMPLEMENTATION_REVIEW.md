# Alternative Implementation Review: TypeScript IATI MCP Server

This document reviews the TypeScript/JavaScript implementation of an IATI MCP server located at `.arc/mcp-iati-main/` and identifies good ideas, patterns, and features that could be incorporated into the Python implementation.

## Overview

The TypeScript implementation (`mcp-iati-main`) is a production-ready MCP server for IATI data that offers several advanced features not present in the current Python implementation:

### Key Differences

| Feature | TypeScript Implementation | Python Implementation | Status |
|---------|-------------------------|----------------------|--------|
| Transport Modes | STDIO + HTTP | STDIO only | ⚠️ Missing |
| Authentication | OAuth 2.1 + X-API-Key | Environment variables | ⚠️ Basic |
| OAuth Support | Built-in OAuth server | None | ⚠️ Missing |
| Hosted Service | Yes (mcp-iati.baobabtech.ai) | No | ⚠️ Missing |
| API Client | Facade methods | Direct HTTPX calls | ✅ Good |
| Error Handling | Comprehensive | Basic | ⚠️ Needs improvement |
| Health Checks | HTTP endpoint | None | ⚠️ Missing |
| Documentation | Extensive (multiple files) | Good | ✅ Good |

## 🏆 Good Ideas to Adopt

### 1. Dual Transport Mode Support

**TypeScript Approach:**
```typescript
// index.ts - Checks environment variable
if (process.env.MCP_TRANSPORT === 'http') {
    // Start HTTP server
    const server = new IATIHttpServer(config);
    await server.start();
} else {
    // Start STDIO server
    const mcpServer = new McpServer(...);
    await mcpServer.connect(new StdioServerTransport());
}
```

**Recommendation for Python:**
- Add HTTP transport mode using FastMCP's HTTP support or Starlette/FastAPI
- Use environment variable `MCP_TRANSPORT` to switch between modes
- Provide both local development and remote deployment options

**Implementation:**
```python
# In server.py
import os
from fastmcp import FastMCP

TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")

if TRANSPORT == "http":
    # Use HTTP transport
    from fastmcp.server import http
    # Or implement custom HTTP server
else:
    # Use STDIO (default)
    mcp.run()
```

---

### 2. Built-in OAuth Server

**TypeScript Approach:**
- Full OAuth 2.1 implementation with client credentials grant
- Built-in OAuth server that issues tokens containing encrypted IATI API keys
- Supports both OAuth Bearer tokens and X-API-Key headers
- Zero external dependencies for authentication

**Key Files:**
- `src/builtin-oauth.ts` - OAuth server implementation
- `src/oauth-middleware.ts` - Authentication middleware
- Token endpoint: `/oauth/token`
- Metadata endpoint: `/.well-known/oauth-authorization-server`

**Recommendation for Python:**
- Add OAuth 2.1 support using Python OAuth libraries (authlib, oauthlib)
- Implement client credentials grant type
- Support both OAuth and X-API-Key for compatibility with different clients

**Benefits:**
- No need for external OAuth providers
- Simplified deployment
- Standards-compliant authentication
- Works with Claude, OpenAI, HuggingChat, and other MCP clients

---

### 3. HTTP Server with MCP Endpoints

**TypeScript Approach:**
- Express.js-based HTTP server
- MCP JSON-RPC endpoint at `/mcp`
- Health check at `/health`
- OAuth metadata at `/.well-known/oauth-protected-resource`
- Proper error handling with HTTP status codes

**Recommendation for Python:**
- Add FastAPI or Starlette HTTP server option
- Expose MCP endpoints over HTTP
- Add health check endpoint
- Implement proper HTTP error handling

**Example Structure:**
```python
# server_http.py
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP(...)

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    # Handle MCP JSON-RPC requests
    pass

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

### 4. API Client Facade Pattern

**TypeScript Approach:**
```typescript
class IATIApiClient {
    // Base query method
    async query(collection: CollectionType, params: IATIQueryParams): Promise<IATIResponse> { ... }
    
    // Facade methods for common queries
    async getActivityByIdentifier(identifier: string) { ... }
    async searchByReportingOrg(orgRef: string, rows = 10) { ... }
    async searchByCountry(countryCode: string, rows = 10) { ... }
    async searchBySector(sectorCode: string, rows = 10) { ... }
    async searchText(searchTerm: string, rows = 10) { ... }
    async getFacets(field: string, query = '*:*', facetLimit = 20) { ... }
}
```

**Current Python Implementation:**
```python
class IATIClient:
    # Base method
    async def query(self, collection: str, **params) -> dict: ...
    
    # Facade methods already exist!
    async def get_activity(self, iati_identifier: str) -> dict: ...
    async def search_activities(self, q: str, rows: int = 10, start: int = 0, **kwargs) -> dict: ...
```

**Recommendation:**
✅ **Already implemented!** The Python client already has good facade methods. No changes needed.

---

### 5. Protected Resource Metadata (RFC 9728)

**TypeScript Implementation:**
```typescript
// OAuth Protected Resource Metadata endpoint
app.get('/.well-known/oauth-protected-resource', (req, res) => {
    const metadata = {
        resource: config.resourceUrl,
        authorization_servers: [config.authServerUrl],
    };
    res.json(metadata);
});
```

**Recommendation for Python:**
- Add this endpoint when implementing HTTP mode
- Required for MCP Authorization Specification compliance
- Helps clients discover OAuth configuration automatically

---

### 6. Dual Authentication Support

**TypeScript Approach:**
- OAuth Bearer tokens (primary)
- X-API-Key header (fallback for clients like HuggingChat)

**Authentication Flow:**
1. Check for `X-API-Key` header first
2. If not present, check for `Authorization: Bearer <token>`
3. Validate token or API key
4. Attach validated client to request context

**Recommendation for Python:**
- Support both authentication methods
- Makes the server compatible with more MCP clients
- Provide clear error messages for authentication failures

---

### 7. Tool Organization and Naming

**TypeScript Tools:**
```typescript
{
    name: 'query_activities',        // Generic Solr query
    name: 'get_activity',            // Get by identifier
    name: 'search_by_organization',  // Filter by org
    name: 'search_by_country',       // Filter by country
    name: 'search_by_sector',        // Filter by sector
    name: 'search_text',             // Full-text search
    name: 'get_facets',              // Get facet counts
}
```

**Current Python Tools:**
```python
unhcr_activities      # List all UNHCR activities
unhcr_activity        # Get specific activity
unhcr_activity_by_country
unhcr_activity_by_sector
unhcr_activity_by_year
unhcr_transactions
unhcr_budgets
unhcr_donors
unhcr_countries
unhcr_analytics_summary
unhcr_health_check
```

**Recommendation:**
- Consider adopting more generic naming for broader applicability
- Current naming (`unhcr_*`) is good for UNHCR-specific use case
- Could add generic versions alongside UNHCR-specific ones
- **No changes needed** - Current naming is appropriate for UNHCR context

---

### 8. Error Handling Pattern

**TypeScript Approach:**
```typescript
// In tool execution
try {
    const result = await executeTool(name, args, client);
    return {
        content: [{ type: 'text', text: result }],
    };
} catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
        content: [{ type: 'text', text: `Error: ${errorMessage}` }],
        isError: true,
    };
}

// In HTTP server
expressRouter.post('/mcp', async (req, res) => {
    try {
        // ... handle request
    } catch (error) {
        res.status(500).json({
            jsonrpc: '2.0',
            id: req.body.id,
            error: {
                code: -32603,
                message: error instanceof Error ? error.message : 'Internal error',
            },
        });
    }
});
```

**Recommendation for Python:**
- Current error handling in tools is good
- Could improve HTTP error responses when implementing HTTP mode
- Use proper HTTP status codes (400, 401, 403, 404, 500)
- Include error codes in JSON responses

---

### 9. Documentation Structure

**TypeScript Documentation Files:**
- `README.md` - Main overview and quick start
- `HOSTED_SERVICE.md` - Using the public hosted service
- `SELF_HOSTING.md` - Self-hosting instructions
- `DEPLOYMENT.md` - Production deployment guide
- `OAUTH.md` - OAuth 2.1 details
- `TOOLS.md` - Tool documentation and examples
- `ENV_TEMPLATE.md` - Environment variables reference

**Recommendation for Python:**
- Create similar documentation structure in `docs/` directory
- Separate concerns: getting started, deployment, configuration, tools
- Include examples for each tool
- Document authentication options

---

### 10. Query Examples and Natural Language Support

**TypeScript TOOLS.md:**
- Provides natural language examples for each tool
- Shows how AI assistants translate questions to tool calls
- Includes Solr query syntax reference
- Lists common field names
- Provides tips for effective queries

**Example:**
```markdown
## How Natural Language Works

Instead of learning query syntax, you can simply ask questions like:
- "Show me UK government projects in Afghanistan"
- "What health projects are funded in Kenya?"
- "Find climate change activities with budgets over $1 million"

The AI assistant understands your intent and translates it into structured tool calls.
```

**Recommendation for Python:**
- Add similar section to `docs/TOOLS.md`
- Document natural language examples
- Include query syntax reference for advanced users
- Help users understand what questions they can ask

---

### 11. Configuration Flexibility

**TypeScript Environment Variables:**
```bash
# Transport mode
MCP_TRANSPORT=http  # or stdio

# HTTP server
PORT=3000
RESOURCE_URL=http://localhost:3000

# OAuth
USE_BUILTIN_OAUTH=true
AUTH_SERVER_URL=https://your-auth-server.com

# IATI
IATI_API_KEY=your_key
```

**Recommendation for Python:**
- Add `MCP_TRANSPORT` environment variable support
- Add `RESOURCE_URL` for HTTP mode
- Add OAuth-related configuration options
- Keep existing IATI configuration

---

### 12. Health Check Endpoint

**TypeScript Implementation:**
```typescript
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'mcp-iati',
        oauth: config.useBuiltInOAuth ? 'built-in' : 'external',
        auth_methods: config.useBuiltInOAuth ? ['oauth', 'x-api-key'] : ['oauth']
    });
});
```

**Recommendation for Python:**
- Add `/health` endpoint when implementing HTTP mode
- Include service status, version, configuration info
- Useful for Kubernetes liveness probes
- Could integrate with existing health check tools

---

## 📊 Implementation Priority

Based on the review, here's the recommended priority for incorporating ideas from the TypeScript implementation:

### Phase 1: High Priority (Production Readiness)
1. **Add HTTP transport mode** - Enables remote deployment
2. **Add built-in OAuth server** - Simplifies authentication
3. **Add X-API-Key header support** - HuggingChat compatibility
4. **Add health check endpoint** - Production monitoring

### Phase 2: Medium Priority (Enhanced Functionality)
5. **Add Protected Resource Metadata endpoint** - OAuth spec compliance
6. **Enhance error handling** - Better HTTP error responses
7. **Improve documentation structure** - Multiple focused docs

### Phase 3: Low Priority (Nice to Have)
8. **Offer hosted service** - Requires infrastructure
9. **Add deployment guides** - Kubernetes, systemd, etc.

---

## 🔄 Migration Path

To gradually adopt features from the TypeScript implementation:

### Step 1: Add HTTP Mode (2-4 hours)
- Create `server_http.py` with FastAPI/Starlette
- Add environment variable `MCP_TRANSPORT`
- Implement basic MCP-over-HTTP endpoint
- Add health check

### Step 2: Add Authentication (4-8 hours)
- Implement OAuth 2.1 client credentials flow
- Add X-API-Key header support
- Create token validation middleware
- Add Protected Resource Metadata endpoint

### Step 3: Enhance Documentation (2-4 hours)
- Create `docs/DEPLOYMENT.md`
- Create `docs/AUTHENTICATION.md`
- Enhance `docs/TOOLS.md` with examples
- Add getting started guide

### Step 4: Production Hardening (4-8 hours)
- Add proper error handling and status codes
- Add rate limiting
- Add request logging
- Add metrics for HTTP endpoints

---

## 📝 Recommendations

### Should Adopt (Strongly Recommended)
✅ **HTTP transport mode** - Essential for remote deployment  
✅ **Built-in OAuth server** - Simplifies authentication significantly  
✅ **X-API-Key header support** - Required for HuggingChat and similar clients  
✅ **Health check endpoint** - Standard practice for production services  
✅ **Protected Resource Metadata** - Required for MCP spec compliance  

### Could Adopt (Recommended if resources allow)
🟡 **Enhanced error handling** - Better user experience  
🟡 **Improved documentation structure** - Better maintainability  
🟡 **Dual authentication** - More flexible security  

### Skip (Not Applicable or Already Implemented)
❌ **Tool naming changes** - Current naming is appropriate for UNHCR  
❌ **API client facade** - Already well-implemented in Python  
❌ **Hosted service** - Requires separate infrastructure  

---

## 📚 Files to Create/Modify

### New Files
1. `src/unhcr_iati_mcp/server_http.py` - HTTP server implementation
2. `src/unhcr_iati_mcp/auth/` - Authentication package
   - `__init__.py`
   - `oauth.py` - OAuth 2.1 server
   - `middleware.py` - Authentication middleware
3. `docs/DEPLOYMENT.md` - Deployment guide
4. `docs/AUTHENTICATION.md` - Authentication documentation
5. `docs/GETTING_STARTED.md` - Getting started guide

### Modified Files
1. `src/unhcr_iati_mcp/server.py` - Add transport mode detection
2. `src/unhcr_iati_mcp/config.py` - Add new environment variables
3. `src/unhcr_iati_mcp/client.py` - Add support for token-based auth
4. `README.md` - Add HTTP mode and OAuth documentation
5. `Dockerfile` - Add dependencies for HTTP/OAuth
6. `docker-compose.yml` - Add HTTP mode configuration

---

## 🔗 References

- [TypeScript Implementation](.arc/mcp-iati-main/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OAuth 2.1 Specification](https://datatracker.ietf.org/doc/html/rfc9728)
- [IATI Datastore API](https://developer.iatistandard.org/)

---

*Review Date: July 3, 2024*  
*Reviewer: Mistral Vibe*  
*Status: COMPLETE*
