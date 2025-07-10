# PowerShell script for Azure App Service deployment

param(
    [string]$ResourceGroup = "rg-agrimayadav-5135_ai",
    [string]$Location = "eastus",
    [string]$SKU = "B1"
)

$AppName = "langchain-rag-bot-$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "🚀 Deploying LangChain RAG Bot to Azure App Service..." -ForegroundColor Green
Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "   App Name: $AppName" -ForegroundColor White
Write-Host "   Location: $Location" -ForegroundColor White
Write-Host "   SKU: $SKU" -ForegroundColor White

# Check if Azure CLI is installed
try {
    az --version | Out-Null
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor White
    exit 1
}

# Check Azure login
Write-Host "🔐 Checking Azure login status..." -ForegroundColor Yellow
try {
    $subscription = az account show --query id -o tsv
    if (-not $subscription) {
        Write-Host "Please log in to Azure:" -ForegroundColor Yellow
        az login
        $subscription = az account show --query id -o tsv
    }
    Write-Host "✅ Using subscription: $subscription" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to get Azure subscription. Please log in first." -ForegroundColor Red
    exit 1
}

# Check resource group
Write-Host "📁 Checking resource group..." -ForegroundColor Yellow
try {
    az group show --name $ResourceGroup | Out-Null
    Write-Host "✅ Resource group exists" -ForegroundColor Green
} catch {
    Write-Host "❌ Resource group '$ResourceGroup' not found!" -ForegroundColor Red
    Write-Host "Please create it first or update the ResourceGroup parameter." -ForegroundColor White
    exit 1
}

# Create App Service Plan
Write-Host "📊 Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name "$AppName-plan" `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku $SKU `
    --is-linux

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create App Service Plan" -ForegroundColor Red
    exit 1
}

# Create App Service
Write-Host "🌐 Creating App Service..." -ForegroundColor Yellow
az webapp create `
    --name $AppName `
    --resource-group $ResourceGroup `
    --plan "$AppName-plan" `
    --runtime "PYTHON:3.11"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create App Service" -ForegroundColor Red
    exit 1
}

# Configure environment variables
Write-Host "⚙️ Setting environment variables..." -ForegroundColor Yellow
az webapp config appsettings set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --settings `
        AZURE_OPENAI_API_KEY="BrX3wG0nYcgfkL3brx0zDH5fqqaO2Smhjd5Mshgjx7GE8cQNrgNtJQQJ99BDAC4f1cMXJ3w3AAAAACOGKUXR" `
        AZURE_OPENAI_ENDPOINT="https://liftr-platorm-service.cognitiveservices.azure.com/" `
        AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1" `
        AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002" `
        AZURE_OPENAI_API_VERSION="2024-12-01-preview" `
        DEFAULT_PROVIDER="azure" `
        WEBSITES_PORT="8501" `
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

# Set startup command
Write-Host "🔧 Setting startup command..." -ForegroundColor Yellow
az webapp config set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --startup-file "startup.sh"

# Create deployment package
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow
if (Test-Path "deployment.zip") {
    Remove-Item "deployment.zip"
}

# Create ZIP file excluding unnecessary files
$excludePatterns = @("*.git*", "*.env*", "__pycache__", "*.pyc", "venv", "node_modules")
Compress-Archive -Path "src", "requirements.txt", "startup.sh", "pdfs" -DestinationPath "deployment.zip"

# Deploy the code
Write-Host "🚀 Deploying application..." -ForegroundColor Yellow
az webapp deployment source config-zip `
    --name $AppName `
    --resource-group $ResourceGroup `
    --src "deployment.zip"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}

# Wait for deployment
Write-Host "⏳ Waiting for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Get app URL
$appUrl = az webapp show --name $AppName --resource-group $ResourceGroup --query hostNames[0] -o tsv

Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "📋 App Details:" -ForegroundColor Cyan
Write-Host "   App Name: $AppName" -ForegroundColor White
Write-Host "   URL: https://$appUrl" -ForegroundColor White
Write-Host "   Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Important Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update the AZURE_OPENAI_API_KEY in the App Service configuration" -ForegroundColor White
Write-Host "2. Verify your Azure OpenAI deployments exist:" -ForegroundColor White
Write-Host "   - Chat deployment: gpt-4.1" -ForegroundColor White
Write-Host "   - Embedding deployment: text-embedding-ada-002" -ForegroundColor White
Write-Host "3. Test the application at: https://$appUrl" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To update environment variables:" -ForegroundColor Cyan
Write-Host "   az webapp config appsettings set --name $AppName --resource-group $ResourceGroup --settings AZURE_OPENAI_API_KEY='your-actual-key'" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 To view logs:" -ForegroundColor Cyan
Write-Host "   az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
Write-Host ""
Write-Host "🗑️  To delete the app (if needed):" -ForegroundColor Cyan
Write-Host "   az webapp delete --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
Write-Host "   az appservice plan delete --name $AppName-plan --resource-group $ResourceGroup" -ForegroundColor Gray

# Cleanup
Remove-Item "deployment.zip" -ErrorAction SilentlyContinue
