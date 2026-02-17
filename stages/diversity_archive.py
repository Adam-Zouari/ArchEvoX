"""Stage 2.5: Diversity Archive — MAP-Elites Selection

Selects a top-K set of maximally diverse candidates from post-mutation
proposals using MAP-Elites behavioral characterization.
"""

import logging
from typing import Union

from llm.client import call_llm
from models.schemas import (
    Proposal,
    MutatedProposal,
    DiversityScores,
    DiversityArchiveInput,
)
from prompts.diversity_scorer import DIVERSITY_SCORER_PROMPT

logger = logging.getLogger(__name__)


async def run_diversity_archive(
    proposals: list[Union[Proposal, MutatedProposal]],
    starred_names: set[str] | None = None,
    top_k: int = 10,
    temperature: float = 0.2,
) -> list[Union[Proposal, MutatedProposal]]:
    """
    MAP-Elites diversity selection:

    1. Score all proposals on 3 behavioral dimensions via LLM.
    2. Place them in a 5x5x5 MAP-Elites grid.
    3. Keep only the best (by quality_heuristic) in each occupied cell.
    4. Select top-K most diverse candidates.
    5. Always include starred proposals.

    Args:
        proposals: All proposals from Stage 2 (originals + mutations).
        starred_names: Names of human-starred proposals (always included).
        top_k: Maximum number of proposals to advance.
        temperature: LLM temperature for scoring (low for consistency).

    Returns:
        Selected diverse subset of proposals.
    """
    if starred_names is None:
        starred_names = set()

    if len(proposals) <= top_k:
        logger.info(
            f"Diversity Archive: Only {len(proposals)} proposals, "
            f"all advance (top_k={top_k}). No filtering needed."
        )
        return proposals

    # Step 1: Score all proposals on 3 behavioral dimensions
    serialized = "\n\n---\n\n".join(
        f"Proposal: {p.architecture_name}\n{p.model_dump_json(indent=2)}"
        for p in proposals
    )

    logger.info(f"Diversity Archive: Scoring {len(proposals)} proposals on behavioral dimensions...")
    scores = await call_llm(
        system_prompt=DIVERSITY_SCORER_PROMPT,
        user_message=f"Score the following {len(proposals)} proposals:\n\n{serialized}",
        response_model=DiversityArchiveInput,
        temperature=temperature,
    )

    # Build name->scores lookup
    scores_by_name: dict[str, DiversityScores] = {
        ds.architecture_name: ds for ds in scores.proposals
    }

    # Step 2-3: Build grid, keep best per cell
    grid: dict[tuple[int, int, int], DiversityScores] = {}
    for ds in scores.proposals:
        cell = (ds.paradigm_novelty, ds.structural_complexity, ds.migration_distance)
        if cell not in grid or ds.quality_heuristic > grid[cell].quality_heuristic:
            grid[cell] = ds

    # Step 4: Select top-K from unique cells, prioritizing diversity
    selected_names: set[str] = set()

    # Always include starred proposals first
    for name in starred_names:
        if any(p.architecture_name == name for p in proposals):
            selected_names.add(name)

    # Greedy diverse selection: pick the cell farthest from all already-selected cells
    selected_cells: list[tuple[int, int, int]] = []

    # Pre-populate selected_cells for starred proposals
    for name in selected_names:
        if name in scores_by_name:
            ds = scores_by_name[name]
            cell = (ds.paradigm_novelty, ds.structural_complexity, ds.migration_distance)
            if cell not in selected_cells:
                selected_cells.append(cell)

    remaining_cells = [
        (cell, ds) for cell, ds in grid.items()
        if ds.architecture_name not in selected_names
    ]

    while len(selected_names) < top_k and remaining_cells:
        if not selected_cells:
            # First pick: highest quality among highest novelty
            remaining_cells.sort(key=lambda x: (-x[0][0], -x[1].quality_heuristic))
            best_cell, best_ds = remaining_cells.pop(0)
        else:
            # Subsequent picks: maximize minimum distance to all selected cells
            def min_distance(cell: tuple[int, int, int]) -> float:
                return min(
                    sum((a - b) ** 2 for a, b in zip(cell, sc)) ** 0.5
                    for sc in selected_cells
                )

            remaining_cells.sort(key=lambda x: -min_distance(x[0]))
            best_cell, best_ds = remaining_cells.pop(0)

        selected_cells.append(best_cell)
        selected_names.add(best_ds.architecture_name)

    # Step 5: Filter original proposals to only selected names
    selected_proposals = [p for p in proposals if p.architecture_name in selected_names]

    # Log what was dropped and why
    dropped = [p for p in proposals if p.architecture_name not in selected_names]
    if dropped:
        logger.info(
            f"Diversity Archive: Selected {len(selected_proposals)}, "
            f"dropped {len(dropped)} similar candidates:"
        )
        for d in dropped:
            ds = scores_by_name.get(d.architecture_name)
            if ds:
                logger.info(
                    f"  Dropped: {d.architecture_name} "
                    f"(novelty={ds.paradigm_novelty}, complexity={ds.structural_complexity}, "
                    f"distance={ds.migration_distance}, quality={ds.quality_heuristic:.1f})"
                )
    else:
        logger.info(f"Diversity Archive: All {len(selected_proposals)} proposals selected.")

    # Log grid coverage
    occupied = len(grid)
    logger.info(
        f"Diversity Archive: Grid coverage = {occupied}/125 cells occupied, "
        f"{len(selected_proposals)} selected from {len(proposals)} candidates."
    )

    return selected_proposals
