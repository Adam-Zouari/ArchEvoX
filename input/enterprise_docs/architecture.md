# Current Data Pipeline Architecture

## Overview
Our data pipeline is a traditional batch-oriented ETL system built primarily on Apache Airflow for orchestration, with PostgreSQL as the primary transactional database and Snowflake as the data warehouse.

## Component Inventory

### Ingestion Layer
- **Fivetran**: SaaS connectors for pulling data from 15+ sources (Salesforce, HubSpot, Stripe, Google Analytics, etc.)
- **Custom Python scripts**: Scheduled via Airflow for internal API data extraction
- **CDC (Change Data Capture)**: Debezium on PostgreSQL for capturing database changes, writing to Kafka

### Orchestration
- **Apache Airflow**: 200+ DAGs running on a Kubernetes-based deployment
- Scheduling: Most DAGs run on hourly or daily cadence
- Task dependencies managed via Airflow's built-in dependency system

### Transformation Layer
- **dbt (data build tool)**: ~400 models organized in staging/intermediate/marts layers
- Runs inside Snowflake via Airflow-triggered dbt jobs
- Testing via dbt tests (schema tests + custom data tests)

### Storage
- **PostgreSQL 15**: Primary transactional database (OLTP)
- **Snowflake**: Data warehouse (OLAP), 3 databases (raw, transformed, analytics)
- **S3**: Raw file storage for unstructured data and backups

### Serving Layer
- **Looker**: Primary BI tool, ~50 dashboards, ~200 explores
- **Internal API**: FastAPI-based data API serving aggregated metrics to internal tools
- **Reverse ETL**: Census for pushing warehouse data back to operational tools

## Data Flow
1. Source systems → Fivetran/Custom scripts → S3 (raw) + Snowflake (raw)
2. Snowflake (raw) → dbt transformations → Snowflake (transformed → marts)
3. Snowflake (marts) → Looker dashboards
4. Snowflake (marts) → Census → Operational tools
5. PostgreSQL → Debezium → Kafka → Custom consumers → Snowflake
