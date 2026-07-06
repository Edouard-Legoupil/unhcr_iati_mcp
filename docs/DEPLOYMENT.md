# Deployment

This document provides comprehensive deployment instructions for the UNHCR IATI MCP Server.

## Quick Start

### Prerequisites

- **Python**: 3.11+ (recommended: 3.12)
- **Package Manager**: Poetry or pip
- **Container Runtime**: Docker (optional, for containerized deployment)
- **API Key**: IATI Datastore subscription key (required)

## Installation Methods

### Using pip (recommended for development)

```bash
# Clone the repository
git clone <repository-url>
cd unhcr_iati_mcp

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your IATI API key
```

### Using Poetry

```bash
# Clone the repository
git clone <repository-url>
cd unhcr_iati_mcp

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your IATI API key
```

## Running the Server

### Development Mode

```bash
# Run the server
python -m unhcr_iati_mcp.server

# Or with module syntax
python -m src.unhcr_iati_mcp.server

# With explicit logging level
LOG_LEVEL=DEBUG python -m unhcr_iati_mcp.server
```

Note: FastMCP uses MCP protocol. Port configuration depends on the MCP client being used.

### Docker Deployment

#### Build the Image

```bash
# Build using docker-compose
docker-compose build

# Or build manually
docker build -t unhcr-iati-mcp:latest .
```

#### Run the Container

```bash
# Using docker-compose
docker-compose up -d

# With environment variables
docker-compose run --env-file .env mcp

# Manual docker run
docker run -d \
  --name unhcr-iati-mcp \
  -p 8000:8000 \
  -e IATI_API_KEY=your-key \
  -e IATI_BASE_URL=https://api.iatistandard.org/datastore \
  -e UNHCR_PUBLISHER_REF=XM-DAC-41121 \
  unhcr-iati-mcp:latest
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Required
IATI_API_KEY="your-iati-subscription-key"
IATI_BASE_URL="https://api.iatistandard.org/datastore"
UNHCR_PUBLISHER_REF="XM-DAC-41121"

# Optional (with defaults shown)
TIMEOUT_SECONDS=120
PAGE_SIZE=1000
LOG_LEVEL="INFO"
```

**Note**: UNHCR's publisher reference in IATI is `XM-DAC-41121`. This is the standard identifier for UNHCR in the IATI registry.

### Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `IATI_API_KEY` | string | **Required** | IATI Datastore API subscription key |
| `IATI_BASE_URL` | string | `https://api.iatistandard.org/datastore` | Base URL for IATI Datastore API |
| `UNHCR_PUBLISHER_REF` | string | `XM-DAC-41121` | UNHCR's publisher reference in IATI |
| `TIMEOUT_SECONDS` | integer | `120` | HTTP request timeout in seconds |
| `PAGE_SIZE` | integer | `1000` | Default number of records per page |
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Docker Compose Configuration

The `docker-compose.yml` file provides a complete development stack:

```yaml
version: '3.8'

services:
  mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - IATI_API_KEY=${IATI_API_KEY}
      - IATI_BASE_URL=${IATI_BASE_URL}
      - UNHCR_PUBLISHER_REF=${UNHCR_PUBLISHER_REF}
      - TIMEOUT_SECONDS=${TIMEOUT_SECONDS:-120}
      - PAGE_SIZE=${PAGE_SIZE:-1000}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - .:/app
    restart: unless-stopped
```

## Production Deployment

### Recommended Production Setup

1. **Use a production-grade MCP client** (e.g., FastMCP with production configuration)
2. **Configure proper logging** with rotation and centralized logging
3. **Set up monitoring** with Prometheus and Grafana
4. **Use a process manager** (systemd, supervisor, or Kubernetes)
5. **Configure proper security** for API keys

### Security Considerations

- **API Key Management**: Store IATI API key in a secrets manager or encrypted configuration
- **Network Security**: Use firewalls to restrict access to the MCP server
- **TLS**: Enable TLS for all external communications
- **Rate Limiting**: Configure rate limiting at the proxy level

