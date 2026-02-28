# 🚀 Deploying IRIS Unity Catalog to Google Cloud Platform

This guide will help you deploy the modified Unity Catalog server with IRIS OT Asset Management extensions to GCP, making it accessible from Databricks and other cloud services.

## 📋 Prerequisites

1. **GCP Project**: Access to `gcp-sandbox-field-eng`
2. **GCloud CLI**: Installed and authenticated
3. **Docker**: Installed locally for building images
4. **Permissions**: Cloud Run Admin, Artifact Registry Admin

## 🏗️ Deployment Options

### Option 1: Cloud Run (Recommended)
**Best for**: Quick deployment, auto-scaling, serverless
**Cost**: Pay per request, scales to zero
**Limitations**: Stateless, 60-minute request timeout

### Option 2: Google Kubernetes Engine (GKE)
**Best for**: Full control, persistent storage, complex deployments
**Cost**: Always running, higher baseline cost

### Option 3: Compute Engine VM
**Best for**: Simple deployment, full control
**Cost**: Fixed cost based on VM size

## 🚀 Quick Deployment to Cloud Run

### Step 1: Prepare for Deployment
```bash
# Navigate to project directory
cd /Users/pravin.varma/Documents/Demo/project-iris/iris

# Make deployment script executable
chmod +x deploy-to-gcp.sh
```

### Step 2: Authenticate with GCP
```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project gcp-sandbox-field-eng
```

### Step 3: Deploy to Cloud Run
```bash
# Run the automated deployment script
./deploy-to-gcp.sh
```

This script will:
1. Enable required APIs
2. Create Artifact Registry repository
3. Build Docker image
4. Push to Artifact Registry
5. Deploy to Cloud Run
6. Return the public URL

### Step 4: Test the Deployment
```bash
# Replace with your actual Cloud Run URL
SERVICE_URL="https://iris-uc-server-xxxxx-uc.a.run.app"

# Test the API
curl $SERVICE_URL/api/2.1/unity-catalog/schemas?catalog_name=unity
```

## 🔧 Manual Deployment Steps

### 1. Build Docker Image
```bash
# Build the image
docker build -t iris-unity-catalog:latest .
```

### 2. Tag for GCP
```bash
# Tag for Artifact Registry
docker tag iris-unity-catalog:latest \
  us-central1-docker.pkg.dev/gcp-sandbox-field-eng/iris-artifacts/iris-unity-catalog:latest
```

### 3. Push to Artifact Registry
```bash
# Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev

# Push image
docker push us-central1-docker.pkg.dev/gcp-sandbox-field-eng/iris-artifacts/iris-unity-catalog:latest
```

### 4. Deploy to Cloud Run
```bash
gcloud run deploy iris-uc-server \
    --image=us-central1-docker.pkg.dev/gcp-sandbox-field-eng/iris-artifacts/iris-unity-catalog:latest \
    --platform=managed \
    --region=us-central1 \
    --port=8080 \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=1 \
    --max-instances=10 \
    --allow-unauthenticated
```

## 🔐 Security Considerations

### Option 1: Public with API Key
```bash
# Deploy with API key requirement
gcloud run deploy iris-uc-server \
    --set-env-vars="API_KEY=your-secure-key-here" \
    --no-allow-unauthenticated
```

### Option 2: IAM Authentication
```bash
# Require authentication
gcloud run deploy iris-uc-server \
    --no-allow-unauthenticated

# Grant access to specific users
gcloud run services add-iam-policy-binding iris-uc-server \
    --member="user:pravin.varma@databricks.com" \
    --role="roles/run.invoker"
```

### Option 3: VPC Connector (Private)
```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create iris-connector \
    --region=us-central1 \
    --subnet=default \
    --subnet-project=gcp-sandbox-field-eng

# Deploy with VPC connector
gcloud run deploy iris-uc-server \
    --vpc-connector=iris-connector \
    --vpc-egress=all-traffic
```

## 📝 Update Databricks Notebooks

