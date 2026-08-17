# Azure Deployment for UNHCR IATI MCP Server

This directory contains configuration files for deploying the UNHCR IATI MCP Server to Azure Function App for Microsoft Copilot Studio integration.

## 📁 Directory Structure

```
azure-deploy/
├── README.md                    # This file
├── function.json                # Azure Function App configuration
├── host.json                   # Azure Functions host configuration
├── local.settings.json.example # Local development settings template
├── requirements.txt            # Python dependencies for Azure
├── requirements.azure.txt     # Azure-specific dependencies
└── deployment/
    ├── arm/                    # ARM templates
    │   └── deploy.json         # ARM template for deployment
    └── bicep/                 # Bicep templates
        └── main.bicep          # Bicep template for deployment
```

## 🚀 Quick Deployment

### Prerequisites

1. **Azure CLI** installed and logged in
2. **Azure Functions Core Tools** v4.x installed
3. **Python 3.12+** installed
4. **Valid IATI API Key** from https://developer.iatistandard.org/

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd unhcr_iati_mcp

# Copy Azure deployment files
cp -r azure-deploy/* .

# Create local settings
cp azure-deploy/local.settings.json.example local.settings.json

# Edit local.settings.json with your IATI API key
```

### Step 2: Create Azure Resources

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "Your-Subscription-Name"

# Create resource group
az group create --name unhcr-mcp-rg --location eastus

# Create storage account
az storage account create \
  --name unhcrmcpstorage$(date +%s) \
  --location eastus \
  --resource-group unhcr-mcp-rg \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --name unhcr-iati-mcp-$(date +%s) \
  --resource-group unhcr-mcp-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.12 \
  --functions-version 4 \
  --storage-account unhcrmcpstorage$(date +%s) \
  --os-type Linux
```

### Step 3: Deploy

```bash
# Deploy using Azure Functions Core Tools
func azure functionapp publish unhcr-iati-mcp-$(date +%s)

# Or use Azure CLI
az functionapp deployment source config-zip \
  --name unhcr-iati-mcp-$(date +%s) \
  --resource-group unhcr-mcp-rg \
  --src ./deploy.zip
```

### Step 4: Configure Environment Variables

```bash
# Set required environment variables
az functionapp config appsettings set \
  --name unhcr-iati-mcp-$(date +%s) \
  --resource-group unhcr-mcp-rg \
  --settings \
    IATI_API_KEY="your-iati-subscription-key" \
    IATI_BASE_URL="https://api.iatistandard.org/datastore" \
    UNHCR_PUBLISHER_REF="XM-DAC-41121" \
    MCP_TRANSPORT="http" \
    USE_BUILTIN_OAUTH="true" \
    AZURE_FUNCTION_APP="true"
```

### Step 5: Configure SSL Certificate

```bash
# Enable managed certificate (recommended)
az functionapp config ssl create \
  --name unhcr-iati-mcp-$(date +%s) \
  --resource-group unhcr-mcp-rg \
  --certificate-name mcp-cert \
  --server-name unhcr-iati-mcp-$(date +%s).azurewebsites.net

# Bind certificate
az functionapp config ssl bind \
  --name unhcr-iati-mcp-$(date +%s) \
  --resource-group unhcr-mcp-rg \
  --certificate-name mcp-cert \
  --ssl-type SNI
```

## 🔧 Configuration Files

### function.json

Azure Function App configuration for MCP endpoints:

```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpAuth",
      "direction": "in"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": "mcp/{*path}",
      "methods": ["get", "post", "put", "delete", "options", "head"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": "oauth/token",
      "methods": ["post"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": ".well-known/oauth-authorization-server",
      "methods": ["get"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": ".well-known/jwks.json",
      "methods": ["get"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": ".well-known/oauth-protected-resource",
      "methods": ["get"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": ".well-known/mcp/schema",
      "methods": ["get"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": "health",
      "methods": ["get"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": "info",
      "methods": ["get"],
      "authLevel": "anonymous"
    },
    {
      "type": "http",
      "direction": "in",
      "name": "req",
      "route": "openapi.json",
      "methods": ["get"],
      "authLevel": "anonymous"
    }
  ]
}
```

### host.json

Azure Functions host configuration:

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.0.0, 5.0.0)"
  },
  "functionTimeout": "00:10:00",
  "functions": {
    "mcp": {
      "maxConcurrentRequests": 100,
      "maxOutstandingRequests": 200
    }
  }
}
```

## 🔐 Security Configuration

### SSL/TLS Requirements

Copilot Studio **requires HTTPS**. You must configure SSL certificates:

1. **Azure Managed Certificate** (Recommended)
2. **Bring Your Own Certificate** (BYOC)
3. **Let's Encrypt** (via Azure App Service Custom Domains)

### Authentication

The MCP server supports two authentication methods:

1. **OAuth 2.1** (Recommended for Copilot Studio)
   - Client Credentials Grant
   - RS256-signed JWT tokens
   - JWKS endpoint for token verification

2. **X-API-Key Header** (Fallback)
   - Simple API key authentication
   - Compatible with HuggingChat and other clients

### CORS Configuration

CORS is configured to allow:
- Microsoft Copilot Studio domains
- Local development domains
- All origins for public endpoints

## 📊 Monitoring and Logging

### Application Insights

Enable Application Insights for monitoring:

```bash
# Enable Application Insights
az functionapp config appsettings set \
  --name unhcr-iati-mcp \
  --resource-group unhcr-mcp-rg \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

### Log Analytics

Configure Log Analytics workspace:

```bash
az monitor log-analytics workspace create \
  --name mcp-logs \
  --resource-group unhcr-mcp-rg \
  --location eastus

az functionapp diagnostic-settings set \
  --name unhcr-iati-mcp \
  --resource-group unhcr-mcp-rg \
  --workspace-id /subscriptions/.../resourceGroups/unhcr-mcp-rg/providers/Microsoft.OperationalInsights/workspaces/mcp-logs
```

## 🧪 Testing

### Test Endpoints

```bash
# Test health endpoint
curl https://unhcr-iati-mcp.azurewebsites.net/api/health

# Test MCP schema endpoint
curl https://unhcr-iati-mcp.azurewebsites.net/.well-known/mcp/schema

# Test OAuth metadata
curl https://unhcr-iati-mcp.azurewebsites.net/.well-known/oauth-authorization-server

# Test JWKS endpoint
curl https://unhcr-iati-mcp.azurewebsites.net/.well-known/jwks.json

# Test token endpoint
curl -X POST https://unhcr-iati-mcp.azurewebsites.net/api/oauth/token \
  -d "grant_type=client_credentials&client_id=default&client_secret=YOUR_IATI_API_KEY"

# Test MCP endpoint
curl -X POST https://unhcr-iati-mcp.azurewebsites.net/api/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Test Copilot Studio Integration

1. **Create Custom Connector** in Copilot Studio
2. **Configure Connection** with your Function App URL
3. **Test Connection** to verify schema retrieval
4. **Test Tool Discovery** to verify tools are discovered
5. **Test Tool Execution** to verify tools work correctly

## 📚 Resources

- [Azure Function App Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Functions Python Developer Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Microsoft Copilot Studio Documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [OAuth 2.1 Specification](https://datatracker.ietf.org/doc/html/rfc9728)

## 🆘 Troubleshooting

### Common Issues

**1. Function App fails to start**
- Check Application Insights logs
- Verify all required environment variables are set
- Check Python version compatibility

**2. SSL certificate not working**
- Verify certificate is bound to the Function App
- Check certificate hostname matches Function App hostname
- Ensure certificate is not expired

**3. Copilot Studio cannot connect**
- Verify HTTPS is configured correctly
- Check CORS headers are properly set
- Verify OAuth endpoints are accessible
- Test MCP schema endpoint is publicly accessible

**4. Authentication failures**
- Verify IATI API key is valid
- Check OAuth token endpoint is working
- Verify JWKS endpoint is accessible
- Test token verification locally

### Debug Commands

```bash
# View Function App logs
az webapp log tail --name unhcr-iati-mcp --resource-group unhcr-mcp-rg

# View Application Insights logs
az monitor app-insights query \
  --app unhcr-iati-mcp \
  --resource-group unhcr-mcp-rg \
  --query "requests | take 10"

# Test locally before deployment
func start

# Test with curl
curl -v http://localhost:7071/api/health
```

## 🎯 Best Practices

1. **Use Managed Identity** for accessing other Azure resources
2. **Enable Auto-scaling** for high availability
3. **Configure Backup** for Function App settings
4. **Use Key Vault** for storing secrets
5. **Enable DDoS Protection** for production deployments
6. **Configure Auto-healing** for unhealthy instances
7. **Use Private Endpoints** for internal resources
8. **Enable IP Restrictions** for additional security