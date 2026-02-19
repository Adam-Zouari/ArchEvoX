from pydantic import BaseModel, Field
from typing import Optional


# ──────────────────────────────────────────────
# Intent Agent Output (Stage 0a)
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# Core Proposal Schema (used by all stages)
# ──────────────────────────────────────────────

class Component(BaseModel):
    """A single component in the proposed architecture."""
    name: str = Field(description="Component name (e.g., 'Event Router', 'Stream Processor')")
    role: str = Field(description="What this component does in the architecture")
    technology_suggestion: Optional[str] = Field(
        default=None,
        description="Suggested technology or implementation approach",
    )


class DataFlowStep(BaseModel):
    """A single step in the data flow."""
    step_number: int
    from_component: str
    to_component: str
    description: str = Field(description="What data moves and how")
    pattern: str = Field(
        description="e.g., 'push', 'pull', 'pub-sub', 'request-response', 'event-driven'"
    )


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
    data_flow: list[DataFlowStep] = Field(
        description="Step-by-step data flow through the system"
    )
    key_innovations: list[str] = Field(
        description="What is genuinely new or unconventional about this design"
    )
    assumptions: list[str] = Field(
        description="What must be true for this architecture to work"
    )
    risks: list[Risk] = Field(description="Known risks, framed as solvable challenges")
    paradigm_source: str = Field(
        description=(
            "Which paradigm generated this: 'streaming', 'event-sourcing', "
            "'declarative', 'cross-domain', or 'mutation-{operator_name}'"
        )
    )


# ──────────────────────────────────────────────
# Mutation Output (extends Proposal)
# ──────────────────────────────────────────────

class MutatedProposal(Proposal):
    """A proposal that was produced by applying a mutation operator."""
    mutation_applied: str = Field(
        description=(
            "Which mutation operator was applied: "
            "'invert', 'merge', 'eliminate', 'analogize', 'temporalize', 'abstract'"
        )
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
        description=(
            "Category: 'cap_theorem', 'complexity_bounds', 'network_physics', "
            "'consistency_model', 'resource_limits', 'data_integrity'"
        )
    )
    description: str = Field(description="What the concern is")
    severity: str = Field(description="'info', 'warning', or 'critical'")
    affected_components: list[str] = Field(description="Which components are affected")
    suggested_mitigation: Optional[str] = Field(
        default=None,
        description="How the proposal could address this constraint",
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
    composite_score: float = Field(description="Weighted composite of all scores")
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
        default=None,
        description="Architecture name of the top conservative option",
    )
    top_moderate: Optional[str] = Field(
        default=None,
        description="Architecture name of the top moderate innovation option",
    )
    top_radical: Optional[str] = Field(
        default=None,
        description="Architecture name of the top radical option",
    )
    executive_summary: str = Field(
        description=(
            "2-3 paragraph summary of the portfolio, highlighting the "
            "innovation-risk frontier and key tradeoffs between the top options"
        )
    )


# ──────────────────────────────────────────────
# Lightweight LLM-facing scoring schemas
# (The LLM returns ONLY scores; code reassembles full Portfolio)
# ──────────────────────────────────────────────

class ProposalScore(BaseModel):
    """Per-proposal scores returned by the LLM.
    The LLM evaluates one proposal at a time and returns this."""
    architecture_name: str = Field(
        description="Exact architecture name from the input proposals"
    )
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
    tier: str = Field(
        description="'conservative', 'moderate_innovation', or 'radical'"
    )
    one_line_summary: str = Field(
        description="One sentence explaining what makes this proposal distinctive"
    )


class ExecutiveSummary(BaseModel):
    """Executive summary generated after all proposals are scored."""
    executive_summary: str = Field(
        description=(
            "2-3 paragraph summary of the portfolio, highlighting the "
            "innovation-risk frontier and key tradeoffs between the top options"
        )
    )


# ──────────────────────────────────────────────
# Diversity Archive (Stage 2.5) — MAP-Elites
# ──────────────────────────────────────────────

class DiversityScores(BaseModel):
    """MAP-Elites behavioral characterization of a single proposal."""
    architecture_name: str
    paradigm_novelty: int = Field(
        ge=1, le=5,
        description="1=incremental improvement, 2=novel combination of known patterns, "
                    "3=significant departure from convention, 4=new paradigm application, "
                    "5=completely new abstraction or paradigm"
    )
    structural_complexity: int = Field(
        ge=1, le=5,
        description="1=minimal (3-4 components), 2=simple (5-7), 3=moderate (8-12), "
                    "4=complex (13-18), 5=highly complex (19+)"
    )
    migration_distance: int = Field(
        ge=1, le=5,
        description="1=small config changes, 2=swap some components, "
                    "3=significant rearchitecture, 4=major rebuild, 5=complete greenfield"
    )
    quality_heuristic: float = Field(
        description="0-10 overall quality estimate: coherence, completeness, "
                    "and strength of the core thesis"
    )
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
                    "(e.g., 'outperformed by X in the same grid cell')"
    )


# ──────────────────────────────────────────────
# Structured Debate (Stage 4.5)
# ──────────────────────────────────────────────

class ArgumentText(BaseModel):
    """Simple wrapper for a debate argument."""
    text: str = Field(description="The argument text")


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


# ──────────────────────────────────────────────
# Domain Critics (Stage 4.7)
# ──────────────────────────────────────────────

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
