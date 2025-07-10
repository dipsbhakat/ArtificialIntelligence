# Azure App Service Deployment Guide for LangChain RAG Bot

## Quick Start

### 1. Prerequisites
- Azure CLI installed and configured
- Azure subscription with Azure OpenAI resource
- Resource group: `rg-agrimayadav-5135_ai`
- Azure OpenAI deployments: `gpt-4.1` and `text-embedding-ada-002`

### 2. One-Click Deployment

#### Option A: PowerShell (Windows)
```powershell
.\deploy_azure_app_service.ps1
```

#### Option B: Bash (Linux/Mac/WSL)
```bash
chmod +x deploy_azure_app_service.sh
./deploy_azure_app_service.sh
```

### 3. Manual Azure Portal Deployment

#### Step 1: Create App Service
1. Go to [Azure Portal](https://portal.azure.com)
2. Create App Service
   - **Name**: `langchain-rag-bot-[unique]`
   - **Resource Group**: `rg-agrimayadav-5135_ai`
   - **Runtime**: Python 3.11
   - **Region**: East US
   - **Plan**: Basic B1 ($13/month)

#### Step 2: Configure Environment Variables
In App Service → Configuration → Application Settings:

| Setting | Value |
|---------|-------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | `https://liftr-platorm-service.cognitiveservices.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-4.1` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | `text-embedding-ada-002` |
| `AZURE_OPENAI_API_VERSION` | `2024-12-01-preview` |
| `DEFAULT_PROVIDER` | `azure` |
| `WEBSITES_PORT` | `8501` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

#### Step 3: Set Startup Command
In App Service → Configuration → General Settings:
- **Startup Command**: `startup.sh`

#### Step 4: Deploy Code
Choose one:
- **ZIP Deploy**: Upload project as ZIP
- **GitHub Actions**: Connect to repository
- **Local Git**: Push to App Service Git repository

### 4. Container Deployment

#### Build and Push to Azure Container Registry
```bash
# Build Docker image
docker build -t langchain-rag-bot .

# Tag for ACR
docker tag langchain-rag-bot your-acr.azurecr.io/langchain-rag-bot:latest

# Push to registry
docker push your-acr.azurecr.io/langchain-rag-bot:latest
```

#### Deploy Container to App Service
```bash
az webapp create \
    --resource-group rg-agrimayadav-5135_ai \
    --plan your-app-service-plan \
    --name your-app-name \
    --deployment-container-image-name your-acr.azurecr.io/langchain-rag-bot:latest
```

## Configuration Details

### Required Azure OpenAI Deployments

1. **Chat Deployment**: `gpt-4.1`
   - Model: GPT-4 or GPT-4 Turbo
   - Use for: Question answering

2. **Embedding Deployment**: `text-embedding-ada-002`
   - Model: text-embedding-ada-002
   - Use for: Document processing and search

### App Service Tiers

#### Basic B1 ($13/month)
- 1.75 GB RAM, 1 vCPU
- Good for: Development and testing
- Limitations: No auto-scaling

#### Standard S1 ($73/month)
- 1.75 GB RAM, 1 vCPU
- Features: Auto-scaling, custom domains
- Good for: Small production workloads

#### Premium P1V3 ($146/month)
- 8 GB RAM, 2 vCPU
- Features: VNet integration, advanced scaling
- Good for: High-traffic production

### Security Best Practices

#### Use Azure Key Vault
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
api_key = client.get_secret("azure-openai-api-key").value
```

#### Enable Managed Identity
- System-assigned identity for secure resource access
- No need to store secrets in environment variables

## Monitoring and Troubleshooting

### Application Insights Setup
1. Create Application Insights resource
2. Add instrumentation key to app settings
3. Monitor performance and errors

### Common Issues

#### App Won't Start
- Check startup command: `startup.sh`
- Verify Python version: 3.11
- Check environment variables

#### Azure OpenAI Errors
- Verify API key is correct
- Check deployment names match exactly
- Ensure deployments are in "Succeeded" status

#### Performance Issues
- Monitor CPU and memory usage
- Consider upgrading to higher tier
- Implement caching for frequent queries

### Viewing Logs
```bash
# Stream logs
az webapp log tail --name your-app-name --resource-group rg-agrimayadev-5135_ai

# Download logs
az webapp log download --name your-app-name --resource-group rg-agrimayadev-5135_ai
```

## Cost Optimization

### Expected Monthly Costs
- **App Service B1**: $13
- **Azure OpenAI**: $0.002/1K tokens (GPT-4)
- **Storage**: ~$1-5 depending on usage
- **Total**: ~$20-50/month for moderate usage

### Cost-Saving Tips
1. Use auto-scaling to scale down during low usage
2. Consider reserved instances for 1-3 year commitments (30-70% savings)
3. Monitor token usage and optimize prompts
4. Use cheaper models when appropriate

## Scaling Considerations

### Auto-Scaling Rules
Set up rules based on:
- CPU percentage > 70%
- Memory percentage > 80%
- HTTP queue length > 100

### Load Testing
Test your app with:
- Multiple concurrent PDF uploads
- High query volumes
- Large document processing

## Support and Maintenance

### Regular Updates
- Update Python dependencies monthly
- Monitor Azure OpenAI API updates
- Review security patches

### Backup Strategy
- Regular database backups (if using external DB)
- Source code in version control
- Configuration backup

### Health Monitoring
- Set up Application Insights alerts
- Monitor response times
- Track error rates

## Next Steps After Deployment

1. **Test the application** with sample PDFs
2. **Configure custom domain** and SSL certificate
3. **Set up monitoring** and alerts
4. **Implement CI/CD pipeline** for updates
5. **Document user guide** for end users
6. **Plan scaling strategy** based on usage patterns

## Troubleshooting Commands

```bash
# Check app status
az webapp show --name your-app-name --resource-group rg-agrimayadev-5135_ai

# Restart app
az webapp restart --name your-app-name --resource-group rg-agrimayadev-5135_ai

# Update environment variable
az webapp config appsettings set \
    --name your-app-name \
    --resource-group rg-agrimayadev-5135_ai \
    --settings AZURE_OPENAI_API_KEY="new-key"

# Check deployment logs
az webapp log deployment show --name your-app-name --resource-group rg-agrimayadev-5135_ai
```
