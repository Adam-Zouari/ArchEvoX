from pydantic import BaseModel, Field
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
