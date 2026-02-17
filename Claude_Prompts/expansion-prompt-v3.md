# Coding Agent Prompt: Expand the Innovation Architecture Generator

## Context

The MVP of the Innovation-Optimized Multi-Agent Architecture Generator is **already implemented and working**. It has the following pipeline:

```
INPUT (enterprise context via MCP servers)
  → Stage 1: Paradigm Agent Generation (4 agents, parallel)
     → [HITL Checkpoint A]
  → Stage 2: Idea Mutation (6 operators, 2-3 per proposal)
     → [HITL Checkpoint B]
  → Stage 3: Self-Refinement (2 rounds per proposal)
  → Stage 4: Physics Critic (annotate-only, never rejects)
     → [HITL Checkpoint C]
  → Stage 5: Portfolio Assembly & Ranking
     → [HITL Checkpoint D]
OUTPUT (portfolio.json + portfolio_report.md)
```

The existing codebase uses:
- `litellm` for model-agnostic LLM calls
- `instructor` (patched on litellm) for structured Pydantic output on every LLM call
- 3 MCP servers (`enterprise-docs-server`, `metadata-server`, `patterns-knowledge-server`)
- HITL checkpoints with boost/seed/star/prune/annotate/deep_dive/re_mutate actions
- `asyncio` for parallel execution within stages
- `config.yaml` for all tunable parameters
- No agent frameworks (no LangChain, LangGraph, CrewAI, AutoGen)

All Pydantic schemas (`Proposal`, `MutatedProposal`, `RefinedProposal`, `AnnotatedProposal`, `ScoredProposal`, `Portfolio`, `CheckpointFeedback`, etc.) are already defined in `models/schemas.py`.

## Your Task

Add **5 new components** to the existing pipeline. Do NOT rewrite or break existing stages. Each new component integrates at a specific point in the pipeline. The updated pipeline will look like this:

```
INPUT (enterprise context via MCP servers)
  → NEW Stage 0a: Intent Agent (understands what the user actually wants)
  → NEW Stage 0b: Prompt Enhancement (enriches paradigm agent prompts with intent + context)
  → Stage 1: Paradigm Agent Generation (4 agents, parallel) — EXISTING, no changes
     → [HITL Checkpoint A] — EXISTING
  → Stage 2: Idea Mutation — EXISTING, no changes
     → [HITL Checkpoint B] — EXISTING
  → NEW Stage 2.5: Diversity Archive (MAP-Elites selection of top-K diverse candidates)
  → Stage 3: Self-Refinement — EXISTING, no changes
  → Stage 4: Physics Critic — EXISTING, no changes
     → [HITL Checkpoint C] — EXISTING
  → NEW Stage 4.5: Structured Debate (asymmetric, innovation-favoring)
  → NEW Stage 4.7: Domain Critics (security, cost, org readiness — annotate-only)
  → Stage 5: Portfolio Assembly & Ranking — EXISTING, but now receives debate + domain annotations
     → [HITL Checkpoint D] — EXISTING
OUTPUT
```

Below are the detailed specifications for each new component.

---

## NEW Component 1: Intent Agent (Stage 0a)

### Purpose

The paradigm agents in Stage 1 currently receive raw enterprise documentation and a fixed system prompt. The problem: the enterprise documentation may be pages long, and the paradigm agents must decide for themselves what's important, what the user's actual priorities are, and what "innovation" means in this specific context. This leads to proposals that are generically innovative rather than *strategically* innovative.

The Intent Agent solves this by analyzing the input documentation and producing a structured **intent brief** that captures:
- What the user is actually trying to achieve (not just what they documented)
- Where the real pain is (not just the listed pain points)
- What implicit constraints exist that aren't written down
- What the innovation opportunity space looks like
- What paradigm shifts would be most valuable for THIS specific situation

### Where it fits

Runs BEFORE Stage 1. It reads the enterprise context (pre-fetched from MCP servers) and produces an `IntentBrief` that is passed to Stage 0b (Prompt Enhancement) and then to all paradigm agents.

### Intent Agent System Prompt

```
You are an enterprise architecture analyst. Your job is NOT to propose solutions — it is to deeply understand the SITUATION before any proposal work begins.

You will receive documentation about an enterprise's current data pipeline: architecture descriptions, business goals, constraints, pain points, metadata, and infrastructure inventory.

Your task is to produce an Intent Brief that answers:

1. CORE OBJECTIVE: What is the user fundamentally trying to achieve? Look beyond the surface-level ask. If they say "optimize our ETL pipeline," they might actually need "get analytical data to business users 10x faster" or "reduce the cost of maintaining 200 pipeline jobs" or "prepare for real-time ML feature serving." Identify the deepest objective.

2. PAIN DIAGNOSIS: What are the root causes of the stated pain points? Don't repeat the symptoms — diagnose the underlying structural issues. Example: "The real problem isn't that jobs fail — it's that the architecture has no observability, so failures cascade undetected for hours."

3. IMPLICIT CONSTRAINTS: What constraints exist that aren't documented? Infer from the technology choices, team size, industry, and organizational structure. Example: if they're running Hadoop in 2025, there's probably a risk-averse culture and a large sunk cost in the platform.

4. INNOVATION OPPORTUNITY MAP: Where are the highest-leverage opportunities for architectural innovation? What parts of the system would benefit most from a paradigm shift vs. which parts are working fine and should be left alone?

5. PARADIGM SHIFT CANDIDATES: What specific paradigm shifts could be most transformative for THIS situation? Not generic — specific to their data volumes, business domain, team capabilities, and strategic direction. For each candidate, explain why it would be transformative.

6. ANTI-GOALS: What should the proposals explicitly NOT do? What would be a waste of innovation effort? What parts of the architecture are not worth redesigning?

7. SUCCESS CRITERIA: How would the user judge whether a proposed architecture is a success? What metrics matter? What would make them say "this is exactly what we needed"?

Be analytical, not prescriptive. Your job is to set up the paradigm agents for success by giving them a precise understanding of the target.
```

### Pydantic Schema

```python
class ParadigmShiftCandidate(BaseModel):
    """A specific paradigm shift opportunity identified by the intent agent."""
    paradigm: str = Field(description="The paradigm shift (e.g., 'batch-to-streaming', 'monolith-to-mesh')")
    target_area: str = Field(description="Which part of the architecture this applies to")
    rationale: str = Field(description="Why this shift would be transformative for THIS specific situation")
    leverage_score: int = Field(
        description="1-10: how much impact this shift would have relative to effort",
        ge=1, le=10
    )

class InnovationOpportunity(BaseModel):
    """A specific area where architectural innovation has high leverage."""
    area: str = Field(description="The area of the architecture")
    current_state: str = Field(description="What it looks like now and why it's limiting")
    opportunity: str = Field(description="What innovation could unlock here")
    priority: str = Field(description="'high', 'medium', or 'low'")

class IntentBrief(BaseModel):
    """Structured output from the Intent Agent. This becomes the foundation
    for all downstream work — it ensures paradigm agents are solving the RIGHT problem."""
    core_objective: str = Field(
        description="The deepest, most fundamental objective — what the user really needs. "
                    "2-3 sentences maximum."
    )
    pain_diagnosis: list[str] = Field(
        description="Root cause diagnoses of the stated pain points (not symptoms, causes)"
    )
    implicit_constraints: list[str] = Field(
        description="Constraints that exist but aren't documented"
    )
    innovation_opportunity_map: list[InnovationOpportunity] = Field(
        description="Where architectural innovation has the highest leverage"
    )
    paradigm_shift_candidates: list[ParadigmShiftCandidate] = Field(
        description="Specific paradigm shifts ranked by transformative potential"
    )
    anti_goals: list[str] = Field(
        description="What proposals should explicitly NOT do or redesign"
    )
    success_criteria: list[str] = Field(
        description="How the user would judge whether a proposal is successful"
    )
    key_context_for_agents: str = Field(
        description="A 2-3 paragraph executive briefing that can be injected directly "
                    "into paradigm agent prompts. Summarizes the situation, priorities, "
                    "and constraints in a way that's immediately actionable."
    )
```

