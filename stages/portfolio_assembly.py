"""Stage 5: Portfolio Assembly & Ranking

Scores each annotated proposal individually across 4 dimensions, assigns them
to tiers, and produces the final ranked portfolio with an executive summary.

Each proposal is scored in its own LLM call (one at a time) to avoid token
overflow. The full output of Stage 4.7 (domain critics) and Stage 4.5
(structured debate) for that proposal is sent as context.
"""

import json
import logging

from llm.client import call_llm
from models.schemas import (
    AnnotatedProposal,
    Portfolio,
    ScoredProposal,
    ProposalScore,
    DebateResult,
    AllDomainCriticsResult,
)
from prompts.portfolio_ranker import PORTFOLIO_RANKER_PROMPT, PORTFOLIO_SUMMARY_PROMPT

logger = logging.getLogger(__name__)


async def _score_single_proposal(
    ap: AnnotatedProposal,
    enterprise_context: str,
    debate_result: DebateResult | None,
    domain_critic_result: AllDomainCriticsResult | None,
    temperature: float,
) -> ProposalScore:
    """Score a single proposal by sending its full context to the LLM."""

    # Build the full proposal context (the complete annotated proposal)
    proposal_json = ap.model_dump_json(indent=2)

    # Build debate context for this specific proposal (from Stage 4.5)
    debate_context = ""
    if debate_result:
        debate_context = (
            f"\n\n## Structured Debate Results for this Proposal\n"
            f"Innovation defense: {debate_result.judgment.innovation_defense_strength}/10\n"
            f"Status quo weakness exposed: {debate_result.judgment.status_quo_weakness_exposed}/10\n"
            f"Risk mitigation quality: {debate_result.judgment.risk_mitigation_quality}/10\n"
            f"Winner: {debate_result.judgment.debate_winner}\n"
            f"Key insight: {debate_result.judgment.key_insight}\n"
            f"Residual concerns: {', '.join(debate_result.judgment.residual_concerns)}\n"
        )
        # Include debate rounds for full context
        for rd in debate_result.rounds:
            debate_context += (
                f"\n  Round {rd.round_number}:\n"
                f"    Advocate: {rd.advocate_argument}\n"
                f"    Devil's Advocate: {rd.devil_advocate_argument}\n"
            )
        for sm in debate_result.steel_mans:
            debate_context += (
                f"\n  Steel-man ({sm.agent_role}):\n"
                f"    Opposition argument: {sm.steel_man_of_opposition}\n"
                f"    Final argument: {sm.final_argument}\n"
            )

    # Build domain critic context for this specific proposal (from Stage 4.7)
    domain_context = ""
    if domain_critic_result:
        domain_context = (
            f"\n\n## Domain Critic Annotations for this Proposal\n"
            f"Critical: {domain_critic_result.total_critical}, "
            f"Warning: {domain_critic_result.total_warning}, "
            f"Info: {domain_critic_result.total_info}\n"
        )
        for cr in domain_critic_result.critic_results:
            domain_context += f"\n[{cr.critic_domain}] {cr.overall_assessment}\n"
            for ann in cr.annotations:
                domain_context += (
                    f"  - [{ann.severity}] {ann.concern} "
                    f"(affects: {', '.join(ann.affected_components)}) "
                    f"mitigation: {ann.suggested_mitigation}\n"
                )

    result = await call_llm(
        system_prompt=PORTFOLIO_RANKER_PROMPT,
        user_message=(
            f"Enterprise context:\n{enterprise_context}\n\n"
            f"Annotated architectural proposal to evaluate:\n{proposal_json}"
            f"{debate_context}"
            f"{domain_context}"
        ),
        response_model=ProposalScore,
        temperature=temperature,
        stage="portfolio_ranker",
        max_retries=2,
    )

    # Ensure the architecture name matches exactly
    result.architecture_name = ap.proposal.architecture_name
    return result


