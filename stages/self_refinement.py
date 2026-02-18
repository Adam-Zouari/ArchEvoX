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
        # Run refinements SEQUENTIALLY (instructor doesn't support parallel)
        refined = []
        for p in current:
            try:
                result = await call_llm(
                    system_prompt=SELF_REFINEMENT_PROMPT,
                    user_message=(
                        f"Refinement round {round_num}. "
                        f"Here is the proposal to refine:\n\n"
                        f"{p.model_dump_json(indent=2)}"
                    ),
                    response_model=RefinedProposal,
                    temperature=temperature,
                )
                result.refinement_round = round_num
                refined.append(result)
            except Exception as e:
                logger.error(
                    f"Refinement round {round_num} failed for "
                    f"'{p.architecture_name}': {e}"
                )
                # On failure, wrap the original as a RefinedProposal so the pipeline continues
                fallback = RefinedProposal(
                    **p.model_dump(),
                    refinements_made=[f"[Refinement round {round_num} failed]"],
                    refinement_round=round_num,
                )
                refined.append(fallback)

        current = refined

    return current
