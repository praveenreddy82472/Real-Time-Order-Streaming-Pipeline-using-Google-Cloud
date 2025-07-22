# Real-Time Order Streaming Pipeline using Google Cloud

This project implements an end-to-end real-time data pipeline for processing streaming order events using Google Cloud services. The pipeline ensures reliable delivery with dead-letter handling and provides dynamic business insights via a Looker Studio dashboard.

---

## 📌 Overview

The pipeline ingests order events via **Pub/Sub**, processes them in real time using **Dataflow (Apache Beam)**, and stores the data in **BigQuery**. Failed events are routed to a **Dead Letter Queue (DLQ)**. Processed data is visualized with custom time-based aggregations in **Looker Studio**.

---

## 🔧 Architecture

              ┌────────────────────────────┐
              │   IoT / Order Data Source  │
              │  (Python Simulator Script) │
              └────────────┬───────────────┘
                           │
                           ▼
                    📩 Pub/Sub Topic
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │         Apache Beam (Dataflow)           │
        │  - Hopping Window Aggregations           │
        │  - Late Data Handling (Watermarks)       │
        │  - Dead Letter Queue via Side Outputs    │
        │  - Retry with Backoff Logic              │
        └──────────────┬──────────────┬────────────┘
                       │              │
                       ▼              ▼
           📊 BigQuery Table     🛑 Dead Letter Topic
                       │
                       ▼
         📈 Looker Studio Dashboard (Real-Time Analytics)
                       │
                       ▼
           ⚡ Low-Latency Cache (Memorystore Redis)


## 🧰 Tools & Services

- **Pub/Sub** – For real-time message ingestion  
- **Dataflow** – Apache Beam pipeline for ETL  
- **BigQuery** – Scalable data warehouse for analytics  
- **Looker Studio** – Visualization and reporting  
- **Cloud Shell / Python** – Local development & deployment