### Environment-Specific Configuration

Create separate configuration files for different environments:

```bash
# .env.production
IATI_API_KEY="production-key"
LOG_LEVEL="WARNING"
TIMEOUT_SECONDS=180
PAGE_SIZE=2000

# .env.staging
IATI_API_KEY="staging-key"
LOG_LEVEL="INFO"
TIMEOUT_SECONDS=120
PAGE_SIZE=1000

# .env.development
IATI_API_KEY="development-key"
LOG_LEVEL="DEBUG"
TIMEOUT_SECONDS=60
PAGE_SIZE=500
```

## Kubernetes Deployment

### Sample Kubernetes Manifest

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unhcr-iati-mcp
  labels:
    app: unhcr-iati-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: unhcr-iati-mcp
  template:
    metadata:
      labels:
        app: unhcr-iati-mcp
    spec:
      containers:
      - name: mcp
        image: unhcr-iati-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: IATI_API_KEY
          valueFrom:
            secretKeyRef:
              name: iati-secrets
              key: api-key
        - name: IATI_BASE_URL
          value: "https://api.iatistandard.org/datastore"
        - name: UNHCR_PUBLISHER_REF
          value: "XM-DAC-41121"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "500m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: unhcr-iati-mcp
spec:
  selector:
    app: unhcr-iati-mcp
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# ingress.yaml (optional)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: unhcr-iati-mcp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - mcp.unhcr.example.com
    secretName: mcp-tls
  rules:
  - host: mcp.unhcr.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: unhcr-iati-mcp
            port:
              number: 80
```

## CI/CD Pipeline

### Sample GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest
    - name: Run tests
      run: pytest tests/

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_TOKEN }}
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: user/app:latest
    - name: Deploy to Kubernetes
      run: |
        # Apply Kubernetes manifests
        kubectl apply -f k8s/
```

## Dockerfile

The provided `Dockerfile` is optimized for production:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from unhcr_iati_mcp.server import health_check; health_check()" || exit 1

# Run the server
CMD ["python", "-m", "unhcr_iati_mcp.server"]
```

## Troubleshooting Deployment

### Common Issues

**Server fails to start**:
- Check that `IATI_API_KEY` is set in the environment
- Verify the API key is valid
- Check network connectivity to the IATI Datastore

**Docker build fails**:
- Ensure Docker is installed and running
- Check Python version compatibility
- Verify all dependencies are available

**Container exits immediately**:
- Check container logs: `docker logs unhcr-iati-mcp`
- Verify all required environment variables are set
- Check for import errors or missing dependencies

**Connection timeout**:
- Increase `TIMEOUT_SECONDS` in configuration
- Check network connectivity and firewalls
- Verify DNS resolution

### Debugging Tools

```bash
# Check container logs
docker-compose logs mcp

# Run container interactively
docker-compose run mcp bash

# Check running containers
docker-compose ps

# View environment variables
docker-compose exec mcp env

# Test API connection from within container
docker-compose exec mcp curl -H "Ocp-Apim-Subscription-Key: $IATI_API_KEY" \
  "https://api.iatistandard.org/datastore/activity/select?q=*:*&rows=1"
```

## Scaling Considerations

### Horizontal Scaling

The MCP server is stateless and can be scaled horizontally. However, consider:

- **Rate Limiting**: IATI Datastore may have rate limits per API key
- **Caching**: Code tables are cached in memory; consider a shared cache (Redis) for multi-instance deployments
- **Connection Pooling**: Each instance maintains its own connection pool

### Performance Optimization

- **Connection Pool Size**: Adjust based on expected concurrent requests
- **Cache Size**: Monitor cache memory usage and adjust as needed
- **Timeout Values**: Tune timeouts based on network conditions
- **Pagination**: Use appropriate page sizes for typical queries

### Resource Requirements

- **CPU**: Light to moderate usage (mostly I/O bound)
- **Memory**: Minimum 256MB, recommended 512MB+ for large datasets
- **Network**: Good connectivity to IATI Datastore API
