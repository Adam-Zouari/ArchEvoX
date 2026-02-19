# Pipeline Stages — Detailed Input/Output Reference

This document describes exactly what each pipeline stage takes as input, what it produces as output, and the data structures involved.

---

## Pre-Pipeline: Context Gathering

Before any stage runs, the pipeline pre-fetches all enterprise context from disk.

| Function | Returns |
|----------|---------|
| `gather_enterprise_context(config)` | `str` — All enterprise docs + metadata concatenated (markdown sections separated by `---`) |
| `gather_patterns_context(config)` | `str` — Emerging, streaming, and event sourcing patterns from the knowledge base |
| `gather_paradigm_patterns(config)` | `dict[str, str]` — Maps each paradigm agent name to its relevant knowledge base patterns |

**Sources read:**
- `input/enterprise_docs/*.md` (architecture, business_goals, constraints, team, pain_points)
- `input/metadata/*.json, *.yaml` (schema_inventory, infrastructure_catalog, pipeline_definitions, volume_stats)
- `knowledge_base/*.md` (streaming_patterns, event_sourcing_patterns, declarative_patterns, biological/economic/physical/social_analogies, emerging_patterns, anti_patterns)

---

## Stage 0a — Intent Agent

**File:** `stages/intent_agent.py`
**LLM calls:** 1
**Can be disabled:** Yes (`pipeline.intent_agent.enabled: false`)

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `enterprise_context` | `str` | Pre-fetched enterprise docs + metadata |
| `temperature` | `float` | `pipeline.intent_agent.temperature` (default: 0.4) |

### Output

**`IntentBrief`** — A structured analysis of what the enterprise actually needs.

| Field | Type | Description |
|-------|------|-------------|
| `core_objective` | `str` | The deepest, most fundamental objective (2-3 sentences) |
| `pain_diagnosis` | `list[str]` | Root cause diagnoses (not symptoms) |
| `implicit_constraints` | `list[str]` | Constraints that exist but aren't documented |
| `innovation_opportunity_map` | `list[InnovationOpportunity]` | Where innovation has the highest leverage |
| `paradigm_shift_candidates` | `list[ParadigmShiftCandidate]` | Specific shifts ranked by transformative potential |
| `anti_goals` | `list[str]` | What proposals should NOT do |
| `success_criteria` | `list[str]` | How the user would judge success |
| `key_context_for_agents` | `str` | 2-3 paragraph executive briefing injected into downstream prompts |

**Nested types:**

`InnovationOpportunity`:
| Field | Type | Description |
|-------|------|-------------|
| `area` | `str` | Area of the architecture |
| `current_state` | `str` | What it looks like now and why it's limiting |
| `opportunity` | `str` | What innovation could unlock |
| `priority` | `str` | `"high"`, `"medium"`, or `"low"` |

`ParadigmShiftCandidate`:
| Field | Type | Description |
|-------|------|-------------|
| `paradigm` | `str` | The paradigm shift (e.g., `"batch-to-streaming"`) |
| `target_area` | `str` | Which part of the architecture this applies to |
| `rationale` | `str` | Why this shift would be transformative |
| `leverage_score` | `int` | 1-10: impact relative to effort |

### Downstream consumers
- Stage 0b (Prompt Enhancement)

---

## Stage 0b — Prompt Enhancement

**File:** `stages/prompt_enhancement.py`
**LLM calls:** 0 (pure Python string composition)
**Can be disabled:** Yes (`pipeline.prompt_enhancement.enabled: false`)
**Requires:** Stage 0a must have produced an `IntentBrief`

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `intent_brief` | `IntentBrief` | Output of Stage 0a |
| `patterns_context` | `dict[str, str]` | From `gather_paradigm_patterns()` — maps agent name to knowledge base patterns |

### Output

**`dict[str, str]`** — Maps each paradigm agent name to its enriched system prompt.

Keys: `"streaming"`, `"event_sourcing"`, `"declarative"`, `"wildcard"`

Each enriched prompt is composed of:
1. The original static paradigm agent prompt template
2. Situation briefing from `intent_brief.key_context_for_agents`
3. Core objective from `intent_brief.core_objective`
4. Anti-goals from `intent_brief.anti_goals`
5. Success criteria from `intent_brief.success_criteria`
6. Innovation opportunity map from `intent_brief.innovation_opportunity_map`
7. Paradigm shift candidates (sorted by leverage score descending)
8. Paradigm-specific patterns from knowledge base
9. Implicit constraints from `intent_brief.implicit_constraints`

