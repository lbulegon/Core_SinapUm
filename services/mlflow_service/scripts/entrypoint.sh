#!/bin/bash
set -e

echo "=== MLflow Tracking Server ==="
echo "Backend Store: ${MLFLOW_BACKEND_URI}"
echo "Artifact Root: ${MLFLOW_ARTIFACT_ROOT:-/mlflow/artifacts}"
echo "Port: 5000"
echo "=============================="

exec mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri "${MLFLOW_BACKEND_URI}" \
  --default-artifact-root "${MLFLOW_ARTIFACT_ROOT:-/mlflow/artifacts}"
