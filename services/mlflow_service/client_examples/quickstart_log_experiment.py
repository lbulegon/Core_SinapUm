"""
MLflow Quickstart - Log Experiment
===================================
Exemplo básico de como logar parâmetros, métricas e artifacts no MLflow
a partir do Core_SinapUm.

Uso:
    export MLFLOW_TRACKING_URI=http://localhost:5050
    python quickstart_log_experiment.py

Pré-requisitos:
    pip install mlflow
"""

import os
import tempfile

import mlflow

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5050")
EXPERIMENT_NAME = "core_sinapum_playground"


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    print(f"MLflow Tracking URI: {TRACKING_URI}")

    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f"Experiment: {EXPERIMENT_NAME}")

    with mlflow.start_run(run_name="quickstart_experiment") as run:
        # Log parâmetros
        mlflow.log_param("alpha", 0.5)
        mlflow.log_param("l1_ratio", 0.1)
        mlflow.log_param("model_type", "linear_regression")
        mlflow.log_param("dataset", "core_sinapum_sample")
        print("Parâmetros logados.")

        # Log métricas (simulando epochs de treino)
        for epoch in range(1, 11):
            loss = 1.0 / epoch
            accuracy = 1.0 - loss
            mlflow.log_metric("loss", loss, step=epoch)
            mlflow.log_metric("accuracy", accuracy, step=epoch)
        print("Métricas logadas (10 epochs).")

        # Log artifact: criar um arquivo texto simples
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, prefix="sinapum_"
        ) as f:
            f.write("Core_SinapUm MLflow Quickstart\n")
            f.write("==============================\n")
            f.write(f"Experiment: {EXPERIMENT_NAME}\n")
            f.write(f"Run ID: {run.info.run_id}\n")
            f.write("Este é um artifact de exemplo.\n")
            artifact_path = f.name

        mlflow.log_artifact(artifact_path, artifact_path="quickstart_outputs")
        os.unlink(artifact_path)
        print("Artifact logado.")

        # Log tags
        mlflow.set_tag("project", "Core_SinapUm")
        mlflow.set_tag("author", "sinapum_team")
        mlflow.set_tag("stage", "development")

        print(f"\nRun finalizado com sucesso!")
        print(f"  Run ID:      {run.info.run_id}")
        print(f"  Experiment:  {EXPERIMENT_NAME}")
        print(f"  UI:          {TRACKING_URI}")
        print(f"\nAcesse a UI do MLflow para visualizar: {TRACKING_URI}")


if __name__ == "__main__":
    main()