### Implementation

```python
# stages/intent_agent.py

async def run_intent_agent(enterprise_context: str) -> IntentBrief:
    """Analyze enterprise context and produce an intent brief."""
    return await call_llm(
        system_prompt=INTENT_AGENT_SYSTEM_PROMPT,
        user_message=(
            "Analyze the following enterprise documentation and produce "
            "an Intent Brief.\n\n"
            f"{enterprise_context}"
        ),
        response_model=IntentBrief,
        temperature=0.4,  # Low — this is analytical, not creative
    )
```

### Config Addition

```yaml
pipeline:
  intent_agent:
    enabled: true
    temperature: 0.4
```

---

## NEW Component 2: Prompt Enhancement (Stage 0b)

### Purpose

The paradigm agents currently have static system prompts. This stage dynamically enriches those prompts using the Intent Brief (from Stage 0a) and relevant patterns from the MCP patterns-knowledge-server. Each paradigm agent receives a tailored prompt that incorporates:

1. The intent brief's `key_context_for_agents` — so agents understand the REAL problem
2. The relevant paradigm shift candidates — so agents know which shifts have the highest leverage
3. Paradigm-specific patterns from the knowledge base — so agents have concrete examples
4. Anti-goals — so agents don't waste effort on areas that don't need innovation

This is NOT a separate LLM call for each agent. It is a **programmatic prompt assembly** step that takes the static system prompt templates, the Intent Brief, and MCP-fetched patterns, and composes the final enriched prompt for each agent.

### Where it fits

Runs AFTER the Intent Agent (Stage 0a), BEFORE Stage 1 (Paradigm Agents). No LLM call required — this is pure Python string composition.

### Implementation

```python
# stages/prompt_enhancement.py

from prompts.paradigm_agents import (
    STREAMING_SYSTEM_PROMPT_TEMPLATE,
    EVENT_SOURCING_SYSTEM_PROMPT_TEMPLATE,
    DECLARATIVE_SYSTEM_PROMPT_TEMPLATE,
    WILDCARD_SYSTEM_PROMPT_TEMPLATE,
)

PARADIGM_TO_KNOWLEDGE_QUERY = {
    "streaming": "streaming",
    "event_sourcing": "event-sourcing",
    "declarative": "declarative",
    "wildcard": None,  # wildcard fetches cross-domain patterns instead
}

async def enhance_prompts(
    intent_brief: IntentBrief,
    patterns_context: dict[str, str],  # paradigm_name -> fetched patterns text
) -> dict[str, str]:
    """Compose enriched system prompts for each paradigm agent.

    Does NOT call an LLM. This is deterministic prompt assembly.

    Returns: dict mapping paradigm name to its enriched system prompt.
    """

    enriched = {}

    # Shared context block injected into every agent's prompt
    shared_context_block = f"""
## Situation Briefing (from Intent Analysis)

{intent_brief.key_context_for_agents}

## Core Objective
{intent_brief.core_objective}

## Anti-Goals (do NOT waste innovation effort here)
{chr(10).join(f'- {ag}' for ag in intent_brief.anti_goals)}

## Success Criteria (how the user will judge your proposal)
{chr(10).join(f'- {sc}' for sc in intent_brief.success_criteria)}

## Highest-Leverage Innovation Opportunities
{chr(10).join(
    f'- [{opp.priority.upper()}] {opp.area}: {opp.opportunity}'
    for opp in intent_brief.innovation_opportunity_map
)}
"""

    # Relevant paradigm shifts block
    paradigm_shifts_block = "\n## Paradigm Shifts With Highest Transformative Potential\n"
    for ps in sorted(intent_brief.paradigm_shift_candidates, key=lambda x: -x.leverage_score):
        paradigm_shifts_block += (
            f"- {ps.paradigm} (leverage: {ps.leverage_score}/10) — "
            f"Target: {ps.target_area}. {ps.rationale}\n"
        )

    # Per-agent enrichment
    for paradigm_name, template in [
        ("streaming", STREAMING_SYSTEM_PROMPT_TEMPLATE),
        ("event_sourcing", EVENT_SOURCING_SYSTEM_PROMPT_TEMPLATE),
        ("declarative", DECLARATIVE_SYSTEM_PROMPT_TEMPLATE),
        ("wildcard", WILDCARD_SYSTEM_PROMPT_TEMPLATE),
    ]:
        # Fetch paradigm-specific patterns from knowledge base
        paradigm_patterns = patterns_context.get(paradigm_name, "")

        # Compose the enriched prompt
        enriched_prompt = f"""{template}

---
THE FOLLOWING CONTEXT IS SPECIFIC TO THIS RUN. USE IT TO GROUND YOUR PROPOSAL.
---

{shared_context_block}

{paradigm_shifts_block}

## Relevant Architectural Patterns (from knowledge base)
{paradigm_patterns if paradigm_patterns else "No specific patterns pre-loaded. Draw from your training knowledge."}

## Implicit Constraints (not documented, but inferred)
{chr(10).join(f'- {ic}' for ic in intent_brief.implicit_constraints)}

---
Remember: your proposal must address the CORE OBJECTIVE above, not just be generically innovative.
Propose a paradigm shift that is transformative for THIS specific situation.
---
"""
        enriched[paradigm_name] = enriched_prompt

    return enriched
```

### Changes to Existing Paradigm Agent Prompts

Rename the existing static system prompts to `*_TEMPLATE` variants. They remain unchanged in content — the enhancement stage wraps them with context. For example:

```python
# prompts/paradigm_agents.py

# BEFORE (existing):
# STREAMING_SYSTEM_PROMPT = "You are a senior data architect who..."

# AFTER (renamed, content unchanged):
STREAMING_SYSTEM_PROMPT_TEMPLATE = "You are a senior data architect who..."
```

### Changes to Stage 1 (Paradigm Agents)

The `run_paradigm_agents` function now receives enriched prompts instead of static ones:

```python
# stages/paradigm_agents.py — MODIFIED (minimal change)

async def run_paradigm_agents(
    enterprise_context: str,
    patterns_context: str,
    enriched_prompts: dict[str, str] | None = None,  # NEW PARAMETER
) -> list[Proposal]:
    """Run all paradigm agents in parallel.
    If enriched_prompts is provided, use those instead of static templates."""

    agents = [
        ("streaming", enriched_prompts["streaming"] if enriched_prompts else STREAMING_SYSTEM_PROMPT_TEMPLATE, enterprise_context),
        ("event_sourcing", enriched_prompts["event_sourcing"] if enriched_prompts else EVENT_SOURCING_SYSTEM_PROMPT_TEMPLATE, enterprise_context),
        ("declarative", enriched_prompts["declarative"] if enriched_prompts else DECLARATIVE_SYSTEM_PROMPT_TEMPLATE, enterprise_context),
        ("wildcard", enriched_prompts["wildcard"] if enriched_prompts else WILDCARD_SYSTEM_PROMPT_TEMPLATE, enterprise_context + "\n\n" + patterns_context),
    ]

    # ... rest of existing implementation unchanged
```

### Fetching Paradigm-Specific Patterns

Extend `mcp_client/context_gatherer.py` to fetch patterns per paradigm:

