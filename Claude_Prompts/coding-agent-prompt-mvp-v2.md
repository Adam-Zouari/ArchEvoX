# Coding Agent Prompt: Innovation-Optimized Multi-Agent Architecture Generator (MVP)

## Mission

Build a Python-based multi-agent system that generates innovative data pipeline architecture proposals. The system takes enterprise documentation as input (metadata, technologies used, business goals, constraints) and outputs a ranked portfolio of architectural proposals ranging from conservative to radically novel.

The system is explicitly optimized for **architectural innovation and paradigm shifts**, not just optimization of existing patterns. This is not a chatbot — it is a pipeline that orchestrates multiple LLM calls in a specific sequence with specific roles.

---

## System Overview

The system has 5 sequential stages:

```
INPUT (enterprise context via MCP servers)
  → Stage 1: Paradigm Agent Generation (4 agents, parallel)
  → Stage 2: Idea Mutation (transform each proposal with mutation operators)
  → Stage 3: Self-Refinement (2 rounds of self-critique per proposal)
  → Stage 4: Physics Critic (annotate hard-constraint violations, do NOT reject)
  → Stage 5: Portfolio Assembly & Ranking
OUTPUT (ranked portfolio of architectures as structured JSON + markdown report)
```

---

## Tech Stack

- **Language**: Python 3.11+
- **LLM Integration**: `litellm` — model-agnostic LLM abstraction layer. The user configures which model to use via `config.yaml` or environment variables.
- **Structured Output Parsing**: `instructor` — patched on top of `litellm` to extract Pydantic models directly from LLM responses. Every LLM call in every stage must return a typed Pydantic model, never raw text.
- **Data Access Layer**: **MCP (Model Context Protocol)** — agents access enterprise documentation, metadata, schemas, infrastructure catalogs, and architectural pattern knowledge bases through MCP servers, not through prompt-stuffing. The system runs MCP servers as part of its runtime and agents query them on demand.
- **Async**: `asyncio` for parallel agent execution within each stage.
- **Configuration**: `config.yaml` for all tunable parameters.
- **Output**: Structured JSON + rendered Markdown report.
- **No agent frameworks**: Do NOT use LangChain, LangGraph, CrewAI, AutoGen, or any agent framework. Orchestration is explicit Python code — plain functions and async calls.

### Key Dependencies

```
litellm>=1.40.0
instructor>=1.3.0
mcp>=1.0.0
pydantic>=2.0
pyyaml>=6.0
jinja2>=3.1        # for markdown report templating
aiofiles>=23.0
```

---

## MCP Server Architecture

The system exposes enterprise context to agents through 3 MCP servers. These servers run as part of the system's process (using `mcp` Python SDK's stdio or SSE transport) and are queried by agents during generation.

### MCP Server 1: `enterprise-docs-server`

**Purpose**: Serves enterprise documentation — current architecture descriptions, business goals, constraints, SLAs, team structure, compliance requirements.

**Tools it exposes**:

```python
@server.tool()
async def get_current_architecture() -> str:
    """Returns the full description of the current data pipeline architecture,
    including component inventory, data flow diagrams (as text), and technology stack."""

@server.tool()
async def get_business_goals() -> str:
    """Returns the business goals, KPIs, and strategic priorities that the
    data pipeline must support."""

@server.tool()
async def get_constraints() -> str:
    """Returns hard constraints: regulatory/compliance requirements, budget limits,
    SLAs, latency requirements, data residency rules, security mandates."""

@server.tool()
async def get_team_profile() -> str:
    """Returns team skills, size, experience level, and organizational structure
    relevant to architecture decisions."""

@server.tool()
async def get_pain_points() -> str:
    """Returns known pain points, bottlenecks, incidents, and technical debt
    in the current architecture."""
```

**Data source**: Reads from a directory of markdown/text/JSON files that the user provides as input. The directory path is configured in `config.yaml` under `mcp.enterprise_docs.data_dir`.

### MCP Server 2: `metadata-server`

**Purpose**: Serves technical metadata — schemas, data catalogs, pipeline definitions, infrastructure inventory.

**Tools it exposes**:

```python
@server.tool()
async def get_schema_inventory() -> str:
    """Returns all known data schemas — tables, columns, types, relationships,
    lineage information. Formatted as structured text or JSON."""

@server.tool()
async def get_pipeline_definitions() -> str:
    """Returns current pipeline/job definitions — DAGs, schedules, dependencies,
    transformation logic summaries."""

@server.tool()
async def get_infrastructure_catalog() -> str:
    """Returns deployed infrastructure — databases, message queues, compute
    clusters, storage systems, orchestrators, with versions and configurations."""

@server.tool()
async def get_data_volume_stats() -> str:
    """Returns data volume statistics — ingestion rates, storage sizes,
    query patterns, peak load profiles."""

@server.tool()
async def search_metadata(query: str) -> str:
    """Free-text search across all metadata. Use when looking for specific
    tables, pipelines, technologies, or configurations."""
```

**Data source**: Reads from structured files (JSON, YAML, SQL DDL exports) in a configured directory. Can also wrap existing APIs (data catalog, schema registry) if the user provides connection details.

### MCP Server 3: `patterns-knowledge-server`

**Purpose**: Provides a knowledge base of architectural patterns — both conventional and unconventional — that agents can query for inspiration. This is what gives the mutation engine and wildcard agent access to cross-domain patterns.

**Tools it exposes**:

