"""
MLflow Quickstart - Log Model (Sklearn)
=========================================
Treina um modelo simples com scikit-learn no dataset Iris
e registra o modelo, métricas e parâmetros no MLflow.

Uso:
    export MLFLOW_TRACKING_URI=http://localhost:5050
    python quickstart_log_model.py

Pré-requisitos:
    pip install mlflow scikit-learn
"""

import os

import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5050")
EXPERIMENT_NAME = "core_sinapum_playground"


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    print(f"MLflow Tracking URI: {TRACKING_URI}")

    mlflow.set_experiment(EXPERIMENT_NAME)
    print(f"Experiment: {EXPERIMENT_NAME}")

    # Carregar dataset Iris
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    print(f"Dataset: Iris ({len(X_train)} train, {len(X_test)} test)")

    # Hiperparâmetros
    params = {
        "C": 1.0,
        "max_iter": 200,
        "solver": "lbfgs",
        "multi_class": "multinomial",
        "random_state": 42,
    }

    with mlflow.start_run(run_name="quickstart_sklearn_model") as run:
        # Log parâmetros
        mlflow.log_params(params)
        mlflow.log_param("dataset", "iris")
        mlflow.log_param("test_size", 0.2)

        # Treinar modelo
        model = LogisticRegression(**params)
        model.fit(X_train, y_train)
        print("Modelo treinado: LogisticRegression")

        # Predições e métricas
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        precision = precision_score(y_test, y_pred, average="weighted")
        recall = recall_score(y_test, y_pred, average="weighted")

        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        print(f"Métricas: accuracy={acc:.4f}, f1={f1:.4f}, precision={precision:.4f}, recall={recall:.4f}")

        # Log do modelo sklearn
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="iris_logistic_regression",
            registered_model_name="core_sinapum_iris_classifier",
        )
        print("Modelo logado e registrado no MLflow Model Registry.")

        # Tags
        mlflow.set_tag("project", "Core_SinapUm")
        mlflow.set_tag("model_type", "LogisticRegression")
        mlflow.set_tag("framework", "scikit-learn")

        print(f"\nRun finalizado com sucesso!")
        print(f"  Run ID:      {run.info.run_id}")
        print(f"  Model:       core_sinapum_iris_classifier")
        print(f"  Accuracy:    {acc:.4f}")
        print(f"  UI:          {TRACKING_URI}")
        print(f"\nAcesse a UI do MLflow para visualizar: {TRACKING_URI}")


if __name__ == "__main__":
    main()
