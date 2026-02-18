# Technical Metadata Directory

**IMPORTANT**: The files in this directory are **EXAMPLES ONLY**. Replace them with your own system metadata before running the system.

## What to Provide

Provide structured data (JSON, YAML, or plain text) about your current data systems. The MCP server can read any format and search across all files.

---

## Template 1: Schema Inventory

**Suggested filename**: `schema_inventory.json` (or `.yaml`)

**What to include**:

```json
{
  "databases": [
    {
      "name": "your_database_name",
      "type": "PostgreSQL 15 / MySQL 8 / etc.",
      "size": "2TB",
      "tables": [
        {
          "name": "table_name",
          "rows": "10M",
          "columns": ["id", "user_id", "created_at", "..."],
          "primary_key": "id",
          "indexes": ["user_id", "created_at"]
        }
      ]
    },
    {
      "name": "your_warehouse",
      "type": "Snowflake / BigQuery / Redshift",
      "schemas": ["raw", "staging", "marts"],
      "models": 250
    }
  ],
  "key_relationships": [
    "users.id -> orders.user_id",
    "orders.id -> order_items.order_id"
  ],
  "lineage_notes": "Optional: describe any complex lineage"
}
```

**Sources for this data**:
- Export from your data catalog (Alation, Atlan, DataHub, etc.)
- `INFORMATION_SCHEMA` queries from your databases
- dbt `manifest.json` for transformation lineage
- Manual documentation if needed

---

## Template 2: Infrastructure Catalog

**Suggested filename**: `infrastructure_catalog.json` (or `.yaml`)

**What to include**:

```json
{
  "compute": [
    {
      "name": "Airflow / Prefect / Dagster / etc.",
      "version": "2.x",
      "deployment": "Kubernetes / ECS / managed",
      "workers": 8,
      "resource_limits": "..."
    }
  ],
  "databases": [
    {
      "name": "Primary DB",
      "type": "PostgreSQL",
      "version": "15.4",
      "deployment": "RDS / self-managed",
      "instance_type": "r6g.2xlarge",
      "storage": "2TB"
    }
  ],
  "streaming": [
    {
      "name": "Kafka / Pulsar / Kinesis / etc.",
      "version": "3.x",
      "brokers": 3,
      "topics": 50,
      "retention": "7 days"
    }
  ],
  "storage": [
    {
      "name": "S3 / GCS / Azure Blob",
      "buckets": ["raw-data", "processed"],
      "total_size": "50TB"
    }
  ],
  "connectors": [
    {
      "name": "Fivetran / Airbyte / etc.",
      "sources": 15,
      "sync_frequency": "hourly"
    }
  ],
  "observability": [
    {
      "name": "Datadog / Prometheus / etc.",
      "purpose": "Infrastructure monitoring"
    }
  ]
}
```

**Sources for this data**:
- Infrastructure-as-code (Terraform/CloudFormation exports)
- Cloud provider console
- APM/observability tool inventory
- Manual documentation

---

## Template 3: Pipeline Definitions

**Suggested filename**: `pipeline_definitions.yaml` (or `.json`)

**What to include**:

```yaml
pipelines:
  - name: source_to_raw
    schedule: "hourly / daily / continuous"
    type: ingestion / transformation / ml_features / reporting
    sources: [list of sources]
    destination: target_system
    dependencies: [upstream pipeline names]

  - name: dbt_staging
    schedule: "hourly"
    type: transformation
    models: 120
    dependencies: [source_to_raw]

  - name: analytics_aggregations
    schedule: "every 4 hours"
    type: transformation
    models: 80
    dependencies: [dbt_staging]
```

**Sources for this data**:
- Airflow DAG exports (`airflow dags list`)
- dbt `manifest.json`
- Prefect/Dagster/etc. workflow exports
- Manual documentation of critical pipelines

---

## Template 4: Data Volume Statistics

**Suggested filename**: `volume_stats.json` (or `.yaml`)

**What to include**:

```json
{
  "ingestion_rates": {
    "source_1": "1M rows/hour",
    "source_2": "500K events/hour",
    "total_daily": "50M events/day"
  },
  "storage_sizes": {
    "transactional_db": "2TB (growing 50GB/month)",
    "warehouse_raw": "10TB",
    "warehouse_transformed": "5TB",
    "object_storage": "50TB"
  },
  "query_patterns": {
    "bi_queries": "2K queries/day",
    "ad_hoc": "500 queries/day",
    "api_queries": "1M requests/day",
    "peak_concurrent": 50
  },
  "peak_load": {
    "daily_peak": "9AM-12PM local time",
    "monthly_peak": "First week of month (reporting)",
    "seasonal": "Q4 holiday season is 3x normal"
  }
}
```

**Sources for this data**:
- Database monitoring (CloudWatch, Datadog, etc.)
- Warehouse query history (`QUERY_HISTORY` in Snowflake, `INFORMATION_SCHEMA.JOBS` in BigQuery)
- Application logs
- Cost reports (Snowflake usage, BigQuery usage, etc.)

---

## Alternative Format: Plain Text

If you don't have structured JSON/YAML, plain text works too:

**Example** (`metadata_summary.txt`):

```
## Databases
- PostgreSQL 15 on RDS, 2TB, 50 tables, 100M+ total rows
- Snowflake warehouse: 15TB total (8TB raw, 5TB transformed, 2TB marts)

## Pipelines
- 200+ Airflow DAGs (mostly hourly batch)
- 400 dbt models
- 25 Kafka topics for CDC

## Data Volumes
- Ingestion: ~2M rows/hour from all sources
- Storage growth: ~500GB/month
- Query load: ~5K queries/day peak

## Technologies
- Airflow 2.7 on Kubernetes
- dbt 1.6 (dbt Cloud)
- Kafka 3.5 (MSK)
- Fivetran (15 connectors)
```

---

## Example Files Provided

The current files (`schema_inventory.json`, `infrastructure_catalog.json`, etc.) describe the **same fictional e-commerce SaaS company** as the enterprise docs:
- 200+ Airflow DAGs
- 400 dbt models
- PostgreSQL + Snowflake
- 15M orders, 500M events

**These are for reference only. Delete or overwrite them with your actual metadata.**

---

## What If You Don't Have This Data?

**Minimum viable**: Just create a simple text file with whatever you know:

```
# metadata_summary.txt

We have:
- MySQL database with ~100 tables, ~50GB
- Daily cron jobs that dump CSVs to S3
- Analysts query S3 with Athena
- ~20 reports in Looker

We're trying to move to real-time and add ML capabilities.
```

The system will work with whatever level of detail you provide. More detail = better proposals.

---

## Tips

1. **Export from existing tools**: Most data catalogs, warehouses, and orchestrators can export metadata programmatically
2. **Don't worry about perfect accuracy**: Approximate numbers are fine (e.g., "~100 tables" instead of exactly 127)
3. **Focus on what's relevant to your problem**: If you're solving data freshness issues, emphasize ingestion rates and pipeline schedules
4. **Include growth trends**: "Growing 500GB/month" is more useful than just "10TB"
