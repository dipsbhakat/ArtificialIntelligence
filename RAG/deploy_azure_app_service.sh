#!/bin/bash

# Azure App Service Deployment Script
# Run this script to deploy your RAG bot to Azure App Service

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="rg-agrimayadav-5135_ai"
APP_NAME="langchain-rag-bot-$(date +%s)"  # Unique name with timestamp
LOCATION="eastus"
SKU="B1"  # Basic tier
PYTHON_VERSION="3.11"

echo "🚀 Deploying LangChain RAG Bot to Azure App Service..."
echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   App Name: $APP_NAME"
echo "   Location: $LOCATION"
echo "   SKU: $SKU"
echo "   Python Version: $PYTHON_VERSION"
echo

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Please log in to Azure:"
    az login
fi

# Get current subscription
SUBSCRIPTION=$(az account show --query id -o tsv)
echo "✅ Using subscription: $SUBSCRIPTION"

# Check if resource group exists
echo "📁 Checking resource group..."
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "❌ Resource group '$RESOURCE_GROUP' not found!"
    echo "Please create it first or update the RESOURCE_GROUP variable in this script."
    exit 1
fi
echo "✅ Resource group exists"

# Create App Service Plan
echo "📊 Creating App Service Plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku $SKU \
    --is-linux

# Create App Service
echo "🌐 Creating App Service..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --runtime "PYTHON|$PYTHON_VERSION"

# Configure environment variables
echo "⚙️ Setting environment variables..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        AZURE_OPENAI_API_KEY="your-actual-api-key-here" \
        AZURE_OPENAI_ENDPOINT="https://liftr-platorm-service.cognitiveservices.azure.com/" \
        AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1" \
        AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002" \
        AZURE_OPENAI_API_VERSION="2024-12-01-preview" \
        DEFAULT_PROVIDER="azure" \
        WEBSITES_PORT="8501" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Set startup command
echo "🔧 Setting startup command..."
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "startup.sh"

# Deploy the code
echo "📦 Deploying code..."
az webapp deployment source config-zip \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --src "$(pwd)/deployment.zip"

# Wait for deployment to complete
echo "⏳ Waiting for deployment to complete..."
sleep 30

# Get the app URL
APP_URL=$(az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query hostNames[0] -o tsv)

echo
echo "🎉 Deployment completed successfully!"
echo "📋 App Details:"
echo "   App Name: $APP_NAME"
echo "   URL: https://$APP_URL"
echo "   Resource Group: $RESOURCE_GROUP"
echo
echo "⚠️  Important Next Steps:"
echo "1. Update the AZURE_OPENAI_API_KEY in the App Service configuration"
echo "2. Verify your Azure OpenAI deployments exist:"
echo "   - Chat deployment: gpt-4.1"
echo "   - Embedding deployment: text-embedding-ada-002"
echo "3. Test the application at: https://$APP_URL"
echo
echo "🔧 To update environment variables:"
echo "   az webapp config appsettings set --name $APP_NAME --resource-group $RESOURCE_GROUP --settings AZURE_OPENAI_API_KEY='your-actual-key'"
echo
echo "📊 To view logs:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo
echo "🗑️  To delete the app (if needed):"
echo "   az webapp delete --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo "   az appservice plan delete --name ${APP_NAME}-plan --resource-group $RESOURCE_GROUP"
