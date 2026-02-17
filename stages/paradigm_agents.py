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
) -> list[Proposal]:
    """Run all enabled paradigm agents in parallel, return typed Proposals."""

    agents = []
    for agent_name in enabled_agents:
        system_prompt = AGENT_PROMPTS.get(agent_name)
        if system_prompt is None:
            logger.warning(f"Unknown agent '{agent_name}', skipping.")
            continue
        # Wildcard agent gets extra patterns context
        context = enterprise_context
        if agent_name == "wildcard":
            context = enterprise_context + "\n\n---\n\n" + patterns_context
        agents.append((agent_name, system_prompt, context))

    tasks = [
        call_llm(
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
        for _, system_prompt, context in agents
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    proposals = []
    for (agent_name, _, _), result in zip(agents, results):
        if isinstance(result, Exception):
            logger.error(f"Agent '{agent_name}' failed: {result}")
            continue
        result.paradigm_source = agent_name
        proposals.append(result)

    return proposals
