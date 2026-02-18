# Input Data Directory

**IMPORTANT**: You must replace the example files in this directory with YOUR OWN enterprise documentation before running the system.

## What You Need to Provide

The system requires two types of input:

### 1. Enterprise Documentation (`enterprise_docs/`)

Create markdown files describing your data pipeline organization. These files are read by the `enterprise-docs-server` MCP server.

**Required information**:
- **Current architecture** — Components, data flow, technologies, integrations
- **Business goals** — Objectives, KPIs, strategic priorities, success metrics
- **Constraints** — Regulatory/compliance, budget, SLAs, security, data residency
- **Team profile** — Team size, skills, experience, organizational structure
- **Pain points** — Known problems, bottlenecks, incidents, technical debt

See `enterprise_docs/README.md` for detailed templates.

### 2. Technical Metadata (`metadata/`)

Provide structured data (JSON/YAML) about your current systems. These files are read by the `metadata-server` MCP server.

**Recommended files**:
- **Schema inventory** — Database schemas, tables, columns, relationships, lineage
- **Infrastructure catalog** — Deployed infrastructure inventory with versions
- **Pipeline definitions** — Current pipeline/DAG definitions, schedules, dependencies
- **Data volume statistics** — Ingestion rates, storage sizes, query patterns

See `metadata/README.md` for detailed templates and examples.

## Current Files

The files currently in `enterprise_docs/` and `metadata/` are **EXAMPLES ONLY** showing a fictional company's data pipeline. They demonstrate the format and level of detail expected.

### Example Company: Fictional E-commerce SaaS

The example describes:
- A batch-oriented ETL system with Airflow, Snowflake, and PostgreSQL
- 200+ DAGs, 400 dbt models, 15+ data sources
- Pain points: data freshness gaps, pipeline fragility, schema evolution issues
- Business goal: sub-hour data freshness for real-time customer 360

**You should replace all example files with your own documentation.**

## How the System Uses This Data

1. **Pre-fetching**: At startup, `main.py` calls `gather_enterprise_context()` which connects to the MCP servers
2. **MCP servers read your files**: Each server loads files from its configured directory
3. **Context injection**: The gathered context is injected into LLM prompts at each stage
4. **Intent analysis**: Stage 0a uses this context to diagnose your specific problem
5. **Paradigm agents**: Stage 1 agents design architectures tailored to YOUR situation

The more specific and detailed your input, the better the proposals will be.

## Minimum Viable Input

If you don't have all the recommended files, the system can still run with:

**Minimum**:
- `enterprise_docs/architecture.md` — Basic description of your current architecture
- `enterprise_docs/pain_points.md` — What you're trying to solve

**Recommended to add**:
- `enterprise_docs/business_goals.md` — What success looks like
- `enterprise_docs/constraints.md` — Hard constraints (budget, compliance, SLAs)
- `metadata/schema_inventory.json` — Basic schema information

## File Naming

File names are flexible — the MCP servers search for keywords. For example:
- `architecture.md`, `current_architecture.md`, or `arch_overview.md` all work
- `business_goals.md`, `goals.md`, or `objectives.md` all work

Use whatever naming makes sense for your organization.