### Downstream consumers
- Stage 1 (Paradigm Agents) — uses enriched prompts instead of static templates

---

## Stage 1 — Paradigm Agent Generation

**File:** `stages/paradigm_agents.py`
**LLM calls:** 4 (one per agent, run sequentially)
**Always enabled**

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `enterprise_context` | `str` | Pre-fetched enterprise docs + metadata |
| `patterns_context` | `str` | Pre-fetched knowledge base patterns |
| `enabled_agents` | `list[str]` | `pipeline.paradigm_agents.enabled_agents` (default: `["streaming", "event_sourcing", "declarative", "wildcard"]`) |
| `temperature` | `float` | `llm.temperature.paradigm_agents` (default: 0.9) |
| `enriched_prompts` | `dict[str, str] | None` | Output of Stage 0b (if enabled) |

### Output

**`list[Proposal]`** — Typically 4 proposals, one per agent.

`Proposal`:
| Field | Type | Description |
|-------|------|-------------|
| `architecture_name` | `str` | Distinctive name for this architecture |
| `core_thesis` | `str` | 1-2 sentence foundational principle |
| `components` | `list[Component]` | All components in the architecture |
| `data_flow` | `list[DataFlowStep]` | Step-by-step data flow through the system |
| `key_innovations` | `list[str]` | What is genuinely new or unconventional |
| `assumptions` | `list[str]` | What must be true for this to work |
| `risks` | `list[Risk]` | Known risks, framed as solvable challenges |
| `paradigm_source` | `str` | Set to the agent name: `"streaming"`, `"event_sourcing"`, `"declarative"`, or `"wildcard"` |

**Nested types:**

`Component`:
| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Component name (e.g., "Event Router") |
| `role` | `str` | What this component does |
| `technology_suggestion` | `str | None` | Suggested technology |

`DataFlowStep`:
| Field | Type | Description |
|-------|------|-------------|
| `step_number` | `int` | Sequence number |
| `from_component` | `str` | Source component |
| `to_component` | `str` | Destination component |
| `description` | `str` | What data moves and how |
| `pattern` | `str` | e.g., `"push"`, `"pull"`, `"pub-sub"`, `"event-driven"` |

`Risk`:
| Field | Type | Description |
|-------|------|-------------|
| `description` | `str` | Risk description |
| `severity` | `str` | `"low"`, `"medium"`, or `"high"` |
| `mitigation` | `str` | How this risk could be addressed |

### Error handling
- If an agent fails, it is skipped and the pipeline continues with fewer proposals.
- If ALL agents fail (0 proposals), the pipeline aborts.

### Downstream consumers
- Stage 2 (Mutation Engine)

---

## Stage 2 — Mutation Engine

**File:** `stages/mutation_engine.py`
**LLM calls:** `len(proposals) × operators_per_proposal` (run sequentially)
**Always enabled**

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `proposals` | `list[Proposal]` | Output of Stage 1 |
| `operators_per_proposal` | `int` | `pipeline.mutation.operators_per_proposal` (default: 3) |
| `available_operators` | `list[str]` | `pipeline.mutation.available_operators` (default: `["invert", "merge", "eliminate", "analogize", "temporalize", "abstract"]`) |
| `temperature` | `float` | `llm.temperature.mutation_engine` (default: 0.85) |

### Output

**`list[MutatedProposal]`** — Mutated variants. Combined with originals in `main.py` as `all_proposals = originals + mutated`.

`MutatedProposal` extends `Proposal` with:
| Field | Type | Description |
|-------|------|-------------|
| *(all Proposal fields)* | | Inherited |
| `mutation_applied` | `str` | Which operator: `"invert"`, `"merge"`, `"eliminate"`, `"analogize"`, `"temporalize"`, `"abstract"` |
| `mutation_description` | `str` | What specifically was changed and why |
| `parent_architecture_name` | `str` | Name of the original proposal this was mutated from |
| `paradigm_source` | `str` | Set to `"mutation-{operator_name}"` |

### How operators are selected
For each proposal, `operators_per_proposal` operators are randomly sampled from `available_operators` (without replacement).

### Expected output count
- With 4 proposals and `operators_per_proposal: 3` → up to 12 mutations
- With 4 proposals and `operators_per_proposal: 1` → up to 4 mutations
- Total candidates after Stage 2 = original proposals + mutations

### Error handling
- If a mutation fails, it is skipped. The pipeline continues.