```python
# mcp_client/context_gatherer.py — ADD this function

async def gather_paradigm_patterns() -> dict[str, str]:
    """Fetch paradigm-specific patterns from the patterns-knowledge MCP server.
    Returns dict mapping paradigm name to patterns text."""

    paradigms = {
        "streaming": "streaming",
        "event_sourcing": "event-sourcing",
        "declarative": "declarative",
        "wildcard": None,
    }

    results = {}
    for agent_name, paradigm_query in paradigms.items():
        if paradigm_query:
            results[agent_name] = await mcp_client.call_tool(
                "get_patterns_by_paradigm", {"paradigm": paradigm_query}
            )
        else:
            # Wildcard gets cross-domain patterns
            bio = await mcp_client.call_tool(
                "get_cross_domain_analogies",
                {"source_domain": "biology", "target_concept": "data pipeline"}
            )
            econ = await mcp_client.call_tool(
                "get_cross_domain_analogies",
                {"source_domain": "economics", "target_concept": "resource allocation"}
            )
            emerging = await mcp_client.call_tool("get_emerging_patterns", {})
            results[agent_name] = f"{bio}\n\n{econ}\n\n{emerging}"

    return results
```

### Config Addition

```yaml
pipeline:
  prompt_enhancement:
    enabled: true   # false = paradigm agents get static prompts (MVP behavior)
```

---

## NEW Component 3: Diversity Archive — MAP-Elites (Stage 2.5)

### Purpose

After Stage 2 (Mutation), the pipeline has 12-16+ candidate proposals. Currently, ALL of them flow into Stage 3 (Self-Refinement), which is expensive (2 LLM calls per proposal per round). Many candidates may be structurally similar — e.g., three mutations of the streaming proposal that all look alike.

The Diversity Archive selects a **top-K set of maximally diverse candidates** using a MAP-Elites inspired approach. It ensures that the proposals entering the expensive refinement stage cover the widest possible range of architectural approaches, and that radical proposals are not drowned out by many similar moderate ones.

### How it works

1. An LLM call scores each proposal on 3 behavioral dimensions (see schema below).
2. The scores define a 3D grid. Each cell in the grid represents a unique combination of characteristics.
3. For each occupied cell, keep only the best proposal (by a quality heuristic).
4. Select the top-K most diverse candidates from the grid — ensuring coverage across all dimensions.
5. Any human-starred proposals from Checkpoint B are automatically included regardless of grid position.

### Behavioral Dimensions

| Dimension | Range | Description |
|---|---|---|
| **paradigm_novelty** | 1-5 (bucketed) | How far this departs from conventional data pipeline patterns. 1 = incremental improvement. 5 = completely new paradigm. |
| **structural_complexity** | 1-5 (bucketed) | How many components and interactions the architecture has. 1 = minimal/elegant. 5 = complex/comprehensive. |
| **migration_distance** | 1-5 (bucketed) | How different this is from the current architecture. 1 = small delta. 5 = complete rebuild. |

A 5×5×5 grid has 125 possible cells. With 12-16 proposals, most cells will be empty. The goal is to ensure the occupied cells are spread across the grid, not clustered in one region.

### Pydantic Schema

```python
class DiversityScores(BaseModel):
    """MAP-Elites behavioral characterization of a single proposal."""
    architecture_name: str
    paradigm_novelty: int = Field(ge=1, le=5,
        description="1=incremental improvement, 2=novel combination of known patterns, "
                    "3=significant departure from convention, 4=new paradigm application, "
                    "5=completely new abstraction or paradigm")
    structural_complexity: int = Field(ge=1, le=5,
        description="1=minimal (3-4 components), 2=simple (5-7), 3=moderate (8-12), "
                    "4=complex (13-18), 5=highly complex (19+)")
    migration_distance: int = Field(ge=1, le=5,
        description="1=small config changes, 2=swap some components, "
                    "3=significant rearchitecture, 4=major rebuild, 5=complete greenfield")
    quality_heuristic: float = Field(
        description="0-10 overall quality estimate: coherence, completeness, "
                    "and strength of the core thesis")
    one_line_summary: str

class DiversityArchiveInput(BaseModel):
    """Input to the diversity scorer — a batch of proposals to characterize."""
    proposals: list[DiversityScores]

class DiversityArchiveResult(BaseModel):
    """Output of the MAP-Elites selection."""
    selected_names: list[str] = Field(
        description="Architecture names of proposals selected for the next stage"
    )
    grid_coverage: str = Field(
        description="Summary of how many cells are occupied and the spread across dimensions"
    )
    dropped_names: list[str] = Field(
        description="Architecture names that were not selected (too similar to a better candidate)"
    )
    dropped_reasons: dict[str, str] = Field(
        description="For each dropped name, why it was dropped "
                    "(e.g., 'outperformed by X in the same grid cell')")
```

### Diversity Scorer Prompt

```
You are a diversity analyst for architectural proposals. Your job is to characterize each proposal along 3 behavioral dimensions so that a MAP-Elites diversity selection algorithm can choose the most diverse set of candidates.

For each proposal, score:

1. PARADIGM NOVELTY (1-5):
   1 = Incremental improvement on conventional patterns (e.g., better ETL orchestration)
   2 = Novel combination of known patterns (e.g., streaming + event sourcing hybrid)
   3 = Significant departure from convention (e.g., replacing orchestration with choreography)
   4 = Applying a paradigm from outside data engineering (e.g., market-based scheduling)
   5 = Completely new abstraction that redefines the problem space

2. STRUCTURAL COMPLEXITY (1-5):
   1 = Minimal/elegant: 3-4 core components
   2 = Simple: 5-7 components
   3 = Moderate: 8-12 components
   4 = Complex: 13-18 components
   5 = Highly complex: 19+ components or deeply nested subsystems

3. MIGRATION DISTANCE (1-5):
   1 = Small configuration/tooling changes to existing architecture
   2 = Swap some components while keeping overall structure
   3 = Significant rearchitecture of data flows and processing model
   4 = Major rebuild affecting most components
   5 = Complete greenfield — share almost nothing with current system

Also provide a QUALITY HEURISTIC (0-10): how coherent, complete, and well-argued is the proposal? This is used to choose between proposals that land in the same grid cell.

Be consistent in your scoring. Two proposals that are structurally similar should get similar scores.
```

### MAP-Elites Selection Algorithm

This part is **pure Python, not an LLM call**. After the LLM scores all proposals, the selection is deterministic:

```python
# stages/diversity_archive.py

async def run_diversity_archive(
    proposals: list[Proposal | MutatedProposal],
    starred_names: set[str],
    top_k: int,
) -> list[Proposal | MutatedProposal]:
    """
    1. Score all proposals on 3 behavioral dimensions via LLM.
    2. Place them in a 5x5x5 MAP-Elites grid.
    3. Keep only the best (by quality_heuristic) in each occupied cell.
    4. Select top-K most diverse candidates.
    5. Always include starred proposals.
    """

    # Step 1: Score all proposals
    serialized = "\n\n---\n\n".join(
        f"Proposal: {p.architecture_name}\n{p.model_dump_json(indent=2)}"
        for p in proposals
    )

    scores = await call_llm(
        system_prompt=DIVERSITY_SCORER_PROMPT,
        user_message=f"Score the following {len(proposals)} proposals:\n\n{serialized}",
        response_model=DiversityArchiveInput,
        temperature=0.2,  # Very low — scoring should be consistent
    )

    # Step 2-3: Build grid, keep best per cell
    grid: dict[tuple[int,int,int], DiversityScores] = {}
    for ds in scores.proposals:
        cell = (ds.paradigm_novelty, ds.structural_complexity, ds.migration_distance)
        if cell not in grid or ds.quality_heuristic > grid[cell].quality_heuristic:
            grid[cell] = ds

    # Step 4: Select top-K from unique cells, prioritizing diversity
    # Sort cells to maximize spread: prefer cells that are far from already-selected cells
    selected_names = set()
    remaining_cells = list(grid.items())

    # Always include starred proposals first
    for name in starred_names:
        matching = [ds for ds in scores.proposals if ds.architecture_name == name]
        if matching:
            selected_names.add(name)

    # Greedy diverse selection: pick the cell farthest from all already-selected cells
    selected_cells = []
    while len(selected_names) < top_k and remaining_cells:
        if not selected_cells:
            # First pick: highest quality among highest novelty
            remaining_cells.sort(key=lambda x: (-x[0][0], -x[1].quality_heuristic))
            best = remaining_cells.pop(0)
        else:
            # Subsequent picks: maximize minimum distance to all selected cells
            def min_distance(cell):
                return min(
                    sum((a - b) ** 2 for a, b in zip(cell, sc)) ** 0.5
                    for sc in selected_cells
                )
            remaining_cells.sort(key=lambda x: -min_distance(x[0]))
            best = remaining_cells.pop(0)

        selected_cells.append(best[0])
        selected_names.add(best[1].architecture_name)

    # Step 5: Filter original proposals to only selected names
    selected_proposals = [p for p in proposals if p.architecture_name in selected_names]

    # Log what was dropped and why
    dropped = [p for p in proposals if p.architecture_name not in selected_names]
    if dropped:
        print(f"  Diversity Archive: selected {len(selected_proposals)}, "
              f"dropped {len(dropped)} similar candidates")
        for d in dropped:
            print(f"    Dropped: {d.architecture_name}")

    return selected_proposals
```

