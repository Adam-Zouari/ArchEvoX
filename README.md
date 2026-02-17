# Innovation-Optimized Multi-Agent Architecture Generator

A Python-based multi-agent system that generates **innovative** data pipeline architecture proposals. Unlike traditional architecture design tools, this system is explicitly optimized for **architectural innovation and paradigm shifts**, not just optimization of existing patterns.

## What Does It Do?

Given enterprise documentation about your current data infrastructure, the system:

1. Generates 4 radically different architectural proposals using specialized AI agents
2. Mutates each proposal to explore the solution space (12-16 candidates total)
3. Refines proposals through self-critique (without making them conservative)
4. Annotates with physics-of-computing constraints (CAP theorem, complexity bounds, etc.)
5. Ranks and tiers proposals on an innovation-risk frontier

**Output**: A portfolio of architectures ranging from conservative to radically novel, scored on innovation, feasibility, business alignment, and migration complexity.

---

## Quick Start

### Prerequisites
- Python 3.11+
- An LLM API key (Anthropic Claude, OpenAI, or any litellm-supported model)

### Installation

```bash
cd innovation_arch_generator
pip install -r requirements.txt
```

### Configuration

Set your API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Or for OpenAI:
export OPENAI_API_KEY="sk-..."
```

Edit `config.yaml` to set your model:
```yaml
llm:
  model: "anthropic/claude-sonnet-4-20250514"  # Or "openai/gpt-4", etc.
```

### Run

```bash
python main.py
```

**Expected runtime**: 10-30 minutes depending on model speed and number of proposals.

**Outputs**:
- `outputs/portfolio.json` — Structured JSON with all proposals and scores
- `outputs/portfolio_report.md` — Human-readable markdown report

---

## Architecture Overview

### System Design

```
INPUT (enterprise context via MCP servers)
  ↓
Stage 1: Paradigm Agent Generation (4 agents, parallel)
  ↓
Stage 2: Idea Mutation (transform each proposal)
  ↓
Stage 3: Self-Refinement (2 rounds of self-critique)
  ↓
Stage 4: Physics Critic (annotate violations, no rejection)
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
| **No agent frameworks** (LangChain, etc.) | Pipeline is a simple 5-stage sequential flow; frameworks add complexity without value |
| **litellm** for LLM calls | Model-agnostic — swap between Claude, GPT, Gemini via config |
| **Physics critic annotates, never rejects** | Prevents premature pruning of innovative ideas by feasibility gatekeepers |
| **Portfolio output** (not single recommendation) | Innovation involves risk; humans should choose their position on the frontier |

---

## Project Structure

```
innovation_arch_generator/
├── config.yaml                  # All tunable parameters
├── main.py                      # Entry point, orchestrates the 5-stage pipeline
├── requirements.txt             # Python dependencies
│
├── stages/                      # The 5 pipeline stages
│   ├── paradigm_agents.py       # Stage 1: 4 parallel agents with different philosophies
│   ├── mutation_engine.py       # Stage 2: Apply mutation operators to proposals
│   ├── self_refinement.py       # Stage 3: Self-critique and improvement loops
│   ├── physics_critic.py        # Stage 4: Hard-constraint annotation
│   └── portfolio_assembly.py    # Stage 5: Ranking, tiering, and output
│
├── prompts/                     # All system prompts (separated from code)
│   ├── paradigm_agents.py       # Prompts for 4 paradigm agents
│   ├── mutation_operators.py    # Prompts for 6 mutation operators
│   ├── self_refinement.py       # Self-critique prompt
│   ├── physics_critic.py        # Physics critic prompt
│   └── portfolio_ranker.py      # Ranking and tiering prompt
│
├── models/
│   └── schemas.py               # All Pydantic models (Proposal, Portfolio, etc.)
│
├── llm/
│   └── client.py                # instructor-patched litellm wrapper with retry
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
│   ├── enterprise_docs/         # Markdown/text describing your organization
│   │   ├── architecture.md      # Current architecture description
│   │   ├── business_goals.md    # Business goals, KPIs, priorities
│   │   ├── constraints.md       # Hard constraints (compliance, SLAs, budget)
│   │   ├── team.md              # Team skills and structure
│   │   └── pain_points.md       # Known pain points and technical debt
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

### Stage 1: Paradigm Agent Generation

**What**: 4 LLM agents run in parallel, each with a radically different architectural philosophy.

**The 4 Agents**:

1. **Stream-First Radical** — Believes batch processing is obsolete; proposes streaming-first architectures
2. **Event-Sourced Purist** — Believes in immutable event logs and CQRS as the foundation
3. **Declarative Abstractionist** — Believes pipelines should be declarative DSLs, not imperative code
4. **Cross-Domain Wildcard** — Draws inspiration from biology, economics, physics, and social systems

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

### Stage 3: Self-Refinement

**What**: Each proposal undergoes 2 rounds of self-critique and improvement.

**Constraint**: Refinement must make proposals **stronger and more coherent** without making them **more conservative**.

**Output**: 12-16 `RefinedProposal` objects.

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

**Output**: 12-16 `AnnotatedProposal` objects.

**Why annotate instead of reject?**: Radical ideas often violate conventional wisdom. Annotations provide information without gatekeeping.

### Stage 5: Portfolio Assembly & Ranking

**What**: Score all proposals across 4 dimensions, assign tiers, produce final portfolio.

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
# In main.py, before Stage 1:
enterprise_context = await gather_enterprise_context()
# Calls: get_current_architecture(), get_business_goals(), get_constraints(),
#        get_pain_points(), get_schema_inventory(), get_infrastructure_catalog()

patterns_context = await gather_patterns_context()
# Calls: get_emerging_patterns(), get_cross_domain_analogies()

# Pre-fetched context is then injected into agent prompts
```

