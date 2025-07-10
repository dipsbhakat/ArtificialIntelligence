# Azure App Service Deployment for LangChain RAG Bot

This guide will help you deploy your LangChain RAG bot to Azure App Service.

## Prerequisites

1. **Azure Account** with an active subscription
2. **Azure CLI** installed and configured
3. **Azure OpenAI Service** with deployments
4. **Resource Group** for your app service

## Quick Deployment Steps

### 1. Prepare Your Environment

Create a `.env` file with your Azure OpenAI credentials:

```bash
AZURE_OPENAI_API_KEY=your-actual-api-key-here
AZURE_OPENAI_ENDPOINT=https://liftr-platorm-service.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-12-01-preview
DEFAULT_PROVIDER=azure
```

### 2. Azure App Service Configuration

Your app will run on:
- **Python 3.11**
- **Streamlit** as the web framework
- **Port 8501** (Streamlit default)

### 3. Deployment Options

#### Option A: Azure CLI Deployment (Recommended)
```bash
# Run the deployment script
./deploy_azure_app_service.sh
```

#### Option B: Azure Portal Deployment
1. Create App Service in Azure Portal
2. Configure Python 3.11 runtime
3. Set environment variables
4. Deploy code via GitHub Actions or ZIP

#### Option C: Docker Container Deployment
```bash
# Build and deploy as container
docker build -t rag-bot .
docker tag rag-bot your-registry.azurecr.io/rag-bot:latest
docker push your-registry.azurecr.io/rag-bot:latest
```

### 4. Environment Variables to Set in App Service

In Azure Portal → Your App Service → Configuration → Application Settings:

| Name | Value |
|------|-------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | https://liftr-platorm-service.cognitiveservices.azure.com/ |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | gpt-4.1 |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | text-embedding-ada-002 |
| `AZURE_OPENAI_API_VERSION` | 2024-12-01-preview |
| `DEFAULT_PROVIDER` | azure |
| `WEBSITES_PORT` | 8501 |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | true |

### 5. Scaling Configuration

#### Basic Tier (B1)
- **Cost**: ~$13/month
- **Memory**: 1.75 GB
- **CPU**: 1 core
- **Good for**: Development/Testing

#### Standard Tier (S1)
- **Cost**: ~$73/month  
- **Memory**: 1.75 GB
- **CPU**: 1 core
- **Features**: Auto-scaling, custom domains
- **Good for**: Production

#### Premium Tier (P1V3)
- **Cost**: ~$146/month
- **Memory**: 8 GB
- **CPU**: 2 cores
- **Features**: Advanced scaling, VNet integration
- **Good for**: High-traffic production

### 6. Security Best Practices

#### Use Azure Key Vault
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-keyvault.vault.azure.net/", credential=credential)
api_key = client.get_secret("azure-openai-api-key").value
```

#### Enable Managed Identity
- System-assigned identity for Azure resource access
- No need to store connection strings in code

### 7. Monitoring and Logging

#### Application Insights
```python
from applicationinsights import TelemetryClient
tc = TelemetryClient('your-instrumentation-key')
tc.track_event('RAG Query', {'query': query, 'response_time': response_time})
```

#### Log Analytics
- Enable diagnostic logs in App Service
- Monitor performance and errors
- Set up alerts for issues

### 8. Cost Optimization

#### Strategies:
- **Auto-scaling**: Scale down during low usage
- **Reserved Instances**: 30-70% cost savings
- **Dev/Test Pricing**: For non-production environments
- **Monitoring**: Track usage patterns and optimize

#### Expected Monthly Costs:
- **App Service B1**: $13
- **Azure OpenAI**: $0.002/1K tokens (GPT-4)
- **Storage**: $0.05/GB/month
- **Networking**: Usually free tier sufficient

### 9. Deployment Checklist

- [ ] Azure OpenAI resource created
- [ ] Required deployments (gpt-4.1, text-embedding-ada-002) exist
- [ ] Resource group prepared
- [ ] Environment variables configured
- [ ] Startup command set: `python -m streamlit run src/rag_bot.py --server.port 8501 --server.address 0.0.0.0`
- [ ] Application Insights configured
- [ ] Custom domain configured (if needed)
- [ ] SSL certificate installed
- [ ] Auto-scaling rules set

### 10. Troubleshooting

#### Common Issues:
- **App won't start**: Check startup command and port configuration
- **Azure OpenAI errors**: Verify API key and deployment names
- **Memory issues**: Upgrade to higher tier or optimize code
- **Slow performance**: Enable caching and optimize queries

#### Debug Steps:
1. Check App Service logs
2. Verify environment variables
3. Test Azure OpenAI connection
4. Monitor resource usage
5. Check Application Insights

## Files Created for Deployment

1. `startup.sh` - App Service startup script
2. `Dockerfile` - Container deployment option
3. `deploy_azure_app_service.sh` - Automated deployment script
4. `azure_app_service_config.json` - ARM template configuration
5. `requirements.txt` - Updated Python dependencies

## Next Steps

1. **Deploy using your preferred method**
2. **Configure custom domain and SSL**
3. **Set up monitoring and alerts**
4. **Test with sample PDFs**
5. **Configure backup and disaster recovery**

## Support

For issues or questions:
- Check Azure App Service documentation
- Monitor Application Insights for errors
- Review App Service logs
- Contact Azure support if needed