### Config Addition

```yaml
pipeline:
  diversity_archive:
    enabled: true
    top_k: 10            # Max proposals to advance to refinement
    temperature: 0.2     # Low — scoring should be consistent
```

### Integration Point

In `main.py`, add after Stage 2 / Checkpoint B and before Stage 3:

```python
    # ── NEW: Stage 2.5 — Diversity Archive (MAP-Elites) ──
    if config.pipeline.diversity_archive.enabled:
        print("Stage 2.5: Running diversity archive (MAP-Elites selection)...")
        starred_names = {s.architecture_name for fb in feedback_history for s in fb.stars}
        diverse_proposals = await run_diversity_archive(
            proposals_after_b,
            starred_names=starred_names,
            top_k=config.pipeline.diversity_archive.top_k,
        )
        print(f"  → Selected {len(diverse_proposals)} diverse candidates from {len(proposals_after_b)}")
    else:
        diverse_proposals = proposals_after_b

    # ── Stage 3: Self-Refinement (EXISTING — now receives diverse_proposals) ──
    refined_proposals = await run_self_refinement(diverse_proposals, ...)
```

---

## NEW Component 4: Structured Debate (Stage 4.5)

### Purpose

After proposals have been self-refined (Stage 3) and annotated by the physics critic (Stage 4), the surviving candidates are well-developed and reality-checked. NOW is the right time for debate — not to generate ideas (that happened in Stages 1-2), but to **stress-test them from multiple angles, surface hidden weaknesses, and strengthen the strongest proposals**.

The debate is structured asymmetrically to **favor innovation over the status quo**:
- Each proposal gets a dedicated **advocate agent** that argues FOR it
- A **devil's advocate** argues against the CONVENTIONAL/status quo approach (not against the novel proposals)
- **Steel-manning is mandatory** — before any agent can critique a proposal, it must first articulate the strongest version of the argument FOR that proposal
- A **judge agent** evaluates the debate and produces structured scores

### How it works

For each proposal, a 3-round debate runs:

```
Round 1: ADVOCATE presents the case for the proposal
         DEVIL'S ADVOCATE presents the case AGAINST the status quo
         (establishes that the current approach has real problems)

Round 2: CROSS-EXAMINATION
         ADVOCATE addresses the physics critic annotations + known risks
         DEVIL'S ADVOCATE argues why the proposal's approach to these risks
         is superior to how the status quo handles similar challenges

Round 3: STEEL-MAN + FINAL ARGUMENTS
         Both agents must steel-man the OTHER side first (mandatory)
         Then present their final argument
```

The JUDGE agent reads the full debate transcript and produces scores.

### Why this structure protects innovation

1. **The devil's advocate attacks the status quo, not the proposal.** This inverts the normal debate dynamic where novel ideas face asymmetric burden of proof.
2. **Steel-manning is mandatory.** This forces the debate to find genuine merit in radical proposals, even if the agent's instinct is to dismiss them.
3. **The debate CANNOT eliminate proposals.** It produces annotations and scores that feed into Portfolio Assembly. No proposal is killed by losing a debate.
4. **The advocate is specifically primed to defend innovation.** Its job is to make the proposal look as strong as possible, not to be balanced.

### Pydantic Schemas

```python
class DebateRound(BaseModel):
    """A single round of debate."""
    round_number: int
    advocate_argument: str = Field(description="The advocate's argument FOR the proposal")
    devil_advocate_argument: str = Field(
        description="The devil's advocate's argument AGAINST the status quo"
    )

class SteelMan(BaseModel):
    """Mandatory steel-man of the opposing position."""
    agent_role: str = Field(description="'advocate' or 'devil_advocate'")
    steel_man_of_opposition: str = Field(
        description="The strongest possible version of the OTHER side's argument, "
                    "presented honestly and charitably"
    )
    final_argument: str = Field(description="The agent's final argument after steel-manning")

class DebateJudgment(BaseModel):
    """The judge's evaluation of the debate."""
    architecture_name: str
    innovation_defense_strength: float = Field(
        ge=0, le=10,
        description="How well the advocate defended the innovative aspects (0-10)"
    )
    status_quo_weakness_exposed: float = Field(
        ge=0, le=10,
        description="How effectively the devil's advocate exposed status quo problems (0-10)"
    )
    risk_mitigation_quality: float = Field(
        ge=0, le=10,
        description="How well the advocate addressed physics critic annotations and risks (0-10)"
    )
    debate_winner: str = Field(
        description="'innovation' or 'status_quo' — who made the stronger overall case"
    )
    key_insight: str = Field(
        description="The single most important insight that emerged from this debate"
    )
    residual_concerns: list[str] = Field(
        description="Concerns that were NOT adequately addressed during the debate"
    )

class DebateResult(BaseModel):
    """Full debate record for a single proposal."""
    architecture_name: str
    rounds: list[DebateRound]
    steel_mans: list[SteelMan]
    judgment: DebateJudgment
```

### Agent Prompts

**Advocate Agent:**
```
You are a passionate advocate for an architectural proposal. Your job is to make the STRONGEST possible case for this architecture.

In Round 1: Present the core value proposition. Why is this architecture transformative? What does it enable that the current approach cannot?

In Round 2: Address the physics critic annotations and known risks head-on. For each concern, explain either why it's manageable, why the benefits outweigh the risk, or how the architecture can be adapted to mitigate it. Do NOT dismiss concerns — engage with them seriously and show how they can be solved.

In Round 3 (Steel-Man): First, honestly articulate the strongest possible argument AGAINST your proposal (the steel-man). Then present your final argument explaining why, even accounting for those concerns, this architecture is the right choice.

Rules:
- Be specific and technical, not hand-wavy
- Reference concrete components and data flows from the proposal
- Acknowledge genuine weaknesses honestly — your credibility depends on it
- Your goal is to ensure the best version of this proposal is what gets judged
```

**Devil's Advocate Agent:**
```
You are a devil's advocate whose target is the STATUS QUO / conventional approach — NOT the innovative proposal. Your job is to expose why the current or conventional architecture is problematic and why change is needed.

In Round 1: Attack the status quo. What are its fundamental structural weaknesses? What problems will get worse over time? What is it preventing the organization from achieving?

In Round 2: When the advocate addresses risks in their proposal, argue why the STATUS QUO has WORSE versions of similar risks that are simply normalized. Example: "Yes, the new architecture has eventual consistency challenges, but the current architecture has silent data corruption that nobody detects for weeks — which is worse?"

In Round 3 (Steel-Man): First, honestly articulate the strongest possible argument FOR the status quo (the steel-man). Then present your final argument for why change is still necessary.

Rules:
- You are NOT attacking the innovative proposal — you are attacking the status quo
- Be honest about genuine strengths of the status quo in your steel-man
- Your purpose is to ensure the debate doesn't default to "just keep what we have"
- Use specific examples from the enterprise context about where the current approach fails
```

