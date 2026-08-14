variable "project_id" {
  description = "The GCP Project ID to deploy resources in"
  type        = string
  default     = "gcp-pde-project-505510"
}

variable "region" {
  description = "The GCP Region to deploy resources in"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP Zone to deploy compute resources in"
  type        = string
  default     = "us-central1-a"
}

variable "dataset_id" {
  description = "The BigQuery dataset ID for the Lakehouse"
  type        = string
  default     = "ecommerce_lakehouse"
}
