# PowerShell script to automate packaging and deployment of Flask app to Azure App Service
# Fill in your Azure resource group and app service name below

$resourceGroup = "<YourResourceGroup>"
$appServiceName = "<YourAppServiceName>"
$deploymentZip = "deployment_flask_gunicorn.zip"

# Remove old zip if exists
if (Test-Path $deploymentZip) { Remove-Item $deploymentZip }

# Create deployment zip (include all files in root and subfolders)
Compress-Archive -Path * -DestinationPath $deploymentZip -Force

# Deploy to Azure App Service
az webapp deployment source config-zip `
  --resource-group $resourceGroup `
  --name $appServiceName `
  --src $deploymentZip

# Restart the app
az webapp restart --resource-group $resourceGroup --name $appServiceName

# Tail the logs (optional, comment out if not needed)
az webapp log tail --resource-group $resourceGroup --name $appServiceName
