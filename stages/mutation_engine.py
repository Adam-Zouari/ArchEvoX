"""Stage 2: Idea Mutation Engine

Takes each proposal from Stage 1 and applies randomly selected mutation
operators, generating mutated variants.
"""

import asyncio
import logging
import random

from llm.client import call_llm
from models.schemas import Proposal, MutatedProposal
from prompts.mutation_operators import OPERATOR_PROMPTS

logger = logging.getLogger(__name__)


async def run_mutations(
    proposals: list[Proposal],
    operators_per_proposal: int = 3,
    available_operators: list[str] | None = None,
    temperature: float = 0.85,
) -> list[MutatedProposal]:
    """Apply random mutation operators to each proposal."""
    if available_operators is None:
        available_operators = list(OPERATOR_PROMPTS.keys())

    # Run mutations SEQUENTIALLY
    mutated = []

    for proposal in proposals:
        k = min(operators_per_proposal, len(available_operators))
        selected_ops = random.sample(available_operators, k=k)

        for op_name in selected_ops:
            system_prompt = OPERATOR_PROMPTS[op_name]
            try:
                result = await call_llm(
                    system_prompt=system_prompt,
                    user_message=(
                        "Here is the architectural proposal to mutate:\n\n"
                        f"{proposal.model_dump_json(indent=2)}"
                    ),
                    response_model=MutatedProposal,
                    temperature=temperature,
                    stage="mutation_engine",
                )
                result.mutation_applied = op_name
                result.parent_architecture_name = proposal.architecture_name
                result.paradigm_source = f"{proposal.paradigm_source}+mutation-{op_name}"
                mutated.append(result)
                logger.info(f"  ✓ Mutated '{proposal.architecture_name}' with {op_name}")
            except Exception as e:
                logger.error(f"Mutation '{op_name}' on '{proposal.architecture_name}' failed: {e}")
                continue

    return mutated
