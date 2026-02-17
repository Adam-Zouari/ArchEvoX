"""Stage 5: Portfolio Assembly & Ranking

Scores all annotated proposals across 4 dimensions, assigns them to tiers,
and produces the final ranked portfolio with an executive summary.
"""

import json
import logging

from llm.client import call_llm
from models.schemas import (
    AnnotatedProposal,
    Portfolio,
    DebateResult,
    AllDomainCriticsResult,
)
from prompts.portfolio_ranker import PORTFOLIO_RANKER_PROMPT

logger = logging.getLogger(__name__)


async def run_portfolio_assembly(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
    score_weights: dict[str, float] | None = None,
    temperature: float = 0.3,
    debate_results: list[DebateResult] | None = None,
    domain_critic_results: dict[str, AllDomainCriticsResult] | None = None,
) -> Portfolio:
    """Score, tier, and rank all proposals into a final portfolio.

    Args:
        annotated_proposals: Proposals with physics critic annotations.
        enterprise_context: Full enterprise context string.
        score_weights: Weights for composite score dimensions.
        temperature: LLM temperature for ranking.
        debate_results: Results from Stage 4.5 (structured debate).
        domain_critic_results: Results from Stage 4.7 (domain critics).
    """
    if score_weights is None:
        score_weights = {
            "innovation": 0.35,
            "feasibility": 0.25,
            "business_alignment": 0.25,
            "migration_complexity": 0.15,
        }

    # Serialize all proposals for the ranker
    proposals_json = json.dumps(
        [ap.model_dump() for ap in annotated_proposals],
        indent=2,
    )

    # Build debate context (from Stage 4.5)
    debate_context = ""
    if debate_results:
        debate_context = "\n\n## Structured Debate Results\n"
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

    # Build domain critic context (from Stage 4.7)
    domain_context = ""
    if domain_critic_results:
        domain_context = "\n\n## Domain Critic Annotations\n"
        for arch_name, acr in domain_critic_results.items():
            domain_context += (
                f"\n--- Domain Critics for {arch_name} ---\n"
                f"Critical: {acr.total_critical}, Warning: {acr.total_warning}, "
                f"Info: {acr.total_info}\n"
            )
            for cr in acr.critic_results:
                domain_context += f"  [{cr.critic_domain}] {cr.overall_assessment}\n"

    portfolio = await call_llm(
        system_prompt=PORTFOLIO_RANKER_PROMPT,
        user_message=(
            "Here are the enterprise context and business goals for reference:\n\n"
            f"{enterprise_context}\n\n"
            "Here are all the annotated architectural proposals to evaluate:\n\n"
            f"{proposals_json}"
            f"{debate_context}"
            f"{domain_context}"
        ),
        response_model=Portfolio,
        temperature=temperature,
    )

    # Apply configured score weights to compute composite scores
    for sp in portfolio.proposals:
        sp.composite_score = (
            sp.innovation_score * score_weights["innovation"]
            + sp.feasibility_score * score_weights["feasibility"]
            + sp.business_alignment_score * score_weights["business_alignment"]
            + sp.migration_complexity_score * score_weights["migration_complexity"]
        )

    # Sort by composite score descending
    portfolio.proposals.sort(key=lambda x: x.composite_score, reverse=True)

    # Identify top per tier
    for tier_name in ["conservative", "moderate_innovation", "radical"]:
        tier_proposals = [p for p in portfolio.proposals if p.tier == tier_name]
        top = (
            tier_proposals[0].proposal.proposal.architecture_name
            if tier_proposals
            else None
        )
        if tier_name == "conservative":
            portfolio.top_conservative = top
        elif tier_name == "moderate_innovation":
            portfolio.top_moderate = top
        elif tier_name == "radical":
            portfolio.top_radical = top

    return portfolio
