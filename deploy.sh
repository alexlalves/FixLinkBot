#! /bin/bash

pipenv run pip freeze > requirements.txt
gcloud run deploy fix-link-bot \
  --source . \
  --env-vars-file .env.yaml \
  --region=us-west1 \
  --allow-unauthenticated