### Downstream consumers
- Stage 2.5 (Diversity Archive) or Stage 3 (Self-Refinement) if diversity is disabled

---

## Stage 2.5 — Diversity Archive (MAP-Elites)

**File:** `stages/diversity_archive.py`
**LLM calls:** 1 (one batch call to characterize all proposals)
**Can be disabled:** Yes (`pipeline.diversity_archive.enabled: false`)

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `proposals` | `list[Proposal | MutatedProposal]` | `all_proposals` from main.py (originals + mutations) |
| `starred_names` | `set[str] | None` | Always `set()` in automated pipeline (reserved for future HITL) |
| `top_k` | `int` | `pipeline.diversity_archive.top_k` (default: 10) |
| `temperature` | `float` | `pipeline.diversity_archive.temperature` (default: 0.2) |

### Internal LLM output

The LLM returns **`DiversityArchiveInput`** containing a list of `DiversityScores`, one per proposal.

`DiversityScores`:
| Field | Type | Description |
|-------|------|-------------|
| `architecture_name` | `str` | Proposal name |
| `paradigm_novelty` | `int (1-5)` | 1=incremental → 5=completely new paradigm |
| `structural_complexity` | `int (1-5)` | 1=minimal (3-4 components) → 5=highly complex (19+) |
| `migration_distance` | `int (1-5)` | 1=small config changes → 5=complete greenfield |
| `quality_heuristic` | `float (0-10)` | Overall quality estimate |
| `one_line_summary` | `str` | Summary |

### Algorithm
1. LLM scores each proposal on 3 dimensions → places in a 5×5×5 grid (125 cells)
2. If multiple proposals land in the same cell, only the one with the highest `quality_heuristic` survives
3. Greedy diverse selection: iteratively picks the cell farthest from all already-selected cells
4. Stops at `top_k` selections

### Output

**`list[Proposal | MutatedProposal]`** — The diverse subset of proposals (at most `top_k`).

If the input count ≤ `top_k`, all proposals pass through unchanged.

### Downstream consumers
- Stage 3 (Self-Refinement)

---

## Stage 3 — Self-Refinement

**File:** `stages/self_refinement.py`
**LLM calls:** `len(proposals) × rounds` (run sequentially)
**Always enabled**

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `proposals` | `list[Proposal | MutatedProposal]` | Output of Stage 2.5 (or Stage 2 if diversity is disabled) |
| `rounds` | `int` | `pipeline.self_refinement.rounds` (default: 2) |
| `temperature` | `float` | `llm.temperature.self_refinement` (default: 0.5) |

### Output

**`list[RefinedProposal]`** — Same proposals, strengthened without being made more conservative.

`RefinedProposal` extends `Proposal` with:
| Field | Type | Description |
|-------|------|-------------|
| *(all Proposal fields)* | | Inherited (but may be modified by the LLM during refinement) |
| `refinements_made` | `list[str]` | List of specific improvements made in this round |
| `refinement_round` | `int` | Which round of refinement (1 or 2) |

### Multi-round behavior
- Round 1 output becomes Round 2 input
- After N rounds, only the final round's `RefinedProposal` objects continue

### Error handling
- If refinement fails for a proposal, it is wrapped as a `RefinedProposal` with `refinements_made: ["[Refinement round N failed]"]` and continues unchanged.

### Downstream consumers
- Stage 4 (Physics Critic)

---

## Stage 4 — Physics Critic

**File:** `stages/physics_critic.py`
**LLM calls:** `len(proposals)` (run sequentially)
**Always enabled**
**Annotates only — never rejects a proposal**

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `proposals` | `list[RefinedProposal]` | Output of Stage 3 |
| `temperature` | `float` | `llm.temperature.physics_critic` (default: 0.3) |

### Output

**`list[AnnotatedProposal]`** — Same proposals with physics annotations attached as metadata.

`AnnotatedProposal`:
| Field | Type | Description |
|-------|------|-------------|
| `proposal` | `RefinedProposal` | The original proposal (unmodified) |
| `annotations` | `list[ConstraintAnnotation]` | Physics constraint annotations |
| `hard_constraint_violations` | `int` | Count of `"critical"` severity annotations |
| `overall_feasibility_note` | `str` | Brief overall feasibility assessment |