**Judge Agent:**
```
You are an impartial judge evaluating a structured debate about an architectural proposal.

You will receive:
1. The proposal itself (with physics critic annotations)
2. The full 3-round debate transcript
3. Both sides' steel-man arguments

Evaluate:
- INNOVATION DEFENSE STRENGTH (0-10): How well did the advocate make the case for innovation? Were the arguments specific and convincing, or vague and hand-wavy?
- STATUS QUO WEAKNESS EXPOSED (0-10): How effectively did the devil's advocate show that the current approach has real problems?
- RISK MITIGATION QUALITY (0-10): How well were the physics critic's concerns and known risks addressed?
- DEBATE WINNER: Overall, did the debate strengthen the case for the innovative proposal ("innovation") or reveal that the status quo is actually adequate ("status_quo")?

Also identify:
- The KEY INSIGHT: What is the single most important thing that emerged from this debate that wasn't obvious before?
- RESIDUAL CONCERNS: What important concerns were NOT adequately addressed?

Be fair but lean toward giving innovative proposals the benefit of the doubt when the debate is close. The system is designed for innovation — a tie goes to the novel approach.
```

### Implementation

```python
# stages/structured_debate.py

async def run_debate_for_proposal(
    annotated_proposal: AnnotatedProposal,
    enterprise_context: str,
) -> DebateResult:
    """Run a 3-round structured debate for a single proposal."""

    proposal_text = annotated_proposal.model_dump_json(indent=2)

    # Round 1: Opening arguments
    advocate_r1 = await call_llm(
        system_prompt=ADVOCATE_PROMPT,
        user_message=(
            f"Round 1: Present your opening case for this proposal.\n\n"
            f"Proposal:\n{proposal_text}\n\n"
            f"Enterprise context:\n{enterprise_context}"
        ),
        response_model=ArgumentText,  # Simple model: just a 'text' field
        temperature=0.6,
    )

    devil_r1 = await call_llm(
        system_prompt=DEVIL_ADVOCATE_PROMPT,
        user_message=(
            f"Round 1: Attack the status quo. Here is the current enterprise context "
            f"and the proposal being considered as a replacement.\n\n"
            f"Enterprise context:\n{enterprise_context}\n\n"
            f"Proposal under consideration:\n{proposal_text}"
        ),
        response_model=ArgumentText,
        temperature=0.6,
    )

    # Round 2: Cross-examination
    advocate_r2 = await call_llm(
        system_prompt=ADVOCATE_PROMPT,
        user_message=(
            f"Round 2: Address the physics critic annotations and known risks.\n\n"
            f"Your Round 1 argument:\n{advocate_r1.text}\n\n"
            f"Devil's advocate Round 1 (attacking status quo):\n{devil_r1.text}\n\n"
            f"Physics critic annotations:\n"
            f"{json.dumps([a.model_dump() for a in annotated_proposal.annotations], indent=2)}"
        ),
        response_model=ArgumentText,
        temperature=0.5,
    )

    devil_r2 = await call_llm(
        system_prompt=DEVIL_ADVOCATE_PROMPT,
        user_message=(
            f"Round 2: The advocate has addressed the risks. Now argue why the status quo "
            f"has WORSE versions of similar problems.\n\n"
            f"Advocate's risk mitigation argument:\n{advocate_r2.text}\n\n"
            f"Enterprise context (evidence of status quo problems):\n{enterprise_context}"
        ),
        response_model=ArgumentText,
        temperature=0.5,
    )

    # Round 3: Steel-man + final arguments
    advocate_steel = await call_llm(
        system_prompt=ADVOCATE_PROMPT,
        user_message=(
            f"Round 3: MANDATORY STEEL-MAN. First, present the STRONGEST possible argument "
            f"AGAINST your proposal. Be honest and charitable. Then present your final argument.\n\n"
            f"Full debate so far:\n"
            f"Advocate R1: {advocate_r1.text}\nDevil R1: {devil_r1.text}\n"
            f"Advocate R2: {advocate_r2.text}\nDevil R2: {devil_r2.text}"
        ),
        response_model=SteelMan,
        temperature=0.5,
    )

    devil_steel = await call_llm(
        system_prompt=DEVIL_ADVOCATE_PROMPT,
        user_message=(
            f"Round 3: MANDATORY STEEL-MAN. First, present the STRONGEST possible argument "
            f"FOR the status quo. Be honest and charitable. Then present your final argument "
            f"for why change is still needed.\n\n"
            f"Full debate so far:\n"
            f"Advocate R1: {advocate_r1.text}\nDevil R1: {devil_r1.text}\n"
            f"Advocate R2: {advocate_r2.text}\nDevil R2: {devil_r2.text}"
        ),
        response_model=SteelMan,
        temperature=0.5,
    )

    # Judge evaluates the full transcript
    judgment = await call_llm(
        system_prompt=JUDGE_PROMPT,
        user_message=(
            f"Judge the following debate about this proposal:\n\n"
            f"PROPOSAL:\n{proposal_text}\n\n"
            f"ROUND 1:\n  Advocate: {advocate_r1.text}\n  Devil's Advocate: {devil_r1.text}\n\n"
            f"ROUND 2:\n  Advocate: {advocate_r2.text}\n  Devil's Advocate: {devil_r2.text}\n\n"
            f"ROUND 3 (Steel-mans + Finals):\n"
            f"  Advocate steel-man of opposition: {advocate_steel.steel_man_of_opposition}\n"
            f"  Advocate final: {advocate_steel.final_argument}\n"
            f"  Devil steel-man of status quo: {devil_steel.steel_man_of_opposition}\n"
            f"  Devil final: {devil_steel.final_argument}"
        ),
        response_model=DebateJudgment,
        temperature=0.3,
    )

    return DebateResult(
        architecture_name=annotated_proposal.proposal.architecture_name,
        rounds=[
            DebateRound(round_number=1, advocate_argument=advocate_r1.text, devil_advocate_argument=devil_r1.text),
            DebateRound(round_number=2, advocate_argument=advocate_r2.text, devil_advocate_argument=devil_r2.text),
        ],
        steel_mans=[advocate_steel, devil_steel],
        judgment=judgment,
    )


async def run_structured_debate(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
) -> list[DebateResult]:
    """Run debates for ALL proposals in parallel."""
    tasks = [
        run_debate_for_proposal(ap, enterprise_context)
        for ap in annotated_proposals
    ]
    return await asyncio.gather(*tasks)
```

### Helper Schema

```python
class ArgumentText(BaseModel):
    """Simple wrapper for a debate argument."""
    text: str = Field(description="The argument text")
```

### Config Addition

```yaml
pipeline:
  structured_debate:
    enabled: true
    temperature:
      advocate: 0.6
      devil_advocate: 0.6
      judge: 0.3
    rounds: 3  # Currently fixed at 3, but configurable for future expansion
```

### Integration Point

In `main.py`, add after Checkpoint C and before Domain Critics:

```python
    # ── NEW: Stage 4.5 — Structured Debate ──
    if config.pipeline.structured_debate.enabled:
        print("Stage 4.5: Running structured debates (asymmetric, innovation-favoring)...")
        debate_results = await run_structured_debate(surviving_proposals, enterprise_context)
        debate_won = sum(1 for d in debate_results if d.judgment.debate_winner == "innovation")
        print(f"  → {len(debate_results)} debates complete. Innovation won {debate_won}/{len(debate_results)}")
    else:
        debate_results = []
```