After deployment, update your notebooks to use the GCP endpoint:

### Before (localhost):
```python
API_BASE = "http://localhost:8080/api/2.1/unity-catalog"
```

### After (Cloud Run):
```python
# Replace with your actual Cloud Run URL
API_BASE = "https://iris-uc-server-xxxxx-uc.a.run.app/api/2.1/unity-catalog"
```

## 🗄️ Persistent Storage (Optional)

Cloud Run is stateless. For persistent storage:

### Option 1: Cloud SQL
```yaml
# Add to Cloud Run deployment
--add-cloudsql-instances=PROJECT:REGION:INSTANCE
--set-env-vars="DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE"
```

### Option 2: Cloud Storage
```python
# Use GCS for asset data
--set-env-vars="GCS_BUCKET=iris-asset-data"
```

## 📊 Monitoring

### View Logs
```bash
# Stream logs
gcloud run logs tail iris-uc-server --region=us-central1

# View in Console
gcloud run services describe iris-uc-server --region=us-central1
```

### Metrics
- Go to: https://console.cloud.google.com/run
- Select `iris-uc-server`
- View metrics, logs, and revisions

## 🔄 Update Deployment

### Deploy New Version
```bash
# Build new image
docker build -t iris-unity-catalog:v2 .

# Tag and push
docker tag iris-unity-catalog:v2 \
  us-central1-docker.pkg.dev/gcp-sandbox-field-eng/iris-artifacts/iris-unity-catalog:v2

docker push us-central1-docker.pkg.dev/gcp-sandbox-field-eng/iris-artifacts/iris-unity-catalog:v2

# Deploy new revision
gcloud run deploy iris-uc-server \
    --image=us-central1-docker.pkg.dev/gcp-sandbox-field-eng/iris-artifacts/iris-unity-catalog:v2
```

### Rollback
```bash
# List revisions
gcloud run revisions list --service=iris-uc-server

# Rollback to previous
gcloud run services update-traffic iris-uc-server \
    --to-revisions=iris-uc-server-00001-abc=100
```

## 💰 Cost Optimization

### Cloud Run Pricing (Estimated)
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests
- **Minimum instances**: 1 instance = ~$50/month

### Optimization Tips
1. Set `--min-instances=0` to scale to zero (adds cold start delay)
2. Reduce `--memory` if possible (test with 1Gi first)
3. Use `--max-instances` to cap costs
4. Enable Cloud CDN for static responses

## 🐛 Troubleshooting

### Common Issues

1. **"Permission denied" during push**
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

2. **"Service not reachable"**
- Check if `--allow-unauthenticated` is set
- Verify service URL is correct

3. **"Out of memory" errors**
- Increase memory: `--memory=4Gi`
- Optimize Java heap: `--set-env-vars="JAVA_OPTS=-Xmx3g"`

4. **Slow cold starts**
- Keep minimum instances: `--min-instances=1`
- Use smaller base image

## 📞 Support

- **GCP Console**: https://console.cloud.google.com/run?project=gcp-sandbox-field-eng
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Project Issues**: Create issue in project repository

## ✅ Deployment Checklist

- [ ] GCloud CLI authenticated
- [ ] Docker installed and running
- [ ] Project set to `gcp-sandbox-field-eng`
- [ ] APIs enabled (Cloud Run, Artifact Registry, Cloud Build)
- [ ] Docker image built successfully
- [ ] Image pushed to Artifact Registry
- [ ] Cloud Run service deployed
- [ ] Service URL obtained
- [ ] API endpoints tested
- [ ] Notebooks updated with new URL
- [ ] Monitoring configured

## 🎉 Success!

Once deployed, your IRIS Unity Catalog server will be available at:
```
https://iris-uc-server-xxxxx-uc.a.run.app
```

The asset management APIs are now accessible from:
- Databricks notebooks
- External applications
- CI/CD pipelines
- Other cloud services

Update all references from `localhost:8080` to your new Cloud Run URL!