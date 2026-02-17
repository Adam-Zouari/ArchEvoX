# Event Sourcing and CQRS Patterns

## Classic Event Sourcing
- **Description**: Instead of storing the current state of an entity, every state change is captured as an immutable event in an append-only event store. The current state is derived by replaying events from the beginning or from a snapshot. This provides a complete audit trail, enables temporal queries, and allows the system to reconstruct state at any point in time.
- **Key Components**:
  - Event store (EventStoreDB, Kafka, DynamoDB Streams, custom RDBMS-backed)
  - Aggregate root (domain entity that emits events)
  - Event handlers / projectors (build read models from events)
  - Snapshot store (periodic state snapshots for replay optimization)
  - Event schema registry and versioning
- **Tradeoffs**:
  - Pro: Full audit trail; perfect for compliance-heavy domains (finance, healthcare)
  - Pro: Enables temporal queries ("what was the state at time T?")
  - Pro: Natural fit for event-driven architectures and domain-driven design
  - Con: Event schema evolution is challenging (upcasting, versioning)
  - Con: Rebuilding state from long event histories is slow without snapshots
  - Con: Developers must shift from CRUD mindset to event-thinking
  - Con: Eventual consistency between event store and read models
- **Real-world Examples**: Banking transaction ledgers, e-commerce order lifecycle, Git version control (commits as events)

## CQRS (Command Query Responsibility Segregation)
- **Description**: Separates the write model (commands that mutate state) from the read model (queries that return data). The write side is optimized for consistency and business rule enforcement; the read side is optimized for query performance with denormalized, purpose-built views. Can be used with or without event sourcing.
- **Key Components**:
  - Command handlers (validate and execute mutations)
  - Command bus / dispatcher
  - Write model / domain model (enforces invariants)
  - Read model projections (denormalized query-optimized stores)
  - Synchronization mechanism (events, CDC, or direct DB replication)
  - Query handlers
- **Tradeoffs**:
  - Pro: Independent scaling of read and write workloads
  - Pro: Read models tailored to specific query patterns (no complex joins)
  - Pro: Write model stays focused on business logic, not query optimization
  - Con: Eventual consistency between write and read models
  - Con: Increased system complexity (multiple models to maintain)
  - Con: Must handle the read-your-own-writes problem for UX
- **Real-world Examples**: High-traffic e-commerce catalogs, social media feeds, reporting dashboards over transactional systems

## Event Sourcing + CQRS Combined
- **Description**: The most powerful combination: commands produce events stored in an event store (event sourcing), and those events are projected into purpose-built read models (CQRS). This gives full audit trails, temporal queries, independent read/write scaling, and the ability to add new read models retroactively by replaying events.
- **Key Components**:
  - All components from both Event Sourcing and CQRS
  - Event bus connecting write side to read side projectors
  - Projection rebuild infrastructure (replay from event store)
  - Idempotency handling in projectors
  - Consistency boundary definition (aggregate boundaries)
- **Tradeoffs**:
  - Pro: Maximum flexibility; new read models without touching write side
  - Pro: Complete system history; debug any state by replaying events
  - Con: Highest complexity; requires deep understanding of both patterns
  - Con: Testing requires event-based test fixtures
  - Con: Eventual consistency across all read models
- **Real-world Examples**: Axon Framework-based applications, large-scale booking systems, financial trading platforms

## Event Store Design Patterns

### Stream-per-Aggregate
- **Description**: Each aggregate instance gets its own event stream (e.g., `order-12345`). Events for that aggregate are appended to its dedicated stream. This is the most common event store partitioning strategy.
- **Key Components**: Aggregate ID-based stream naming, optimistic concurrency per stream, stream-level subscriptions
- **Tradeoffs**:
  - Pro: Natural concurrency boundary; no cross-aggregate contention
  - Pro: Simple to load an aggregate (read one stream)
  - Con: Cross-aggregate queries require projections or category streams
- **Real-world Examples**: EventStoreDB default model, Marten event store

### Stream-per-Type with Partitioning
- **Description**: Events are stored in streams organized by aggregate type (e.g., `orders`, `customers`), partitioned by aggregate ID. Better for systems with very high aggregate counts where per-aggregate streams would create too many streams.
- **Key Components**: Type-based stream naming, partition key on aggregate ID, global sequence numbers
- **Tradeoffs**:
  - Pro: Fewer streams to manage; easier category-level subscriptions
  - Con: Must filter by aggregate ID when loading a single aggregate
- **Real-world Examples**: Kafka-backed event stores (topic per aggregate type, partition by ID)

## Projection Patterns

### Synchronous (Inline) Projections
- **Description**: Read models are updated in the same transaction as event persistence. Provides strong consistency between events and projections at the cost of write latency.
- **Key Components**: Transactional outbox, same-process projection handlers
- **Tradeoffs**:
  - Pro: No eventual consistency lag; read-your-own-writes guaranteed
  - Con: Slower writes; projection failure blocks command processing

