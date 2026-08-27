#!/usr/bin/env bash
# Enable GCP APIs for Alkhidmat Relief Copilot deploy.
set -euo pipefail
PROJECT="${GCP_PROJECT:-x-saas-488416}"
gcloud config set project "$PROJECT"
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com
echo "APIs enabled on $PROJECT"