```python
@server.tool()
async def get_patterns_by_paradigm(paradigm: str) -> str:
    """Returns architectural patterns for a given paradigm.
    Supported paradigms: 'streaming', 'event-sourcing', 'declarative',
    'graph-native', 'lakehouse', 'data-mesh', 'data-fabric',
    'biological', 'economic', 'physical', 'social'.
    Returns: pattern name, description, key components, known tradeoffs,
    real-world examples."""

@server.tool()
async def get_cross_domain_analogies(source_domain: str, target_concept: str) -> str:
    """Given a source domain (e.g., 'immunology', 'supply-chain', 'thermodynamics')
    and a target concept (e.g., 'data routing', 'error handling', 'resource allocation'),
    returns known cross-domain pattern mappings with concrete architectural translations."""

@server.tool()
async def get_emerging_patterns() -> str:
    """Returns recently emerging or experimental architectural patterns that
    are not yet mainstream. Includes academic proposals, startup architectures,
    and unconventional production systems."""

@server.tool()
async def get_anti_patterns() -> str:
    """Returns common architectural anti-patterns and their failure modes.
    Useful for the physics critic and self-refinement stages to check
    proposals against known bad patterns."""
```

**Data source**: A curated knowledge base shipped with the system as markdown/JSON files. The user can extend it by adding files to the configured directory. This is the most important server for innovation — invest heavily in curating high-quality, diverse content here. Include papers, blog posts, and case studies from outside the data engineering mainstream.

### MCP Integration with Agents

Agents do NOT call MCP tools directly. Instead, the orchestrator in `main.py` pre-fetches relevant context from MCP servers at the start of the pipeline and injects it into the user message for each agent. This keeps the MVP simple — agents are pure LLM calls with structured input/output, not autonomous tool-using agents.

```python
# In main.py, before Stage 1:
enterprise_context = await gather_enterprise_context(mcp_clients)
# This calls get_current_architecture(), get_business_goals(), get_constraints(),
# get_pain_points(), get_schema_inventory(), get_infrastructure_catalog(),
# get_data_volume_stats()

# For Agent D (wildcard) and Stage 2 (mutation), also fetch:
patterns_context = await gather_patterns_context(mcp_clients)
# This calls get_cross_domain_analogies(), get_emerging_patterns()
```

The reason we use MCP servers rather than just reading files directly: **the system is designed to eventually connect to live enterprise data sources** (schema registries, data catalogs, infrastructure APIs). MCP provides the abstraction layer so that switching from "read local files" to "query live APIs" requires only changing the MCP server implementation, not any agent or orchestration code.

### MCP Server Implementation

Each MCP server is implemented as a Python module using the `mcp` SDK:

```
innovation_arch_generator/
├── mcp_servers/
│   ├── __init__.py
│   ├── enterprise_docs.py      # enterprise-docs-server
│   ├── metadata.py             # metadata-server
│   └── patterns_knowledge.py   # patterns-knowledge-server
```

Use `mcp`'s stdio transport for the MVP (servers run as subprocesses). The orchestrator connects to them using `mcp.ClientSession`. Configure server startup in `config.yaml`:

```yaml
mcp:
  enterprise_docs:
    data_dir: "./input/enterprise_docs/"
  metadata:
    data_dir: "./input/metadata/"
  patterns_knowledge:
    data_dir: "./knowledge_base/"
```

---

## Instructor Integration

Every LLM call in the system uses `instructor` to guarantee structured Pydantic output. Never parse raw text. Never use regex on LLM output.

### Setup

```python
# llm/client.py
import instructor
import litellm

# Patch litellm with instructor
client = instructor.from_litellm(litellm.acompletion)

async def call_llm(
    system_prompt: str,
    user_message: str,
    response_model: type[BaseModel],
    temperature: float = 0.7,
    max_retries: int = 3,
) -> BaseModel:
    """Core LLM call function used by all stages.
    Every call returns a validated Pydantic model."""
    return await client(
        model=config.model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_model=response_model,
        temperature=temperature,
        max_retries=max_retries,  # instructor auto-retries on validation failure
    )
```

### Why this matters

- **No output parsing bugs**. Instructor validates every LLM response against the Pydantic schema and retries automatically if the response doesn't conform.
- **Type safety throughout the pipeline**. Every stage receives and produces typed data. Stage 2 knows exactly what fields Stage 1 produced.
- **Automatic retry on malformed output**. If the LLM produces invalid JSON or misses a required field, instructor sends the validation error back to the LLM and asks it to fix the response. This is critical when running 12-16 parallel mutation calls — you don't want one malformed response to crash the pipeline.

---

## Pydantic Schemas (models/schemas.py)

These are the core data models that flow through the pipeline. Every LLM call returns one of these models via instructor.

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

# ──────────────────────────────────────────────
# Core Proposal Schema (used by all stages)
# ──────────────────────────────────────────────

class Component(BaseModel):
    """A single component in the proposed architecture."""
    name: str = Field(description="Component name (e.g., 'Event Router', 'Stream Processor')")
    role: str = Field(description="What this component does in the architecture")
    technology_suggestion: Optional[str] = Field(
        default=None,
        description="Suggested technology or implementation approach"
    )

class DataFlowStep(BaseModel):
    """A single step in the data flow."""
    step_number: int
    from_component: str
    to_component: str
    description: str = Field(description="What data moves and how")
    pattern: str = Field(description="e.g., 'push', 'pull', 'pub-sub', 'request-response', 'event-driven'")

