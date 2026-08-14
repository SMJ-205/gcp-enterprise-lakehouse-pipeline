-- BigQuery ML: Evaluate trained model metrics
SELECT * 
FROM ML.EVALUATE(MODEL `gcp-pde-project-505510.ecommerce_lakehouse.model_churn_prediction`);

-- BigQuery ML: Batch Scoring Inference on active users to predict future churn probability
SELECT
  user_id,
  predicted_is_churned,
  predicted_is_churned_probs[OFFSET(0)].prob AS churn_probability
FROM ML.PREDICT(
  MODEL `gcp-pde-project-505510.ecommerce_lakehouse.model_churn_prediction`,
  (SELECT * FROM `gcp-pde-project-505510.ecommerce_lakehouse.view_ml_features_active_users`)
);
