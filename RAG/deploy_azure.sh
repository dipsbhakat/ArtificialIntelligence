# Azure App Service deployment script
#!/bin/bash

# Set variables
RESOURCE_GROUP="rg-agrimayadev-5135_ai"
APP_NAME="rag-bot-app"
LOCATION="eastus"
PLAN_NAME="rag-bot-plan"

# Create App Service Plan
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --deployment-container-image-name nginx

# Configure app settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_NAME \
  --settings \
    AZURE_OPENAI_API_KEY="your-api-key" \
    AZURE_OPENAI_ENDPOINT="https://liftr-platorm-service.cognitiveservices.azure.com/" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002" \
    AZURE_OPENAI_API_VERSION="2024-12-01-preview"

echo "App deployed to: https://$APP_NAME.azurewebsites.net"
