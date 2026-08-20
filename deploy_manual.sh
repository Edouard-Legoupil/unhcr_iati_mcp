#!/bin/bash
# Manual deployment commands for Azure Function App

echo "=== Step 1: Create deployment package ==="
zip -r functionapp.zip \
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
    -x "local.settings.json" \
    -x "deploy_*.sh" \
    -x "DEPLOYMENT_FIX.md"

echo ""
echo "=== Step 2: Verify package contents ==="
zip -l functionapp.zip | grep -E "(function_app|host\.json|requirements|src/|\.deployment)" | head -10

echo ""
echo "=== Step 3: Deploy to Azure (run this command manually) ==="
echo "az functionapp deployment source config-zip \\"
echo "  -g mcp \\"
echo "  -n unhcr-iati-mcp-function \\"
echo "  --src functionapp.zip"

echo ""
echo "=== Step 4: Verify deployment (run these commands manually) ==="
echo "az functionapp function list --name unhcr-iati-mcp-function --resource-group mcp"
echo ""
echo "=== Step 5: Cleanup ==="
echo "rm functionapp.zip"
