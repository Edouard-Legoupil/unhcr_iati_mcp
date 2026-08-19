#!/bin/bash
# Deployment script for Azure Function App
# This script creates a proper deployment package for Azure Functions v4 Python

set -e

echo "=== Azure Function App Deployment ==="
echo ""

# Configuration
FUNCTION_APP_NAME="unhcr-iati-mcp-function"
RESOURCE_GROUP="mcp"
DEPLOYMENT_PACKAGE="functionapp.zip"

# Clean up previous deployment package
if [ -f "$DEPLOYMENT_PACKAGE" ]; then
    rm "$DEPLOYMENT_PACKAGE"
    echo "Removed previous deployment package: $DEPLOYMENT_PACKAGE"
fi

# Create deployment package
echo "Creating deployment package..."
zip -r "$DEPLOYMENT_PACKAGE" \
    function_app.py \
    host.json \
    requirements.txt \
    .deployment \
    src/ \
    -x "*.git*" \
    -x "*.vscode*" \
    -x "logs/*" \
    -x "metrics/*" \
    -x "tests/*" \
    -x ".venv/*" \
    -x "azure-deploy/*" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x ".Python" \
    -x "build/*" \
    -x "dist/*" \
    -x "*.egg-info/*" \
    -x ".installed.cfg" \
    -x "*.md" \
    -x "docker-compose.yml" \
    -x "Dockerfile" \
    -x "dockerignore" \
    -x ".env" \
    -x "local.settings.json"

echo "Deployment package created: $DEPLOYMENT_PACKAGE"
echo ""

# Verify package contents
echo "Package contents:"
zip -l "$DEPLOYMENT_PACKAGE" | grep -E "(function_app|host\.json|requirements|src/|\.deployment)" | head -10

echo ""
echo "=== Deploying to Azure ==="

# Deploy to Azure
az functionapp deployment source config-zip \
    -g "$RESOURCE_GROUP" \
    -n "$FUNCTION_APP_NAME" \
    --src "$DEPLOYMENT_PACKAGE" \
    --target-path /home/site/wwwroot

echo ""
echo "=== Deployment Complete ==="
echo "Verifying deployment..."

# Verify deployment
az functionapp function list \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP"

echo ""
echo "=== Cleanup ==="
rm "$DEPLOYMENT_PACKAGE"
echo "Removed deployment package: $DEPLOYMENT_PACKAGE"
