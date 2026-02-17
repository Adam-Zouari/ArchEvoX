"""Stage 0b: Prompt Enhancement

Dynamically enriches paradigm agent system prompts with:
- Intent Brief context (from Stage 0a)
- Paradigm-specific patterns from the knowledge base
- Anti-goals and success criteria

This is pure Python string composition — NO LLM call required.
"""

import logging

from models.schemas import IntentBrief
from prompts.paradigm_agents import (
    STREAMING_SYSTEM_PROMPT_TEMPLATE,
    EVENT_SOURCING_SYSTEM_PROMPT_TEMPLATE,
    DECLARATIVE_SYSTEM_PROMPT_TEMPLATE,
    WILDCARD_SYSTEM_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)

_PARADIGM_TEMPLATES = {
    "streaming": STREAMING_SYSTEM_PROMPT_TEMPLATE,
    "event_sourcing": EVENT_SOURCING_SYSTEM_PROMPT_TEMPLATE,
    "declarative": DECLARATIVE_SYSTEM_PROMPT_TEMPLATE,
    "wildcard": WILDCARD_SYSTEM_PROMPT_TEMPLATE,
}


async def enhance_prompts(
    intent_brief: IntentBrief,
    patterns_context: dict[str, str],
) -> dict[str, str]:
    """Compose enriched system prompts for each paradigm agent.

    Does NOT call an LLM. This is deterministic prompt assembly.

    Args:
        intent_brief: The structured intent brief from Stage 0a.
        patterns_context: Dict mapping paradigm name to fetched patterns text.

    Returns:
        Dict mapping paradigm name to its enriched system prompt.
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
    for ps in sorted(
        intent_brief.paradigm_shift_candidates, key=lambda x: -x.leverage_score
    ):
        paradigm_shifts_block += (
            f"- {ps.paradigm} (leverage: {ps.leverage_score}/10) — "
            f"Target: {ps.target_area}. {ps.rationale}\n"
        )

    # Per-agent enrichment
    for paradigm_name, template in _PARADIGM_TEMPLATES.items():
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

    logger.info(f"Prompt Enhancement: Composed {len(enriched)} enriched prompts.")
    return enriched
