"""Stage 4.7: Domain Critics

A panel of specialized critic agents that evaluate proposals against
soft, domain-specific constraints. Like the physics critic, they
annotate only — they CANNOT reject or eliminate proposals.

Critics: Security, Cost, Organizational Readiness, Data Quality.
"""

import asyncio
import logging

from llm.client import call_llm
from models.schemas import (
    AnnotatedProposal,
    DebateResult,
    DomainCriticResult,
    AllDomainCriticsResult,
)
from prompts.domain_critics import DOMAIN_CRITIC_PROMPTS

logger = logging.getLogger(__name__)


async def run_domain_critic(
    critic_domain: str,
    critic_prompt: str,
    annotated_proposal: AnnotatedProposal,
    enterprise_context: str,
    debate_result: DebateResult | None = None,
    temperature: float = 0.3,
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

    result = await call_llm(
        system_prompt=critic_prompt,
        user_message=(
            f"Review this architectural proposal:\n\n"
            f"{annotated_proposal.model_dump_json(indent=2)}\n\n"
            f"Enterprise context:\n{enterprise_context}"
            f"{debate_context}"
        ),
        response_model=DomainCriticResult,
        temperature=temperature,
        stage="domain_critics",
    )

    # Ensure fields are set correctly
    result.architecture_name = annotated_proposal.proposal.architecture_name
    result.critic_domain = critic_domain

    return result


async def run_all_domain_critics(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
    debate_results: list[DebateResult] | None = None,
    enabled_critics: list[str] | None = None,
    temperature: float = 0.3,
) -> dict[str, AllDomainCriticsResult]:
    """Run all enabled domain critics against all proposals in parallel.

    Args:
        annotated_proposals: Proposals annotated by the physics critic.
        enterprise_context: Full enterprise context string.
        debate_results: Results from structured debate (Stage 4.5).
        enabled_critics: List of critic domains to run. Defaults to all.
        temperature: LLM temperature for critics.

    Returns:
        Dict mapping architecture_name to aggregated results.
    """
    if debate_results is None:
        debate_results = []

    if enabled_critics is None:
        enabled_critics = list(DOMAIN_CRITIC_PROMPTS.keys())

    # Build debate lookup
    debate_map = {dr.architecture_name: dr for dr in debate_results}

    # Launch all critic × proposal combinations in parallel
    tasks = []
    task_metadata: list[str] = []  # Track which proposal each task belongs to

    for ap in annotated_proposals:
        arch_name = ap.proposal.architecture_name
        for domain in enabled_critics:
            prompt = DOMAIN_CRITIC_PROMPTS.get(domain)
            if prompt is None:
                logger.warning(f"Unknown domain critic '{domain}', skipping.")
                continue
            tasks.append(
                run_domain_critic(
                    critic_domain=domain,
                    critic_prompt=prompt,
                    annotated_proposal=ap,
                    enterprise_context=enterprise_context,
                    debate_result=debate_map.get(arch_name),
                    temperature=temperature,
                )
            )
            task_metadata.append(arch_name)

    logger.info(
        f"Domain Critics: Running {len(tasks)} evaluations "
        f"({len(annotated_proposals)} proposals × {len(enabled_critics)} critics)..."
    )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Aggregate by proposal
    aggregated: dict[str, AllDomainCriticsResult] = {}
    for arch_name, result in zip(task_metadata, results):
        if isinstance(result, Exception):
            logger.error(f"Domain critic failed for '{arch_name}': {result}")
            continue

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

    total_annotations = sum(
        r.total_critical + r.total_warning + r.total_info
        for r in aggregated.values()
    )
    logger.info(
        f"Domain Critics: {len(aggregated)} proposals reviewed, "
        f"{total_annotations} total annotations."
    )

    return aggregated