async def run_portfolio_assembly(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
    score_weights: dict[str, float] | None = None,
    temperature: float = 0.3,
    debate_results: list[DebateResult] | None = None,
    domain_critic_results: dict[str, AllDomainCriticsResult] | None = None,
) -> Portfolio:
    """Score, tier, and rank all proposals into a final portfolio.

    Each proposal is scored individually (one LLM call per proposal) to avoid
    token overflow. The full Stage 4.5 and 4.7 output for each proposal is
    sent as context.

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

    # Build lookup maps for debate and domain critic results
    debate_map: dict[str, DebateResult] = {}
    if debate_results:
        debate_map = {dr.architecture_name: dr for dr in debate_results}

    domain_map: dict[str, AllDomainCriticsResult] = {}
    if domain_critic_results:
        domain_map = domain_critic_results  # Already a dict keyed by arch name

    # Score each proposal one at a time
    scored_proposals: list[ScoredProposal] = []
    for ap in annotated_proposals:
        arch_name = ap.proposal.architecture_name
        logger.info(f"Portfolio: Scoring '{arch_name}'...")

        try:
            ps = await _score_single_proposal(
                ap=ap,
                enterprise_context=enterprise_context,
                debate_result=debate_map.get(arch_name),
                domain_critic_result=domain_map.get(arch_name),
                temperature=temperature,
            )

            composite = (
                ps.innovation_score * score_weights["innovation"]
                + ps.feasibility_score * score_weights["feasibility"]
                + ps.business_alignment_score * score_weights["business_alignment"]
                + ps.migration_complexity_score * score_weights["migration_complexity"]
            )

            scored_proposals.append(ScoredProposal(
                proposal=ap,
                innovation_score=ps.innovation_score,
                feasibility_score=ps.feasibility_score,
                business_alignment_score=ps.business_alignment_score,
                migration_complexity_score=ps.migration_complexity_score,
                composite_score=composite,
                tier=ps.tier,
                one_line_summary=ps.one_line_summary,
            ))

            logger.info(
                f"  -> '{arch_name}': innovation={ps.innovation_score}, "
                f"feasibility={ps.feasibility_score}, "
                f"alignment={ps.business_alignment_score}, "
                f"migration={ps.migration_complexity_score}, "
                f"tier={ps.tier}, composite={composite:.2f}"
            )

        except Exception as e:
            logger.error(f"Scoring failed for '{arch_name}': {e}")
            scored_proposals.append(ScoredProposal(
                proposal=ap,
                innovation_score=5.0,
                feasibility_score=5.0,
                business_alignment_score=5.0,
                migration_complexity_score=5.0,
                composite_score=5.0,
                tier="moderate_innovation",
                one_line_summary=f"{arch_name} (scoring failed)",
            ))

    # Sort by composite score descending
    scored_proposals.sort(key=lambda x: x.composite_score, reverse=True)

    # Identify top per tier
    top_conservative = None
    top_moderate = None
    top_radical = None
    for tier_name in ["conservative", "moderate_innovation", "radical"]:
        tier_proposals = [p for p in scored_proposals if p.tier == tier_name]
        top = (
            tier_proposals[0].proposal.proposal.architecture_name
            if tier_proposals
            else None
        )
        if tier_name == "conservative":
            top_conservative = top
        elif tier_name == "moderate_innovation":
            top_moderate = top
        elif tier_name == "radical":
            top_radical = top

    # Generate executive summary with a compact view of all scores
    scores_summary = json.dumps([
        {
            "name": sp.proposal.proposal.architecture_name,
            "innovation": sp.innovation_score,
            "feasibility": sp.feasibility_score,
            "alignment": sp.business_alignment_score,
            "migration": sp.migration_complexity_score,
            "composite": round(sp.composite_score, 2),
            "tier": sp.tier,
            "summary": sp.one_line_summary,
        }
        for sp in scored_proposals
    ], indent=2)

    logger.info("Portfolio: Generating executive summary...")
    try:
        from models.schemas import ExecutiveSummary
        summary_result = await call_llm(
            system_prompt=PORTFOLIO_SUMMARY_PROMPT,
            user_message=(
                f"Here are the scored proposals (ranked by composite score):\n\n"
                f"{scores_summary}\n\n"
                f"Top conservative: {top_conservative}\n"
                f"Top moderate: {top_moderate}\n"
                f"Top radical: {top_radical}"
            ),
            response_model=ExecutiveSummary,
            temperature=temperature,
            stage="portfolio_ranker",
        )
        executive_summary = summary_result.executive_summary
    except Exception as e:
        logger.error(f"Executive summary generation failed: {e}")
        executive_summary = (
            f"Portfolio contains {len(scored_proposals)} proposals across "
            f"{len(set(sp.tier for sp in scored_proposals))} tiers. "
            f"Top-ranked: {scored_proposals[0].proposal.proposal.architecture_name} "
            f"(composite: {scored_proposals[0].composite_score:.2f})."
        )

    portfolio = Portfolio(
        proposals=scored_proposals,
        top_conservative=top_conservative,
        top_moderate=top_moderate,
        top_radical=top_radical,
        executive_summary=executive_summary,
    )

    return portfolio
