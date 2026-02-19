"""Stage 0a: Intent Agent

Analyzes enterprise context and produces a structured IntentBrief
that captures what the user really needs, where the pain is, and
what paradigm shifts would be most valuable.
"""

import logging

from llm.client import call_llm
from models.schemas import IntentBrief
from prompts.intent_agent import INTENT_AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def run_intent_agent(
    enterprise_context: str,
    temperature: float = 0.4,
) -> IntentBrief:
    """Analyze enterprise context and produce an intent brief.

    This runs BEFORE Stage 1 to ensure paradigm agents understand
    the real problem, not just the documented one.
    """
    logger.info("Intent Agent: Analyzing enterprise context...")

    intent_brief = await call_llm(
        system_prompt=INTENT_AGENT_SYSTEM_PROMPT,
        user_message=(
            "Analyze the following enterprise documentation and produce "
            "an Intent Brief.\n\n"
            f"{enterprise_context}"
        ),
        response_model=IntentBrief,
        temperature=temperature,
        stage="intent_agent",
    )

    logger.info(
        f"Intent Agent: Identified {len(intent_brief.paradigm_shift_candidates)} "
        f"paradigm shift candidates and {len(intent_brief.innovation_opportunity_map)} "
        f"innovation opportunities."
    )

    return intent_brief
