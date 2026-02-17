# Architectural Anti-Patterns & Failure Modes

## 1. The God Pipeline

- **Description**: A single monolithic pipeline that ingests, transforms, validates, enriches, and serves data in one massive DAG. Any change risks breaking everything.
- **Failure Mode**: Deployment fear, 6+ hour recovery times, impossible to test components in isolation.
- **Root Cause**: Organic growth without modularization boundaries.
- **Fix**: Decompose into independent pipeline segments with clear contracts at boundaries.

## 2. Schema-on-Pray

- **Description**: No schema enforcement at ingestion or transformation boundaries. Data schemas are assumed to be stable and correct, with no validation.
- **Failure Mode**: Silent data corruption propagates through the entire pipeline before detection. Downstream models and dashboards produce wrong results for days.
- **Root Cause**: Schema validation seen as "too expensive" or "too slow."
- **Fix**: Schema registries, data contracts, and validation at every boundary.

## 3. The Batch Trap

- **Description**: Defaulting to batch processing for every use case, including those that would benefit from streaming. Hourly or daily batch jobs become the universal solution.
- **Failure Mode**: Data freshness expectations can never be met. Each request for "more real-time" adds another batch job running at higher frequency, increasing cost and fragility.
- **Root Cause**: Team familiarity with batch tools, fear of streaming complexity.
- **Fix**: Evaluate each data flow on its latency requirements; use streaming where sub-minute freshness is needed.

## 4. Distributed Monolith

- **Description**: Microservices or pipeline components that are deployed independently but are tightly coupled through shared databases, synchronous calls, or implicit data contracts.
- **Failure Mode**: Cascading failures, impossible to deploy or scale independently, worst of both worlds (distributed complexity + monolithic coupling).
- **Root Cause**: Decomposition by technical layer instead of by domain boundary.
- **Fix**: Domain-driven decomposition, event-driven communication, each service owns its data.

## 5. The Golden Dataset Illusion

- **Description**: Building a single "golden" dataset or data model that is supposed to serve all use cases. Every team adds their requirements to the golden model.
- **Failure Mode**: The golden model becomes impossibly complex, slow to query, expensive to maintain, and still doesn't serve anyone's needs perfectly.
- **Root Cause**: Desire for a single source of truth taken to its extreme.
- **Fix**: Multiple purpose-built materialized views derived from a shared event log or clean base tables.

## 6. ETL Spaghetti

- **Description**: Point-to-point data integrations between every source and destination, with each integration having its own custom code, schedule, and error handling.
- **Failure Mode**: Exponential growth in integration complexity (N sources × M destinations), impossible to maintain lineage or understand data flow.
- **Root Cause**: No centralized integration architecture; each team builds their own connectors.
- **Fix**: Hub-and-spoke architecture with a central data platform (event bus or data lake) as the interchange.

## 7. Premature Aggregation

- **Description**: Aggregating or summarizing data too early in the pipeline, destroying granular detail that downstream consumers need.
- **Failure Mode**: New analytical questions require re-engineering the pipeline from scratch. "We can't answer that because we threw away the raw data."
- **Root Cause**: Storage cost optimization or performance concerns applied too aggressively.
- **Fix**: Store raw events immutably; aggregate only at the serving layer for specific use cases.

## 8. The Accidental Data Lake

- **Description**: Dumping all data into a data lake without organization, cataloging, or quality controls. The "just put it in S3" approach.
- **Failure Mode**: Data swamp — nobody knows what data exists, its quality, its freshness, or how to use it. The lake becomes write-only.
- **Root Cause**: Treating storage as free and assuming discovery will happen organically.
- **Fix**: Data cataloging, metadata management, quality gates at ingestion, clear ownership.

## 9. Observability Afterthought

- **Description**: Building complex data pipelines with no monitoring, alerting, or data quality observability. Failures are discovered by end users.
- **Failure Mode**: Silent data issues persist for days or weeks. Trust in data erodes. Teams build shadow systems to manually verify data.
- **Root Cause**: Observability treated as a nice-to-have rather than a core requirement.
- **Fix**: Data observability built into the pipeline from day one — freshness, volume, schema, and value distribution monitoring.

## 10. Resume-Driven Architecture

- **Description**: Choosing technologies because they are trendy or impressive on a resume, not because they solve the actual problem. Using Kafka for 100 events/day, Kubernetes for 3 cron jobs, etc.
- **Failure Mode**: Massive operational overhead for simple problems. Team can't maintain systems they don't understand.
- **Root Cause**: Hype cycles, conference talks, and FOMO.
- **Fix**: Start with the simplest technology that meets requirements. Upgrade when you hit actual scaling limits, not anticipated ones.

## 11. Synchronous Data Pipeline

- **Description**: Building data pipelines with synchronous, blocking calls between stages. Each stage waits for the previous one to complete before starting.
- **Failure Mode**: End-to-end latency is the sum of all stage latencies. One slow stage blocks everything. No parallelism.
- **Root Cause**: Imperative programming habits applied to data flow.
- **Fix**: Asynchronous, event-driven pipeline stages that decouple producers from consumers.

## 12. Ignoring Backpressure

- **Description**: Not handling the case where data producers generate data faster than consumers can process it. No flow control mechanism.
- **Failure Mode**: Memory exhaustion, dropped data, cascading failures as buffers overflow.
- **Root Cause**: Testing only with normal load, not peak or burst scenarios.
- **Fix**: Explicit backpressure mechanisms — bounded queues, rate limiting, reactive streams.
