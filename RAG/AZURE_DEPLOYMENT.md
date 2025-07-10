# Azure AI Studio deployment guide

## Prerequisites
- Azure subscription
- Azure AI Studio workspace
- Azure OpenAI resource with deployments

## Deployment Options

### 1. Azure AI Studio Notebooks
1. Go to https://ai.azure.com
2. Open your workspace
3. Create new notebook
4. Upload `azure_rag_bot.py` 
5. Install dependencies:
   ```bash
   !pip install streamlit langchain langchain-openai langchain-community chromadb pypdf python-dotenv azure-identity
   ```

### 2. Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image rag-bot:latest .

# Deploy to Container Instances
az container create \
  --resource-group rg-agrimayadev-5135_ai \
  --name rag-bot \
  --image myregistry.azurecr.io/rag-bot:latest \
  --dns-name-label rag-bot-unique \
  --ports 8501 \
  --environment-variables \
    AZURE_OPENAI_API_KEY="your-key" \
    AZURE_OPENAI_ENDPOINT="https://liftr-platorm-service.cognitiveservices.azure.com/" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002" \
    AZURE_OPENAI_API_VERSION="2024-12-01-preview"
```

### 3. Azure App Service
```bash
# Make deploy script executable
chmod +x deploy_azure.sh

# Run deployment
./deploy_azure.sh
```

### 4. Azure ML Endpoints
1. Upload code to Azure ML workspace
2. Create environment with requirements.txt
3. Deploy as real-time endpoint
4. Configure auto-scaling

## Configuration

### Environment Variables
Set these in your Azure service:
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Chat model deployment name
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Embedding model deployment name
- `AZURE_OPENAI_API_VERSION`: API version

### Managed Identity (Recommended for Production)
1. Enable managed identity on your Azure service
2. Grant OpenAI permissions to the managed identity
3. Remove API key from environment variables
4. The code will automatically use managed identity

## Security Best Practices
1. Use managed identity instead of API keys
2. Store secrets in Azure Key Vault
3. Enable private endpoints
4. Configure network security groups
5. Use Azure Monitor for logging

## Monitoring
1. Enable Application Insights
2. Set up alerts for errors
3. Monitor token usage
4. Track response times

## Scaling
- Azure Container Instances: Manual scaling
- Azure App Service: Auto-scaling rules
- Azure ML Endpoints: Auto-scaling with traffic patterns
- Azure Kubernetes Service: Advanced scaling options

## Cost Optimization
1. Use appropriate compute sizes
2. Enable auto-shutdown for dev environments
3. Monitor OpenAI token usage
4. Use spot instances for non-critical workloads
