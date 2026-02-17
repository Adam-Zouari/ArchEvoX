"""Main orchestrator — runs the full 5-stage innovation architecture pipeline."""

import asyncio
import json
import logging
import sys
from pathlib import Path

import yaml

# Ensure the package root is on sys.path so relative imports work
_package_root = Path(__file__).resolve().parent
if str(_package_root) not in sys.path:
    sys.path.insert(0, str(_package_root))

from mcp_client.context_gatherer import gather_enterprise_context, gather_patterns_context
from stages.paradigm_agents import run_paradigm_agents
from stages.mutation_engine import run_mutations
from stages.self_refinement import run_self_refinement
from stages.physics_critic import run_physics_critic
from stages.portfolio_assembly import run_portfolio_assembly
from utils.report_renderer import render_portfolio_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pipeline")


def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = _package_root / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


async def run_pipeline():
    config = load_config()
    llm_cfg = config["llm"]
    pipeline_cfg = config["pipeline"]
    output_cfg = config["output"]

    # ── Pre-fetch context from MCP servers ──
    logger.info("Connecting to MCP servers and gathering enterprise context...")
    enterprise_context, patterns_context = await asyncio.gather(
        gather_enterprise_context(config),
        gather_patterns_context(config),
    )
    logger.info("Enterprise context gathered successfully.")

    # ── Stage 1: Paradigm Agent Generation ──
    logger.info("Stage 1: Running paradigm agents in parallel...")
    original_proposals = await run_paradigm_agents(
        enterprise_context=enterprise_context,
        patterns_context=patterns_context,
        enabled_agents=pipeline_cfg["paradigm_agents"]["enabled_agents"],
        temperature=llm_cfg["temperature"]["paradigm_agents"],
    )
    logger.info(f"  -> Generated {len(original_proposals)} original proposals")

    if not original_proposals:
        logger.error("No proposals generated in Stage 1. Aborting.")
        return

    # ── Stage 2: Idea Mutation ──
    logger.info("Stage 2: Applying mutation operators...")
    mutated_proposals = await run_mutations(
        proposals=original_proposals,
        operators_per_proposal=pipeline_cfg["mutation"]["operators_per_proposal"],
        available_operators=pipeline_cfg["mutation"]["available_operators"],
        temperature=llm_cfg["temperature"]["mutation_engine"],
    )
    all_proposals = list(original_proposals) + list(mutated_proposals)
    logger.info(
        f"  -> Generated {len(mutated_proposals)} mutations, "
        f"{len(all_proposals)} total candidates"
    )

    # ── Stage 3: Self-Refinement ──
    rounds = pipeline_cfg["self_refinement"]["rounds"]
    logger.info(f"Stage 3: Running {rounds} rounds of self-refinement...")
    refined_proposals = await run_self_refinement(
        proposals=all_proposals,
        rounds=rounds,
        temperature=llm_cfg["temperature"]["self_refinement"],
    )
    logger.info(f"  -> Refined {len(refined_proposals)} proposals")

    # ── Stage 4: Physics Critic ──
    logger.info("Stage 4: Running physics critic (annotate only, no rejection)...")
    annotated_proposals = await run_physics_critic(
        proposals=refined_proposals,
        temperature=llm_cfg["temperature"]["physics_critic"],
    )
    critical_count = sum(
        1 for ap in annotated_proposals if ap.hard_constraint_violations > 0
    )
    logger.info(
        f"  -> Annotated {len(annotated_proposals)} proposals, "
        f"{critical_count} have critical flags"
    )

    if len(annotated_proposals) < 6:
        logger.warning(
            f"Only {len(annotated_proposals)} proposals survived to Stage 5 "
            f"(minimum recommended: 6). Continuing anyway."
        )

    # ── Stage 5: Portfolio Assembly ──
    logger.info("Stage 5: Scoring and ranking portfolio...")
    portfolio = await run_portfolio_assembly(
        annotated_proposals=annotated_proposals,
        enterprise_context=enterprise_context,
        score_weights=pipeline_cfg["portfolio"]["score_weights"],
        temperature=llm_cfg["temperature"]["portfolio_ranker"],
    )

    # ── Output ──
    output_dir = Path(_package_root / output_cfg["dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    portfolio_json_path = output_dir / "portfolio.json"
    with open(portfolio_json_path, "w", encoding="utf-8") as f:
        json.dump(portfolio.model_dump(), f, indent=2, ensure_ascii=False)
    logger.info(f"Portfolio JSON written to {portfolio_json_path}")

    if output_cfg.get("render_markdown_report", True):
        report = render_portfolio_report(portfolio)
        report_path = output_dir / "portfolio_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"Markdown report written to {report_path}")

    print(f"\nDone. Portfolio written to {output_dir}/")
    print(f"  Top conservative: {portfolio.top_conservative}")
    print(f"  Top moderate:     {portfolio.top_moderate}")
    print(f"  Top radical:      {portfolio.top_radical}")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
