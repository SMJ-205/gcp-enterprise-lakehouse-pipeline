-- Gold Layer: User behavior features view for ML training
CREATE OR REPLACE VIEW `gcp-pde-project-505510.ecommerce_lakehouse.view_ml_features` AS
SELECT
  t.user_id,
  COUNT(DISTINCT t.transaction_id) as total_orders_last_30d,
  SUM(t.amount) as total_spend_amount,
  COALESCE(SUM(a.event_count) * 120, 0) as avg_session_duration_seconds, -- estimated session duration based on activity
  DATE_DIFF(CURRENT_DATE(), MAX(DATE(t.transaction_timestamp)), DAY) as days_since_last_order,
  CASE 
    WHEN DATE_DIFF(CURRENT_DATE(), MAX(DATE(t.transaction_timestamp)), DAY) > 15 THEN 1 
    ELSE 0 
  END as is_churned
FROM `gcp-pde-project-505510.ecommerce_lakehouse.fact_transactions` t
LEFT JOIN `gcp-pde-project-505510.ecommerce_lakehouse.realtime_user_activity` a
  ON t.user_id = a.user_id
-- Require partition filter for cost optimization when querying fact_transactions
WHERE DATE(t.transaction_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY t.user_id;

-- Gold Layer: Subset for Active Users to run batch prediction on
CREATE OR REPLACE VIEW `gcp-pde-project-505510.ecommerce_lakehouse.view_ml_features_active_users` AS
SELECT * 
FROM `gcp-pde-project-505510.ecommerce_lakehouse.view_ml_features`
WHERE is_churned = 0;
