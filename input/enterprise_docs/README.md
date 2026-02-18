# Enterprise Documentation Directory

**IMPORTANT**: The files in this directory are **EXAMPLES ONLY**. Replace them with your own organization's documentation before running the system.

## What to Provide

Create markdown files describing your data pipeline organization. The MCP server searches for keywords in filenames, so exact naming isn't critical.

---

## Template 1: Current Architecture

**Suggested filename**: `architecture.md` or `current_architecture.md`

**What to include**:

```markdown
# Current Data Pipeline Architecture

## Overview
[High-level description of your data architecture]

## Component Inventory
### Ingestion Layer
- [Data sources and ingestion tools]
- [Connectors, CDC systems, API integrations]

### Orchestration
- [Orchestration tool: Airflow, Prefect, Dagster, etc.]
- [Number of DAGs/workflows]
- [Scheduling patterns]

### Transformation Layer
- [Transformation tools: dbt, Spark, Dataform, etc.]
- [Number of models/transformations]
- [Testing approach]

### Storage
- [Databases: transactional and analytical]
- [Data warehouse/lakehouse]
- [Object storage]

### Serving Layer
- [BI tools]
- [Data APIs]
- [Reverse ETL]
- [ML serving]

## Data Flow
[Describe how data flows through the system, step by step]

## Technologies
[List all major technologies with versions if relevant]
```

---

## Template 2: Business Goals

**Suggested filename**: `business_goals.md`

**What to include**:

```markdown
# Business Goals & Strategic Priorities

## Mission
[Overall mission for your data platform]

## Key Business Goals
1. **[Goal 1 Name]**
   - Description
   - Target metrics
   - KPIs
   - Timeline

2. **[Goal 2 Name]**
   - Description
   - Target metrics
   - KPIs
   - Timeline

[Continue for each major goal]

## Success Criteria
[How you'll measure success of a new architecture]
```

**Examples of goals**:
- Real-time operational analytics (< 1 minute latency)
- ML/AI platform with feature store
- Cost reduction (specific target %)
- Improved data quality (specific metrics)
- Faster time-to-insight for analysts
- Compliance/governance automation

---

## Template 3: Constraints

**Suggested filename**: `constraints.md`

**What to include**:

```markdown
# Constraints & Requirements

## Regulatory / Compliance
- [GDPR, CCPA, HIPAA, SOC 2, etc.]
- [Data residency requirements]
- [PII handling requirements]
- [Audit requirements]

## Budget
- Current annual data infrastructure spend: $[amount]
- Maximum acceptable increase: [%] or $[amount]
- Pricing preference: [usage-based, reserved capacity, etc.]

## SLAs
- [Data freshness SLAs]
- [Query performance SLAs]
- [Uptime requirements]
- [Recovery time objectives (RTO)]

## Security
- [Authentication/authorization requirements]
- [Network security requirements]
- [Access control requirements]
- [Encryption requirements]

## Technical
- [Cloud provider requirements: AWS, GCP, Azure, multi-cloud]
- [Deployment requirements: Kubernetes, serverless, etc.]
- [Infrastructure-as-code requirements]
- [Other technical constraints]
```

---

## Template 4: Team Profile

**Suggested filename**: `team.md`

**What to include**:

```markdown
# Team Profile

## Data Engineering Team
- Team size: [number]
- Seniority: [breakdown]
- Strong skills: [list]
- Moderate skills: [list]
- Limited skills / learning: [list]

## Analytics Engineering Team
- Team size: [number]
- Strong skills: [list]
- Focus areas: [list]

## Platform / Infrastructure
- Team size: [number]
- Bandwidth for data-specific work: [full-time, shared, limited]
- Skills: [list]

## Data Science / ML Engineering
- Team size: [number]
- Focus: [ML models, experimentation, feature engineering, etc.]

## Organization
- Reporting structure
- Development methodology (Agile, Scrum, Kanban, etc.)
- On-call rotation
- Key stakeholders
```

---

## Template 5: Pain Points & Technical Debt

**Suggested filename**: `pain_points.md`

**What to include**:

```markdown
# Pain Points & Technical Debt

## Critical Pain Points

### 1. [Pain Point Name]
- **Description**: [What's broken or limiting]
- **Impact**: [Business impact, who's affected]
- **Frequency**: [How often this causes problems]
- **Root cause** (if known): [Why this happens]

### 2. [Pain Point Name]
[Same structure]

[Continue for each major pain point]

## Technical Debt
- [List major areas of technical debt]
- [Workarounds that need to be eliminated]
- [Legacy systems that need replacement]

## Recent Incidents
- [Brief description of recent data incidents/outages]
- [Patterns in failures]
```

**Common pain points to consider**:
- Data freshness gaps
- Pipeline fragility / frequent failures
- Schema evolution nightmares
- Data quality issues
- Cost creep
- Slow query performance
- Difficulty debugging
- Lack of observability
- Complex backfills
- Team bottlenecks

---

## Example Files Provided

The current files (`architecture.md`, `business_goals.md`, etc.) describe a **fictional e-commerce SaaS company** with:
- Airflow + Snowflake + dbt stack
- Batch-heavy architecture with real-time aspirations
- Standard pain points: data freshness, pipeline fragility, schema changes

**These are for reference only. Delete or overwrite them with your actual documentation.**

---

## Tips for Good Documentation

1. **Be specific**: Numbers, metrics, and concrete examples are better than vague descriptions
2. **Include scale**: Data volumes, team sizes, user counts, etc.
3. **Describe what works AND what doesn't**: Don't just list problems — also describe what's working well
4. **Use your team's language**: If you call it a "data lake," don't call it a "data warehouse"
5. **Include recent context**: Recent incidents, recent decisions, recent changes

The better your input documentation, the more tailored and relevant the architecture proposals will be.
