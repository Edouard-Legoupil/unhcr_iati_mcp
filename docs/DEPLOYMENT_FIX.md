# Azure Function App Deployment Fix

## Problem
The Azure Function App was only deploying `host.json` to `/home/site/wwwroot`, resulting in:
- "No HTTP routes mapped"
- 0 functions found
- Container startup failures

## Root Cause
1. **`.funcignore` was excluding critical files** (Dockerfile, docker-compose.yml, etc.) which may have confused the deployment system
2. **Missing `.deployment` file** to guide Oryx build system
3. **Deployment method mismatch** - If using ZIP deploy or GitHub Actions, `.funcignore` is ignored

## Minimal Fix Applied

### 1. Fixed `.funcignore`
**Before:**
```bash
# Docker
Dockerfile
docker-compose.yml
dockerignore

# OS files
.DS_Store
Thumbs.db

src/unhcr_iati_mcp/server_local.py
```

**After:**
```bash
# OS files
.DS_Store
Thumbs.db

# Explicitly include required files for Azure Functions deployment
!function_app.py
!host.json
!requirements.txt
!src/
```

**Changes:**
- Removed `Dockerfile`, `docker-compose.yml`, `dockerignore` exclusions (these were not needed)
- Removed `src/unhcr_iati_mcp/server_local.py` exclusion (was too specific)
- Added explicit inclusions for critical files using `!` prefix

### 2. Added `.deployment` File
Created `.deployment` to guide Oryx build system:
```ini
[config]
SCM_SCRIPT_GENERATOR_ARGS = --python --targetPath .
```

### 3. Created Deployment Script
Created `deploy_azure.sh` for reliable deployment:
```bash
#!/bin/bash
zip -r functionapp.zip function_app.py host.json requirements.txt .deployment src/ -x "exclusions..."
az functionapp deployment source config-zip -g mcp -n unhcr-iati-mcp-function --src functionapp.zip
```

## Files Modified
- `.funcignore` - Fixed exclusions and added inclusions

## Files Created
- `.deployment` - Oryx build configuration
- `deploy_azure.sh` - Deployment script

## Deployment Instructions

### Option 1: Using the Deployment Script
```bash
chmod +x deploy_azure.sh
./deploy_azure.sh
```

### Option 2: Manual ZIP Deploy
```bash
# Create ZIP package
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
    -x ".venv/*"

# Deploy to Azure
az functionapp deployment source config-zip \
    -g mcp \
    -n unhcr-iati-mcp-function \
    --src functionapp.zip
```

### Option 3: Using func CLI
```bash
func azure functionapp publish unhcr-iati-mcp-function
```

## Verification

### 1. Check Deployed Files
```bash
az webapp ssh --name unhcr-iati-mcp-function --resource-group mcp
ls -la /home/site/wwwroot
```
**Expected Output:**
```
host.json
function_app.py
requirements.txt
src/
```

### 2. List Deployed Functions
```bash
az functionapp function list --name unhcr-iati-mcp-function --resource-group mcp
```
**Expected Output:** List of functions (mcp, health, info, etc.)

### 3. Test Endpoints
```bash
curl https://unhcr-iati-mcp-function.azurewebsites.net/api/health
curl https://unhcr-iati-mcp-function.azurewebsites.net/api/mcp
```
**Expected:** HTTP 200 responses

## Notes
- The `.funcignore` file is only used by `func azure functionapp publish`
- For ZIP deploy or GitHub Actions, use the `.deployment` file and explicit ZIP creation
- The `!` prefix in `.funcignore` forces inclusion of files that would otherwise be excluded
