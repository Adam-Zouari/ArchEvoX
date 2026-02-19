# Structured Debate (Stage 4.5)

## 📋 Table of Contents
- [Overview](#overview)
- [Why Debate?](#why-debate)
- [The Innovation Bias](#the-innovation-bias)
- [Three Agents, Three Roles](#three-agents-three-roles)
- [The 3-Round Protocol](#the-3-round-protocol)
- [Steel-Manning Explained](#steel-manning-explained)
- [Implementation Details](#implementation-details)
- [Data Structures](#data-structures)
- [Parallelization Strategy](#parallelization-strategy)
- [Scoring & Judgment](#scoring--judgment)
- [Examples](#examples)
- [Configuration & Tuning](#configuration--tuning)
- [Design Decisions](#design-decisions)
- [Common Misconceptions](#common-misconceptions)

---

## Overview

**Structured Debate** is a multi-agent deliberation system that subjects each architectural proposal to rigorous adversarial testing. Unlike traditional code review or design critique, this debate is **asymmetric** and **innovation-favoring**: it forces both sides to honestly confront weaknesses while ensuring novel ideas aren't killed by status quo bias.

**Purpose**: Test whether innovative proposals can withstand intellectual scrutiny and whether they genuinely solve problems the status quo cannot.

**Input**: 10 proposals (post-diversity filtering, annotated by physics critic)
**Output**: Debate transcripts, scores, and key insights for each proposal
**Method**: 3-round structured debate with mandatory steel-manning

**Key Principle**: *Debates don't eliminate proposals* — they produce annotations and scores that inform portfolio assembly. All proposals survive to Stage 5.

---

## Why Debate?

### The Problem with Traditional Review

In typical enterprise architecture reviews:
- **Status quo bias**: "We're already doing X, why change?"
- **Cognitive laziness**: "This looks complicated, let's stick with what we know"
- **Risk aversion**: "What if this fails?" (without asking "what if we DON'T innovate?")
- **Strawman attacks**: Critics attack weak versions of new ideas
- **Unexamined assumptions**: Nobody questions whether the current approach is actually working

**Result**: Innovative ideas die not because they're bad, but because defending the status quo is cognitively easier.

### How Debate Fixes This

1. **Asymmetric roles**: One agent attacks the status quo (not the proposal)
2. **Mandatory steel-manning**: Both sides must articulate the OTHER side's best argument
3. **Context-aware**: Uses enterprise context to ground arguments in reality
4. **Physics critic integration**: Debate explicitly addresses known technical risks
5. **Innovation-favoring**: Ties go to the novel approach (by design)

**Result**: Proposals are tested fairly, and the status quo doesn't get a free pass.

---

## The Innovation Bias

This debate system is **intentionally asymmetric** to counteract organizational inertia.

### Traditional Debate (Symmetric):
```
Advocate: "This new architecture is better because..."
Opponent: "But the current architecture is proven and reliable"
Judge: "Tie goes to the status quo (safer choice)"
```

**Problem**: Innovation must be 10x better to overcome switching costs and risk aversion.

### Innovation-Favoring Debate (Asymmetric):
```
Advocate: "This new architecture enables X that the current approach cannot"
Devil's Advocate: "The current architecture has fundamental problem Y that's getting worse"
Judge: "Tie goes to innovation (system is designed for exploration)"
```

**Result**: Novel ideas are judged on merit, not on whether they're "safe."

### Why This Makes Sense

The pipeline's purpose is **innovation generation**, not status quo validation. If you want conservative, battle-tested patterns, you don't need this system — just use Lambda architecture.

**Design philosophy**: If a debate is 50/50, that means the innovative proposal is *at least as good* as the status quo, so we should explore it.

---

## Three Agents, Three Roles

### 1. **Advocate** (Pro-Innovation)

**Mission**: Make the strongest possible case FOR the proposal

**Responsibilities**:
- **Round 1**: Present core value proposition (what problems does this solve?)
- **Round 2**: Address physics critic annotations and known risks
- **Round 3**: Steel-man the opposition, then deliver final argument

**Temperature**: 0.6 (creative but grounded)

**Prohibited behaviors**:
- Hand-waving ("it'll just work")
- Dismissing concerns ("that's not a real problem")
- Strawman attacks on status quo ("old architecture is trash")

**Required behaviors**:
- Specific technical arguments (reference components, data flows)
- Honest acknowledgment of weaknesses
- Concrete mitigation strategies for identified risks

**Key Instruction**:
> "Your credibility depends on acknowledging genuine weaknesses honestly. Your goal is to ensure the BEST version of this proposal is what gets judged."

---

### 2. **Devil's Advocate** (Anti-Status-Quo)

**Mission**: Expose why the STATUS QUO is problematic (NOT attack the proposal)

**Responsibilities**:
- **Round 1**: Attack status quo's fundamental structural weaknesses
- **Round 2**: Show that status quo has WORSE versions of proposal's risks
- **Round 3**: Steel-man the status quo, then argue why change is still needed

**Temperature**: 0.6 (creative but grounded)

**Critical distinction**: This is NOT a traditional opponent. They're NOT saying "proposal is bad" — they're saying "current approach is worse."

**Example argument**:
> "Yes, the proposed architecture has eventual consistency challenges. But the current monolithic database has silent data corruption that goes undetected for weeks, cascading failures that take down the entire system, and a 6-hour recovery SLA. Which is worse: visible, bounded inconsistency or invisible, unbounded corruption?"

**Prohibited behaviors**:
- Attacking the innovative proposal directly
- Generic criticism ("change is risky")
- Ignoring genuine status quo strengths

**Required behaviors**:
- Use enterprise context to cite real status quo failures
- Comparative risk analysis (status quo risk vs. proposal risk)
- Honest steel-man of status quo strengths

**Key Instruction**:
> "Your purpose is to ensure the debate doesn't default to 'just keep what we have' without examining whether that's actually working."

---

### 3. **Judge** (Impartial Evaluator)

**Mission**: Evaluate the full debate and produce scores

**Responsibilities**:
- Assess innovation defense strength (0-10)
- Assess status quo weakness exposed (0-10)
- Assess risk mitigation quality (0-10)
- Declare winner: "innovation" or "status_quo"
- Identify key insight (what did we learn?)
- List residual concerns (what wasn't addressed?)

**Temperature**: 0.3 (low variance, consistent scoring)

**Evaluation criteria**:
- **Specificity**: Are arguments concrete or hand-wavy?
- **Evidence**: Do arguments cite components, flows, and context?
- **Honesty**: Did both sides steel-man fairly?
- **Mitigation**: Were risks addressed or dismissed?

**Tie-breaking rule**:
> "Be fair but lean toward giving innovative proposals the benefit of the doubt when the debate is close. The system is designed for innovation — a tie goes to the novel approach."

**Why low temperature?** We want consistent scoring across proposals. If the same debate happened twice, the judge should give similar scores.

---

## The 3-Round Protocol

### **Round 1: Opening Arguments**

**Timing**: Both agents argue in parallel (no dependency)

#### Advocate (Round 1)
**Prompt**: "Present your opening case for this proposal."

**Input**:
- Full proposal JSON (architecture, components, innovations)
- Enterprise context (business goals, constraints, current pain points)

**Expected output**:
- Core value proposition
- What problems does this solve?
- Why is this transformative?
- What can it enable that the current approach cannot?

**Example**:
> "Event Sourcing with CQRS enables temporal queries that are impossible in the current CRUD system. Our regulatory compliance team currently spends 40 hours/month reconstructing historical state from audit logs because the current database only stores snapshots. With this architecture, any historical state is a first-class query, reducing compliance overhead by 80% while improving audit accuracy."

---

#### Devil's Advocate (Round 1)
**Prompt**: "Attack the status quo. Here is the current enterprise context and the proposal being considered as a replacement."

**Input**:
- Enterprise context (current architecture, pain points, constraints)
- Proposal being considered (for context only, NOT to attack)

**Expected output**:
- Fundamental weaknesses of current architecture
- Problems getting worse over time
- What the status quo prevents the organization from achieving

**Example**:
> "The current monolithic PostgreSQL setup has three fatal flaws: (1) Write contention during peak hours causes 30% of transactions to timeout, losing revenue. (2) Schema migrations require 4-hour maintenance windows, blocking critical releases. (3) The database is a single point of failure — when it goes down (monthly), the entire business stops. These aren't edge cases; they're structural problems that will only worsen as we scale."

---

### **Round 2: Cross-Examination**

**Timing**: Both agents argue in parallel (both have access to Round 1 transcripts)

#### Advocate (Round 2)
**Prompt**: "Address the physics critic annotations and known risks."

**Input**:
- Advocate's Round 1 argument
- Devil's advocate's Round 1 argument
- Physics critic annotations (technical feasibility concerns)

**Expected output**:
- Direct response to each physics critic annotation
- Mitigation strategies for identified risks
- Acknowledgment of genuine challenges + concrete solutions

**Example**:
> "The physics critic flagged eventual consistency as a risk. This is valid. Our mitigation: (1) Use conflict-free replicated data types (CRDTs) for inventory counts, guaranteeing convergence. (2) Implement saga orchestration with compensating transactions for order workflows. (3) Maintain strong consistency for financial transactions using the existing relational DB. This is a hybrid approach that isolates consistency requirements by domain, not a blanket 'everything is eventually consistent' model."

---

#### Devil's Advocate (Round 2)
**Prompt**: "The advocate has addressed the risks. Now argue why the status quo has WORSE versions of similar problems."

**Input**:
- Advocate's Round 1 (risk mitigation argument)
- Enterprise context (evidence of status quo problems)

**Expected output**:
- Comparative risk analysis
- Show that status quo has hidden/normalized versions of the same risks
- Contextualize "proposal risk" vs. "status quo risk"

**Example**:
> "The advocate acknowledges eventual consistency challenges and proposes CRDTs. Fair. But let's talk about what we have NOW: the current system has race conditions in the inventory service that cause overselling 2-3 times per week. Customer Service manually resolves these by issuing refunds and apology coupons — costing $15K/month. That's not 'strong consistency' — that's silent failure with human cleanup. The proposed architecture makes inconsistency VISIBLE and BOUNDED, which is vastly better than invisible and unbounded."

---

### **Round 3: Steel-Man + Final Arguments**

**Timing**: Both agents provide steel-mans + finals in parallel (both have access to full debate so far)

#### Advocate (Round 3)
**Prompt**: "MANDATORY STEEL-MAN. First, present the STRONGEST possible argument AGAINST your proposal. Be honest and charitable. Then present your final argument."

**Input**:
- Full debate transcript (Rounds 1-2 from both sides)

**Expected output** (structured as `SteelMan` schema):
1. **steel_man_of_opposition**: Best argument AGAINST the proposal
2. **final_argument**: Final case for the proposal, accounting for the steel-man

**Example**:
```json
{
  "agent_role": "advocate",
  "steel_man_of_opposition": "The strongest argument against Event Sourcing is operational complexity. Our team has zero experience with event stores, CQRS, or saga patterns. Training would take 6+ months. The current PostgreSQL setup is well-understood, has 24/7 on-call coverage, and benefits from decades of collective knowledge. Introducing a novel paradigm risks creating a 'black box' system that nobody can debug during incidents. The migration itself could take 18 months and introduce serious operational risk.",

  "final_argument": "That steel-man is valid, and it's why we propose a PHASED rollout: (1) Start with read-only reporting (low risk, high learning value). (2) Move non-critical domains (user preferences, activity logs) next. (3) Keep financial transactions on PostgreSQL for the first year. This de-risks the learning curve while delivering immediate value (faster reports, better compliance tooling). We also propose hiring ONE senior event sourcing consultant for 6 months to upskill the team. This isn't a reckless rewrite — it's a strategic, risk-managed evolution."
}
```

**Key point**: The advocate must *genuinely* articulate the strongest opposing argument, not a weak strawman. This forces intellectual honesty.

---

#### Devil's Advocate (Round 3)
**Prompt**: "MANDATORY STEEL-MAN. First, present the STRONGEST possible argument FOR the status quo. Be honest and charitable. Then present your final argument for why change is still needed."

**Input**:
- Full debate transcript (Rounds 1-2 from both sides)

**Expected output** (structured as `SteelMan` schema):
1. **steel_man_of_opposition**: Best argument FOR the status quo
2. **final_argument**: Final case for why change is necessary

**Example**:
```json
{
  "agent_role": "devil_advocate",
  "steel_man_of_opposition": "The current PostgreSQL monolith has one massive advantage: simplicity. When something breaks, there's one place to look. Transactions are ACID-compliant with zero edge cases. Schema changes are painful but predictable. The team knows how to operate it. This is 'boring technology' in the best sense — reliable, understood, and proven at scale. The devil you know is often better than the devil you don't.",

  "final_argument": "That simplicity is real, but it's COLLAPSING under current load. Three outages in the last quarter were caused by write contention on the monolithic schema. The 'one place to look' is also a single point of failure. Yes, the current system is simple — but it's simple in the way a one-lane bridge is simple. It works great until traffic doubles, and then it's a bottleneck. We're at that inflection point NOW. Sticking with simplicity means accepting monthly outages, 4-hour maintenance windows, and lost revenue. That's not sustainable."
}
```

**Key point**: The devil's advocate must *genuinely* articulate the status quo's strengths, not dismissively handwave them.

---

### **Judge Evaluation**

**Timing**: After all 3 rounds complete

**Prompt**: "Judge the following debate about this proposal."

**Input**:
- Full proposal JSON
- Full 3-round debate transcript
- Both steel-man arguments

**Output** (structured as `DebateJudgment` schema):

```json
{
  "architecture_name": "Event Sourcing with CQRS",
  "innovation_defense_strength": 8.5,
  "status_quo_weakness_exposed": 9.0,
  "risk_mitigation_quality": 7.5,
  "debate_winner": "innovation",
  "key_insight": "The current system's 'simplicity' is actually a liability at current scale — the proposal's complexity is essential, not accidental, and can be managed through phased rollout.",
  "residual_concerns": [
    "6-month learning curve for team upskilling is aggressive; may need 9-12 months",
    "Saga orchestration failure modes not fully addressed (what happens if compensating transaction fails?)",
    "Cost estimate for event store infrastructure not provided"
  ]
}
```

**Scoring breakdown**:

| Score | Description |
|-------|-------------|
| **innovation_defense_strength** (8.5/10) | Advocate made specific, technical arguments with concrete mitigations. Lost 1.5 points for not addressing saga failure modes comprehensively. |
| **status_quo_weakness_exposed** (9.0/10) | Devil's advocate cited real failures (3 outages, overselling incidents, maintenance windows) with financial impact. Strong comparative risk analysis. |
| **risk_mitigation_quality** (7.5/10) | Physics critic concerns were addressed, but phased rollout timeline may be optimistic. |
| **debate_winner** | "innovation" — proposal survived scrutiny AND exposed status quo weaknesses. |

**Key insight**: The single most important thing learned from the debate. Often reveals hidden tradeoffs or reframes the problem.

**Residual concerns**: What wasn't answered? These feed into portfolio assembly — a proposal might be top-tier despite residual concerns if its strengths are overwhelming.

---

## Implementation Details

### File: `stages/structured_debate.py`

### Main Function: `run_structured_debate()`

```python
async def run_structured_debate(
    annotated_proposals: list[AnnotatedProposal],
    enterprise_context: str,
    advocate_temperature: float = 0.6,
    devil_temperature: float = 0.6,
    judge_temperature: float = 0.3,
) -> list[DebateResult]
```

**Parameters**:
- `annotated_proposals`: Proposals with physics critic annotations
- `enterprise_context`: Business goals, constraints, current pain points
- `advocate_temperature`: Creativity for advocate (default: 0.6)
- `devil_temperature`: Creativity for devil's advocate (default: 0.6)
- `judge_temperature`: Consistency for judge (default: 0.3)

**Returns**: List of `DebateResult` objects (one per proposal)

---

### Per-Proposal Function: `run_debate_for_proposal()`

```python
async def run_debate_for_proposal(
    annotated_proposal: AnnotatedProposal,
    enterprise_context: str,
    ...
) -> DebateResult
```

**Flow**:
1. **Round 1** (parallel): Advocate + Devil's advocate opening arguments
2. **Round 2** (parallel): Cross-examination by both
3. **Round 3** (parallel): Steel-mans + final arguments
4. **Judgment** (sequential): Judge evaluates full transcript

**Key insight**: Rounds run in parallel where possible to minimize latency.

---

## Data Structures

### `DebateResult`

```python
class DebateResult(BaseModel):
    architecture_name: str
    rounds: list[DebateRound]          # 2 rounds (R1, R2)
    steel_mans: list[SteelMan]         # 2 steel-mans (advocate, devil)
    judgment: DebateJudgment           # Judge's scores + verdict
```

**Why only 2 rounds in the list?** Round 3 is captured in `steel_mans` (separate structure).

---

### `DebateRound`

```python
class DebateRound(BaseModel):
    round_number: int                  # 1 or 2
    advocate_argument: str             # Advocate's argument FOR proposal
    devil_advocate_argument: str       # Devil's argument AGAINST status quo
```

**Simple structure**: Each round is just two text arguments.

---

### `SteelMan`

```python
class SteelMan(BaseModel):
    agent_role: str                           # "advocate" or "devil_advocate"
    steel_man_of_opposition: str              # Best argument for OTHER side
    final_argument: str                       # Final argument after steel-manning
```

**Critical field**: `steel_man_of_opposition` forces agents to argue AGAINST themselves before concluding.

---

### `DebateJudgment`

```python
class DebateJudgment(BaseModel):
    architecture_name: str
    innovation_defense_strength: float        # 0-10
    status_quo_weakness_exposed: float        # 0-10
    risk_mitigation_quality: float            # 0-10
    debate_winner: str                        # "innovation" or "status_quo"
    key_insight: str                          # Single most important learning
    residual_concerns: list[str]              # Unresolved questions
```

**Feeds into**: Portfolio assembly (Stage 5) uses these scores to rank proposals.

---

## Parallelization Strategy

### **Within a Single Debate** (3 rounds):

```python
# Round 1: Both argue in parallel
advocate_r1, devil_r1 = await asyncio.gather(
    call_llm(..., advocate_prompt_r1),
    call_llm(..., devil_prompt_r1)
)

# Round 2: Both argue in parallel (depends on R1)
advocate_r2, devil_r2 = await asyncio.gather(
    call_llm(..., advocate_prompt_r2),  # Uses R1 transcripts
    call_llm(..., devil_prompt_r2)      # Uses R1 transcripts
)

# Round 3: Both steel-man in parallel (depends on R2)
advocate_steel, devil_steel = await asyncio.gather(
    call_llm(..., advocate_prompt_r3),  # Uses R1+R2 transcripts
    call_llm(..., devil_prompt_r3)      # Uses R1+R2 transcripts
)

# Judgment: Sequential (depends on all rounds)
judgment = await call_llm(..., judge_prompt)
```

**Result**: 7 LLM calls execute as 4 sequential steps (R1, R2, R3, Judge), not 7 sequential steps.

**Latency savings**: ~50% faster than naive sequential execution.

---

### **Across All Debates** (10 proposals):

```python
tasks = [
    run_debate_for_proposal(ap, enterprise_context)
    for ap in annotated_proposals
]

results = await asyncio.gather(*tasks, return_exceptions=True)
```

**All 10 debates run in parallel**. If each debate takes 2 minutes, total stage time is ~2 minutes (not 20 minutes).

**Concurrency**: Limited by Mistral API rate limits (5 requests/second). With 10 debates × 7 calls/debate = 70 calls, this takes ~14 seconds at max rate + LLM processing time (~2 minutes total).

---

## Scoring & Judgment

### How Scores Feed Into Portfolio Assembly

**Stage 4.5 Output** → **Stage 5 Input**:

```json
{
  "architecture_name": "Event Sourcing CQRS",
  "innovation_defense_strength": 8.5,
  "status_quo_weakness_exposed": 9.0,
  "risk_mitigation_quality": 7.5,
  "debate_winner": "innovation"
}
```

**Portfolio Assembly uses**:
- `innovation_defense_strength` → Contributes to innovation_score
- `risk_mitigation_quality` → Contributes to feasibility_score
- `status_quo_weakness_exposed` → Contributes to business_alignment_score
- `debate_winner` → Tie-breaker when composite scores are close

**Weighted composite formula** (in portfolio assembly):
```python
composite_score = (
    0.35 * innovation_score +
    0.25 * feasibility_score +
    0.25 * business_alignment_score +
    0.15 * (10 - migration_complexity_score)  # Lower migration = higher score
)
```

**Debate contribution** (approximate):
- Innovation score: 40% from debate, 60% from domain critics
- Feasibility score: 30% from debate, 70% from physics critic
- Business alignment: 50% from debate, 50% from domain critics

---

## Examples

### Example 1: Debate Where Innovation Wins

**Proposal**: "Temporal Graph Database for Supply Chain Traceability"

**Round 1**:
- **Advocate**: "Current relational schema requires 7-table joins to trace product origin. Temporal graph enables one-hop queries, reducing trace time from 45 seconds to 200ms. Critical for compliance (15-second SLA)."
- **Devil**: "Current PostgreSQL setup cannot handle bi-temporal queries (transaction time + valid time). Recent salmonella outbreak required 6 hours to trace contaminated lettuce. Customers were at risk during that window."

**Round 2**:
- **Advocate**: "Physics critic flagged graph query complexity. Mitigation: Use Neo4j with time-travel indexes (built-in). Pre-compute critical paths nightly (99% of queries hit cache). Worst-case uncached query: 2 seconds (still beats 45-second JOIN)."
- **Devil**: "Advocate mentions 2-second worst case. Current system has 45-second BEST case, and it times out 20% of the time during peak load (failures, not just slow queries)."

**Round 3**:
- **Advocate Steel-Man**: "Strongest argument against: Our team has zero graph DB experience. Neo4j ops are fundamentally different from PostgreSQL. Learning curve is steep."
- **Advocate Final**: "Hire Neo4j consultant for 3 months. Start with read-only traceability queries (de-risked). Keep transactional writes in PostgreSQL initially."
- **Devil Steel-Man**: "Status quo strength: SQL is universal. Every engineer knows it. Recruiting is easy."
- **Devil Final**: "That universality is why we're stuck with 7-table JOINs. The problem is NP-hard in relational — no amount of SQL expertise will fix it. Need the right tool for the job."

**Judgment**:
```json
{
  "innovation_defense_strength": 9.0,
  "status_quo_weakness_exposed": 8.5,
  "risk_mitigation_quality": 8.0,
  "debate_winner": "innovation",
  "key_insight": "This is a problem that SQL fundamentally cannot solve efficiently — graph DB isn't a 'nice-to-have', it's the correct model for bi-temporal traceability.",
  "residual_concerns": ["3-month consultant timeline may be too short for full team upskilling"]
}
```

**Outcome**: Top radical tier in portfolio.

---

### Example 2: Debate Where Status Quo Wins (Rare)

**Proposal**: "Blockchain-Based Audit Logging"

**Round 1**:
- **Advocate**: "Blockchain provides immutable, cryptographically-verified audit logs. No admin can tamper with records. Perfect for compliance."
- **Devil**: "Current audit logs in PostgreSQL can be modified by DBAs. Trust issues exist."

**Round 2**:
- **Advocate**: "Physics critic flagged throughput (10 TPS max for blockchain). Mitigation: Use private Ethereum fork with faster consensus (100 TPS)."
- **Devil**: "Current system has... actually, current audit logs have never been tampered with in 8 years. The 'trust issue' is theoretical."

**Round 3**:
- **Advocate Steel-Man**: "Blockchain is over-engineered for this problem. Append-only logs with cryptographic signatures (WORM storage + SHA-256) achieve the same guarantee without consensus overhead."
- **Advocate Final**: "Fair point, but blockchain also provides decentralized verification — auditors can run their own nodes."
- **Devil Steel-Man**: "Current system is simple, proven, and has zero tampering incidents. WORM storage would be a cheaper incremental improvement."
- **Devil Final**: "Blockchain adds 100ms latency, 10x infrastructure cost, and operational complexity for a threat that's never materialized. WORM storage solves the actual problem."

**Judgment**:
```json
{
  "innovation_defense_strength": 4.0,
  "status_quo_weakness_exposed": 3.0,
  "risk_mitigation_quality": 5.0,
  "debate_winner": "status_quo",
  "key_insight": "This is 'innovation for innovation's sake' — the problem (log tampering) is theoretical, and simpler solutions (WORM storage) exist.",
  "residual_concerns": ["If decentralized verification is truly needed, blockchain may be justified, but that requirement wasn't established."]
}
```

**Outcome**: Dropped from portfolio or ranked lowest tier.

---

### Example 3: Close Call (Innovation Wins on Tiebreaker)

**Proposal**: "Event-Driven Microservices with Kafka"

**Round 1**:
- **Advocate**: "Decouples services, enables async processing, scales horizontally."
- **Devil**: "Current monolith has tight coupling. Every feature touches 5 modules. Deployment risk is high."

**Round 2**:
- **Advocate**: "Physics critic flagged distributed tracing complexity. Mitigation: Use OpenTelemetry from day 1."
- **Devil**: "Monolith has no tracing at all. Current debugging: grep logs for 2 hours."

**Round 3**:
- **Advocate Steel-Man**: "Microservices introduce network latency, partial failures, and eventual consistency. Monolith's in-process calls are faster and more reliable."
- **Advocate Final**: "True, but monolith's failures are total (entire app down). Microservices fail gracefully (one service down, others continue)."
- **Devil Steel-Man**: "Monolith is easier to reason about. One codebase, one deployment, one database."
- **Devil Final**: "That simplicity is why we can't scale. Monolith deploys take 3 hours and block all teams."

**Judgment**:
```json
{
  "innovation_defense_strength": 6.5,
  "status_quo_weakness_exposed": 7.0,
  "risk_mitigation_quality": 6.0,
  "debate_winner": "innovation",
  "key_insight": "This is a VERY close call. Microservices aren't a slam dunk, but monolith pain is real and worsening. Innovation wins on tiebreaker.",
  "residual_concerns": ["Team has no Kafka experience", "OpenTelemetry adds overhead"]
}
```

**Outcome**: Moderate tier in portfolio (not top, but worth exploring).

---

## Configuration & Tuning

### File: `config.yaml`

```yaml
structured_debate:
  enabled: true
  advocate_temperature: 0.6    # Creativity for pro-innovation arguments
  devil_temperature: 0.6       # Creativity for anti-status-quo arguments
  judge_temperature: 0.3       # Low variance for consistent scoring
  rounds: 3                    # Fixed (not configurable currently)
  require_steel_mans: true     # Mandatory in current implementation
```

---

### Tuning Guide

| Parameter | Default | Effect of Increasing | Effect of Decreasing |
|-----------|---------|---------------------|---------------------|
| **advocate_temperature** | 0.6 | More creative arguments, higher variance | More conservative, repetitive arguments |
| **devil_temperature** | 0.6 | More aggressive status quo critique | More measured, cautious critique |
| **judge_temperature** | 0.3 | More variance in scoring (bad) | More consistent scoring (good) |

**Recommended settings**:
- **Exploratory pipeline**: advocate_temp=0.7, devil_temp=0.7 (encourage bold arguments)
- **Production pipeline**: advocate_temp=0.6, devil_temp=0.6 (balanced)
- **Risk-averse pipeline**: advocate_temp=0.5, devil_temp=0.5 (conservative arguments)

**Don't touch**: `judge_temperature` should stay at 0.3 for score consistency.

---

### Cost Analysis

**Per debate** (7 LLM calls):
- Round 1: 2 calls × $0.05 = $0.10
- Round 2: 2 calls × $0.05 = $0.10
- Round 3: 2 calls × $0.05 = $0.10
- Judge: 1 call × $0.10 (large context) = $0.10
- **Total**: ~$0.40/debate

**Full stage** (10 proposals):
- 10 debates × $0.40 = **$4.00 total**

**Time**: ~2 minutes (with full parallelization)

**Value**: Eliminates "innovation for innovation's sake" proposals, provides detailed justification for portfolio choices, reduces downstream risk.

---

## Design Decisions

### Why 3 Rounds?

**Tested alternatives**:
- **1 round**: Too shallow, no cross-examination
- **2 rounds**: No steel-manning (critical for intellectual honesty)
- **3 rounds**: Optimal balance (opening, cross-exam, steel-man)
- **4+ rounds**: Diminishing returns, increased cost, LLMs start repeating

**Optimal**: 3 rounds cover the full argument lifecycle.

---

### Why Asymmetric (Devil Attacks Status Quo)?

**Symmetric debate**:
```
Pro-Innovation: "New architecture is better"
Anti-Innovation: "Old architecture is proven"
Judge: "Tie → stick with old"
```

**Result**: Status quo bias (innovation must be 10x better to win).

**Asymmetric debate**:
```
Pro-Innovation: "New architecture solves X"
Anti-Status-Quo: "Old architecture has fatal flaw Y"
Judge: "Both make valid points → explore innovation"
```

**Result**: Fair evaluation (innovation judged on merit, status quo doesn't get free pass).

**Why this works**: In real organizations, status quo doesn't need an advocate (inertia is its advocate). Asymmetry compensates for structural bias.

---

### Why Mandatory Steel-Manning?

**Without steel-manning**:
- Agents cherry-pick weak arguments from the other side (strawman attacks)
- Debates become performative, not truth-seeking
- Winner is determined by rhetorical skill, not proposal merit

**With steel-manning**:
- Agents must genuinely confront strongest opposing arguments
- Forces intellectual honesty ("here's the REAL reason this might fail")
- Residual concerns are real (not strawmen), so portfolio assembly can address them

**Inspired by**: Rationalist debate culture (LessWrong, SSC), Kahneman's "adversarial collaboration."

---

### Why Low Judge Temperature (0.3)?

**Experiment**:
```
Temperature 0.0: Judge always gives same scores (no discrimination between proposals)
Temperature 0.3: Consistent scoring with sensitivity to real differences
Temperature 0.7: Same debate produces scores from 6-9 randomly (unreliable)
```

**Optimal**: 0.3 balances consistency with sensitivity.

**Why consistency matters**: Portfolio assembly compares scores across proposals. If scoring is noisy, rankings are meaningless.

---

### Why Debates Don't Eliminate Proposals?

**Alternative design**: Debates as a filter (drop proposals that lose).

**Problem**:
- Judge might be wrong (LLMs aren't perfect)
- Some proposals are "high risk, high reward" (lose debate but worth exploring)
- Portfolio assembly needs diversity (conservative + radical options)

**Current design**: Debates **annotate** proposals with scores and insights. Portfolio assembly makes final elimination decisions using debate scores + critic scores + diversity considerations.

**Result**: Debates inform, they don't decide.

---

## Common Misconceptions

### ❌ "Devil's advocate attacks the proposal"

**Wrong**. Devil's advocate attacks the **status quo**. Both agents are pro-change.

**Correct framing**:
- Advocate: "This proposal is good"
- Devil: "Current approach is bad"
- Judge: "Is the proposal better than the current approach?"

---

### ❌ "Debates are adversarial"

**Wrong**. Debates are **collaborative truth-seeking**. Both agents want to find the best path forward.

**Correct framing**:
- Advocate: "Here's why this proposal works"
- Devil: "Here's why we can't stay where we are"
- Both: "Let's steel-man each other to find the truth"

---

### ❌ "Winning the debate means being in the portfolio"

**Wrong**. Debate winner is just one input to portfolio assembly.

**Portfolio considers**:
- Debate scores (innovation defense, risk mitigation)
- Physics critic scores (technical feasibility)
- Domain critic scores (security, cost, org readiness)
- Diversity (need conservative + radical options)

A proposal can lose the debate but still be top-tier if it's the only radical option with high feasibility.

---

### ❌ "Steel-manning is optional"

**Wrong**. Steel-manning is **mandatory** (enforced by schema).

**Why**: Without steel-manning, agents don't genuinely confront weaknesses. The debate becomes performative.

**Enforcement**: LLM must return a `SteelMan` object with `steel_man_of_opposition` field populated. If it refuses or gives a weak strawman, the call retries.

---

### ❌ "Judge is perfectly objective"

**Wrong**. Judge is an LLM with biases (training data, prompt phrasing, randomness).

**Mitigations**:
- Low temperature (0.3) for consistency
- Explicit tie-breaker rule (innovation-favoring)
- Structured output (forces scoring on specific dimensions)
- Human review in dashboard (users can override if judge is clearly wrong)

**Realistic expectation**: Judge is 80-90% accurate, not 100%.

---

## Future Enhancements

### 1. **Multi-Proposal Debates** (Comparative)

**Current**: Each proposal debated in isolation
**Future**: Debate pits Proposal A vs. Proposal B

**Example**:
- "Event Sourcing" vs. "CQRS with Event Streaming"
- Agents argue which solves the problem better
- Forces direct comparison (not just "is this better than status quo?")

---

### 2. **Human-in-the-Loop Interjections**

**Current**: Fully automated debates
**Future**: User can inject questions/challenges mid-debate

**Example**:
```
User: "Advocate, you claim 6-month timeline. What if the team needs 12 months?"
Advocate: "Then we'd phase it: read-only queries in month 6, writes in month 12."
```

---

### 3. **Ensemble Judging**

**Current**: Single judge
**Future**: 3 judges vote (reduces variance)

**Why**: LLMs are stochastic. Ensemble reduces noise.

**Cost**: 3× judge calls (+$0.20/debate)

---

### 4. **Debate Visualization in Dashboard**

**Current**: Debates saved to JSON
**Future**: Interactive transcript viewer with:
- Round-by-round expansion
- Score breakdown per round
- Highlight key insights and residual concerns
- Compare debates across proposals

---

## References

- **Adversarial Collaboration**: Kahneman & Klein (2009), "Conditions for Intuitive Expertise"
- **Steel-Manning**: Rationalist community (LessWrong, Slate Star Codex)
- **Asymmetric Debate**: Irving et al. (2018), "AI Safety via Debate" (OpenAI)
- **Innovation Bias**: Christensen, "The Innovator's Dilemma" (disruption requires bias toward novelty)

---

## Quick Reference

**When to Enable**: Always (core stage of pipeline)
**When to Disable**: Debugging, cost-critical experiments, pure feasibility testing (no innovation needed)
**Recommended Temperatures**: advocate=0.6, devil=0.6, judge=0.3
**Expected Outcomes**: 60-80% of debates won by innovation (system is innovation-favoring by design)
**Cost**: ~$4 per pipeline run (10 debates)
**Processing Time**: ~2 minutes (with full parallelization)
**Output**: Debate transcripts, scores, key insights, residual concerns

---

**Last Updated**: 2026-02-18
**Version**: 1.0
**Author**: Innovation Architecture Generator Team