### How Debate Results Feed Into Portfolio Assembly

The debate results are passed to Stage 5 (Portfolio Assembly). The portfolio ranker prompt receives:
- The debate judgment scores as additional scoring signals
- The key insights from each debate
- The residual concerns

Modify the portfolio ranker's user message to include:

```python
    debate_context = ""
    if debate_results:
        for dr in debate_results:
            debate_context += (
                f"\n--- Debate for {dr.architecture_name} ---\n"
                f"Innovation defense: {dr.judgment.innovation_defense_strength}/10\n"
                f"Status quo weakness exposed: {dr.judgment.status_quo_weakness_exposed}/10\n"
                f"Risk mitigation quality: {dr.judgment.risk_mitigation_quality}/10\n"
                f"Winner: {dr.judgment.debate_winner}\n"
                f"Key insight: {dr.judgment.key_insight}\n"
                f"Residual concerns: {', '.join(dr.judgment.residual_concerns)}\n"
            )
```

---

## NEW Component 5: Domain Critics (Stage 4.7)

### Purpose

The physics critic (Stage 4) only checks **hard constraints** — CAP theorem, computational complexity, network physics. It intentionally ignores soft concerns like security posture, cost, organizational readiness, and tooling maturity.

Domain Critics fill this gap. They are a panel of specialized critic agents that evaluate proposals against **soft, domain-specific constraints**. Critically, like the physics critic, they **annotate only — they CANNOT reject or eliminate proposals**.

Domain critics run AFTER the structured debate (Stage 4.5) so that:
1. Proposals have already been stress-tested by debate
2. The debate's risk mitigation arguments provide context for the critics
3. Critics can reference debate insights in their annotations

### The 4 Domain Critics

**Security Critic:**
```
You are a security architect reviewing a data pipeline architecture proposal. Your job is to identify security concerns and suggest mitigations.

Evaluate:
- Data at rest and in transit encryption implications
- Authentication and authorization model for pipeline components
- Data access control and least-privilege adherence
- Sensitive data handling (PII, PHI, financial data)
- Attack surface analysis — new components and interfaces introduced
- Compliance implications (GDPR, HIPAA, SOX, etc. — based on enterprise context)

IMPORTANT:
- You are an ANNOTATOR, not a GATEKEEPER.
- Do NOT reject the proposal. Annotate concerns with severity and suggested mitigations.
- Severity levels: 'info' (noting a consideration), 'warning' (needs attention before deployment), 'critical' (must be addressed for the architecture to be viable)
- Novel security approaches are acceptable. "This is different from what we normally do" is NOT a security concern. "This exposes PII without access control" IS a security concern.
- For each concern, suggest at least one concrete mitigation approach.
```

**Cost Critic:**
```
You are a cloud economics and infrastructure cost analyst reviewing a data pipeline architecture proposal. Your job is to identify cost implications and optimization opportunities.

Evaluate:
- Compute cost implications (always-on vs. serverless vs. scheduled)
- Storage cost implications (data duplication, retention policies, tiering)
- Network/egress cost implications
- Licensing costs for proposed technologies
- Operational cost (team size, skill requirements, on-call burden)
- Total cost of ownership trajectory over 1, 3, and 5 years
- Cost comparison to the current architecture (is this more or less expensive?)

IMPORTANT:
- You are an ANNOTATOR, not a GATEKEEPER.
- "More expensive than current" is NOT automatically a critical concern. If the proposal delivers 10x more value, higher cost may be justified.
- Annotate with severity: 'info' (noting a cost consideration), 'warning' (significant cost increase needs justification), 'critical' (cost is prohibitive or unsustainable)
- For each concern, suggest at least one cost optimization approach.
```

**Organizational Readiness Critic:**
```
You are an organizational change management analyst reviewing a data pipeline architecture proposal. Your job is to assess whether the organization can realistically adopt this architecture.

Evaluate:
- Team skill gap: what new skills would the team need? How significant is the learning curve?
- Hiring implications: does this require hiring specialists that are hard to find?
- Organizational culture fit: does this require a different way of working (e.g., DevOps culture, streaming mindset)?
- Change management burden: how disruptive is the transition?
- Training timeline: how long before the team is productive with the new architecture?
- Vendor/tooling ecosystem: are the proposed technologies well-supported, documented, and actively maintained?

IMPORTANT:
- You are an ANNOTATOR, not a GATEKEEPER.
- "The team doesn't know this technology" is a WARNING, not a rejection. Teams can learn.
- "This technology has 3 GitHub stars and no documentation" is a legitimate concern.
- Severity: 'info', 'warning', 'critical'
- For each concern, suggest mitigation: training programs, phased rollout, hiring plan, etc.
```

**Data Quality Critic:**
```
You are a data quality and data governance specialist reviewing a data pipeline architecture proposal. Your job is to assess data quality implications.

Evaluate:
- Schema evolution strategy: how does the architecture handle schema changes?
- Data validation: where and how is data validated in the pipeline?
- Data lineage: can you trace data from source to consumption?
- Data freshness guarantees: are the SLAs on data freshness achievable?
- Error handling and dead letter strategies: what happens when data is malformed?
- Idempotency and exactly-once processing: where applicable, is this guaranteed?
- Testing strategy: how would this architecture be tested (unit, integration, end-to-end)?

IMPORTANT:
- You are an ANNOTATOR, not a GATEKEEPER.
- Novel data quality approaches (e.g., probabilistic validation, eventual consistency with correction) are valid — evaluate them on merit, not familiarity.
- Severity: 'info', 'warning', 'critical'
```

### Pydantic Schema

```python
class DomainCriticAnnotation(BaseModel):
    """A single annotation from a domain critic."""
    critic_domain: str = Field(
        description="'security', 'cost', 'org_readiness', or 'data_quality'"
    )
    concern: str = Field(description="Description of the concern")
    severity: str = Field(description="'info', 'warning', or 'critical'")
    affected_components: list[str] = Field(description="Which components are affected")
    suggested_mitigation: str = Field(description="Concrete mitigation approach")

class DomainCriticResult(BaseModel):
    """All annotations from a single domain critic for a single proposal."""
    architecture_name: str
    critic_domain: str
    annotations: list[DomainCriticAnnotation]
    overall_assessment: str = Field(
        description="1-2 sentence summary of this domain's assessment"
    )

class AllDomainCriticsResult(BaseModel):
    """Aggregated domain critic results for a single proposal."""
    architecture_name: str
    critic_results: list[DomainCriticResult]
    total_critical: int = Field(description="Count of critical-severity annotations across all critics")
    total_warning: int = Field(description="Count of warning-severity annotations across all critics")
    total_info: int = Field(description="Count of info-severity annotations across all critics")
```

### Implementation

