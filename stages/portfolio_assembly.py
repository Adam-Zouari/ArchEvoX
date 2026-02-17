"""Stage 5: Portfolio Assembly & Ranking

Scores all annotated proposals across 4 dimensions, assigns them to tiers,
and produces the final ranked portfolio with an executive summary.
"""

import json
import logging

from llm.client import call_llm
from models.schemas import AnnotatedProposal, Portfolio
from prompts.portfolio_ranker import PORTFOLIO_RANKER_PROMPT

logger = logging.getLogger(__name__)


async def run_portfolio_assembly(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
    score_weights: dict[str, float] | None = None,
    temperature: float = 0.3,
) -> Portfolio:
    """Score, tier, and rank all proposals into a final portfolio."""
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

    portfolio = await call_llm(
        system_prompt=PORTFOLIO_RANKER_PROMPT,
        user_message=(
            "Here are the enterprise context and business goals for reference:\n\n"
            f"{enterprise_context}\n\n"
            "Here are all the annotated architectural proposals to evaluate:\n\n"
            f"{proposals_json}"
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
