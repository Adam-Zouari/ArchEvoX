"""Stage 3: Self-Refinement

Each proposal gets multiple rounds of self-refinement. The LLM critiques
the proposal and produces a stronger version without making it more conservative.
"""

import asyncio
import logging

from llm.client import call_llm
from models.schemas import Proposal, MutatedProposal, RefinedProposal
from prompts.self_refinement import SELF_REFINEMENT_PROMPT

logger = logging.getLogger(__name__)


async def run_self_refinement(
    proposals: list[Proposal | MutatedProposal],
    rounds: int = 2,
    temperature: float = 0.5,
) -> list[RefinedProposal]:
    """Run N rounds of self-refinement on all proposals."""
    current = proposals

    for round_num in range(1, rounds + 1):
        tasks = [
            call_llm(
                system_prompt=SELF_REFINEMENT_PROMPT,
                user_message=(
                    f"Refinement round {round_num}. "
                    f"Here is the proposal to refine:\n\n"
                    f"{p.model_dump_json(indent=2)}"
                ),
                response_model=RefinedProposal,
                temperature=temperature,
            )
            for p in current
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        refined = []
        for original, result in zip(current, results):
            if isinstance(result, Exception):
                logger.error(
                    f"Refinement round {round_num} failed for "
                    f"'{original.architecture_name}': {result}"
                )
                # On failure, wrap the original as a RefinedProposal so the pipeline continues
                fallback = RefinedProposal(
                    **original.model_dump(),
                    refinements_made=[f"[Refinement round {round_num} failed]"],
                    refinement_round=round_num,
                )
                refined.append(fallback)
            else:
                result.refinement_round = round_num
                refined.append(result)

        current = refined

    return current
