-- Bronze Layer: External Table mapping raw Parquet transaction files in GCS
CREATE OR REPLACE EXTERNAL TABLE `gcp-pde-project-505510.ecommerce_lakehouse.bronze_transactions`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://gcp-pde-project-505510-bronze-lakehouse/transactions/*.parquet']
);
