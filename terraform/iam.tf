# 1. Create a Service Account for local pipeline execution
resource "google_service_account" "local_pipeline_sa" {
  account_id   = "lakehouse-local-sa"
  display_name = "Lakehouse Local Pipeline Service Account"
  project      = var.project_id
}

# 2. Assign Pub/Sub Publisher Role (needed for mock clickstream generator)
resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.local_pipeline_sa.email}"
}

# 3. Assign Pub/Sub Subscriber Role (needed for Apache Beam DirectRunner consumer)
resource "google_project_iam_member" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.local_pipeline_sa.email}"
}

# 4. Assign BigQuery Admin Role (needed for DDL, query scan, and BQML)
resource "google_project_iam_member" "bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.local_pipeline_sa.email}"
}

# 5. Assign Storage Object Admin Role (needed for uploading batch parquet logs)
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.local_pipeline_sa.email}"
}

# 6. Generate the private key JSON file for local authentication
resource "google_service_account_key" "local_sa_key" {
  service_account_id = google_service_account.local_pipeline_sa.name
}

# Save key locally inside the project directory
resource "local_file" "local_sa_key_file" {
  content  = base64decode(google_service_account_key.local_sa_key.private_key)
  filename = "${path.module}/../gcp-sa-key.json"
}
