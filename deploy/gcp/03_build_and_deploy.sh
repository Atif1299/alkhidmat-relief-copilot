#!/usr/bin/env bash
# Build images and deploy Cloud Run api + web.
set -euo pipefail

PROJECT="${GCP_PROJECT:-x-saas-488416}"
REGION="${GCP_REGION:-asia-south1}"
AR_REPO="${AR_REPO:-relief}"
SQL_INSTANCE="${SQL_INSTANCE:-relief-pg}"
DB_NAME="${DB_NAME:-aiddesk}"
DB_USER="${DB_USER:-aiddesk}"
SERVICE_API="${SERVICE_API:-relief-api}"
SERVICE_WEB="${SERVICE_WEB:-relief-web}"
DASHSCOPE_BASE_URL="${DASHSCOPE_BASE_URL:-https://dashscope-intl.aliyuncs.com/compatible-mode/v1}"
DASHSCOPE_MODEL="${DASHSCOPE_MODEL:-qwen-plus}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

gcloud config set project "$PROJECT"
CONNECTION_NAME="${PROJECT}:${REGION}:${SQL_INSTANCE}"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT}/${AR_REPO}"
IMG_API="${REGISTRY}/api:latest"
IMG_WEB="${REGISTRY}/web:latest"

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

DB_PASS="$(gcloud secrets versions access latest --secret=db-password)"
# URL-encode is unnecessary if password is alphanumeric (02_bootstrap generates such)
DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASS}@/${DB_NAME}?host=/cloudsql/${CONNECTION_NAME}"

# Store DATABASE_URL as secret (avoids shell/env escaping issues)
if gcloud secrets describe database-url &>/dev/null; then
  echo -n "$DATABASE_URL" | gcloud secrets versions add database-url --data-file=-
else
  echo -n "$DATABASE_URL" | gcloud secrets create database-url --data-file=-
fi

echo "=== Building API image ==="
gcloud builds submit "$ROOT/backend" --tag "$IMG_API"

echo "=== Deploying API ==="
gcloud run deploy "$SERVICE_API" \
  --image "$IMG_API" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --timeout 300 \
  --cpu 1 \
  --memory 1Gi \
  --min-instances 0 \
  --max-instances 3 \
  --set-cloudsql-instances "$CONNECTION_NAME" \
  --set-secrets "DASHSCOPE_API_KEY=dashscope-api-key:latest,DATABASE_URL=database-url:latest" \
  --set-env-vars "LLM_MODE=qwen,DASHSCOPE_MODEL=${DASHSCOPE_MODEL},DASHSCOPE_BASE_URL=${DASHSCOPE_BASE_URL},CORS_ORIGINS=*"

API_URL="$(gcloud run services describe "$SERVICE_API" --region "$REGION" --format='value(status.url)')"
echo "API_URL=$API_URL"

echo "=== Building Web image ==="
gcloud builds submit "$ROOT" \
  --config "$ROOT/deploy/gcp/cloudbuild.web.yaml" \
  --substitutions "_IMG_WEB=${IMG_WEB},_API_URL=${API_URL}"

echo "=== Deploying Web ==="
gcloud run deploy "$SERVICE_WEB" \
  --image "$IMG_WEB" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --timeout 60 \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 3

WEB_URL="$(gcloud run services describe "$SERVICE_WEB" --region "$REGION" --format='value(status.url)')"
echo "WEB_URL=$WEB_URL"

echo "=== Updating API CORS ==="
gcloud run services update "$SERVICE_API" \
  --region "$REGION" \
  --update-env-vars "CORS_ORIGINS=${WEB_URL}"

echo ""
echo "DONE"
echo "Live API: $API_URL"
echo "Live Web: $WEB_URL"
