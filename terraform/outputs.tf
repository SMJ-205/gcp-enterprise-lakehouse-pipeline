output "gcs_bronze_bucket" {
  description = "The name of the GCS Bronze bucket"
  value       = google_storage_bucket.bronze_bucket.name
}

output "pubsub_topic" {
  description = "The Pub/Sub Clickstream topic name"
  value       = google_pubsub_topic.clickstream_topic.name
}

output "pubsub_subscription" {
  description = "The Pub/Sub Clickstream subscription name"
  value       = google_pubsub_subscription.clickstream_sub.name
}

output "bigquery_dataset" {
  description = "The BigQuery dataset name"
  value       = google_bigquery_dataset.lakehouse_dataset.dataset_id
}

output "sa_key_path" {
  description = "The relative path to the generated Service Account key"
  value       = "gcp-sa-key.json"
}
