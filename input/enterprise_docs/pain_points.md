# Pain Points & Technical Debt

## Critical Pain Points

### 1. Data Freshness Gap
- Most dashboards refresh hourly at best; executives want near-real-time
- CDC pipeline (Debezium → Kafka) exists but only covers PostgreSQL; 60% of data sources are batch-only
- Real-time customer profile updates are blocked by batch ETL dependencies

### 2. Pipeline Fragility
- 200+ Airflow DAGs with complex interdependencies
- Average of 3-5 pipeline failures per week requiring manual intervention
- Silent failures: some pipelines succeed but produce incorrect data (caught days later)
- Backfill operations are painful and error-prone

### 3. Schema Evolution Nightmares
- Source schema changes break downstream dbt models regularly
- No automated schema change detection or migration
- Average time to fix a schema-break incident: 4-6 hours

### 4. Data Quality Gaps
- dbt tests catch ~40% of quality issues; rest discovered by end users
- No data observability tooling beyond basic dbt tests
- Duplicate records are a recurring problem across multiple sources

### 5. Cost Creep
- Snowflake costs have grown 50% year-over-year
- Many unused or underutilized dbt models still running
- No clear cost attribution per team or use case

## Technical Debt
- 30% of Airflow DAGs are undocumented
- Custom Python scripts for data extraction lack tests
- No centralized data catalog or data dictionary
- Feature store is a spreadsheet maintained manually by data scientists
