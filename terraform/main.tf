terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# 1. Enable APIs (Free to enable, required for services to function)
resource "google_project_service" "pubsub_api" {
  project            = var.project_id
  service            = "pubsub.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "storage_api" {
  project            = var.project_id
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "bigquery_api" {
  project            = var.project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

# 2. Pub/Sub Resources (Eligible for 10 GB free ingestion tier)
resource "google_pubsub_topic" "clickstream_topic" {
  name       = "clickstream-events"
  project    = var.project_id
  depends_on = [google_project_service.pubsub_api]
}

resource "google_pubsub_subscription" "clickstream_sub" {
  name                 = "clickstream-sub"
  topic                = google_pubsub_topic.clickstream_topic.name
  project              = var.project_id
  ack_deadline_seconds = 20
  depends_on           = [google_project_service.pubsub_api]
}

# 3. GCS Bucket (Bronze Layer - Eligible for GCS 5 GB free tier in us-central1)
resource "google_storage_bucket" "bronze_bucket" {
  name                        = "${var.project_id}-bronze-lakehouse"
  location                    = var.region
  project                     = var.project_id
  force_destroy               = true
  uniform_bucket_level_access = true

  # Standard storage is free-tier eligible in us-central1
  storage_class = "STANDARD"

  depends_on = [google_project_service.storage_api]
}

# 4. BigQuery Dataset (Eligible for 10 GB storage and 1 TB query scans free tier)
resource "google_bigquery_dataset" "lakehouse_dataset" {
  dataset_id                  = var.dataset_id
  friendly_name               = "Ecommerce Data Lakehouse Dataset"
  description                 = "Contains raw streaming and transactional batch data layers"
  location                    = var.region
  project                     = var.project_id
  delete_contents_on_destroy  = true

  depends_on = [google_project_service.bigquery_api]
}
