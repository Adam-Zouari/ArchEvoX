"""Stage 4.5: Structured Debate

Asymmetric, innovation-favoring debate for each proposal:
- Advocate argues FOR the proposal
- Devil's advocate argues AGAINST the status quo (not the proposal)
- Steel-manning is mandatory
- Judge evaluates and scores

Debates CANNOT eliminate proposals — they produce annotations and scores
that feed into Portfolio Assembly.
"""

import asyncio
import json
import logging

from llm.client import call_llm
from models.schemas import (
    AnnotatedProposal,
    ArgumentText,
    DebateRound,
    SteelMan,
    DebateJudgment,
    DebateResult,
)
from prompts.debate_agents import ADVOCATE_PROMPT, DEVIL_ADVOCATE_PROMPT, JUDGE_PROMPT

logger = logging.getLogger(__name__)


async def run_debate_for_proposal(
    annotated_proposal: AnnotatedProposal,
    enterprise_context: str,
    advocate_temperature: float = 0.6,
    devil_temperature: float = 0.6,
    judge_temperature: float = 0.3,
) -> DebateResult:
    """Run a 3-round structured debate for a single proposal."""

    proposal_text = annotated_proposal.model_dump_json(indent=2)
    arch_name = annotated_proposal.proposal.architecture_name

    logger.info(f"Debate: Starting for '{arch_name}'...")

    # Round 1: Opening arguments (can run in parallel)
    advocate_r1_task = call_llm(
        system_prompt=ADVOCATE_PROMPT,
        user_message=(
            f"Round 1: Present your opening case for this proposal.\n\n"
            f"Proposal:\n{proposal_text}\n\n"
            f"Enterprise context:\n{enterprise_context}"
        ),
        response_model=ArgumentText,
        temperature=advocate_temperature,
    )

    devil_r1_task = call_llm(
        system_prompt=DEVIL_ADVOCATE_PROMPT,
        user_message=(
            f"Round 1: Attack the status quo. Here is the current enterprise context "
            f"and the proposal being considered as a replacement.\n\n"
            f"Enterprise context:\n{enterprise_context}\n\n"
            f"Proposal under consideration:\n{proposal_text}"
        ),
        response_model=ArgumentText,
        temperature=devil_temperature,
    )

    advocate_r1, devil_r1 = await asyncio.gather(advocate_r1_task, devil_r1_task)

    # Round 2: Cross-examination (depends on Round 1, can run in parallel)
    annotations_json = json.dumps(
        [a.model_dump() for a in annotated_proposal.annotations], indent=2
    )

    advocate_r2_task = call_llm(
        system_prompt=ADVOCATE_PROMPT,
        user_message=(
            f"Round 2: Address the physics critic annotations and known risks.\n\n"
            f"Your Round 1 argument:\n{advocate_r1.text}\n\n"
            f"Devil's advocate Round 1 (attacking status quo):\n{devil_r1.text}\n\n"
            f"Physics critic annotations:\n{annotations_json}"
        ),
        response_model=ArgumentText,
        temperature=advocate_temperature,
    )

    devil_r2_task = call_llm(
        system_prompt=DEVIL_ADVOCATE_PROMPT,
        user_message=(
            f"Round 2: The advocate has addressed the risks. Now argue why the status quo "
            f"has WORSE versions of similar problems.\n\n"
            f"Advocate's risk mitigation argument:\n{advocate_r1.text}\n\n"
            f"Enterprise context (evidence of status quo problems):\n{enterprise_context}"
        ),
        response_model=ArgumentText,
        temperature=devil_temperature,
    )

    advocate_r2, devil_r2 = await asyncio.gather(advocate_r2_task, devil_r2_task)

    # Round 3: Steel-man + final arguments (depends on Round 2, can run in parallel)
    debate_transcript = (
        f"Advocate R1: {advocate_r1.text}\n"
        f"Devil R1: {devil_r1.text}\n"
        f"Advocate R2: {advocate_r2.text}\n"
        f"Devil R2: {devil_r2.text}"
    )

    advocate_steel_task = call_llm(
        system_prompt=ADVOCATE_PROMPT,
        user_message=(
            f"Round 3: MANDATORY STEEL-MAN. First, present the STRONGEST possible argument "
            f"AGAINST your proposal. Be honest and charitable. Then present your final argument.\n\n"
            f"Full debate so far:\n{debate_transcript}"
        ),
        response_model=SteelMan,
        temperature=advocate_temperature,
    )

    devil_steel_task = call_llm(
        system_prompt=DEVIL_ADVOCATE_PROMPT,
        user_message=(
            f"Round 3: MANDATORY STEEL-MAN. First, present the STRONGEST possible argument "
            f"FOR the status quo. Be honest and charitable. Then present your final argument "
            f"for why change is still needed.\n\n"
            f"Full debate so far:\n{debate_transcript}"
        ),
        response_model=SteelMan,
        temperature=devil_temperature,
    )

    advocate_steel, devil_steel = await asyncio.gather(
        advocate_steel_task, devil_steel_task
    )

    # Ensure agent_role fields are set correctly
    advocate_steel.agent_role = "advocate"
    devil_steel.agent_role = "devil_advocate"

    # Judge evaluates the full transcript
    judgment = await call_llm(
        system_prompt=JUDGE_PROMPT,
        user_message=(
            f"Judge the following debate about this proposal:\n\n"
            f"PROPOSAL:\n{proposal_text}\n\n"
            f"ROUND 1:\n  Advocate: {advocate_r1.text}\n  Devil's Advocate: {devil_r1.text}\n\n"
            f"ROUND 2:\n  Advocate: {advocate_r2.text}\n  Devil's Advocate: {devil_r2.text}\n\n"
            f"ROUND 3 (Steel-mans + Finals):\n"
            f"  Advocate steel-man of opposition: {advocate_steel.steel_man_of_opposition}\n"
            f"  Advocate final: {advocate_steel.final_argument}\n"
            f"  Devil steel-man of status quo: {devil_steel.steel_man_of_opposition}\n"
            f"  Devil final: {devil_steel.final_argument}"
        ),
        response_model=DebateJudgment,
        temperature=judge_temperature,
    )

    # Ensure architecture_name is set on the judgment
    judgment.architecture_name = arch_name

    logger.info(
        f"Debate: '{arch_name}' — Winner: {judgment.debate_winner}, "
        f"Innovation defense: {judgment.innovation_defense_strength}/10"
    )

    return DebateResult(
        architecture_name=arch_name,
        rounds=[
            DebateRound(
                round_number=1,
                advocate_argument=advocate_r1.text,
                devil_advocate_argument=devil_r1.text,
            ),
            DebateRound(
                round_number=2,
                advocate_argument=advocate_r2.text,
                devil_advocate_argument=devil_r2.text,
            ),
        ],
        steel_mans=[advocate_steel, devil_steel],
        judgment=judgment,
    )


async def run_structured_debate(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
    advocate_temperature: float = 0.6,
    devil_temperature: float = 0.6,
    judge_temperature: float = 0.3,
) -> list[DebateResult]:
    """Run debates for ALL proposals in parallel."""
    logger.info(f"Structured Debate: Running {len(annotated_proposals)} debates in parallel...")

    tasks = [
        run_debate_for_proposal(
            ap, enterprise_context,
            advocate_temperature=advocate_temperature,
            devil_temperature=devil_temperature,
            judge_temperature=judge_temperature,
        )
        for ap in annotated_proposals
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    debate_results = []
    for ap, result in zip(annotated_proposals, results):
        if isinstance(result, Exception):
            logger.error(
                f"Debate failed for '{ap.proposal.architecture_name}': {result}"
            )
            continue
        debate_results.append(result)

    won = sum(1 for d in debate_results if d.judgment.debate_winner == "innovation")
    logger.info(
        f"Structured Debate: {len(debate_results)} debates complete. "
        f"Innovation won {won}/{len(debate_results)}."
    )

    return debate_results
