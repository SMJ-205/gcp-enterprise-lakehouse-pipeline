# 🚀 Enterprise-Scale Real-Time Streaming & Batch Lakehouse on GCP

![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Apache Beam](https://img.shields.io/badge/Apache_Beam-Dataflow-FF6600?style=for-the-badge&logo=apache-beam&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-Lakehouse_&_ML-669DF6?style=for-the-badge&logo=google-bigquery&logoColor=white)
![Airflow](https://img.shields.io/badge/Cloud_Composer-Airflow-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Certification](https://img.shields.io/badge/Aligned_With-Google_Cloud_PDE-success?style=for-the-badge)

An end-to-end modern **Data Lakehouse architecture** on **Google Cloud Platform (GCP)**. This project demonstrates enterprise-scale data engineering capabilities aligned with the **Google Cloud Professional Data Engineer (GCP PDE)** certification standard.

---

## 📌 Executive Summary & Architecture

This repository showcases a hybrid Kappa/Lambda data platform designed to process high-throughput e-commerce clickstream events in real-time while orchestrating daily transactional batch data.

```text
[ Data Sources ]
  │
  ├──► Real-Time Clickstream (Web/Mobile)
  │      │
  │      ▼
  │   [ Cloud Pub/Sub ] (Topic: clickstream-events)
  │      │
  │      ▼
  │   [ Cloud Dataflow (Apache Beam) ] ──► (Sliding Windows + Watermarks)
  │      │
  │      ├──────────────────────────────────────────────────────┐
  │      ▼                                                      │
  └──► Daily Transaction Logs (ERP / SQL DB)                    ▼
         │                                            [ Google BigQuery Lakehouse ]
         ▼                                              ├─ Bronze Layer (Raw External GCS)
      [ Cloud Storage (GCS) ]                           ├─ Silver Layer (Cleaned & PII-Masked)
         │                                              ├─ Gold Layer (Aggregated Data Mart)
         ▼                                              └─ BigQuery ML (Model Training)
      [ Cloud Composer (Airflow DAG) ] ─────────────────────────┘
                                                                │
                                                                ▼
                                                        [ Looker Studio Dashboard ]