```python
# stages/domain_critics.py

DOMAIN_CRITICS = {
    "security": SECURITY_CRITIC_PROMPT,
    "cost": COST_CRITIC_PROMPT,
    "org_readiness": ORG_READINESS_CRITIC_PROMPT,
    "data_quality": DATA_QUALITY_CRITIC_PROMPT,
}

async def run_domain_critic(
    critic_domain: str,
    critic_prompt: str,
    annotated_proposal: AnnotatedProposal,
    enterprise_context: str,
    debate_result: DebateResult | None,
) -> DomainCriticResult:
    """Run a single domain critic against a single proposal."""

    debate_context = ""
    if debate_result:
        debate_context = (
            f"\n\nDebate context for this proposal:\n"
            f"Key insight: {debate_result.judgment.key_insight}\n"
            f"Residual concerns: {', '.join(debate_result.judgment.residual_concerns)}\n"
            f"Risk mitigation quality: {debate_result.judgment.risk_mitigation_quality}/10"
        )

    return await call_llm(
        system_prompt=critic_prompt,
        user_message=(
            f"Review this architectural proposal:\n\n"
            f"{annotated_proposal.model_dump_json(indent=2)}\n\n"
            f"Enterprise context:\n{enterprise_context}"
            f"{debate_context}"
        ),
        response_model=DomainCriticResult,
        temperature=0.3,
    )


async def run_all_domain_critics(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
    debate_results: list[DebateResult],
) -> dict[str, AllDomainCriticsResult]:
    """Run all 4 domain critics against all proposals in parallel.
    Returns dict mapping architecture_name to aggregated results."""

    # Build debate lookup
    debate_map = {dr.architecture_name: dr for dr in debate_results}

    # Launch all critic × proposal combinations in parallel
    tasks = []
    task_metadata = []  # Track which task belongs to which proposal + critic

    for ap in annotated_proposals:
        for domain, prompt in DOMAIN_CRITICS.items():
            tasks.append(
                run_domain_critic(
                    domain, prompt, ap, enterprise_context,
                    debate_map.get(ap.proposal.architecture_name),
                )
            )
            task_metadata.append(ap.proposal.architecture_name)

    results = await asyncio.gather(*tasks)

    # Aggregate by proposal
    aggregated: dict[str, AllDomainCriticsResult] = {}
    for arch_name, result in zip(task_metadata, results):
        if arch_name not in aggregated:
            aggregated[arch_name] = AllDomainCriticsResult(
                architecture_name=arch_name,
                critic_results=[],
                total_critical=0,
                total_warning=0,
                total_info=0,
            )
        aggregated[arch_name].critic_results.append(result)
        for ann in result.annotations:
            if ann.severity == "critical":
                aggregated[arch_name].total_critical += 1
            elif ann.severity == "warning":
                aggregated[arch_name].total_warning += 1
            else:
                aggregated[arch_name].total_info += 1

    return aggregated
```

### Config Addition

```yaml
pipeline:
  domain_critics:
    enabled: true
    critics: ["security", "cost", "org_readiness", "data_quality"]  # Enable/disable individual critics
    temperature: 0.3
```

### Integration Point

In `main.py`, add after Structured Debate (Stage 4.5) and before Portfolio Assembly (Stage 5):

```python
    # ── NEW: Stage 4.7 — Domain Critics ──
    if config.pipeline.domain_critics.enabled:
        print("Stage 4.7: Running domain critics (annotate-only)...")
        domain_critic_results = await run_all_domain_critics(
            surviving_proposals, enterprise_context, debate_results
        )
        total_annotations = sum(
            r.total_critical + r.total_warning + r.total_info
            for r in domain_critic_results.values()
        )
        print(f"  → {len(domain_critic_results)} proposals reviewed, {total_annotations} annotations total")
    else:
        domain_critic_results = {}
```

---

## Updated main.py Orchestration

Here is the full updated `run_pipeline()` showing where all 5 new components integrate with the existing code. Lines marked `# NEW` are additions — everything else is existing and should not be modified.

```python
async def run_pipeline():
    feedback_history = []

    # ── Pre-fetch context from MCP servers ──
    print("Connecting to MCP servers and gathering enterprise context...")
    enterprise_context = await gather_enterprise_context()
    patterns_context = await gather_patterns_context()
    paradigm_patterns = await gather_paradigm_patterns()       # NEW

    # ── NEW: Stage 0a — Intent Agent ──
    intent_brief = None
    if config.pipeline.intent_agent.enabled:
        print("Stage 0a: Running intent agent...")
        intent_brief = await run_intent_agent(enterprise_context)
        print(f"  → Core objective: {intent_brief.core_objective[:100]}...")
        print(f"  → {len(intent_brief.paradigm_shift_candidates)} paradigm shift candidates identified")

    # ── NEW: Stage 0b — Prompt Enhancement ──
    enriched_prompts = None
    if config.pipeline.prompt_enhancement.enabled and intent_brief:
        print("Stage 0b: Enhancing paradigm agent prompts with intent + patterns...")
        enriched_prompts = await enhance_prompts(intent_brief, paradigm_patterns)
        print(f"  → {len(enriched_prompts)} enriched prompts composed")

    # ── Stage 1: Paradigm Agent Generation (EXISTING) ──
    print("Stage 1: Running 4 paradigm agents in parallel...")
    original_proposals = await run_paradigm_agents(
        enterprise_context, patterns_context,
        enriched_prompts=enriched_prompts,                     # NEW parameter
    )
    print(f"  → Generated {len(original_proposals)} original proposals")

    # ── HITL Checkpoint A (EXISTING) ──
    proposals_after_a, feedback_a = await checkpoint_a(original_proposals)
    feedback_history.append(feedback_a)
    if feedback_a.action == "abort":
        return

    # ── Stage 2: Idea Mutation (EXISTING) ──
    print("Stage 2: Applying mutation operators...")
    mutation_config_overrides = apply_boosts_to_mutation(feedback_history)
    mutated_proposals = await run_mutations(proposals_after_a, boost_overrides=mutation_config_overrides)
    what_if_seeds = [s for fb in feedback_history for s in fb.seeds if s.seed_type == "what_if"]
    if what_if_seeds:
        seed_mutations = await run_seed_mutations(proposals_after_a, what_if_seeds)
        mutated_proposals.extend(seed_mutations)
    all_proposals = proposals_after_a + mutated_proposals
    print(f"  → {len(all_proposals)} total candidates")

    # ── HITL Checkpoint B (EXISTING) ──
    proposals_after_b, feedback_b = await checkpoint_b(all_proposals, feedback_history)
    feedback_history.append(feedback_b)
    if feedback_b.action == "abort":
        return

    # ── NEW: Stage 2.5 — Diversity Archive (MAP-Elites) ──
    if config.pipeline.diversity_archive.enabled:
        print("Stage 2.5: Running diversity archive (MAP-Elites)...")
        starred_names = {s.architecture_name for fb in feedback_history for s in fb.stars}
        diverse_proposals = await run_diversity_archive(
            proposals_after_b,
            starred_names=starred_names,
            top_k=config.pipeline.diversity_archive.top_k,
        )
        print(f"  → Selected {len(diverse_proposals)} diverse candidates from {len(proposals_after_b)}")
    else:
        diverse_proposals = proposals_after_b

    # ── Stage 3: Self-Refinement (EXISTING — now receives diverse_proposals) ──
    print("Stage 3: Running self-refinement...")
    refinement_rounds_overrides = apply_boosts_to_refinement(feedback_history)
    refined_proposals = await run_self_refinement(diverse_proposals, rounds_overrides=refinement_rounds_overrides)
    print(f"  → Refined {len(refined_proposals)} proposals")

    # ── Stage 4: Physics Critic (EXISTING) ──
    print("Stage 4: Running physics critic...")
    annotated_proposals = await run_physics_critic(refined_proposals)
    critical_count = sum(1 for ap in annotated_proposals if ap.hard_constraint_violations > 0)
    print(f"  → {len(annotated_proposals)} annotated, {critical_count} with critical flags")

    # ── HITL Checkpoint C (EXISTING) ──
    surviving_proposals, feedback_c = await checkpoint_c(annotated_proposals, feedback_history)
    feedback_history.append(feedback_c)
    if feedback_c.action == "abort":
        return

    # ── NEW: Stage 4.5 — Structured Debate ──
    debate_results = []
    if config.pipeline.structured_debate.enabled:
        print("Stage 4.5: Running structured debates...")
        debate_results = await run_structured_debate(surviving_proposals, enterprise_context)
        debate_won = sum(1 for d in debate_results if d.judgment.debate_winner == "innovation")
        print(f"  → {debate_won}/{len(debate_results)} debates won by innovation")

    # ── NEW: Stage 4.7 — Domain Critics ──
    domain_critic_results = {}
    if config.pipeline.domain_critics.enabled:
        print("Stage 4.7: Running domain critics...")
        domain_critic_results = await run_all_domain_critics(
            surviving_proposals, enterprise_context, debate_results
        )
        total_anns = sum(r.total_critical + r.total_warning + r.total_info for r in domain_critic_results.values())
        print(f"  → {total_anns} domain annotations across {len(domain_critic_results)} proposals")

    # ── Stage 5: Portfolio Assembly (EXISTING — now receives debate + domain results) ──
    print("Stage 5: Scoring and ranking portfolio...")
    portfolio = await run_portfolio_assembly(
        surviving_proposals,
        enterprise_context,
        human_boosts=[b.architecture_name for fb in feedback_history for b in fb.boosts],
        starred_proposals=[s.architecture_name for fb in feedback_history for s in fb.stars],
        debate_results=debate_results,                  # NEW parameter
        domain_critic_results=domain_critic_results,    # NEW parameter
    )

    # ── HITL Checkpoint D (EXISTING) ──
    final_portfolio = await checkpoint_d(portfolio, enterprise_context, feedback_history)

    # ── Output (EXISTING) ──
    output_dir = config.output.dir
    with open(f"{output_dir}/portfolio.json", "w") as f:
        json.dump(final_portfolio.model_dump(), f, indent=2)
    if config.output.render_markdown_report:
        report = render_portfolio_report(final_portfolio)
        with open(f"{output_dir}/portfolio_report.md", "w") as f:
            f.write(report)
    print(f"\nDone. Portfolio written to {output_dir}/")
```