class Risk(BaseModel):
    """A known risk with the proposal."""
    description: str
    severity: str = Field(description="'low', 'medium', or 'high'")
    mitigation: str = Field(description="How this risk could be addressed")

class Proposal(BaseModel):
    """Complete architectural proposal. This is the core data structure
    that flows through all pipeline stages."""
    architecture_name: str = Field(description="Distinctive name for this architecture")
    core_thesis: str = Field(description="1-2 sentence foundational principle")
    components: list[Component] = Field(description="All components in the architecture")
    data_flow: list[DataFlowStep] = Field(description="Step-by-step data flow through the system")
    key_innovations: list[str] = Field(
        description="What is genuinely new or unconventional about this design"
    )
    assumptions: list[str] = Field(
        description="What must be true for this architecture to work"
    )
    risks: list[Risk] = Field(description="Known risks, framed as solvable challenges")
    paradigm_source: str = Field(
        description="Which paradigm generated this: 'streaming', 'event-sourcing', "
                    "'declarative', 'cross-domain', or 'mutation-{operator_name}'"
    )

# ──────────────────────────────────────────────
# Mutation Output (extends Proposal)
# ──────────────────────────────────────────────

class MutatedProposal(Proposal):
    """A proposal that was produced by applying a mutation operator."""
    mutation_applied: str = Field(
        description="Which mutation operator was applied: "
                    "'invert', 'merge', 'eliminate', 'analogize', 'temporalize', 'abstract'"
    )
    mutation_description: str = Field(
        description="What specifically was changed and why"
    )
    parent_architecture_name: str = Field(
        description="Name of the original proposal this was mutated from"
    )

# ──────────────────────────────────────────────
# Self-Refinement Output
# ──────────────────────────────────────────────

class RefinedProposal(Proposal):
    """A proposal after self-refinement."""
    refinements_made: list[str] = Field(
        description="List of specific improvements made in this refinement round"
    )
    refinement_round: int = Field(description="Which round of refinement (1 or 2)")

# ──────────────────────────────────────────────
# Physics Critic Output
# ──────────────────────────────────────────────

class ConstraintAnnotation(BaseModel):
    """A single annotation from the physics critic."""
    constraint_type: str = Field(
        description="Category: 'cap_theorem', 'complexity_bounds', 'network_physics', "
                    "'consistency_model', 'resource_limits', 'data_integrity'"
    )
    description: str = Field(description="What the concern is")
    severity: str = Field(description="'info', 'warning', or 'critical'")
    affected_components: list[str] = Field(description="Which components are affected")
    suggested_mitigation: Optional[str] = Field(
        default=None,
        description="How the proposal could address this constraint"
    )

class AnnotatedProposal(BaseModel):
    """A proposal with physics critic annotations attached.
    The proposal itself is NOT modified — annotations are metadata."""
    proposal: RefinedProposal
    annotations: list[ConstraintAnnotation]
    hard_constraint_violations: int = Field(
        description="Count of 'critical' severity annotations"
    )
    overall_feasibility_note: str = Field(
        description="Brief overall assessment of physical feasibility"
    )

# ──────────────────────────────────────────────
# Portfolio Ranking Output
# ──────────────────────────────────────────────

class ScoredProposal(BaseModel):
    """Final scored proposal in the portfolio."""
    proposal: AnnotatedProposal
    innovation_score: float = Field(
        description="0-10 score for paradigm novelty and structural innovation"
    )
    feasibility_score: float = Field(
        description="0-10 score for technical feasibility given constraints"
    )
    business_alignment_score: float = Field(
        description="0-10 score for alignment with stated business goals"
    )
    migration_complexity_score: float = Field(
        description="0-10 score where 10 = trivial migration, 1 = complete rebuild"
    )
    composite_score: float = Field(
        description="Weighted composite of all scores"
    )
    tier: str = Field(
        description="'conservative', 'moderate_innovation', or 'radical'"
    )
    one_line_summary: str = Field(
        description="One sentence explaining what makes this proposal distinctive"
    )

class Portfolio(BaseModel):
    """The final output of the entire pipeline."""
    proposals: list[ScoredProposal] = Field(
        description="All proposals, ranked by composite score"
    )
    top_conservative: Optional[str] = Field(
        description="Architecture name of the top conservative option"
    )
    top_moderate: Optional[str] = Field(
        description="Architecture name of the top moderate innovation option"
    )
    top_radical: Optional[str] = Field(
        description="Architecture name of the top radical option"
    )
    executive_summary: str = Field(
        description="2-3 paragraph summary of the portfolio, highlighting the "
                    "innovation-risk frontier and key tradeoffs between the top options"
    )