### Asynchronous Projections
- **Description**: Events are published to subscribers that update read models independently and asynchronously. The standard approach for CQRS systems.
- **Key Components**: Event subscription/polling mechanism, checkpoint tracking, idempotent projectors, catch-up subscription
- **Tradeoffs**:
  - Pro: Write performance unaffected by projection complexity
  - Pro: Can add new projections without modifying write side
  - Con: Eventual consistency; stale reads possible

### Live + Catch-Up Projections
- **Description**: Combines historical replay (catch-up) with live subscription. On startup or rebuild, the projector replays all historical events, then seamlessly switches to live processing. Essential for adding new read models to an existing system.
- **Key Components**: Catch-up subscription, position tracking, seamless handoff to live, backfill progress monitoring
- **Tradeoffs**:
  - Pro: New projections can be added at any time without data migration
  - Con: Replay of large event stores can take hours/days

## Saga / Process Manager Pattern
- **Description**: Coordinates long-running business processes that span multiple aggregates or services by reacting to events and issuing commands. Maintains its own state to track the progress of the process. Unlike a simple event handler, a saga can make decisions based on the combination of events it has received.
- **Key Components**:
  - Saga state machine (tracks process progress)
  - Event handlers (react to domain events)
  - Command dispatchers (issue commands to aggregates/services)
  - Timeout handlers (handle non-response scenarios)
  - Compensation logic (undo previous steps on failure)
- **Tradeoffs**:
  - Pro: Manages complex multi-step business processes without distributed transactions
  - Pro: Explicit failure handling and compensation
  - Con: Saga state must be persisted reliably
  - Con: Complex sagas become hard to reason about and test
  - Con: Temporal coupling between services through the saga
- **Real-world Examples**: Order fulfillment (reserve inventory, charge payment, ship), travel booking (flight + hotel + car), insurance claim processing

## Outbox Pattern
- **Description**: Solves the dual-write problem (writing to a database and publishing an event must both succeed or both fail). Instead of publishing events directly, events are written to an "outbox" table in the same database transaction as the state change. A separate process reads the outbox and publishes events to the message broker.
- **Key Components**:
  - Outbox table in the application database
  - Outbox publisher (polling or CDC-based)
  - Deduplication mechanism on the consumer side
  - Outbox cleanup/archival process
- **Tradeoffs**:
  - Pro: Guarantees atomicity between state change and event publication
  - Pro: No distributed transaction (2PC) needed
  - Con: Adds latency (polling interval) or complexity (CDC setup)
  - Con: Outbox table can become a bottleneck under high write load
- **Real-world Examples**: Debezium outbox connector, microservice state-event consistency

## Snapshot Pattern
- **Description**: Periodically saves a snapshot of an aggregate's current state to avoid replaying the full event history every time the aggregate is loaded. On load, the system reads the latest snapshot and only replays events that occurred after the snapshot.
- **Key Components**:
  - Snapshot store (separate from event store or same store)
  - Snapshot frequency policy (every N events, every N minutes)
  - Snapshot versioning (handle code changes)
  - Fallback to full replay if snapshot is incompatible
- **Tradeoffs**:
  - Pro: Dramatically reduces aggregate load time for long-lived aggregates
  - Pro: Enables practical event sourcing for aggregates with thousands of events
  - Con: Snapshot versioning adds complexity during code evolution
  - Con: Storage overhead for snapshot data
- **Real-world Examples**: Account balance snapshots in banking, game state saves, shopping cart state

## Event Versioning and Upcasting
- **Description**: As the system evolves, event schemas change. Upcasting transforms old event versions to the current version during replay, so that application code only needs to handle the latest event schema. This is crucial for long-lived event-sourced systems.
- **Key Components**:
  - Event version metadata
  - Upcaster chain (transforms v1 -> v2 -> v3 -> ... -> vN)
  - Schema registry with compatibility checks
  - Event migration tooling (for breaking changes)
- **Tradeoffs**:
  - Pro: Application code only handles current event versions
  - Pro: Old events remain immutable in the store
  - Con: Upcaster chains grow over time and must be maintained
  - Con: Breaking schema changes may require event store migration
- **Real-world Examples**: Axon Framework upcasters, EventStoreDB event transformations

## Anti-Corruption Layer for Event Integration
- **Description**: When integrating event-sourced systems with external or legacy systems, an anti-corruption layer translates between the internal domain events and the external system's model. This prevents external system concerns from leaking into the domain model.
- **Key Components**:
  - Translator/adapter between internal and external event formats
  - Bounded context mapping
  - Event filtering (only expose relevant events externally)
  - Schema transformation pipeline
- **Tradeoffs**:
  - Pro: Domain model stays pure; external changes do not ripple inward
  - Pro: Can evolve internal and external models independently
  - Con: Additional translation layer to build and maintain
  - Con: Potential for information loss in translation
- **Real-world Examples**: Legacy system integration in banking, third-party API event bridges, multi-bounded-context communication
