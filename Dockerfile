# UNHCR IATI MCP Server Dockerfile
# Multi-stage build for production deployment
# Optimized for Azure Function App and Copilot Studio integration

# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY pyproject.toml .
COPY .env.example .
RUN pip install --no-cache-dir --user -e .

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ src/
COPY .env .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /root/.local
USER appuser

# Environment variables for HTTP mode (Copilot Studio compatible)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    MCP_TRANSPORT=http \
    USE_BUILTIN_OAUTH=true \
    AZURE_FUNCTION_APP=false

# Expose port for HTTP mode
EXPOSE 8000

# Health check for HTTP mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()" || exit 1

# Run the server in HTTP mode for Copilot Studio
CMD ["python", "-m", "unhcr_iati_mcp.server"]

# ============================================================================
# Azure Function App Dockerfile (Alternative)
# ============================================================================
# To build for Azure Functions, use:
# FROM mcr.microsoft.com/azure-functions/python:4.0-python3.12
# WORKDIR /home/site/wwwroot
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# ENV AzureWebJobsStorage=""
# ENV FUNCTIONS_WORKER_RUNTIME="python"
# ENV FUNCTIONS_EXTENSION_VERSION="~4"
# CMD ["func", "start"]
