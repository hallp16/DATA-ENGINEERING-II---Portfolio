# Brazilian Traffic Incidents – Batch Data Engineering Pipeline

A containerized, resilient, and scalable batch data engineering pipeline built with **Docker**, **PostgreSQL**, and **Apache Spark (PySpark)** for the analysis of Brazilian traffic incident data (~1.8 million records).

---

## 🏗 Architecture Overview

The system follows a modern **ELT (Extract, Load, Transform)** and **Medallion Architecture** deployed as isolated microservices via Docker Compose:

1. **Ingestion Layer (Python / Pandas / SQLAlchemy):**
   - Ingests raw CSV data into PostgreSQL using **Memory Chunking** (`chunksize=10,000`) to prevent Out-Of-Memory (OOM) exceptions.
   - Enforces **Idempotency** via pre-execution table drops / upsert patterns.
   - Loads data as raw text (`Bronze Layer`) to prevent schema inference crashes during ingestion.

2. **Storage Layer (PostgreSQL 14.12):**
   - Serves as the central ACID-compliant storage engine.
   - Configured with persistent volumes and healthcheck mechanisms.

3. **Processing & Analytics Layer (Apache Spark 3.5.1):**
   - Connects to PostgreSQL via JDBC.
   - Performs schema casting, data cleansing (`Silver Layer`), and aggregations (`Gold Layer`).
   - Writes the analytical business table (`analytics_state_yearly`) back to the database for reporting and BI consumption.

---

## 🛡️ Software Quality & Governance Highlights

- **Reliability:** Idempotent ingestion routines and Docker healthchecks prevent partial or inconsistent data states.
- **Scalability:** The transformation logic is implemented in Apache Spark, enabling distributed horizontal scaling for multi-gigabyte datasets.
- **Maintainability:** Infrastructure as Code (IaC) via Docker Compose with pinned image versions (`python:3.9.18-slim`, `postgres:14.12`, `apache/spark:3.5.1`).
- **Data Security & Governance:** Environment variables (`.env`) isolate sensitive database credentials from version control.

---

## 🚀 Getting Started (Local Deployment)

### Prerequisites
- [Docker Desktop](https://www.docker.com/) installed and running.
- [Git](https://git-scm.com/) installed.

### 1. Setup Environment
Clone the repository and prepare the configuration:
```bash
cp .env.example .env