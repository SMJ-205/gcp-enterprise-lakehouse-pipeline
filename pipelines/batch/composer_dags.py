import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

# Configure GCP params
PROJECT_ID = os.getenv("GCP_PROJECT", "gcp-pde-project-505510")
DATASET_ID = "ecommerce_lakehouse"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "gcp_lakehouse_batch_pipeline",
    default_args=default_args,
    description="Daily transactional analytics and churn model orchestration",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Merge new transactions from Bronze GCS external table into Silver partitioned table
    merge_bronze_to_silver = BigQueryInsertJobOperator(
        task_id="merge_bronze_to_silver",
        configuration={
            "query": {
                "query": f"""
                    MERGE INTO `{PROJECT_ID}.{DATASET_ID}.fact_transactions` T
                    USING `{PROJECT_ID}.{DATASET_ID}.bronze_transactions` S
                    ON T.transaction_id = S.transaction_id
                    WHEN NOT MATCHED THEN
                      INSERT (transaction_id, user_id, merchant_id, amount, payment_method, status, transaction_timestamp)
                      VALUES (S.transaction_id, S.user_id, S.merchant_id, S.amount, S.payment_method, S.status, S.transaction_timestamp);
                """,
                "useLegacySql": False,
            }
        },
    )

    # Task 2: Retrain the churn prediction model inside BigQuery ML
    train_bqml_model = BigQueryInsertJobOperator(
        task_id="train_bqml_model",
        configuration={
            "query": {
                "query": f"""
                    CREATE OR REPLACE MODEL `{PROJECT_ID}.{DATASET_ID}.model_churn_prediction`
                    OPTIONS (
                      model_type = 'BOOSTED_TREE_CLASSIFIER',
                      input_label_cols = ['is_churned'],
                      auto_class_weights = true,
                      max_iterations = 20
                    ) AS
                    SELECT
                      user_id,
                      total_orders_last_30d,
                      total_spend_amount,
                      avg_session_duration_seconds,
                      days_since_last_order,
                      is_churned
                    FROM `{PROJECT_ID}.{DATASET_ID}.view_ml_features`;
                """,
                "useLegacySql": False,
            }
        },
    )

    # Task 3: Evaluate model performance
    evaluate_bqml_model = BigQueryInsertJobOperator(
        task_id="evaluate_bqml_model",
        configuration={
            "query": {
                "query": f"""
                    SELECT * 
                    FROM ML.EVALUATE(MODEL `{PROJECT_ID}.{DATASET_ID}.model_churn_prediction`);
                """,
                "useLegacySql": False,
            }
        },
    )

    # Task 4: Run batch inference to predict churn probability for currently active users
    run_churn_inference = BigQueryInsertJobOperator(
        task_id="run_churn_inference",
        configuration={
            "query": {
                "query": f"""
                    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.churn_predictions` AS
                    SELECT
                      user_id,
                      predicted_is_churned,
                      predicted_is_churned_probs[OFFSET(0)].prob AS churn_probability,
                      CURRENT_TIMESTAMP() as prediction_timestamp
                    FROM ML.PREDICT(
                      MODEL `{PROJECT_ID}.{DATASET_ID}.model_churn_prediction`,
                      (SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.view_ml_features_active_users`)
                    );
                """,
                "useLegacySql": False,
            }
        },
    )

    # Define DAG execution sequence
    merge_bronze_to_silver >> train_bqml_model >> evaluate_bqml_model >> run_churn_inference
