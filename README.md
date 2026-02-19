# Innovation-Optimized Multi-Agent Architecture Generator

A Python-based multi-agent system that generates **innovative** data pipeline architecture proposals. Unlike traditional architecture design tools, this system is explicitly optimized for **architectural innovation and paradigm shifts**, not just optimization of existing patterns.

## What Does It Do?

Given enterprise documentation about your current data infrastructure, the system:

1. **Understands intent** — An intent agent diagnoses root causes, identifies paradigm shift opportunities, and writes an executive briefing for downstream agents
2. **Enhances prompts** — Paradigm agent prompts are dynamically enriched with intent context and domain-specific patterns
3. **Generates 4 radically different proposals** using specialized AI agents with different architectural philosophies
4. **Mutates proposals** to explore the solution space (12-16 candidates)
5. **Selects for diversity** via a MAP-Elites archive, keeping the most diverse and highest-quality subset
6. **Refines** proposals through 2 rounds of self-critique (without making them conservative)
7. **Annotates** with physics-of-computing constraints (CAP theorem, complexity bounds, etc.)
8. **Debates** each proposal in a structured 3-round asymmetric debate (innovation-favoring)
9. **Reviews** proposals through 4 domain critics (security, cost, org readiness, data quality)
10. **Ranks and tiers** proposals on an innovation-risk frontier

**Output**: A portfolio of architectures ranging from conservative to radically novel, scored on innovation, feasibility, business alignment, and migration complexity.

---

## Quick Start

