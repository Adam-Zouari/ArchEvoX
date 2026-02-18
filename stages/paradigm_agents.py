"""Stage 1: Paradigm Agent Generation

Runs 4 LLM agents in parallel. Each agent receives enterprise context
and has a radically different system prompt. Each returns a Proposal.
"""

import asyncio
import logging

from llm.client import call_llm
from models.schemas import Proposal
from prompts.paradigm_agents import AGENT_PROMPTS

logger = logging.getLogger(__name__)


async def run_paradigm_agents(
    enterprise_context: str,
    patterns_context: str,
    enabled_agents: list[str],
    temperature: float = 0.9,
    enriched_prompts: dict[str, str] | None = None,
) -> list[Proposal]:
    """Run all enabled paradigm agents in parallel, return typed Proposals.

    Args:
        enterprise_context: Full enterprise context string.
        patterns_context: Patterns knowledge context string.
        enabled_agents: List of agent names to run.
        temperature: LLM temperature for generation.
        enriched_prompts: If provided (from Stage 0b), use these instead
                          of the static AGENT_PROMPTS templates.
    """

    agents = []
    for agent_name in enabled_agents:
        # Use enriched prompt if available, otherwise fall back to static template
        if enriched_prompts and agent_name in enriched_prompts:
            system_prompt = enriched_prompts[agent_name]
        else:
            system_prompt = AGENT_PROMPTS.get(agent_name)
            if system_prompt is None:
                logger.warning(f"Unknown agent '{agent_name}', skipping.")
                continue
        # Wildcard agent gets extra patterns context (only if not using enriched prompts)
        context = enterprise_context
        if agent_name == "wildcard" and not enriched_prompts:
            context = enterprise_context + "\n\n---\n\n" + patterns_context
        agents.append((agent_name, system_prompt, context))

    # Run agents SEQUENTIALLY (instructor doesn't support parallel)
    proposals = []
    for agent_name, system_prompt, context in agents:
        logger.info(f"  Running agent: {agent_name}...")
        try:
            result = await call_llm(
                system_prompt=system_prompt,
                user_message=(
                    "Here is the enterprise context describing the current data pipeline "
                    "architecture, technologies, business goals, and constraints.\n\n"
                    f"{context}\n\n"
                    "Based on this, generate your architectural proposal."
                ),
                response_model=Proposal,
                temperature=temperature,
            )
            result.paradigm_source = agent_name
            proposals.append(result)
            logger.info(f"  ✓ {agent_name}: '{result.architecture_name}'")
        except Exception as e:
            logger.error(f"Agent '{agent_name}' failed: {e}")
            continue

    return proposals
