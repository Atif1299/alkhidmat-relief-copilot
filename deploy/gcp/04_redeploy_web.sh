#!/usr/bin/env bash
set -euo pipefail
PROJECT=x-saas-488416
REGION=asia-south1
API_URL="${API_URL:-https://relief-api-4idrhaffca-el.a.run.app}"
IMG_WEB="${REGION}-docker.pkg.dev/${PROJECT}/relief/web:latest"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
gcloud config set project "$PROJECT"
gcloud builds submit "$ROOT" \
  --config "$ROOT/deploy/gcp/cloudbuild.web.yaml" \
  --substitutions "_IMG_WEB=${IMG_WEB},_API_URL=${API_URL}"
gcloud run deploy relief-web \
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
WEB_URL="$(gcloud run services describe relief-web --region "$REGION" --format='value(status.url)')"
gcloud run services update relief-api \
  --region "$REGION" \
  --update-env-vars "CORS_ORIGINS=${WEB_URL}"
echo "WEB_REDEPLOY_DONE ${WEB_URL}"