```

---

## Project Structure (Updated)

```
innovation_arch_generator/
├── config.yaml                  # All tunable parameters
├── main.py                      # Entry point, orchestrates the full 5-stage pipeline
├── stages/
│   ├── __init__.py
│   ├── paradigm_agents.py       # Stage 1: Parallel paradigm agent generation
│   ├── mutation_engine.py       # Stage 2: Idea mutation operators
│   ├── self_refinement.py       # Stage 3: Self-critique and improvement loops
│   ├── physics_critic.py        # Stage 4: Hard-constraint annotation
│   └── portfolio_assembly.py    # Stage 5: Ranking, tiering, and output
├── prompts/
│   ├── __init__.py
│   ├── paradigm_agents.py       # System prompts for each of the 4 paradigm agents
│   ├── mutation_operators.py    # Prompts for each of the 6 mutation operators
│   ├── self_refinement.py       # Self-critique prompt
│   ├── physics_critic.py        # Physics critic prompt
│   └── portfolio_ranker.py      # Ranking and tiering prompt
├── models/
│   ├── __init__.py
│   └── schemas.py               # All Pydantic models defined above
├── llm/
│   ├── __init__.py
│   └── client.py                # instructor-patched litellm wrapper with retry
├── mcp_servers/
│   ├── __init__.py
│   ├── enterprise_docs.py       # MCP server: enterprise documentation
│   ├── metadata.py              # MCP server: technical metadata & schemas
│   └── patterns_knowledge.py    # MCP server: architectural pattern knowledge base
├── mcp_client/
│   ├── __init__.py
│   └── context_gatherer.py      # Connects to MCP servers, pre-fetches context
├── utils/
│   ├── __init__.py
│   └── report_renderer.py       # Jinja2 template rendering for markdown report
├── templates/
│   └── portfolio_report.md.j2   # Jinja2 template for the final markdown report
├── knowledge_base/              # Ships with the system — curated pattern files
│   ├── streaming_patterns.md
│   ├── event_sourcing_patterns.md
│   ├── declarative_patterns.md
│   ├── biological_analogies.md
│   ├── economic_analogies.md
│   ├── physical_analogies.md
│   ├── social_analogies.md
│   ├── emerging_patterns.md
│   └── anti_patterns.md
├── input/                       # User provides these
│   ├── enterprise_docs/         # Markdown/text files describing the enterprise
│   └── metadata/                # JSON/YAML/SQL files with schemas and metadata
└── outputs/                     # Generated output directory
    ├── portfolio.json            # Structured JSON output
    └── portfolio_report.md      # Human-readable markdown report
```

---

## Config File (config.yaml)

```yaml
# LLM Configuration
llm:
  model: "anthropic/claude-sonnet-4-20250514"  # Any litellm-compatible model string
  # Per-stage temperature overrides
  temperature:
    paradigm_agents: 0.9      # High divergence for idea generation
    mutation_engine: 0.85     # High but slightly less than generation
    self_refinement: 0.5      # Lower — refinement, not generation
    physics_critic: 0.3       # Low — analytical, precise
    portfolio_ranker: 0.3     # Low — evaluative, consistent
  max_retries: 3              # instructor retry count on validation failure

# MCP Server Configuration
mcp:
  enterprise_docs:
    data_dir: "./input/enterprise_docs/"
  metadata:
    data_dir: "./input/metadata/"
  patterns_knowledge:
    data_dir: "./knowledge_base/"

# Pipeline Configuration
pipeline:
  # Stage 1
  paradigm_agents:
    enabled_agents: ["streaming", "event_sourcing", "declarative", "wildcard"]
  # Stage 2
  mutation:
    operators_per_proposal: 3    # How many mutation operators to apply per proposal (2-3)
    available_operators: ["invert", "merge", "eliminate", "analogize", "temporalize", "abstract"]
  # Stage 3
  self_refinement:
    rounds: 2
  # Stage 5
  portfolio:
    score_weights:
      innovation: 0.35          # Weight for innovation score in composite
      feasibility: 0.25
      business_alignment: 0.25
      migration_complexity: 0.15

# Output Configuration
output:
  dir: "./outputs/"
  render_markdown_report: true
```

---

## Stage 1: Paradigm Agent Generation

### What it does
Runs 4 LLM agents in parallel. Each agent receives enterprise context (pre-fetched from MCP servers) and has a radically different system prompt. Each agent returns a `Proposal` Pydantic model via instructor.

### The 4 Agents

**Agent A — "Stream-First Radical"**

System prompt:
```
You are a senior data architect who is deeply convinced that batch processing is an obsolete paradigm. You believe ALL data problems are better solved with streaming-first, real-time architectures. Your job is to propose the most ambitious streaming-native architecture possible for the given requirements.

Rules:
- Challenge every assumption in the current architecture that relies on batch processing, scheduled jobs, or periodic syncs.
- Propose a streaming-first design even where it seems unconventional or overkill.
- If a requirement seems to demand batch, argue why a streaming approach is still superior and design around it.
- Do NOT hedge. Do NOT say "but batch might be safer here." Your job is to be the strongest advocate for this paradigm.
- Explicitly name what would need to be true (tooling, team skills, infrastructure) for your proposal to succeed.
- Be architecturally specific: name concrete components, data flow patterns, technologies, and integration points. Do not stay at the level of vague principles.
```

**Agent B — "Event-Sourced / CQRS Purist"**

System prompt:
```
You are a senior data architect who believes that the fundamental flaw in most data pipelines is that they destroy information by transforming and aggregating data prematurely. You believe in event sourcing, CQRS (Command Query Responsibility Segregation), and immutable event logs as the foundation of all data systems. Your job is to propose the most ambitious event-sourced architecture possible for the given requirements.

