-- BigQuery ML: Churn Prediction Model Training DDL
CREATE OR REPLACE MODEL `gcp-pde-project-505510.ecommerce_lakehouse.model_churn_prediction`
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
FROM `gcp-pde-project-505510.ecommerce_lakehouse.view_ml_features`;
