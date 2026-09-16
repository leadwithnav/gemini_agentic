uvicorn app:app --host 0.0.0.0 --port 8080

enable artifactregistry.googleapis.com
        cloudbuild.googleapis.com
        run.googleapis.com

 gcloud run deploy cme-incident-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-build-env-vars GOOGLE_ENTRYPOINT="uvicorn app:app --host 0.0.0.0 --port 8080"


gcloud run deploy cme-incident-mcp   --source .   --region=us-central1   --no-allow-unauthenticated  --set-build-env-vars="GOOGLE_ENTRYPOINT=python app.py"


gcloud run services describe cme-incident-mcp \
  --region=us-central1 \
  --project=instructor-02

gcloud run services logs read cme-incident-mcp \
  --region=us-central1 \
  --limit=50

gcloud run services proxy cme-incident-mcp \
  --project=instructor-02 \
  --region=us-central1 \
  --port=8002

adk deploy cloud_run \
  --project=instructor-02 \
  --region=us-central1 \
  --service_name=cme-support-agent \
  --with_ui \
  .

gcloud run services logs read cme-support-agent \
  --project=instructor-02 \
  --region=us-central1 \
  --limit=100

gcloud run services proxy cme-support-agent \
  --project=instructor-02 \
  --region=us-central1 \
  --port=8080

