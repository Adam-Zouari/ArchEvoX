"""Stage 4: Physics Critic

Annotates each proposal with hard-constraint violations.
Does NOT reject or modify proposals — only attaches metadata.
"""

import asyncio
import logging

from llm.client import call_llm
from models.schemas import RefinedProposal, AnnotatedProposal
from prompts.physics_critic import PHYSICS_CRITIC_PROMPT

logger = logging.getLogger(__name__)


async def run_physics_critic(
    proposals: list[RefinedProposal],
    temperature: float = 0.3,
) -> list[AnnotatedProposal]:
    """Annotate all proposals with physics constraints. Never reject."""
    tasks = [
        call_llm(
            system_prompt=PHYSICS_CRITIC_PROMPT,
            user_message=(
                "Here is the architectural proposal to annotate:\n\n"
                f"{p.model_dump_json(indent=2)}"
            ),
            response_model=AnnotatedProposal,
            temperature=temperature,
        )
        for p in proposals
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    annotated = []
    for proposal, result in zip(proposals, results):
        if isinstance(result, Exception):
            logger.error(
                f"Physics critic failed for '{proposal.architecture_name}': {result}"
            )
            # Create a minimal annotation so the pipeline continues
            fallback = AnnotatedProposal(
                proposal=proposal,
                annotations=[],
                hard_constraint_violations=0,
                overall_feasibility_note="[Physics critic evaluation failed]",
            )
            annotated.append(fallback)
        else:
            annotated.append(result)

    return annotated
