# Streaming Architecture Patterns

## Kappa Architecture
- **Description**: A simplification of Lambda architecture that treats all data as streams. Instead of maintaining separate batch and speed layers, Kappa processes everything through a single stream processing engine with replayable logs. The immutable log (e.g., Kafka) serves as the system of record, and derived views are rebuilt by replaying the log when processing logic changes.
- **Key Components**:
  - Immutable append-only log (Kafka, Pulsar, Kinesis)
  - Stream processing engine (Flink, Kafka Streams, Spark Structured Streaming)
  - Materialized views / serving layer (RocksDB, Cassandra, Elasticsearch)
  - Schema registry for evolution
- **Tradeoffs**:
  - Pro: Single codebase for all processing; simpler operational model
  - Pro: Natural fit for event-driven microservices
  - Con: Reprocessing large historical datasets can be slow and expensive
  - Con: Complex aggregations over long time windows are harder to express
  - Con: Log retention costs grow with data volume
- **Real-world Examples**: LinkedIn activity feed processing, Uber trip event processing, Netflix real-time personalization

## Lambda Architecture
- **Description**: A hybrid architecture with parallel batch and speed (real-time) layers that merge results in a serving layer. The batch layer provides comprehensive, accurate views over complete datasets; the speed layer compensates for batch latency with approximate real-time views. Results are merged at query time.
- **Key Components**:
  - Batch layer (Hadoop, Spark batch jobs)
  - Speed layer (Storm, Flink, Kafka Streams)
  - Serving layer (Druid, HBase, Cassandra)
  - Master dataset (immutable, append-only)
  - Merge/reconciliation logic
- **Tradeoffs**:
  - Pro: Handles both historical and real-time use cases well
  - Pro: Batch layer can correct errors from speed layer
  - Con: Dual codebase maintenance (batch + streaming logic must be kept in sync)
  - Con: Operational complexity of running two parallel systems
  - Con: Merge logic can become a source of subtle bugs
- **Real-world Examples**: Twitter trending topics, traditional data warehouse + real-time dashboard setups

## Streaming-First / Stream-Native Architecture
- **Description**: An architecture where streaming is the default paradigm for all data movement. Batch is treated as a special case of streaming (bounded streams). All services communicate via event streams, and tables are derived views of streams. This inverts the traditional model where batch is primary and streaming is an add-on.
- **Key Components**:
  - Event backbone (Kafka, Redpanda, Pulsar)
  - Stream processing framework with table-stream duality (ksqlDB, Flink SQL)
  - Changelog capture for all stateful stores
  - Stream catalog and governance layer
  - Exactly-once semantics infrastructure
- **Tradeoffs**:
  - Pro: Uniform programming model; lower end-to-end latency
  - Pro: Natural support for event-driven microservices and reactive systems
  - Con: Higher infrastructure baseline cost (always-on processing)
  - Con: Requires team skill shift from batch-oriented thinking
  - Con: Debugging distributed stream topologies is challenging
- **Real-world Examples**: Confluent-native architectures, modern fintech payment processing

## Change Data Capture (CDC)
- **Description**: A pattern that captures row-level changes (inserts, updates, deletes) from database transaction logs and publishes them as a stream of events. This enables real-time data integration without polling, triggers, or application-level dual writes. CDC bridges the gap between operational databases and streaming/analytical systems.
- **Key Components**:
  - Log-based CDC connector (Debezium, Maxwell, AWS DMS)
  - Source database with accessible transaction log (MySQL binlog, PostgreSQL WAL, MongoDB oplog)
  - Event streaming platform (Kafka) as change event transport
  - Schema evolution handling
  - Sink connectors for target systems
- **Tradeoffs**:
  - Pro: Zero-impact on source database performance (reads from log)
  - Pro: Captures all changes including deletes; preserves ordering
  - Pro: Enables real-time data mesh and event-driven integration
  - Con: Schema evolution must be managed carefully across source and consumers
  - Con: Database-specific; different CDC mechanisms per database engine
  - Con: Initial snapshot of existing data can be resource-intensive
- **Real-world Examples**: Debezium-based data lake ingestion, real-time cache invalidation, cross-region database replication

## Real-Time ETL / Streaming ETL
- **Description**: Replaces traditional batch ETL with continuous, low-latency data transformation pipelines. Data is extracted, transformed, and loaded as it arrives rather than in scheduled batches. Enables operational analytics and reduces the gap between data generation and data availability.
- **Key Components**:
  - Stream ingestion layer (Kafka Connect, Flume, custom producers)
  - Stream transformation engine (Flink, Beam, Spark Structured Streaming)
  - Quality validation and dead-letter queues
  - Exactly-once delivery guarantees
  - Streaming data catalog and lineage tracking
- **Tradeoffs**:
  - Pro: Minutes/seconds latency vs. hours for batch ETL
  - Pro: Continuous validation catches data quality issues faster
  - Con: Harder to handle late-arriving data and out-of-order events
  - Con: Windowing semantics add complexity to aggregations
  - Con: Error recovery and reprocessing are more complex than batch reruns
- **Real-world Examples**: Real-time fraud scoring, continuous IoT sensor data warehousing, live marketing attribution

