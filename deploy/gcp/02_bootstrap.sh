#!/usr/bin/env bash
# Bootstrap Artifact Registry + Cloud SQL + placeholder secrets.
# Prerequisites: billing on project; gcloud auth; 01_enable_apis.sh done.
# Create dashscope-api-key yourself:
#   echo -n "KEY" | gcloud secrets create dashscope-api-key --data-file=-
set -euo pipefail

PROJECT="${GCP_PROJECT:-x-saas}"
REGION="${GCP_REGION:-asia-south1}"
AR_REPO="${AR_REPO:-relief}"
SQL_INSTANCE="${SQL_INSTANCE:-relief-pg}"
DB_NAME="${DB_NAME:-aiddesk}"
DB_USER="${DB_USER:-aiddesk}"

gcloud config set project "$PROJECT"

if ! gcloud artifacts repositories describe "$AR_REPO" --location="$REGION" &>/dev/null; then
  gcloud artifacts repositories create "$AR_REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Alkhidmat Relief Copilot images"
  echo "Created Artifact Registry $AR_REPO"
else
  echo "Artifact Registry $AR_REPO exists"
fi

if ! gcloud sql instances describe "$SQL_INSTANCE" &>/dev/null; then
  # Generate DB password once and store in Secret Manager
  DB_PASS="$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)"
  echo -n "$DB_PASS" | gcloud secrets create db-password --data-file=- \
    || echo -n "$DB_PASS" | gcloud secrets versions add db-password --data-file=-

  gcloud sql instances create "$SQL_INSTANCE" \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region="$REGION" \
    --storage-size=10GB \
    --storage-auto-increase \
    --root-password="$DB_PASS" \
    --assign-ip

  gcloud sql databases create "$DB_NAME" --instance="$SQL_INSTANCE"
  gcloud sql users create "$DB_USER" --instance="$SQL_INSTANCE" --password="$DB_PASS"
  echo "Cloud SQL $SQL_INSTANCE ready (db=$DB_NAME user=$DB_USER)"
else
  echo "Cloud SQL $SQL_INSTANCE exists"
fi

if ! gcloud secrets describe dashscope-api-key &>/dev/null; then
  echo "MISSING: create secret dashscope-api-key:"
  echo "  echo -n \"YOUR_KEY\" | gcloud secrets create dashscope-api-key --data-file=-"
  exit 1
fi

echo "Bootstrap OK. CONNECTION: ${PROJECT}:${REGION}:${SQL_INSTANCE}"
