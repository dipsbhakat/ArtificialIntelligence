# Azure App Service Deployment Checklist

## Pre-Deployment ✅

### Azure Resources
- [ ] Azure subscription active
- [ ] Resource group `rg-agrimayadav-5135_ai` exists
- [ ] Azure OpenAI resource `liftr-platorm-service` deployed
- [ ] Azure OpenAI API key obtained

### Required Deployments
- [ ] Chat deployment: `gpt-4.1` (status: Succeeded)
- [ ] Embedding deployment: `text-embedding-ada-002` (status: Succeeded)

### Local Setup
- [ ] Azure CLI installed and configured
- [ ] Project code ready in current directory
- [ ] All required files present:
  - [ ] `src/rag_bot.py`
  - [ ] `requirements.txt`
  - [ ] `startup.sh`
  - [ ] `Dockerfile`
  - [ ] Deployment scripts

## Deployment Options

### Option 1: Automated Script (Recommended)
```powershell
# Windows PowerShell
.\deploy_azure_app_service.ps1
```

```bash
# Linux/Mac/WSL
chmod +x deploy_azure_app_service.sh
./deploy_azure_app_service.sh
```

### Option 2: Manual Portal Deployment
1. [ ] Create App Service in Azure Portal
2. [ ] Configure Python 3.11 runtime
3. [ ] Set environment variables (see below)
4. [ ] Set startup command: `startup.sh`
5. [ ] Deploy code via ZIP upload

### Option 3: Container Deployment
1. [ ] Build Docker image: `docker build -t rag-bot .`
2. [ ] Push to Azure Container Registry
3. [ ] Deploy as container app

## Environment Variables (Required)

Copy these to Azure Portal → App Service → Configuration:

```
AZURE_OPENAI_API_KEY=your-actual-api-key-here
AZURE_OPENAI_ENDPOINT=https://liftr-platorm-service.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-12-01-preview
DEFAULT_PROVIDER=azure
WEBSITES_PORT=8501
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

## Post-Deployment ✅

### Immediate Testing
- [ ] App starts successfully (no startup errors)
- [ ] Homepage loads at `https://your-app-name.azurewebsites.net`
- [ ] Azure OpenAI connection works
- [ ] File upload functionality works
- [ ] Chat functionality works with sample questions

### Configuration Verification
- [ ] API key is correctly set (not the placeholder)
- [ ] Endpoint URL is correct
- [ ] Deployment names match exactly
- [ ] All environment variables are set

### Performance Testing
- [ ] Upload a test PDF (< 10MB)
- [ ] Process the document successfully
- [ ] Ask sample questions:
  - "What is this document about?"
  - "Summarize the key points"
  - "What recommendations are provided?"

## Troubleshooting

### Common Issues

#### App Won't Start
**Symptoms**: 503 Service Unavailable, startup timeout
**Solutions**:
- [ ] Check logs: `az webapp log tail --name your-app-name --resource-group rg-agrimayadav-5135_ai`
- [ ] Verify startup command is set to `startup.sh`
- [ ] Check Python version is 3.11
- [ ] Verify all dependencies in requirements.txt

#### Azure OpenAI Connection Failed
**Symptoms**: 401 Unauthorized, 404 Not Found, DeploymentNotFound
**Solutions**:
- [ ] Verify API key is correct (not placeholder)
- [ ] Check endpoint URL format
- [ ] Confirm deployment names match exactly
- [ ] Ensure deployments are in "Succeeded" status

#### File Upload Issues
**Symptoms**: File upload fails, processing errors
**Solutions**:
- [ ] Check file size limits (Azure App Service: 250MB max)
- [ ] Verify tmp directory permissions
- [ ] Check available disk space

#### Performance Issues
**Symptoms**: Slow responses, timeouts
**Solutions**:
- [ ] Monitor CPU/memory usage in Azure Portal
- [ ] Consider upgrading to higher tier (S1 or P1V3)
- [ ] Implement query caching
- [ ] Optimize document chunking strategy

## Monitoring Setup

### Application Insights
- [ ] Create Application Insights resource
- [ ] Connect to App Service
- [ ] Set up performance alerts

### Log Analytics
- [ ] Enable diagnostic logging
- [ ] Set up custom queries
- [ ] Create monitoring dashboard

### Cost Monitoring
- [ ] Set up budget alerts
- [ ] Monitor Azure OpenAI token usage
- [ ] Track App Service costs

## Maintenance

### Regular Tasks
- [ ] Monitor application health weekly
- [ ] Review error logs monthly
- [ ] Update dependencies quarterly
- [ ] Review security patches

### Scaling Preparation
- [ ] Set up auto-scaling rules
- [ ] Define scaling triggers
- [ ] Test scaling behavior
- [ ] Plan for traffic spikes

## Security Checklist

### Best Practices
- [ ] Use HTTPS only (enabled by default)
- [ ] Enable Application Insights for monitoring
- [ ] Consider using Azure Key Vault for secrets
- [ ] Set up managed identity (if applicable)
- [ ] Review access controls

### Secret Management
- [ ] API keys stored securely
- [ ] No secrets in source code
- [ ] Regular key rotation planned
- [ ] Access logging enabled

## Success Criteria

### Functionality
- [ ] ✅ App loads without errors
- [ ] ✅ PDF upload and processing works
- [ ] ✅ Chat interface responds correctly
- [ ] ✅ Source citations are displayed
- [ ] ✅ Error handling works gracefully

### Performance
- [ ] ✅ App starts in < 30 seconds
- [ ] ✅ PDF processing completes in reasonable time
- [ ] ✅ Chat responses arrive in < 10 seconds
- [ ] ✅ No memory leaks or crashes

### Reliability
- [ ] ✅ App remains stable under normal load
- [ ] ✅ Graceful error handling
- [ ] ✅ Proper logging and monitoring
- [ ] ✅ Backup and recovery plan

## Next Steps

1. **Customize UI**: Modify Streamlit interface for your branding
2. **Add Authentication**: Implement user login if needed
3. **Enhance Features**: Add document management, chat history
4. **Optimize Performance**: Implement caching, optimize queries
5. **Scale Planning**: Prepare for increased usage

## Support Resources

- **Azure App Service Docs**: https://docs.microsoft.com/en-us/azure/app-service/
- **Azure OpenAI Docs**: https://docs.microsoft.com/en-us/azure/cognitive-services/openai/
- **Streamlit Docs**: https://docs.streamlit.io/
- **LangChain Docs**: https://docs.langchain.com/

---

**Estimated Deployment Time**: 15-30 minutes  
**Monthly Cost**: $20-50 (depending on usage)  
**Maintenance**: 1-2 hours per month