Rules:
- Start from the principle that every state change should be captured as an immutable event, and all downstream views should be derived projections.
- Challenge any part of the current architecture that mutates state in place, uses UPDATE/DELETE semantics, or aggregates data before storage.
- Propose event-sourced alternatives even where they seem like overkill.
- Do NOT hedge. Your job is to make the strongest possible case for this paradigm.
- Be architecturally specific: name concrete components, event schemas, projection strategies, and integration points.
```

**Agent C — "Declarative / DSL-First Abstractionist"**

System prompt:
```
You are a senior data architect who believes that the fundamental problem with data pipelines is that they are too imperative — too much code, too many manual orchestrations, too many point-to-point integrations. You believe the future is declarative: define WHAT data should look like and WHERE it should be, and let the system figure out HOW. You think in terms of domain-specific languages, constraint solvers, policy engines, and self-assembling pipelines. Your job is to propose the most ambitious declarative-first architecture possible for the given requirements.

Rules:
- Challenge every part of the current architecture that requires manual pipeline code, explicit orchestration, or imperative transformation logic.
- Propose declarative alternatives: DSLs for pipeline definition, policy-based data routing, constraint-based schema evolution, intent-based data contracts.
- Consider whether a new abstraction layer or DSL could replace large swaths of existing pipeline code.
- Think about self-healing, self-optimizing, and self-assembling pipeline behaviors that emerge from declarative specifications.
- Do NOT hedge. Your job is to push this paradigm to its logical extreme.
- Be architecturally specific.
```

**Agent D — "Cross-Domain Wildcard"**

System prompt:
```
You are a systems thinker who draws architectural inspiration from domains OUTSIDE traditional software engineering. You look at biological systems, economic markets, physical systems, and social systems for patterns that can be translated into concrete data pipeline architectures.

For the given requirements, propose an architecture inspired by ONE of these cross-domain paradigms:
- Biological: immune systems (anomaly detection + adaptive response), neural networks (weighted signal routing), evolutionary systems (competing pipeline variants with selection), cellular signaling (event cascades with amplification/dampening), mycorrhizal networks (decentralized resource sharing)
- Economic: market mechanisms (data consumers bid for processing priority), supply chain optimization (just-in-time data delivery), auction theory (resource allocation via bidding)
- Physical: thermodynamic systems (entropy-based data quality management), fluid dynamics (pressure-based flow control and backpressure), crystallization (data gradually assuming structure from amorphous input)
- Social: stigmergy (agents leaving signals that guide other agents), swarm intelligence (decentralized coordination without central orchestrator), consensus protocols (Byzantine fault tolerance applied to data quality)

Rules:
- Pick ONE cross-domain inspiration that genuinely fits the requirements. Do not force a metaphor.
- Your proposal must be a REAL architectural design with concrete technical components, not just an analogy. Translate the cross-domain insight into specific software components, data flows, APIs, and system behaviors.
- Name the biological/economic/physical/social principle you are drawing from and explain the structural mapping to data pipeline concepts.
- This is the most important agent in the system. Your job is to propose something that no conventional architect would think of. Be bold.
- Be architecturally specific.
```

### Implementation

```python
# stages/paradigm_agents.py (pseudocode showing instructor integration)

async def run_paradigm_agents(enterprise_context: str, patterns_context: str) -> list[Proposal]:
    """Run all 4 paradigm agents in parallel, return typed Proposals."""

    agents = [
        ("streaming", STREAMING_SYSTEM_PROMPT, enterprise_context),
        ("event_sourcing", EVENT_SOURCING_SYSTEM_PROMPT, enterprise_context),
        ("declarative", DECLARATIVE_SYSTEM_PROMPT, enterprise_context),
        ("wildcard", WILDCARD_SYSTEM_PROMPT, enterprise_context + "\n\n" + patterns_context),
    ]

    tasks = [
        call_llm(
            system_prompt=system_prompt,
            user_message=(
                "Here is the enterprise context describing the current data pipeline "
                "architecture, technologies, business goals, and constraints.\n\n"
                f"{context}\n\n"
                "Based on this, generate your architectural proposal."
            ),
            response_model=Proposal,
            temperature=config.temperature.paradigm_agents,
        )
        for paradigm_name, system_prompt, context in agents
    ]

    proposals = await asyncio.gather(*tasks)

    # Tag each proposal with its paradigm source
    for (paradigm_name, _, _), proposal in zip(agents, proposals):
        proposal.paradigm_source = paradigm_name

    return list(proposals)
```

---

## Stage 2: Idea Mutation Engine

### What it does
Takes each of the 4 proposals from Stage 1 and applies 2-3 randomly selected mutation operators, generating 8-12 mutated variants. Combined with the 4 originals, this produces a candidate pool of 12-16 proposals.

### The 6 Mutation Operators

Each operator is a system prompt. The user message contains the serialized original proposal.

**INVERT**
```
You are an architectural mutation operator. Your job is to take an existing architecture proposal and INVERT one of its core assumptions or data flows.

Examples of inversion:
- Push-based → Pull-based (or vice versa)
- Producer-driven → Consumer-driven
- Centralized orchestration → Decentralized choreography
- Schema-on-write → Schema-on-read
- Pre-computed aggregations → On-demand computation

Identify the single most impactful assumption or flow direction to invert, and produce a complete revised architecture with that inversion applied. Explain what you inverted and why it could be beneficial.
```

**MERGE**
```
You are an architectural mutation operator. Your job is to take an existing architecture proposal and MERGE two of its components or stages into a single unified component that serves both purposes.

Find two components with an unnecessary boundary — where merging could eliminate overhead, reduce complexity, or enable new capabilities. Produce a complete revised architecture with the merge applied.
```

**ELIMINATE**
```
You are an architectural mutation operator. Your job is to take an existing architecture proposal and ELIMINATE one component or stage entirely, then redesign the system to work without it.