`ConstraintAnnotation`:
| Field | Type | Description |
|-------|------|-------------|
| `constraint_type` | `str` | Category: `"cap_theorem"`, `"complexity_bounds"`, `"network_physics"`, `"consistency_model"`, `"resource_limits"`, `"data_integrity"` |
| `description` | `str` | What the concern is |
| `severity` | `str` | `"info"`, `"warning"`, or `"critical"` |
| `affected_components` | `list[str]` | Which components are affected |
| `suggested_mitigation` | `str | None` | How the proposal could address this |

### Error handling
- If the physics critic fails for a proposal, a fallback `AnnotatedProposal` is created with `annotations: []` and `hard_constraint_violations: 0`.

### Downstream consumers
- Stage 4.5 (Structured Debate)
- Stage 4.7 (Domain Critics)
- Stage 5 (Portfolio Assembly)

---

## Stage 4.5 — Structured Debate

**File:** `stages/structured_debate.py`
**LLM calls:** 7 per proposal (debates run in parallel across proposals)
**Can be disabled:** Yes (`pipeline.structured_debate.enabled: false`)

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `annotated_proposals` | `list[AnnotatedProposal]` | Output of Stage 4 |
| `enterprise_context` | `str` | Pre-fetched enterprise docs + metadata |
| `advocate_temperature` | `float` | `pipeline.structured_debate.temperature.advocate` (default: 0.6) |
| `devil_temperature` | `float` | `pipeline.structured_debate.temperature.devil_advocate` (default: 0.6) |
| `judge_temperature` | `float` | `pipeline.structured_debate.temperature.judge` (default: 0.3) |

### Debate structure per proposal (7 LLM calls)

| Call # | Agent | Round | Input | Output type |
|--------|-------|-------|-------|-------------|
| 1 | Advocate | R1 | Proposal + enterprise context | `ArgumentText` |
| 2 | Devil's Advocate | R1 | Enterprise context + proposal | `ArgumentText` |
| 3 | Advocate | R2 | R1 arguments + physics annotations | `ArgumentText` |
| 4 | Devil's Advocate | R2 | Advocate R1 + enterprise context | `ArgumentText` |
| 5 | Advocate | R3 | Full transcript → steel-man opposition + final | `SteelMan` |
| 6 | Devil's Advocate | R3 | Full transcript → steel-man status quo + final | `SteelMan` |
| 7 | Judge | — | Full transcript (all 6 arguments) | `DebateJudgment` |

Calls 1-2 run in parallel. Calls 3-4 run in parallel. Calls 5-6 run in parallel. Call 7 runs last.

### Output

**`list[DebateResult]`** — One per successfully debated proposal.

