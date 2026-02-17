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

    tasks = []
    task_meta = []  # Track which proposal/operator for error reporting

    for proposal in proposals:
        k = min(operators_per_proposal, len(available_operators))
        selected_ops = random.sample(available_operators, k=k)

        for op_name in selected_ops:
            system_prompt = OPERATOR_PROMPTS[op_name]
            tasks.append(
                call_llm(
                    system_prompt=system_prompt,
                    user_message=(
                        "Here is the architectural proposal to mutate:\n\n"
                        f"{proposal.model_dump_json(indent=2)}"
                    ),
                    response_model=MutatedProposal,
                    temperature=temperature,
                )
            )
            task_meta.append((proposal.architecture_name, op_name))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    mutated = []
    for (parent_name, op_name), result in zip(task_meta, results):
        if isinstance(result, Exception):
            logger.error(f"Mutation '{op_name}' on '{parent_name}' failed: {result}")
            continue
        result.mutation_applied = op_name
        result.parent_architecture_name = parent_name
        result.paradigm_source = f"mutation-{op_name}"
        mutated.append(result)

    return mutated