## Event Stream Processing with Complex Event Processing (CEP)
- **Description**: A pattern focused on detecting meaningful patterns, correlations, and sequences across multiple event streams in real time. CEP engines match incoming events against predefined or dynamic pattern rules and trigger actions when patterns are detected. Useful for monitoring, fraud detection, and operational intelligence.
- **Key Components**:
  - CEP engine (Esper, Flink CEP, Siddhi, Apache Samza)
  - Pattern definition language / rules DSL
  - Temporal windowing and sequencing operators
  - Alert/action dispatcher
  - Event correlation store
- **Tradeoffs**:
  - Pro: Detects multi-event patterns that single-event processing misses
  - Pro: Temporal reasoning (within X minutes, followed by, etc.)
  - Con: Pattern explosion: complex rules become hard to test and maintain
  - Con: State management for long-running patterns is memory-intensive
  - Con: Debugging why a pattern did or did not fire is difficult
- **Real-world Examples**: Credit card fraud detection (unusual sequence of transactions), network intrusion detection, supply chain anomaly monitoring

## Micro-Batching
- **Description**: A pragmatic middle ground between pure streaming and batch processing. Events are collected into small batches (typically 1-30 seconds) and processed as mini-batches. Provides near-real-time latency with the simpler programming model of batch processing.
- **Key Components**:
  - Micro-batch scheduler (Spark Streaming, custom accumulators)
  - Batch-interval tuning mechanism
  - Checkpoint and recovery infrastructure
  - Output commit protocol (for exactly-once)
- **Tradeoffs**:
  - Pro: Simpler fault tolerance (replay a small batch vs. per-record checkpointing)
  - Pro: Higher throughput due to batch-level optimizations
  - Con: Latency floor set by batch interval (cannot go sub-second easily)
  - Con: Not suitable for true event-at-a-time processing (e.g., CEP)
  - Con: Window boundary effects can cause processing skew
- **Real-world Examples**: Spark Streaming jobs, near-real-time dashboards, log aggregation pipelines

## Windowed Stream Aggregation
- **Description**: A core streaming pattern for computing aggregates (counts, sums, averages, percentiles) over defined time windows. Windows can be tumbling (fixed, non-overlapping), sliding (overlapping), session-based (activity-driven), or global. Proper watermark and late-data handling is essential.
- **Key Components**:
  - Window assigner (tumbling, sliding, session, global)
  - Watermark generator (for event-time processing)
  - Trigger policy (when to emit results)
  - Allowed lateness configuration
  - State backend for in-progress windows
- **Tradeoffs**:
  - Pro: Enables real-time metrics, monitoring, and analytics
  - Pro: Session windows capture user-behavior patterns naturally
  - Con: Late data handling introduces complexity and potential inaccuracy
  - Con: Large windows or high-cardinality keys cause state explosion
  - Con: Choosing watermark strategy involves an accuracy-vs-latency tradeoff
- **Real-world Examples**: Real-time click-through rate computation, IoT sensor anomaly detection windows, ride-sharing demand forecasting

## Streaming Data Mesh
- **Description**: Applies data mesh principles (domain ownership, data as product, self-serve platform, federated governance) to streaming architectures. Each domain team owns and publishes its event streams as data products with defined schemas, SLAs, and discoverability. A self-serve streaming platform provides shared infrastructure.
- **Key Components**:
  - Domain-owned stream topics with schema contracts
  - Self-serve streaming platform (managed Kafka/Flink)
  - Stream catalog and discovery service
  - Federated schema governance (schema registry with compatibility rules)
  - Cross-domain event routing and access control
  - SLA monitoring and data quality metrics per stream
- **Tradeoffs**:
  - Pro: Scales organizational ownership; reduces central bottleneck
  - Pro: Domain teams iterate on their streams independently
  - Con: Cross-domain stream joins require careful coordination
  - Con: Governance overhead to maintain interoperability standards
  - Con: Risk of schema drift without strong enforcement
- **Real-world Examples**: Large enterprise event-driven microservice ecosystems, financial institutions with domain-specific real-time feeds

## Backpressure and Flow Control Patterns
- **Description**: Mechanisms for handling situations where upstream producers generate data faster than downstream consumers can process. Without backpressure, systems either drop data or exhaust memory. Proper flow control ensures system stability under variable load.
- **Key Components**:
  - Reactive Streams / backpressure protocol (request-based pull)
  - Buffer management with overflow strategies (drop, buffer, throttle)
  - Credit-based flow control
  - Dynamic scaling triggers (autoscaling consumers)
  - Dead-letter queues for unprocessable messages
- **Tradeoffs**:
  - Pro: Prevents out-of-memory failures and data loss under load spikes
  - Pro: Enables graceful degradation instead of cascading failure
  - Con: Backpressure propagation can cause head-of-line blocking
  - Con: Buffering adds latency; dropping loses data; both have costs
  - Con: Tuning buffer sizes and thresholds requires empirical testing
- **Real-world Examples**: Flink network buffer backpressure, Reactive Streams in Akka/Project Reactor, Kafka consumer lag-based autoscaling