---

## Updated Project Structure

Add these new files to the existing project. Do NOT modify existing files unless explicitly noted above.

```
innovation_arch_generator/
├── stages/
│   ├── intent_agent.py           # NEW — Stage 0a
│   ├── prompt_enhancement.py     # NEW — Stage 0b
│   ├── diversity_archive.py      # NEW — Stage 2.5
│   ├── structured_debate.py      # NEW — Stage 4.5
│   ├── domain_critics.py         # NEW — Stage 4.7
│   ├── paradigm_agents.py        # EXISTING — minor change: accept enriched_prompts param
│   ├── mutation_engine.py        # EXISTING — no changes
│   ├── self_refinement.py        # EXISTING — no changes
│   ├── physics_critic.py         # EXISTING — no changes
│   └── portfolio_assembly.py     # EXISTING — minor change: accept debate + domain results
├── prompts/
│   ├── intent_agent.py           # NEW
│   ├── diversity_scorer.py       # NEW
│   ├── debate_agents.py          # NEW — advocate, devil's advocate, judge prompts
│   ├── domain_critics.py         # NEW — security, cost, org readiness, data quality
│   ├── paradigm_agents.py        # EXISTING — rename constants to *_TEMPLATE
│   └── ...                       # EXISTING — no changes
├── models/
│   └── schemas.py                # EXISTING — ADD new schemas listed above
├── mcp_client/
│   └── context_gatherer.py       # EXISTING — ADD gather_paradigm_patterns()
└── main.py                       # EXISTING — updated orchestration as shown above
```

---

## Files That Need Modification (Minimal Changes)

These existing files need small, targeted changes:

| File | Change |
|---|---|
| `stages/paradigm_agents.py` | Add `enriched_prompts: dict[str, str] | None = None` parameter. If provided, use enriched prompts instead of static templates. |
| `stages/portfolio_assembly.py` | Add `debate_results` and `domain_critic_results` parameters. Include their data in the portfolio ranker's user message context. |
| `prompts/paradigm_agents.py` | Rename `STREAMING_SYSTEM_PROMPT` → `STREAMING_SYSTEM_PROMPT_TEMPLATE` (and same for all 4 agents). Content stays identical. |
| `models/schemas.py` | Add all new schemas defined in this document (IntentBrief, DiversityScores, DebateResult, DomainCriticAnnotation, etc.) |
| `mcp_client/context_gatherer.py` | Add `gather_paradigm_patterns()` function. |
| `config.yaml` | Add config sections for: `intent_agent`, `prompt_enhancement`, `diversity_archive`, `structured_debate`, `domain_critics`. |
| `main.py` | Update orchestration as shown in the "Updated main.py" section above. |

---

## Full Updated Config Section

Add these blocks to `config.yaml` under `pipeline:`:

```yaml
pipeline:
  # NEW
  intent_agent:
    enabled: true
    temperature: 0.4

  # NEW
  prompt_enhancement:
    enabled: true   # false = agents get static prompts (MVP behavior)

  # EXISTING — unchanged
  paradigm_agents:
    enabled_agents: ["streaming", "event_sourcing", "declarative", "wildcard"]

  # EXISTING — unchanged
  mutation:
    operators_per_proposal: 3
    available_operators: ["invert", "merge", "eliminate", "analogize", "temporalize", "abstract"]

  # NEW
  diversity_archive:
    enabled: true
    top_k: 10
    temperature: 0.2

  # EXISTING — unchanged
  self_refinement:
    rounds: 2

  # NEW
  structured_debate:
    enabled: true
    temperature:
      advocate: 0.6
      devil_advocate: 0.6
      judge: 0.3
    rounds: 3

  # NEW
  domain_critics:
    enabled: true
    critics: ["security", "cost", "org_readiness", "data_quality"]
    temperature: 0.3

  # EXISTING — unchanged
  portfolio:
    score_weights:
      innovation: 0.35
      feasibility: 0.25
      business_alignment: 0.25
      migration_complexity: 0.15
```

---

## LLM Call Budget Estimate

With these additions, the full pipeline makes approximately:

| Stage | LLM Calls | Notes |
|---|---|---|
| 0a: Intent Agent | 1 | Single analytical call |
| 0b: Prompt Enhancement | 0 | Pure Python, no LLM |
| 1: Paradigm Agents | 4 | Parallel |
| 2: Mutation | 8-12 | Parallel |
| 2.5: Diversity Archive | 1 | Single scoring call for all proposals |
| 3: Self-Refinement | 20 (10 proposals × 2 rounds) | Parallel within each round |
| 4: Physics Critic | 10 | Parallel |
| 4.5: Structured Debate | 70 (10 proposals × 7 calls each) | Most expensive stage. 7 calls = 2 advocate + 2 devil + 2 steel-man + 1 judge. Parallel across proposals. |
| 4.7: Domain Critics | 40 (10 proposals × 4 critics) | Parallel |
| 5: Portfolio Assembly | 1 | Single ranking call |
| **Total** | **~155-170** | Most are parallel; wall-clock time dominated by sequential stages |

The structured debate is by far the most expensive new component. If cost is a concern, it can be disabled (`structured_debate.enabled: false`) or limited to top-5 proposals only.

---

## Summary: What's New vs. What's Unchanged

| Component | Status | Purpose |
|---|---|---|
| Intent Agent (0a) | **NEW** | Understands what the user REALLY needs before agents start generating |
| Prompt Enhancement (0b) | **NEW** | Dynamically enriches agent prompts with intent + patterns (no LLM call) |
| Paradigm Agents (1) | Existing, minor param change | Now receives enriched prompts |
| Mutation (2) | Unchanged | |
| Diversity Archive (2.5) | **NEW** | MAP-Elites selection ensures maximum architectural diversity |
| Self-Refinement (3) | Unchanged | |
| Physics Critic (4) | Unchanged | |
| Structured Debate (4.5) | **NEW** | Asymmetric debate that stress-tests proposals while favoring innovation |
| Domain Critics (4.7) | **NEW** | Security, cost, org readiness, data quality — annotate-only |
| Portfolio Assembly (5) | Existing, minor param change | Now receives debate + domain critic results |
| All HITL Checkpoints | Unchanged | |
| MCP Servers | Existing, minor addition | New `gather_paradigm_patterns()` fetcher |
