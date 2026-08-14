-- Silver Layer: DDL for Fact Transactions (Internal Partitioned & Clustered Table)
CREATE OR REPLACE TABLE `gcp-pde-project-505510.ecommerce_lakehouse.fact_transactions`
(
  transaction_id STRING NOT NULL,
  user_id STRING NOT NULL,
  merchant_id STRING NOT NULL,
  amount NUMERIC,
  payment_method STRING,
  status STRING,
  transaction_timestamp TIMESTAMP NOT NULL
)
PARTITION BY DATE(transaction_timestamp)
CLUSTER BY merchant_id, user_id
OPTIONS (
  description = "Cleaned transactions, partitioned daily by timestamp and clustered by merchant and user",
  require_partition_filter = true
);

-- Silver Layer: Streaming clickstream target table
CREATE OR REPLACE TABLE `gcp-pde-project-505510.ecommerce_lakehouse.realtime_user_activity`
(
  user_id STRING NOT NULL,
  event_count INT64 NOT NULL,
  processed_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(processed_at)
OPTIONS (
  description = "Real-time user event count streaming table aggregated from Pub/Sub"
);