### Prerequisites
- Python 3.11+
- An LLM provider — **one** of the following:
  - **Ollama** (local, free) — any model installed locally
  - **Anthropic Claude** — API key required
  - **OpenAI** — API key required
  - Any other [litellm-supported model](https://docs.litellm.ai/docs/providers)

### Installation

```bash
cd innovation_arch_generator
pip install -r requirements.txt
```

### Provide Your Enterprise Documentation

**⚠️ CRITICAL FIRST STEP**: The system requires YOUR organization's documentation to generate relevant proposals.

1. Navigate to `input/enterprise_docs/` and `input/metadata/`
2. Read the `README.md` files in each directory for detailed templates
3. **Replace the example files** with your actual:
   - Current architecture description (`architecture.md`)
   - Business goals and priorities (`business_goals.md`)
   - Constraints: budget, compliance, SLAs (`constraints.md`)
   - Team skills and structure (`team.md`)
   - Pain points and technical debt (`pain_points.md`)
   - Schema inventory (`schema_inventory.json`)
   - Infrastructure catalog (`infrastructure_catalog.json`)
   - Pipeline definitions (`pipeline_definitions.yaml`)
   - Data volume statistics (`volume_stats.json`)

**The current files are EXAMPLES describing a fictional e-commerce company.** They are for reference only.

See `input/README.md` for complete instructions and templates.

### Configuration

#### Option A: Local models with Ollama (recommended for getting started)

Install [Ollama](https://ollama.com/), pull a model, then edit `config.yaml`:

```yaml
llm:
  model: "ollama_chat/qwen3:1.7b"     # Or any model: deepseek-r1:8b, llama3, etc.
  api_base: "http://localhost:11434"   # Ollama default
```

No API key needed.

#### Option B: Cloud API (Anthropic, OpenAI, etc.)

Set your API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Or for OpenAI:
export OPENAI_API_KEY="sk-..."
```

Edit `config.yaml`:
```yaml
llm:
  model: "anthropic/claude-sonnet-4-20250514"  # Or "openai/gpt-4", etc.
  api_base: null                               # Remove or set to null for cloud APIs
```

### Run

```bash
python main.py
```

**Expected runtime**: 15-45 minutes depending on model speed, number of proposals, and whether new stages are enabled.

**Outputs**:
- `outputs/portfolio.json` — Structured JSON with all proposals and scores
- `outputs/portfolio_report.md` — Human-readable markdown report

---

## Architecture Overview

### System Design

```
INPUT (enterprise context via MCP servers)
  ↓
Stage 0a: Intent Agent (diagnose intent, identify paradigm shifts)          [NEW]
  ↓
Stage 0b: Prompt Enhancement (enrich agent prompts with intent + patterns)  [NEW]
  ↓
Stage 1: Paradigm Agent Generation (4 agents, parallel)
  ↓
Stage 2: Idea Mutation (transform each proposal)
  ↓
Stage 2.5: Diversity Archive / MAP-Elites (select diverse subset)           [NEW]
  ↓
Stage 3: Self-Refinement (2 rounds of self-critique)
  ↓
Stage 4: Physics Critic (annotate violations, no rejection)
  ↓
Stage 4.5: Structured Debate (3-round asymmetric, innovation-favoring)      [NEW]
  ↓
Stage 4.7: Domain Critics (security, cost, org readiness, data quality)     [NEW]
  ↓
Stage 5: Portfolio Assembly & Ranking
  ↓
OUTPUT (ranked portfolio as JSON + markdown report)
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **instructor** for all LLM output | Type safety, automatic retry on malformed output, no parsing bugs |
| **MCP servers** for enterprise data | Abstraction layer that scales from local files to live APIs without changing agent code |
| **No agent frameworks** (LangChain, etc.) | Pipeline is a 10-stage sequential flow; frameworks add complexity without value |
| **litellm** for LLM calls | Model-agnostic — swap between Claude, GPT, Gemini, Ollama via config |
| **Ollama support** | Run entirely locally with no API keys or cloud costs |
| **Intent agent before generation** | Ensures paradigm agents solve the RIGHT problem, not just any problem |
| **MAP-Elites diversity selection** | Prevents convergence to similar solutions; maximizes behavioral diversity |
| **Asymmetric debate** | Innovation-favoring debate structure stress-tests proposals without killing radical ideas |
| **Domain critics annotate, never reject** | Prevents premature pruning of innovative ideas by feasibility gatekeepers |
| **Portfolio output** (not single recommendation) | Innovation involves risk; humans should choose their position on the frontier |

---

## Project Structure

```
innovation_arch_generator/
├── config.yaml                  # All tunable parameters (model, stages, weights)
├── main.py                      # Entry point, orchestrates the 10-stage pipeline
├── requirements.txt             # Python dependencies
│
├── stages/                      # All pipeline stages
│   ├── intent_agent.py          # Stage 0a: Intent analysis & paradigm shift identification
│   ├── prompt_enhancement.py    # Stage 0b: Dynamic prompt enrichment (no LLM call)
│   ├── paradigm_agents.py       # Stage 1: 4 parallel agents with different philosophies
│   ├── mutation_engine.py       # Stage 2: Apply mutation operators to proposals
│   ├── diversity_archive.py     # Stage 2.5: MAP-Elites diversity selection
│   ├── self_refinement.py       # Stage 3: Self-critique and improvement loops
│   ├── physics_critic.py        # Stage 4: Hard-constraint annotation
│   ├── structured_debate.py     # Stage 4.5: 3-round asymmetric debate per proposal
│   ├── domain_critics.py        # Stage 4.7: Security, cost, org, data quality critics
│   └── portfolio_assembly.py    # Stage 5: Ranking, tiering, and output
│
├── prompts/                     # All system prompts (separated from code)
│   ├── intent_agent.py          # Intent agent system prompt
│   ├── paradigm_agents.py       # Prompts for 4 paradigm agents (template-based)
│   ├── mutation_operators.py    # Prompts for 6 mutation operators
│   ├── diversity_scorer.py      # MAP-Elites behavioral characterization prompt
│   ├── self_refinement.py       # Self-critique prompt
│   ├── physics_critic.py        # Physics critic prompt
│   ├── debate_agents.py         # Advocate, devil's advocate, and judge prompts
│   ├── domain_critics.py        # 4 domain critic prompts (security, cost, org, data)
│   └── portfolio_ranker.py      # Ranking and tiering prompt
│
├── models/
│   └── schemas.py               # All Pydantic models (IntentBrief, Proposal, Portfolio, etc.)
│
├── llm/
│   └── client.py                # instructor-patched litellm wrapper (supports Ollama + cloud)
│
├── mcp_servers/                 # Model Context Protocol servers
│   ├── enterprise_docs.py       # Serves enterprise documentation
│   ├── metadata.py              # Serves technical metadata & schemas
│   └── patterns_knowledge.py    # Serves architectural pattern knowledge base
│
├── mcp_client/
│   └── context_gatherer.py      # Connects to MCP servers, pre-fetches context
│
├── utils/
│   └── report_renderer.py       # Jinja2 template rendering for markdown report
│
├── templates/
│   └── portfolio_report.md.j2   # Jinja2 template for the final report
│
├── knowledge_base/              # Curated architectural pattern reference files
│   ├── streaming_patterns.md
│   ├── event_sourcing_patterns.md
│   ├── declarative_patterns.md
│   ├── biological_analogies.md
│   ├── economic_analogies.md
│   ├── physical_analogies.md
│   ├── social_analogies.md
│   ├── emerging_patterns.md
│   └── anti_patterns.md
│
├── input/                       # User-provided enterprise context
│   ├── enterprise_docs/         # Markdown describing your organization
│   │   ├── architecture.md
│   │   ├── business_goals.md
│   │   ├── constraints.md
│   │   ├── team.md
│   │   └── pain_points.md
│   └── metadata/                # JSON/YAML with schemas and metadata
│       ├── schema_inventory.json
│       ├── infrastructure_catalog.json
│       ├── pipeline_definitions.yaml
│       └── volume_stats.json
│
└── outputs/                     # Generated output (created at runtime)
    ├── portfolio.json
    └── portfolio_report.md
```

---

## How It Works

### Stage 0a: Intent Agent *(new)*

**What**: Before any proposal generation, an intent agent deeply analyzes the enterprise context to understand the *real* problem.

**Produces an `IntentBrief`** containing:
- **Core objective** — What the user truly needs (not what they literally asked for)
- **Pain diagnosis** — Root causes, not symptoms
- **Implicit constraints** — Constraints that exist but aren't documented
- **Innovation opportunity map** — Where innovation has the highest leverage
- **Paradigm shift candidates** — Specific shifts ranked by transformative potential
- **Anti-goals** — What proposals should NOT do
- **Success criteria** — How the user would judge success
- **Key context for agents** — A 2-3 paragraph executive briefing injected into downstream prompts

**Why?**: Without intent analysis, paradigm agents solve a generic problem. With it, they solve *this specific* problem.

### Stage 0b: Prompt Enhancement *(new)*

**What**: Dynamically enriches each paradigm agent's system prompt with intent context and paradigm-specific patterns from the knowledge base.

**How**: Pure Python string composition — no LLM call needed. Combines:
1. The original paradigm agent prompt template
2. The intent agent's executive briefing
3. Paradigm-specific patterns fetched via MCP from the knowledge base

**Output**: A `dict[str, str]` mapping each agent name to its enriched prompt.

**Why?**: Static prompts treat every enterprise the same. Enhanced prompts give each agent mission-specific intelligence.

### Stage 1: Paradigm Agent Generation

**What**: 4 LLM agents run in parallel, each with a radically different architectural philosophy.

**The 4 Agents**:

1. **Stream-First Radical** — Believes batch processing is obsolete; proposes streaming-first architectures
2. **Event-Sourced Purist** — Believes in immutable event logs and CQRS as the foundation
3. **Declarative Abstractionist** — Believes pipelines should be declarative DSLs, not imperative code
4. **Cross-Domain Wildcard** — Draws inspiration from biology, economics, physics, and social systems

If prompt enhancement is enabled, each agent receives an enriched prompt with intent context and domain-specific patterns.

**Output**: 4 `Proposal` objects, each with components, data flow, innovations, assumptions, and risks.

**Why 4 agents?**: Diversity of thought. Traditional architecture reviews have groupthink; this system forces divergent exploration.

### Stage 2: Idea Mutation

**What**: Each proposal gets mutated by 2-3 randomly selected operators to expand the solution space.

**The 6 Mutation Operators**:

- **INVERT** — Flip a core assumption (push→pull, centralized→decentralized, etc.)
- **MERGE** — Combine two components into one unified component
- **ELIMINATE** — Remove a component entirely and redesign without it
- **ANALOGIZE** — Inject a pattern from a different domain (biological, economic, etc.)
- **TEMPORALIZE** — Change the temporal model (batch→streaming, sync→async, etc.)
- **ABSTRACT** — Raise abstraction level (specific→declarative, concrete→policy-driven)

**Output**: 8-12 `MutatedProposal` objects. Combined with originals: 12-16 candidates.

**Why mutation?**: Even good ideas can be improved by systematic transformation. This is inspired by genetic algorithms and creative problem-solving techniques.

### Stage 2.5: Diversity Archive / MAP-Elites *(new)*

**What**: An LLM characterizes each proposal along 3 behavioral dimensions (paradigm novelty, structural complexity, migration distance), then a MAP-Elites algorithm selects the most diverse, highest-quality subset.

**How it works**:
1. The LLM scores each proposal on a 1-5 scale across 3 dimensions → a 5×5×5 grid
2. Each proposal is placed in a grid cell based on its scores
3. If multiple proposals fall in the same cell, only the highest-quality one survives
4. The top-K most diverse proposals are selected via greedy selection maximizing grid coverage

**Output**: A reduced set of ~10 proposals (configurable via `top_k`) that maximize behavioral diversity.

**Why?**: Without diversity selection, the mutation stage can produce many similar variants. MAP-Elites ensures the downstream pipeline evaluates a maximally diverse set.

### Stage 3: Self-Refinement

**What**: Each proposal undergoes 2 rounds of self-critique and improvement.

**Constraint**: Refinement must make proposals **stronger and more coherent** without making them **more conservative**.

**Output**: `RefinedProposal` objects.

**Why 2 rounds?**: First round fixes obvious inconsistencies; second round adds specificity and addresses objections.

### Stage 4: Physics Critic

**What**: A "physics of computing" critic annotates each proposal with hard-constraint violations.

**Checks for**:
- CAP theorem violations
- Computational complexity issues
- Network physics violations (latency, bandwidth, reliability assumptions)
- Consistency model contradictions
- Resource limits (memory, storage, compute)
- Data integrity gaps

**CRITICAL**: The critic **annotates only** — it never rejects a proposal. Even proposals with critical violations pass through with their annotations.

**Output**: `AnnotatedProposal` objects.

**Why annotate instead of reject?**: Radical ideas often violate conventional wisdom. Annotations provide information without gatekeeping.

### Stage 4.5: Structured Debate *(new)*

**What**: Each proposal is debated in a 3-round structured format between an **Advocate** (argues for innovation) and a **Devil's Advocate** (argues for staying with the status quo).

**Debate structure** (7 LLM calls per proposal):
1. **Round 1-3**: Advocate argues for the proposal, Devil's Advocate argues against
2. **Steel-manning**: Each side must present the strongest version of the OTHER side's argument
3. **Judge**: An impartial judge evaluates the debate and scores:
   - Innovation defense strength (0-10)
   - Status quo weakness exposed (0-10)
   - Risk mitigation quality (0-10)
   - Debate winner: "innovation" or "status_quo"
   - Key insight and residual concerns

**Asymmetric design**: The Advocate has access to the full proposal and its innovations. The Devil's Advocate argues from the perspective of the current architecture. The judge focuses on intellectual honesty and argument quality — not conservative safety.

**Output**: `DebateResult` objects fed into portfolio assembly for additional scoring context.

**Why debate?**: Proposals that survive rigorous adversarial scrutiny are genuinely stronger. Debates also surface insights that no single critic would find.

### Stage 4.7: Domain Critics *(new)*

**What**: 4 specialized domain critics review each annotated proposal, adding domain-specific annotations.

**The 4 Critics**:
1. **Security Critic** — Authentication, authorization, data protection, compliance
2. **Cost Critic** — Infrastructure costs, operational overhead, ROI analysis
3. **Org Readiness Critic** — Team skills, change management, adoption complexity
4. **Data Quality Critic** — Data lineage, quality gates, schema evolution, observability

**Like the physics critic**: Domain critics **annotate only** — they never reject. Each annotation includes concern, severity (info/warning/critical), affected components, and suggested mitigation.

**Output**: `AllDomainCriticsResult` per proposal, fed into portfolio assembly.

**Why 4 separate critics?**: Specialized critics produce deeper analysis than a generalist. Running them in parallel keeps latency low.

### Stage 5: Portfolio Assembly & Ranking

**What**: Score all proposals across 4 dimensions, assign tiers, produce final portfolio. If structured debates and domain critics ran, their results are included as additional context for the ranker.

**Scoring Dimensions** (0-10 scale):

1. **Innovation Score** — How structurally novel is this? Paradigm shift or incremental?
2. **Feasibility Score** — Given physics annotations and constraints, how doable is this?
3. **Business Alignment Score** — How well does this serve stated business goals?
4. **Migration Complexity Score** — How difficult to migrate from current state? (10 = trivial, 1 = rebuild)

**Tiering Rules**:
- Conservative: Innovation score ≤ 4
- Moderate Innovation: Innovation score 5-7
- Radical: Innovation score ≥ 8

**Output**: `Portfolio` object with all proposals ranked by composite score, plus executive summary.

---

## MCP Server Architecture

The system uses **Model Context Protocol (MCP)** servers to provide enterprise context to agents. This is a key architectural decision.

### Why MCP?

Traditional approach: Dump all files into the prompt → **context window explosion**.

MCP approach: Run specialized servers that agents query on-demand → **scalable, modular, future-proof**.

### The 3 MCP Servers

#### 1. `enterprise-docs-server`
**Serves**: Current architecture, business goals, constraints, team profile, pain points.

**Tools**:
- `get_current_architecture()`
- `get_business_goals()`
- `get_constraints()`
- `get_team_profile()`
- `get_pain_points()`

**Data source**: `input/enterprise_docs/` directory.

#### 2. `metadata-server`
**Serves**: Schemas, pipeline definitions, infrastructure catalog, data volumes.

**Tools**:
- `get_schema_inventory()`
- `get_pipeline_definitions()`
- `get_infrastructure_catalog()`
- `get_data_volume_stats()`
- `search_metadata(query: str)`

**Data source**: `input/metadata/` directory.

#### 3. `patterns-knowledge-server`
**Serves**: Architectural pattern knowledge base for inspiration.

**Tools**:
- `get_patterns_by_paradigm(paradigm: str)`
- `get_cross_domain_analogies(source_domain: str, target_concept: str)`
- `get_emerging_patterns()`
- `get_anti_patterns()`

**Data source**: `knowledge_base/` directory (curated patterns shipped with the system).

### MCP Integration Flow

```python
# In main.py, before Stage 0a:
enterprise_context = await gather_enterprise_context()
patterns_context = await gather_patterns_context()

# If prompt enhancement is enabled, also fetch paradigm-specific patterns:
paradigm_patterns = await gather_paradigm_patterns()
# Calls: get_patterns_by_paradigm() for each enabled agent

# Pre-fetched context is injected into the intent agent and paradigm agent prompts
```

**Why pre-fetch instead of on-demand agent calls?**: Keeps the MVP simple. Agents are pure LLM calls, not autonomous tool-using agents. Future versions could let agents query MCP directly.

---

## Configuration

### `config.yaml`

```yaml
# LLM Configuration
# For Ollama (local):  model: "ollama_chat/qwen3:1.7b"
# For Anthropic:       model: "anthropic/claude-sonnet-4-20250514"
# For OpenAI:          model: "openai/gpt-4"
llm:
  model: "ollama_chat/qwen3:1.7b"
  api_base: "http://localhost:11434"   # Ollama default. Remove or set to null for cloud APIs.
  temperature:
    paradigm_agents: 0.9       # High divergence for idea generation
    mutation_engine: 0.85      # High but slightly less
    self_refinement: 0.5       # Lower for refinement
    physics_critic: 0.3        # Low for analytical work
    portfolio_ranker: 0.3      # Low for evaluation
  max_retries: 3               # instructor retry count on validation failure

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
  # Stage 0a — Intent Agent
  intent_agent:
    enabled: true
    temperature: 0.4

  # Stage 0b — Prompt Enhancement
  prompt_enhancement:
    enabled: true              # false = paradigm agents get static prompts (MVP behavior)

  # Stage 1 — Paradigm Agents
  paradigm_agents:
    enabled_agents: ["streaming", "event_sourcing", "declarative", "wildcard"]

  # Stage 2 — Mutation
  mutation:
    operators_per_proposal: 3
    available_operators: ["invert", "merge", "eliminate", "analogize", "temporalize", "abstract"]

  # Stage 2.5 — Diversity Archive (MAP-Elites)
  diversity_archive:
    enabled: true
    top_k: 10                  # How many diverse proposals to keep
    temperature: 0.2

  # Stage 3 — Self-Refinement
  self_refinement:
    rounds: 2

  # Stage 4.5 — Structured Debate
  structured_debate:
    enabled: true
    temperature:
      advocate: 0.6
      devil_advocate: 0.6
      judge: 0.3
    rounds: 3

  # Stage 4.7 — Domain Critics
  domain_critics:
    enabled: true
    critics: ["security", "cost", "org_readiness", "data_quality"]
    temperature: 0.3

  # Stage 5 — Portfolio Assembly
  portfolio:
    score_weights:
      innovation: 0.35
      feasibility: 0.25
      business_alignment: 0.25
      migration_complexity: 0.15

# Output Configuration
output:
  dir: "./outputs/"
  render_markdown_report: true
```

### Enabling / Disabling New Stages

All 5 new stages have an `enabled` flag. Set to `false` to revert to the original 5-stage pipeline:

```yaml
pipeline:
  intent_agent:
    enabled: false
  prompt_enhancement:
    enabled: false
  diversity_archive:
    enabled: false
  structured_debate:
    enabled: false
  domain_critics:
    enabled: false
```

### Using Ollama (Local Models)

1. Install [Ollama](https://ollama.com/) and pull a model: `ollama pull qwen3:1.7b`
2. Set the model in `config.yaml` with the `ollama_chat/` prefix:
   ```yaml
   llm:
     model: "ollama_chat/qwen3:1.7b"
     api_base: "http://localhost:11434"
   ```
3. No API key needed. The system automatically sets a 10-minute timeout for local models.

### Tuning Recommendations

**For more conservative proposals**: Lower `temperature.paradigm_agents` to 0.7, reduce `mutation.operators_per_proposal` to 1, disable diversity archive.

**For more radical proposals**: Increase `temperature.paradigm_agents` to 1.0, increase `mutation.operators_per_proposal` to 4, increase `portfolio.score_weights.innovation` to 0.5.

**For faster runs**: Disable new stages (`intent_agent`, `diversity_archive`, `structured_debate`, `domain_critics`), reduce `self_refinement.rounds` to 1, use a faster model.

**For maximum quality**: Enable all stages, use a strong model (Claude Sonnet/Opus, GPT-4), set `diversity_archive.top_k` to 12-15.

---

## Customizing Your Input

**⚠️ The example files currently in `input/` are for a FICTIONAL e-commerce company and must be replaced with YOUR documentation before running.**

All example files have been marked with warnings. See detailed templates and instructions in:
- `input/README.md` — Overview of what to provide
- `input/enterprise_docs/README.md` — Enterprise documentation templates
- `input/metadata/README.md` — Metadata file templates

### Enterprise Documentation (`input/enterprise_docs/`)

Create markdown files describing your organization. The file names are flexible (the MCP server searches for keywords).

**Recommended files**:
- `architecture.md` — Current data pipeline architecture, components, technologies, data flow
- `business_goals.md` — Business objectives, KPIs, strategic priorities
- `constraints.md` — Regulatory requirements, budget limits, SLAs, security mandates
- `team.md` — Team skills, size, experience, org structure
- `pain_points.md` — Known problems, bottlenecks, incidents, technical debt

**Tips**:
- Be specific. Vague descriptions → vague proposals.
- Include numbers: data volumes, team size, SLA targets, budget.
- Describe both what works and what doesn't.

### Metadata (`input/metadata/`)

**Formats supported**: JSON, YAML, plain text.

**Recommended files**:
- `schema_inventory.json` — Database schemas, tables, columns, relationships
- `infrastructure_catalog.json` — Deployed infrastructure inventory
- `pipeline_definitions.yaml` — Current pipeline/DAG definitions
- `volume_stats.json` — Data volume statistics, ingestion rates, query patterns

**Tips**:
- The MCP server can search across all files, so partial information is fine.
- You can export schemas from your data catalog or schema registry.

### Extending the Knowledge Base (`knowledge_base/`)

The knowledge base is a key differentiator. It gives the mutation engine and wildcard agent access to cross-domain patterns.

**Current files**:
- `streaming_patterns.md`, `event_sourcing_patterns.md`, `declarative_patterns.md` — Conventional data patterns
- `biological_analogies.md`, `economic_analogies.md`, `physical_analogies.md`, `social_analogies.md` — Cross-domain inspiration
- `emerging_patterns.md` — Cutting-edge patterns (Data Mesh, Lakehouse, etc.)
- `anti_patterns.md` — Known failure modes to avoid

**To extend**: Add markdown files with new patterns. The MCP server will automatically serve them.

**Format**:
```markdown
## Pattern Name
- **Description**: What it is
- **Key Components**: What you need
- **Tradeoffs**: Pros and cons
- **Real-world examples**: Who's using it
- **Architectural translation**: How to apply to data pipelines
```

---

## Output Format

### `portfolio.json`

Structured JSON with the complete portfolio:

```json
{
  "proposals": [
    {
      "proposal": {
        "proposal": {
          "architecture_name": "...",
          "core_thesis": "...",
          "components": [...],
          "data_flow": [...],
          "key_innovations": [...],
          "assumptions": [...],
          "risks": [...]
        },
        "annotations": [...],
        "hard_constraint_violations": 0,
        "overall_feasibility_note": "..."
      },
      "innovation_score": 8.5,
      "feasibility_score": 6.0,
      "business_alignment_score": 7.5,
      "migration_complexity_score": 3.0,
      "composite_score": 6.75,
      "tier": "radical",
      "one_line_summary": "..."
    }
  ],
  "top_conservative": "...",
  "top_moderate": "...",
  "top_radical": "...",
  "executive_summary": "..."
}
```

### `portfolio_report.md`

Human-readable markdown report with:

1. **Executive Summary** — 2-3 paragraph overview of the innovation-risk frontier
2. **Top Picks by Tier** — Best conservative, moderate, and radical options
3. **Innovation-Risk Frontier Table** — All proposals with scores
4. **Full Proposal Details** — For each proposal:
   - Core thesis
   - Components and data flow
   - Key innovations
   - Assumptions and risks
   - Physics critic annotations (with severity color coding)

---

## Troubleshooting

### "No proposals generated in Stage 1"

**Cause**: All 4 agents failed, likely due to API errors or invalid responses.

**Fix**:
1. Check your API key is set correctly
2. Check API rate limits
3. Review logs for specific error messages
4. Try a different model in `config.yaml`

### "Only X proposals survived to Stage 5"

**Cause**: Some agents or mutations failed during the pipeline.

**Fix**: This is expected behavior. The pipeline uses `return_exceptions=True` to continue even when individual calls fail. As long as ≥6 proposals reach Stage 5, the portfolio is still useful.

### High cost / slow runtime

**Cause**: A full pipeline run with all stages enabled makes 60-100+ LLM calls (1 intent + 4 agents + 8-12 mutations + 10 diversity scores + 10-20 refinements × 2 + 10-20 critics + 7 × N debate calls + 4 × N domain critics + 1 ranker).

**Fix**:
1. Use Ollama with a fast local model for development/testing
2. Disable stages you don't need: `structured_debate.enabled: false`, `domain_critics.enabled: false`
3. Reduce `diversity_archive.top_k` from 10 to 6 (fewer proposals flow downstream)
4. Reduce `mutation.operators_per_proposal` from 3 to 2
5. Reduce `self_refinement.rounds` from 2 to 1
6. Use a cheaper/faster cloud model for non-critical stages

### MCP server connection errors

**Cause**: The MCP servers run as subprocesses. If they fail to start, context gathering fails.

**Fix**:
1. Ensure Python can execute `python -m mcp_servers.enterprise_docs`
2. Check that `input/` directories exist and contain files
3. Review `mcp_client/context_gatherer.py` logs for specific errors

---

## Development

### Running Tests

```bash
# TODO: Add pytest tests for schemas, prompts, and pipeline stages
pytest tests/
```

### Extending with New Agents

To add a 5th paradigm agent:

1. Add prompt template to `prompts/paradigm_agents.py`:
   ```python
   MY_NEW_AGENT_SYSTEM_PROMPT_TEMPLATE = """..."""
   AGENT_PROMPTS["my_new_agent"] = MY_NEW_AGENT_SYSTEM_PROMPT_TEMPLATE
   ```

2. Enable in `config.yaml`:
   ```yaml
   enabled_agents: ["streaming", "event_sourcing", "declarative", "wildcard", "my_new_agent"]
   ```

Note: Prompts use `_SYSTEM_PROMPT_TEMPLATE` naming since Stage 0b dynamically enriches them with intent context.

### Extending with New Mutation Operators

1. Add prompt to `prompts/mutation_operators.py`:
   ```python
   MY_OPERATOR_PROMPT = """..."""
   OPERATOR_PROMPTS["my_operator"] = MY_OPERATOR_PROMPT
   ```

2. Enable in `config.yaml`:
   ```yaml
   available_operators: [..., "my_operator"]
   ```

---

## Design Philosophy

### Why This System Exists

Traditional architecture design processes suffer from:
1. **Anchoring bias** — Starting with the current architecture and optimizing it incrementally
2. **Groupthink** — Architectural review committees converge on safe, conventional solutions
3. **Recency bias** — Recent experiences dominate; cross-domain insights are rare
4. **Premature optimization** — Feasibility concerns kill radical ideas before they're fully developed

This system is designed to counteract these biases:
- **Intent agent** ensures agents solve the right problem, not just any problem
- **Divergent agents** with enhanced prompts force exploration of fundamentally different paradigms
- **Mutation operators** systematically transform ideas in ways humans don't naturally consider
- **MAP-Elites diversity archive** prevents convergence to similar solutions
- **Self-refinement** strengthens radical ideas before exposing them to criticism
- **Physics critic annotates without rejecting** — information, not gatekeeping
- **Structured debate** stress-tests proposals without killing innovation
- **Domain critics** provide specialized scrutiny across security, cost, org, and data quality
- **Portfolio output** presents the innovation-risk frontier instead of a single "best" answer

### What This System Is NOT

- **Not a chatbot** — It's a 10-stage pipeline with a specific sequence of operations
- **Not production-ready architecture** — Proposals are starting points for human evaluation and refinement
- **Not a replacement for architects** — It's a tool to expand the solution space, not make final decisions
- **Not optimized for conventional solutions** — If you want incremental improvement, use traditional methods

### When to Use This System

**Good fit**:
- Greenfield architecture design
- Architecture redesign / modernization projects
- Exploring alternatives to an existing architecture
- Validating your architecture against radical alternatives
- Generating ideas for architectural RFCs

**Poor fit**:
- Operational troubleshooting
- Small incremental changes to existing systems
- Well-understood, commodity architectures (e.g., "build a CRUD API")

---

## License

MIT

---

## Credits

Inspired by:
- **Genetic algorithms** and evolutionary computation (mutation operators)
- **MAP-Elites** quality-diversity algorithm (diversity archive)
- **Divergent thinking** techniques from creative problem-solving
- **Red team / blue team** exercises (paradigm agents as different "teams")
- **Structured academic debate** and steel-manning (structured debate stage)
- **Innovation management** frameworks (innovation-risk portfolio approach)
- **Wardley Mapping** and strategic architecture thinking

Built with:
- [litellm](https://github.com/BerriAI/litellm) — Model-agnostic LLM client
- [instructor](https://github.com/jxnl/instructor) — Structured LLM outputs
- [MCP (Model Context Protocol)](https://github.com/modelcontextprotocol) — Standardized LLM-tool integration
- [Pydantic](https://github.com/pydantic/pydantic) — Data validation
- [Jinja2](https://github.com/pallets/jinja) — Template rendering