`DebateResult`:
| Field | Type | Description |
|-------|------|-------------|
| `architecture_name` | `str` | Proposal name |
| `rounds` | `list[DebateRound]` | 2 entries (R1 and R2) |
| `steel_mans` | `list[SteelMan]` | 2 entries (advocate + devil's advocate) |
| `judgment` | `DebateJudgment` | Judge's final evaluation |

`DebateRound`:
| Field | Type | Description |
|-------|------|-------------|
| `round_number` | `int` | 1 or 2 |
| `advocate_argument` | `str` | Advocate's argument FOR the proposal |
| `devil_advocate_argument` | `str` | Devil's advocate's argument AGAINST the status quo |

`SteelMan`:
| Field | Type | Description |
|-------|------|-------------|
| `agent_role` | `str` | `"advocate"` or `"devil_advocate"` |
| `steel_man_of_opposition` | `str` | Strongest version of the OTHER side's argument |
| `final_argument` | `str` | Agent's final argument after steel-manning |

`DebateJudgment`:
| Field | Type | Description |
|-------|------|-------------|
| `architecture_name` | `str` | Proposal name |
| `innovation_defense_strength` | `float (0-10)` | How well the advocate defended innovation |
| `status_quo_weakness_exposed` | `float (0-10)` | How effectively the devil's advocate exposed status quo problems |
| `risk_mitigation_quality` | `float (0-10)` | How well the advocate addressed risks |
| `debate_winner` | `str` | `"innovation"` or `"status_quo"` |
| `key_insight` | `str` | Most important insight from the debate |
| `residual_concerns` | `list[str]` | Concerns not adequately addressed |

### Error handling
- If a debate fails for a proposal, that proposal's debate result is dropped. The proposal still continues to Stage 5.

### Downstream consumers
- Stage 4.7 (Domain Critics) — debate results provide additional context
- Stage 5 (Portfolio Assembly) — debate scores inform ranking

---

## Stage 4.7 — Domain Critics

**File:** `stages/domain_critics.py`
**LLM calls:** `len(proposals) × len(enabled_critics)` (all run in parallel via `asyncio.gather`)
**Can be disabled:** Yes (`pipeline.domain_critics.enabled: false`)
**Annotates only — never rejects a proposal**

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `annotated_proposals` | `list[AnnotatedProposal]` | Output of Stage 4 |
| `enterprise_context` | `str` | Pre-fetched enterprise docs + metadata |
| `debate_results` | `list[DebateResult] | None` | Output of Stage 4.5 (if enabled) |
| `enabled_critics` | `list[str]` | `pipeline.domain_critics.critics` (default: `["security", "cost", "org_readiness", "data_quality"]`) |
| `temperature` | `float` | `pipeline.domain_critics.temperature` (default: 0.3) |

### Per-critic LLM output

**`DomainCriticResult`** — Annotations from one critic for one proposal.

| Field | Type | Description |
|-------|------|-------------|
| `architecture_name` | `str` | Proposal name |
| `critic_domain` | `str` | `"security"`, `"cost"`, `"org_readiness"`, or `"data_quality"` |
| `annotations` | `list[DomainCriticAnnotation]` | Domain-specific annotations |
| `overall_assessment` | `str` | 1-2 sentence summary |

`DomainCriticAnnotation`:
| Field | Type | Description |
|-------|------|-------------|
| `critic_domain` | `str` | Which critic produced this |
| `concern` | `str` | Description of the concern |
| `severity` | `str` | `"info"`, `"warning"`, or `"critical"` |
| `affected_components` | `list[str]` | Which components are affected |
| `suggested_mitigation` | `str` | Concrete mitigation approach |

### Aggregated output

**`dict[str, AllDomainCriticsResult]`** — Maps `architecture_name` to aggregated results.

`AllDomainCriticsResult`:
| Field | Type | Description |
|-------|------|-------------|
| `architecture_name` | `str` | Proposal name |
| `critic_results` | `list[DomainCriticResult]` | Results from each critic |
| `total_critical` | `int` | Count of critical-severity annotations across all critics |
| `total_warning` | `int` | Count of warning-severity annotations |
| `total_info` | `int` | Count of info-severity annotations |

### Error handling
- If a critic fails for a proposal, that result is skipped. Other critics' results remain.

### Downstream consumers
- Stage 5 (Portfolio Assembly) — domain critic annotations inform ranking

---

## Stage 5 — Portfolio Assembly & Ranking

**File:** `stages/portfolio_assembly.py`
**LLM calls:** 1
**Always enabled**

### Input

| Parameter | Type | Source |
|-----------|------|--------|
| `annotated_proposals` | `list[AnnotatedProposal]` | Output of Stage 4 |
| `enterprise_context` | `str` | Pre-fetched enterprise docs + metadata |
| `score_weights` | `dict[str, float]` | `pipeline.portfolio.score_weights` (default: `{innovation: 0.35, feasibility: 0.25, business_alignment: 0.25, migration_complexity: 0.15}`) |
| `temperature` | `float` | `llm.temperature.portfolio_ranker` (default: 0.3) |
| `debate_results` | `list[DebateResult] | None` | Output of Stage 4.5 (if enabled) |
| `domain_critic_results` | `dict[str, AllDomainCriticsResult] | None` | Output of Stage 4.7 (if enabled) |

### What gets sent to the LLM

A **compact summary** of each proposal (not the full Pydantic dump — to avoid token overflow). Includes:
- `architecture_name`, `core_thesis`, `paradigm_source`
- `components` (name, role, technology)
- `data_flow` (flattened to strings)
- `key_innovations`, `assumptions`, `risks`
- `physics_annotations` (type, severity, description)
- Debate results (if available): scores, winner, key insight, residual concerns
- Domain critic results (if available): totals per severity, per-critic assessments

### LLM output

**`LightweightPortfolio`** — Scores only, no full proposal data.

| Field | Type | Description |
|-------|------|-------------|
| `proposals` | `list[ProposalScore]` | Scores for each proposal |
| `executive_summary` | `str` | 2-3 paragraph portfolio summary |

`ProposalScore`:
| Field | Type | Description |
|-------|------|-------------|
| `architecture_name` | `str` | Exact name from input |
| `innovation_score` | `float (0-10)` | Paradigm novelty and structural innovation |
| `feasibility_score` | `float (0-10)` | Technical feasibility given constraints |
| `business_alignment_score` | `float (0-10)` | Alignment with business goals |
| `migration_complexity_score` | `float (0-10)` | 10 = trivial migration, 1 = complete rebuild |
| `tier` | `str` | `"conservative"` (innovation ≤ 4), `"moderate_innovation"` (5-7), `"radical"` (≥ 8) |
| `one_line_summary` | `str` | What makes this proposal distinctive |

### Reassembly (code, not LLM)

The code matches each `ProposalScore` back to its original `AnnotatedProposal` by `architecture_name`, computes the `composite_score` using the configured weights, and assembles the full `Portfolio`.

### Final output

**`Portfolio`** — Written to `outputs/portfolio.json`.

| Field | Type | Description |
|-------|------|-------------|
| `proposals` | `list[ScoredProposal]` | All proposals, sorted by composite score descending |
| `top_conservative` | `str | None` | Name of the top conservative proposal |
| `top_moderate` | `str | None` | Name of the top moderate innovation proposal |
| `top_radical` | `str | None` | Name of the top radical proposal |
| `executive_summary` | `str` | 2-3 paragraph portfolio summary |

`ScoredProposal`:
| Field | Type | Description |
|-------|------|-------------|
| `proposal` | `AnnotatedProposal` | Full proposal with physics annotations |
| `innovation_score` | `float` | 0-10 |
| `feasibility_score` | `float` | 0-10 |
| `business_alignment_score` | `float` | 0-10 |
| `migration_complexity_score` | `float` | 0-10 |
| `composite_score` | `float` | Weighted sum using `score_weights` |
| `tier` | `str` | `"conservative"`, `"moderate_innovation"`, or `"radical"` |
| `one_line_summary` | `str` | One sentence description |

### Error handling
- If the LLM slightly modifies an `architecture_name`, fuzzy matching is attempted (substring match).
- Any proposals the LLM missed are added with default scores of 5.0 and tier `"moderate_innovation"`.

---

## Output Files

| File | Contents |
|------|----------|
| `outputs/portfolio.json` | Full `Portfolio` as JSON (all proposals with scores) |
| `outputs/portfolio_report.md` | Rendered Jinja2 template with executive summary, frontier table, and full proposal details |
| `outputs/progress.json` | Real-time progress tracker (stage status, proposals, debate/critic results) |

---

## Pipeline Flow Summary

```
enterprise_context (str)  ──────────────────────────────────────────────┐
patterns_context (str)  ────────────────────────────────────────────────┤
paradigm_patterns (dict[str, str])  ────────────────────────────────────┤
                                                                        │
Stage 0a: Intent Agent                                                  │
  Input:  enterprise_context                                            │
  Output: IntentBrief                                                   │
     │                                                                  │
Stage 0b: Prompt Enhancement                                            │
  Input:  IntentBrief + paradigm_patterns                               │
  Output: dict[str, str] (enriched prompts)                             │
     │                                                                  │
Stage 1: Paradigm Agents                                                │
  Input:  enterprise_context + patterns_context + enriched_prompts      │
  Output: list[Proposal]  (4 proposals)                                 │
     │                                                                  │
Stage 2: Mutation Engine                                                │
  Input:  list[Proposal]                                                │
  Output: list[MutatedProposal]                                        │
     │  (combined: originals + mutations = all_proposals)               │
     │                                                                  │
Stage 2.5: Diversity Archive                                            │
  Input:  list[Proposal | MutatedProposal]                              │
  Output: list[Proposal | MutatedProposal]  (diverse subset)            │
     │                                                                  │
Stage 3: Self-Refinement                                                │
  Input:  list[Proposal | MutatedProposal]                              │
  Output: list[RefinedProposal]                                         │
     │                                                                  │
Stage 4: Physics Critic                                                 │
  Input:  list[RefinedProposal]                                         │
  Output: list[AnnotatedProposal]                                       │
     │                                                                  │
Stage 4.5: Structured Debate                                            │
  Input:  list[AnnotatedProposal] + enterprise_context                  │
  Output: list[DebateResult]                                            │
     │                                                                  │
Stage 4.7: Domain Critics                                               │
  Input:  list[AnnotatedProposal] + enterprise_context + debate_results │
  Output: dict[str, AllDomainCriticsResult]                             │
     │                                                                  │
Stage 5: Portfolio Assembly                                             │
  Input:  list[AnnotatedProposal] + enterprise_context                  │
          + debate_results + domain_critic_results                      │
  Output: Portfolio  →  outputs/portfolio.json                          │
                     →  outputs/portfolio_report.md                     │
```