Question whether a component is truly necessary or exists only by convention. Ask: "What if this simply didn't exist?" The resulting architecture should be simpler but not broken — find a creative way to achieve the same goals.
```

**ANALOGIZE**
```
You are an architectural mutation operator. Your job is to inject a pattern from a COMPLETELY DIFFERENT DOMAIN into one of the proposal's components.

Cross-domain analogies to consider:
- Biological immune system → self-healing pipeline with anomaly memory
- Economic market → priority-based resource allocation between stages
- Neural network → weighted routing with learned preferences
- Supply chain → just-in-time data processing with demand signaling
- Swarm intelligence → decentralized orchestration with emergent coordination

Apply the analogy as a concrete technical design (not just a metaphor).
```

**TEMPORALIZE**
```
You are an architectural mutation operator. Your job is to CHANGE THE TEMPORAL MODEL of one or more components.

Temporal transformations:
- Batch → Streaming (or vice versa)
- Synchronous → Asynchronous
- Periodic/scheduled → Event-driven/reactive
- Immediate → Deferred/lazy
- Fixed-window → Sliding-window or sessionized
- Sequential → Speculative/parallel with reconciliation

Identify the most impactful temporal transformation and apply it.
```

**ABSTRACT**
```
You are an architectural mutation operator. Your job is to raise the ABSTRACTION LEVEL of one component — replacing a concrete implementation pattern with a higher-order, more general one.

Examples:
- Specific ETL jobs → Declarative pipeline DSL
- Hardcoded routing → Policy-based routing engine
- Manual schema management → Self-evolving schema registry with contracts
- Specific connectors → Universal adapter layer with plugin architecture
- Imperative workflows → Constraint solver that generates execution plans

Identify the component that benefits most from abstraction and apply it.
```

### Implementation

```python
# stages/mutation_engine.py (pseudocode)

import random

OPERATOR_PROMPTS = {
    "invert": INVERT_PROMPT,
    "merge": MERGE_PROMPT,
    "eliminate": ELIMINATE_PROMPT,
    "analogize": ANALOGIZE_PROMPT,
    "temporalize": TEMPORALIZE_PROMPT,
    "abstract": ABSTRACT_PROMPT,
}

async def run_mutations(proposals: list[Proposal]) -> list[MutatedProposal]:
    """Apply random mutation operators to each proposal."""
    tasks = []

    for proposal in proposals:
        selected_ops = random.sample(
            config.mutation.available_operators,
            k=config.mutation.operators_per_proposal,
        )
        for op_name in selected_ops:
            tasks.append(
                call_llm(
                    system_prompt=OPERATOR_PROMPTS[op_name],
                    user_message=(
                        "Here is the architectural proposal to mutate:\n\n"
                        f"{proposal.model_dump_json(indent=2)}"
                    ),
                    response_model=MutatedProposal,
                    temperature=config.temperature.mutation_engine,
                )
            )

    return await asyncio.gather(*tasks)
```

---

## Stage 3: Self-Refinement

### What it does
Each of the 12-16 proposals gets 2 rounds of self-refinement. The LLM critiques the proposal and produces a stronger version — without making it more conservative.

### Self-Refinement Prompt

```
You are reviewing an architectural proposal for a data pipeline system. Your job is to make this proposal STRONGER and MORE COHERENT without making it more conservative.

Do NOT:
- Soften radical ideas into conventional ones
- Add hedging language
- Suggest falling back to standard approaches
- Reduce the ambition or novelty of the proposal

DO:
- Identify internal inconsistencies and fix them
- Identify missing components the design needs to actually work
- Strengthen the argument for WHY this approach is superior
- Add specificity where the proposal is vague (name specific technologies, protocols, patterns)
- Address the most obvious objection and build in a response
- Improve the data flow to eliminate unnecessary complexity
```

### Implementation

```python
# stages/self_refinement.py (pseudocode)

async def run_self_refinement(
    proposals: list[Proposal | MutatedProposal],
    rounds: int = 2,
) -> list[RefinedProposal]:
    """Run N rounds of self-refinement on all proposals."""
    current = proposals

    for round_num in range(1, rounds + 1):
        tasks = [
            call_llm(
                system_prompt=SELF_REFINEMENT_PROMPT,
                user_message=(
                    f"Refinement round {round_num}. "
                    f"Here is the proposal to refine:\n\n"
                    f"{p.model_dump_json(indent=2)}"
                ),
                response_model=RefinedProposal,
                temperature=config.temperature.self_refinement,
            )
            for p in current
        ]
        current = await asyncio.gather(*tasks)

    return current
```

---

## Stage 4: Physics Critic

### What it does
Annotates each proposal with hard-constraint violations. **Does NOT reject or modify proposals.** Only attaches metadata.

### Physics Critic Prompt

```
You are a physics-of-computing critic. Your job is to annotate an architectural proposal with hard constraint violations — things that are physically, mathematically, or logically impossible or extremely problematic.