**Why pre-fetch instead of on-demand agent calls?**: Keeps the MVP simple. Agents are pure LLM calls, not autonomous tool-using agents. Future versions could let agents query MCP directly.

---

## Configuration

### `config.yaml`

```yaml
# LLM Configuration
llm:
  model: "anthropic/claude-sonnet-4-20250514"  # Any litellm-compatible model
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
  paradigm_agents:
    enabled_agents: ["streaming", "event_sourcing", "declarative", "wildcard"]
  mutation:
    operators_per_proposal: 3  # How many mutations per proposal (2-3)
    available_operators: ["invert", "merge", "eliminate", "analogize", "temporalize", "abstract"]
  self_refinement:
    rounds: 2
  portfolio:
    score_weights:
      innovation: 0.35          # Weight for innovation in composite score
      feasibility: 0.25
      business_alignment: 0.25
      migration_complexity: 0.15

# Output Configuration
output:
  dir: "./outputs/"
  render_markdown_report: true
```

### Tuning Recommendations

**For more conservative proposals**: Lower `temperature.paradigm_agents` to 0.7, reduce `mutation.operators_per_proposal` to 1.

**For more radical proposals**: Increase `temperature.paradigm_agents` to 1.0, increase `mutation.operators_per_proposal` to 4, increase `portfolio.score_weights.innovation` to 0.5.

**For faster runs**: Reduce `self_refinement.rounds` to 1, use a faster model (e.g., `anthropic/claude-haiku-4-5`).

---

## Customizing Your Input

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

**Cause**: Each pipeline run makes 30-50 LLM calls (4 agents + 8-12 mutations + 12-16 refinements × 2 + 12-16 critics + 1 ranker).

**Fix**:
1. Use a cheaper/faster model for non-critical stages (e.g., Haiku for refinement and critic)
2. Reduce `mutation.operators_per_proposal` from 3 to 2
3. Reduce `self_refinement.rounds` from 2 to 1
4. Disable specific agents in `pipeline.paradigm_agents.enabled_agents`

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

1. Add prompt to `prompts/paradigm_agents.py`:
   ```python
   MY_NEW_AGENT_PROMPT = """..."""
   AGENT_PROMPTS["my_new_agent"] = MY_NEW_AGENT_PROMPT
   ```

2. Enable in `config.yaml`:
   ```yaml
   enabled_agents: ["streaming", "event_sourcing", "declarative", "wildcard", "my_new_agent"]
   ```

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
- **Divergent agents** force exploration of fundamentally different paradigms
- **Mutation operators** systematically transform ideas in ways humans don't naturally consider
- **Self-refinement** strengthens radical ideas before exposing them to criticism
- **Physics critic annotates without rejecting** — information, not gatekeeping
- **Portfolio output** presents the innovation-risk frontier instead of a single "best" answer

### What This System Is NOT

- **Not a chatbot** — It's a pipeline with a specific sequence of operations
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
- **Divergent thinking** techniques from creative problem-solving
- **Red team / blue team** exercises (paradigm agents as different "teams")
- **Innovation management** frameworks (innovation-risk portfolio approach)
- **Wardley Mapping** and strategic architecture thinking

Built with:
- [litellm](https://github.com/BerriAI/litellm) — Model-agnostic LLM client
- [instructor](https://github.com/jxnl/instructor) — Structured LLM outputs
- [MCP (Model Context Protocol)](https://github.com/modelcontextprotocol) — Standardized LLM-tool integration
- [Pydantic](https://github.com/pydantic/pydantic) — Data validation
- [Jinja2](https://github.com/pallets/jinja) — Template rendering
