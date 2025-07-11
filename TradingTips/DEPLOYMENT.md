# 🚀 Azure Deployment Guide

This guide will help you deploy your Advanced Trading Dashboard to Azure using Azure Container Registry (ACR) and Azure App Service.

## Prerequisites

- Azure CLI installed and logged in
- Docker installed (for local testing)
- Azure subscription with appropriate permissions
- Azure OpenAI service deployed

## Step 1: Prepare for Deployment

### 1.1 Test Locally First
```bash
# Test the application locally
python test_setup.py

# Run locally to ensure everything works
streamlit run enhanced_trading_app.py
```

### 1.2 Set Environment Variables
Ensure your `.env` file has the correct Azure OpenAI credentials:
```
AZURE_OPENAI_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

## Step 2: Azure Setup

### 2.1 Login to Azure
```bash
az login
az account list --output table
az account set --subscription "your-subscription-id"
```

### 2.2 Create Resource Group
```bash
az group create --name tradingtips-rg --location eastus
```

## Step 3: Container Registry Setup

### 3.1 Create Azure Container Registry
```bash
az acr create --resource-group tradingtips-rg --name tradingacr --sku Basic --admin-enabled true
```

### 3.2 Login to ACR
```bash
az acr login --name tradingacr
```

### 3.3 Build and Push Image
```bash
# Build the Docker image
docker build -t tradingacr.azurecr.io/trading-app:latest .

# Push to ACR
docker push tradingacr.azurecr.io/trading-app:latest
```

## Step 4: App Service Setup

### 4.1 Create App Service Plan
```bash
az appservice plan create \
  --name tradingtips-plan \
  --resource-group tradingtips-rg \
  --is-linux \
  --sku B1
```

### 4.2 Create Web App
```bash
az webapp create \
  --resource-group tradingtips-rg \
  --plan tradingtips-plan \
  --name tradingtips-app \
  --deployment-container-image-name tradingacr.azurecr.io/trading-app:latest
```

### 4.3 Configure Container Settings
```bash
# Configure the web app to use the container from ACR
az webapp config container set \
  --name tradingtips-app \
  --resource-group tradingtips-rg \
  --container-image-name tradingacr.azurecr.io/trading-app:latest \
  --container-registry-url https://tradingacr.azurecr.io
```

### 4.4 Set Environment Variables
```bash
az webapp config appsettings set \
  --resource-group tradingtips-rg \
  --name tradingtips-app \
  --settings \
    AZURE_OPENAI_KEY="your-azure-openai-key" \
    AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint" \
    AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
```

## Step 5: Configure Networking (Important!)

### 5.1 Get App Service Outbound IPs
```bash
az webapp show --name tradingtips-app --resource-group tradingtips-rg --query outboundIpAddresses --output tsv
```

### 5.2 Configure Azure OpenAI Network Access
1. Go to Azure Portal → Your Azure OpenAI resource
2. Navigate to "Networking" section
3. Under "Firewall", select "Selected networks and private endpoints"
4. Add the outbound IP addresses from Step 5.1
5. Save the configuration

## Step 6: Verify Deployment

### 6.1 Check App Status
```bash
az webapp show --name tradingtips-app --resource-group tradingtips-rg --query state
```

### 6.2 View Logs
```bash
az webapp log tail --name tradingtips-app --resource-group tradingtips-rg
```

### 6.3 Test the Application
Open your browser and navigate to: `https://tradingtips-app.azurewebsites.net`

## Step 7: Monitoring and Maintenance

### 7.1 Enable Application Insights (Optional)
```bash
az monitor app-insights component create \
  --app tradingtips-insights \
  --location eastus \
  --resource-group tradingtips-rg
```

### 7.2 Update Application
When you need to update the application:

```bash
# Build new image
docker build -t tradingacr.azurecr.io/trading-app:v2 .

# Push to ACR
docker push tradingacr.azurecr.io/trading-app:v2

# Update web app
az webapp config container set \
  --name tradingtips-app \
  --resource-group tradingtips-rg \
  --container-image-name tradingacr.azurecr.io/trading-app:v2
```

## Troubleshooting

### Common Issues

1. **App not starting**: Check logs with `az webapp log tail`
2. **Azure OpenAI connection failed**: Verify IP whitelisting in Azure OpenAI networking
3. **Container pull failed**: Ensure ACR credentials are correctly configured

### Useful Commands

```bash
# Restart the web app
az webapp restart --name tradingtips-app --resource-group tradingtips-rg

# Scale the app service plan
az appservice plan update --name tradingtips-plan --resource-group tradingtips-rg --sku S1

# View application settings
az webapp config appsettings list --name tradingtips-app --resource-group tradingtips-rg

# Delete resources (cleanup)
az group delete --name tradingtips-rg --yes --no-wait
```

## Security Best Practices

1. **Use Key Vault**: Store secrets in Azure Key Vault instead of environment variables
2. **Enable HTTPS**: Ensure HTTPS only access
3. **Network Restrictions**: Limit access to specific IP ranges if needed
4. **Regular Updates**: Keep container images updated

## Cost Optimization

1. **Use appropriate SKU**: Start with Basic (B1) and scale as needed
2. **Monitor usage**: Use Azure Cost Management
3. **Auto-shutdown**: Consider auto-shutdown for development environments

## Support

If you encounter issues:
1. Check Azure Status page
2. Review Azure documentation
3. Contact Azure support if needed

---

**Deployment Complete! 🎉**

Your Advanced Trading Dashboard should now be running on Azure. Access it at:
`https://tradingtips-app.azurewebsites.net`