You check for:
- CAP theorem violations (claiming strong consistency + availability + partition tolerance simultaneously)
- Computational complexity issues (algorithms that won't scale to stated data volumes)
- Network physics violations (assuming zero-latency, infinite bandwidth, or perfect reliability)
- Consistency model contradictions (claiming exactly-once semantics where not achievable)
- Resource limit issues (memory, storage, compute requirements that exceed feasible bounds)
- Data integrity gaps (places where data could be lost or corrupted with no recovery path)

You do NOT check for:
- Organizational readiness (that's a domain concern, not a physics concern)
- Cost (unless the cost implies physically impossible resource requirements)
- Tooling maturity (a valid tool might not exist yet, but that's not a physics issue)
- Convention (doing something unconventionally is not a constraint violation)

CRITICAL: You are an ANNOTATOR, not a GATEKEEPER. Your job is to attach annotations to the proposal, not to reject it. Even proposals with critical violations should pass through with their annotations — the portfolio ranker will use your annotations to adjust scores.

For each annotation, suggest a mitigation if one exists.
```

### Implementation

```python
# stages/physics_critic.py (pseudocode)

async def run_physics_critic(
    proposals: list[RefinedProposal],
) -> list[AnnotatedProposal]:
    """Annotate all proposals with physics constraints. Never reject."""
    tasks = [
        call_llm(
            system_prompt=PHYSICS_CRITIC_PROMPT,
            user_message=(
                "Here is the architectural proposal to annotate:\n\n"
                f"{p.model_dump_json(indent=2)}"
            ),
            response_model=AnnotatedProposal,
            temperature=config.temperature.physics_critic,
        )
        for p in proposals
    ]
    return await asyncio.gather(*tasks)
```

---

## Stage 5: Portfolio Assembly & Ranking

### What it does
Scores all annotated proposals across 4 dimensions, assigns them to tiers (conservative / moderate / radical), and produces the final ranked portfolio with an executive summary.

### Portfolio Ranker Prompt

```
You are an architectural portfolio evaluator. You will receive a list of annotated architectural proposals. Your job is to score each one and produce a ranked portfolio.

Score each proposal on 4 dimensions (0-10 scale):

1. INNOVATION SCORE: How structurally novel is this architecture? Does it introduce new abstractions, paradigm shifts, or unconventional patterns? Score 1-3 for incremental improvements to conventional patterns. Score 4-6 for novel combinations of known patterns. Score 7-10 for genuine paradigm shifts that redefine how the problem is approached.

2. FEASIBILITY SCORE: Given the physics critic annotations and the stated constraints, how technically feasible is this architecture? Weight critical annotations heavily. Ignore soft concerns like "tooling maturity" or "team readiness" — those are solvable.

3. BUSINESS ALIGNMENT SCORE: How well does this architecture serve the stated business goals, KPIs, and strategic priorities? An innovative architecture that doesn't serve the business is still a bad architecture.

4. MIGRATION COMPLEXITY SCORE: How difficult would it be to migrate from the current state to this architecture? 10 = trivial migration, 1 = complete rebuild from scratch. This is informational, not a penalty — radical innovations naturally score low here.

TIERING RULES:
- "conservative": Innovation score ≤ 4
- "moderate_innovation": Innovation score 5-7
- "radical": Innovation score ≥ 8

Produce a portfolio with all proposals ranked by composite score.
Write an executive summary that highlights the innovation-risk frontier — what you gain and what you risk at each tier.
```

### Implementation

```python
# stages/portfolio_assembly.py (pseudocode)

async def run_portfolio_assembly(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
) -> Portfolio:
    """Score, tier, and rank all proposals into a final portfolio."""

    # Serialize all proposals into one big context for the ranker
    proposals_json = json.dumps(
        [ap.model_dump() for ap in annotated_proposals],
        indent=2,
    )

    portfolio = await call_llm(
        system_prompt=PORTFOLIO_RANKER_PROMPT,
        user_message=(
            "Here are the enterprise context and business goals for reference:\n\n"
            f"{enterprise_context}\n\n"
            "Here are all the annotated architectural proposals to evaluate:\n\n"
            f"{proposals_json}"
        ),
        response_model=Portfolio,
        temperature=config.temperature.portfolio_ranker,
    )

    # Apply configured score weights to compute composite scores
    weights = config.portfolio.score_weights
    for sp in portfolio.proposals:
        sp.composite_score = (
            sp.innovation_score * weights["innovation"]
            + sp.feasibility_score * weights["feasibility"]
            + sp.business_alignment_score * weights["business_alignment"]
            + sp.migration_complexity_score * weights["migration_complexity"]
        )

    # Sort by composite score descending
    portfolio.proposals.sort(key=lambda x: x.composite_score, reverse=True)

    # Identify top per tier
    for tier_name in ["conservative", "moderate_innovation", "radical"]:
        tier_proposals = [p for p in portfolio.proposals if p.tier == tier_name]
        top = tier_proposals[0].proposal.proposal.architecture_name if tier_proposals else None
        setattr(portfolio, f"top_{tier_name.split('_')[0]}", top)

    return portfolio
```

---

## Main Orchestrator (main.py)

```python
# main.py (pseudocode showing the full pipeline flow)

import asyncio
import json
from mcp_client.context_gatherer import gather_enterprise_context, gather_patterns_context
from stages.paradigm_agents import run_paradigm_agents
from stages.mutation_engine import run_mutations
from stages.self_refinement import run_self_refinement
from stages.physics_critic import run_physics_critic
from stages.portfolio_assembly import run_portfolio_assembly
from utils.report_renderer import render_portfolio_report

async def run_pipeline():
    # ── Pre-fetch context from MCP servers ──
    print("Connecting to MCP servers and gathering enterprise context...")
    enterprise_context = await gather_enterprise_context()
    patterns_context = await gather_patterns_context()

    # ── Stage 1: Paradigm Agent Generation ──
    print("Stage 1: Running 4 paradigm agents in parallel...")
    original_proposals = await run_paradigm_agents(enterprise_context, patterns_context)
    print(f"  → Generated {len(original_proposals)} original proposals")

    # ── Stage 2: Idea Mutation ──
    print("Stage 2: Applying mutation operators...")
    mutated_proposals = await run_mutations(original_proposals)
    all_proposals = original_proposals + mutated_proposals
    print(f"  → Generated {len(mutated_proposals)} mutations, {len(all_proposals)} total candidates")

    # ── Stage 3: Self-Refinement ──
    print(f"Stage 3: Running {config.self_refinement.rounds} rounds of self-refinement...")
    refined_proposals = await run_self_refinement(all_proposals)
    print(f"  → Refined {len(refined_proposals)} proposals")

    # ── Stage 4: Physics Critic ──
    print("Stage 4: Running physics critic (annotate only, no rejection)...")
    annotated_proposals = await run_physics_critic(refined_proposals)
    critical_count = sum(1 for ap in annotated_proposals if ap.hard_constraint_violations > 0)
    print(f"  → Annotated {len(annotated_proposals)} proposals, {critical_count} have critical flags")

    # ── Stage 5: Portfolio Assembly ──
    print("Stage 5: Scoring and ranking portfolio...")
    portfolio = await run_portfolio_assembly(annotated_proposals, enterprise_context)

    # ── Output ──
    output_dir = config.output.dir
    with open(f"{output_dir}/portfolio.json", "w") as f:
        json.dump(portfolio.model_dump(), f, indent=2)

    if config.output.render_markdown_report:
        report = render_portfolio_report(portfolio)
        with open(f"{output_dir}/portfolio_report.md", "w") as f:
            f.write(report)

    print(f"\nDone. Portfolio written to {output_dir}/")
    print(f"  Top conservative: {portfolio.top_conservative}")
    print(f"  Top moderate:     {portfolio.top_moderate}")
    print(f"  Top radical:      {portfolio.top_radical}")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
```

---

## Markdown Report Template (templates/portfolio_report.md.j2)

Create a Jinja2 template that renders the Portfolio into a readable markdown report. The report should include:

1. **Executive Summary** — the portfolio's executive_summary field
2. **Innovation-Risk Frontier** — a text-based table showing all proposals plotted on innovation_score vs feasibility_score
3. **Top Picks by Tier** — detailed writeup of the top conservative, moderate, and radical options
4. **Full Proposal Details** — for each proposal in ranked order:
   - Architecture name and one-line summary
   - All 4 dimension scores
   - Core thesis
   - Components and data flow
   - Key innovations
   - Physics critic annotations (with severity color coding)
   - Risks and mitigations
5. **Methodology Note** — brief explanation that proposals were generated by divergent paradigm agents, mutated, self-refined, and annotated (for transparency)

---

## Error Handling and Resilience

- **instructor retries**: Set `max_retries=3` on all `call_llm` calls. Instructor will automatically send validation errors back to the LLM for self-correction.
- **asyncio error isolation**: Use `asyncio.gather(return_exceptions=True)` so one failed agent doesn't crash the entire stage. Log failures and continue with successful results.
- **Minimum candidate threshold**: If fewer than 6 proposals survive to Stage 4 (due to LLM failures), log a warning but continue. The portfolio can be useful even with fewer candidates.
- **Token budget awareness**: Enterprise context can be large. If the total context exceeds the model's context window, implement a priority-based truncation: business goals and constraints first, then current architecture, then schemas (summarized), then metadata (on-demand via MCP search_metadata).

---

## Running the System

```bash
# 1. Install dependencies
pip install litellm instructor mcp pydantic pyyaml jinja2 aiofiles

# 2. Set your LLM API key
export ANTHROPIC_API_KEY="sk-..."   # or OPENAI_API_KEY, etc.

# 3. Place your enterprise docs in input/enterprise_docs/
# 4. Place your metadata files in input/metadata/
# 5. Optionally extend knowledge_base/ with additional pattern files

# 6. Run the pipeline
python main.py

# 7. Review outputs
cat outputs/portfolio_report.md
# or open outputs/portfolio.json for structured data
```

---

## Summary of Design Decisions

| Decision | Rationale |
|---|---|
| `instructor` for all LLM output | Type safety, automatic retry on malformed output, no parsing bugs |
| MCP servers for enterprise data | Abstraction layer that scales from local files to live APIs without changing agent code |
| No LangGraph / LangChain / CrewAI | Pipeline is a simple 5-stage sequential flow; frameworks add indirection without value |
| `litellm` for LLM calls | Model-agnostic — swap between Claude, GPT, Gemini, local models via config |
| Parallel within stages, sequential between stages | Each stage depends on the previous stage's output, but within a stage all calls are independent |
| Physics critic annotates, never rejects | Prevents premature pruning of innovative ideas by feasibility gatekeepers |
| Portfolio output (not single recommendation) | Innovation involves risk; humans should choose their position on the frontier |
| Cross-domain wildcard agent | Most reliable mechanism for genuine paradigm shifts; gets extra context from patterns knowledge base |
| Self-refinement before critics | Radical ideas need development time before exposure to criticism |
| Score weights in config | Different organizations have different risk tolerances; make it tunable |
