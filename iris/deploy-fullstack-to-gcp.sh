#!/bin/bash

# Deploy Unity Catalog with IRIS Extensions + React UI to Google Cloud Platform
# This script deploys both the UC server and React browser to Cloud Run

set -e

# Configuration
PROJECT_ID="gcp-sandbox-field-eng"
REGION="us-central1"
SERVICE_NAME="iris-uc-fullstack"
IMAGE_NAME="iris-unity-catalog-fullstack"
ARTIFACT_REGISTRY="us-central1-docker.pkg.dev"
REPOSITORY_NAME="iris-artifacts"

echo "🚀 Deploying Unity Catalog + React UI to GCP"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check if gcloud is logged in
echo "📝 Checking GCloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated. Please run: gcloud auth login"
    exit 1
fi

# Set project
echo "🎯 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required GCP APIs..."
gcloud services enable \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    compute.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo "📦 Creating Artifact Registry repository..."
gcloud artifacts repositories create $REPOSITORY_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="IRIS Unity Catalog Docker images" \
    2>/dev/null || echo "Repository already exists"

# Configure Docker auth for Artifact Registry
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker $ARTIFACT_REGISTRY

# Build the Docker image with fullstack Dockerfile
IMAGE_TAG="$ARTIFACT_REGISTRY/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE_NAME:latest"
echo "🔨 Building Docker image with React UI: $IMAGE_TAG"
docker build -f Dockerfile.fullstack -t $IMAGE_TAG .

# Push to Artifact Registry
echo "📤 Pushing image to Artifact Registry..."
docker push $IMAGE_TAG

# Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --platform=managed \
    --region=$REGION \
    --port=8080 \
    --memory=4Gi \
    --cpu=4 \
    --timeout=600 \
    --cpu-boost \
    --min-instances=1 \
    --max-instances=10 \
    --allow-unauthenticated \
    --set-env-vars="HOME=/home/unitycatalog,JAVA_OPTS=-Xmx3g"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform=managed \
    --region=$REGION \
    --format="value(status.url)")

echo ""
echo "✅ Deployment Complete!"
echo "=================================================="
echo "🌐 Service URL: $SERVICE_URL"
echo "🖥️  React UI: $SERVICE_URL"
echo "🔌 API Endpoint: $SERVICE_URL/api/2.1/unity-catalog"
echo ""
echo "Test the deployment:"
echo "  # Open in browser:"
echo "  open $SERVICE_URL"
echo ""
echo "  # Test API:"
echo "  curl $SERVICE_URL/api/2.1/unity-catalog/catalogs"
echo ""
echo "Update notebooks to use:"
echo "  API_BASE = '$SERVICE_URL/api/2.1/unity-catalog'"
echo ""
