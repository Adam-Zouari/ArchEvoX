# Innovation Mechanisms in Multi-Agent Architectural Design Systems

## A Research-Level Analysis of Debate, Exploration, and Paradigm-Shift Generation

---

## 1. Is Debate a Good Mechanism for Architectural Innovation?

**Short answer: It's a good mechanism for *refinement and stress-testing*, but a mediocre mechanism for *generation of novel ideas*.**

Debate-based multi-agent systems (inspired by Irving et al., 2018 and subsequent work) were originally designed for **alignment and truthfulness** — the core premise is that adversarial argumentation surfaces flaws and converges toward defensible positions. This is fundamentally a *convergent* dynamic, not a *divergent* one.

When applied to architectural innovation, debate has real strengths:

- **Stress-testing proposals**: A debate mechanism excels at finding weaknesses in a proposed architecture. If Agent A proposes replacing batch ETL with a streaming-first ECL pattern, Agent B can surface failure modes (e.g., exactly-once semantics under partition failures, state management complexity).
- **Forcing articulation of assumptions**: Debate forces each proposal agent to make its reasoning explicit, which can expose hidden assumptions that constrain thinking.
- **Preventing groupthink within a single model's reasoning trace**: Multiple agents with different priming or system prompts can surface considerations a single agent would miss.

But debate has structural limitations for innovation:

- **Adversarial pressure favors defensibility over novelty**. When an agent knows its proposal will be attacked, it is incentivized to propose ideas it can *defend*, not ideas that are maximally creative. Defensible ideas are, almost by definition, ideas grounded in established patterns.
- **Consensus pressure is inherent**. Debate mechanisms typically require some form of resolution — a judge, a vote, or convergence. This resolution step compresses the solution space toward the intersection of what multiple agents find acceptable.
- **The "Overton window" problem**. Agents trained on the same foundation model share implicit priors about what constitutes a "reasonable" architecture. Debate between such agents explores the surface of a shared latent space rather than escaping it.

**Verdict**: Use debate *downstream* of idea generation, not as the primary innovation mechanism.

---

## 2. Does Debate Increase Novelty, or Does It Converge Toward Safe Consensus?

Empirically and theoretically, **debate tends toward convergence**. Here's why:

### 2.1 The Selection Pressure Argument

In any debate system, there is implicit or explicit selection pressure on which ideas survive. This pressure has a well-known bias: **ideas that are easy to argue for survive; ideas that are hard to argue for (but potentially revolutionary) are eliminated early**. Paradigm shifts are, almost by definition, ideas that are hard to argue for within the current paradigm — they violate existing assumptions, lack precedent, and appear risky.

Consider a concrete example in your domain: an agent proposes replacing a traditional data warehouse star schema with a graph-native analytical engine that treats all data relationships as first-class citizens. In a debate:

- Critics can point to lack of enterprise tooling maturity
- Critics can cite performance benchmarks for existing columnar stores
- Critics can raise organizational readiness concerns

All of these are *valid* criticisms within the current paradigm. The graph-native proposal might be architecturally superior for the specific use case, but it will lose the debate because the burden of proof is asymmetric — **novel ideas must justify their existence against the status quo, while the status quo needs only to exist**.

### 2.2 When Debate Does Increase Novelty

There is one specific configuration where debate can enhance novelty: **when agents are explicitly assigned adversarial roles against the status quo**. If you configure the debate not as "which architecture is best?" but as "why is the current/conventional approach fundamentally wrong?", you invert the burden of proof. This is closer to a *red team* than a debate.

### 2.3 The Empirical Pattern

Multi-agent debate experiments in reasoning tasks (Du et al., 2023; Liang et al., 2023) show that debate improves *accuracy* on well-defined problems but does not increase the diversity of solution strategies. Agents converge on correct answers faster, but the set of approaches considered narrows. This is exactly the wrong dynamic for innovation.

---

## 3. Conditions Where Debate Enhances vs. Suppresses Innovation

| Condition | Effect on Innovation |
|---|---|
| Agents share the same foundation model | **Suppresses** — shared priors limit exploration |
| Debate has a single judge/arbiter | **Suppresses** — single evaluation bottleneck |
| Agents are penalized for "losing" debates | **Suppresses** — incentivizes defensibility |
| Agents are explicitly role-assigned to different paradigms | **Enhances** — forces exploration of unfamiliar territory |
| Debate is structured as critique-only (no winner) | **Enhances** — separates evaluation from generation |
| Debate includes a mandatory "steel-man the opposition" phase | **Enhances** — forces agents to find merit in unfamiliar ideas |
| The judge rewards novelty explicitly | **Enhances** — changes the optimization target |
| Debate runs on proposals generated by a separate divergent process | **Enhances** — debate refines rather than generates |

**Key insight**: Debate enhances innovation only when the debate structure is explicitly designed to resist convergence. By default, it suppresses it.

---

## 4. Do Domain-Specific Critics Reduce Radical Ideas Too Early?

**Yes, this is one of the highest-risk failure modes in your proposed architecture.**

Domain-specific critics (e.g., a "security critic," a "cost critic," a "scalability critic") are evaluative agents. Their job is to apply domain constraints to proposals. The problem is that **radical ideas almost always violate some domain constraint when first proposed**, not because they're infeasible, but because:

1. **The constraint model is calibrated to the current paradigm**. A security critic trained on conventional data pipeline security patterns will flag a novel architecture as risky simply because it's unfamiliar.
2. **Critics optimize for local feasibility, not global optimality**. A cost critic might reject a proposal that has higher upfront cost but dramatically lower total cost of ownership — because the critic evaluates against near-term budget constraints.
3. **Critics lack the ability to evaluate transformative potential**. A critic can assess whether a proposal meets current requirements, but it cannot assess whether a proposal *redefines what's possible*.

### 4.1 The Premature Pruning Problem

If critics operate on proposals *before those proposals have been fully developed*, they prune the search tree at shallow depth. A half-formed radical idea will always look worse than a fully-developed conventional one. This is the architectural equivalent of killing a seedling because it's shorter than a mature tree.

### 4.2 Mitigation Strategies

- **Delay critic evaluation**. Let proposals develop through multiple self-refinement iterations before exposing them to critics.
- **Use critics as annotators, not filters**. Critics should *label* concerns (e.g., "security: needs novel auth model") rather than *reject* proposals.
- **Weight critic feedback by paradigm-awareness**. If a critic's objection is "this doesn't fit existing patterns," that should be scored as a weak objection. If the objection is "this violates a physical constraint" (e.g., CAP theorem), that's a strong objection.
- **Separate feasibility critics from paradigm critics**. A "laws of physics" critic (CAP theorem, network latency, computational complexity) is useful early. A "current best practices" critic should only enter late.

---

## 5. Single DeepThink-Style LLM with Reflection Loops vs. Multi-Agent Debate

This is a critical comparison. Let's be precise.

### 5.1 Single-Agent Reflection (DeepThink / o1-style)

**Strengths for innovation:**
- Extended chain-of-thought can explore deeper reasoning paths
- No adversarial pressure toward defensibility
- Can maintain a coherent radical vision across many reasoning steps
- Self-critique can be gentler and more constructive than external critique
- The model can "talk itself into" a radical idea by building up supporting arguments incrementally

**Weaknesses for innovation:**
- **Mode collapse**: A single model tends to settle into familiar reasoning patterns. Its reflection loops explore the neighborhood of its initial idea rather than jumping to distant regions of the solution space.
- **Self-reinforcement**: Reflection loops can become echo chambers where the model convinces itself its initial (conventional) approach is correct.
- **Limited paradigm diversity**: A single model, no matter how capable, draws from one set of learned priors. It cannot spontaneously adopt a fundamentally different worldview.

### 5.2 Multi-Agent Without Debate (Parallel Divergent Exploration)

**Strengths for innovation:**
- Multiple agents with different system prompts/temperatures/priming can explore genuinely different regions of the solution space
- No convergence pressure if there's no resolution mechanism
- Can be combined with explicit diversity objectives

**Weaknesses for innovation:**
- Without any interaction, proposals may be incoherent or redundant
- No mechanism to build on each other's ideas (combinatorial innovation)

### 5.3 Verdict

**Neither pure single-agent reflection nor pure multi-agent debate is optimal.** The best architecture for innovation is a *hybrid* — and it's neither of these two patterns. See Section 7 for the recommended design.

For generating paradigm shifts specifically, **multi-agent parallel divergent exploration beats both debate and single-agent reflection**, provided the agents are sufficiently diverse and there is a downstream integration phase.

---

## 6. Better Architectural Patterns for Maximizing Innovation

Debate is one tool in a much larger space of innovation mechanisms. Here are the alternatives, ranked by their suitability for generating paradigm-shifting architectural proposals:

### 6.1 Evolutionary / Genetic Architecture Search

**Mechanism**: Maintain a population of architectural proposals. Apply mutation operators (swap a component, change a data flow pattern, introduce a new abstraction layer). Evaluate fitness. Select, crossbreed, mutate, repeat.

**Strengths**:
- Naturally explores large search spaces
- Mutation operators can produce genuinely novel combinations
- No convergence toward "defensible" — fitness is the only selection criterion
- Can discover non-obvious compositions that no single agent would propose

**Weaknesses**:
- Requires a well-defined fitness function (hard for "innovation")
- Many generations needed for complex architectures
- Mutations may produce incoherent architectures without domain-aware operators

**Suitability for your use case**: **High**, especially if you use LLM agents as the mutation/crossover operators (they can make semantically meaningful mutations, not random ones).

### 6.2 MAP-Elites / Quality-Diversity Search

**Mechanism**: Instead of optimizing for a single best solution, maintain a map of diverse high-quality solutions across multiple dimensions (e.g., cost vs. latency vs. paradigm novelty). Fill every cell of this map with the best solution found for that combination of characteristics.

**Strengths**:
- **Explicitly optimizes for diversity**, not just quality
- Maintains radical solutions alongside conservative ones
- Prevents convergence by design
- Produces a portfolio of architectures rather than a single recommendation

**Weaknesses**:
- Requires defining the behavioral dimensions of the map
- Computationally expensive

**Suitability for your use case**: **Very high**. This is arguably the most promising approach for your stated goal. You could define dimensions like: `paradigm_novelty × cost × complexity × migration_difficulty` and maintain the best architecture found for each cell.

### 6.3 Stochastic Idea Exploration with Temperature Scheduling

**Mechanism**: Run multiple LLM agents at very high temperature (high randomness) for initial ideation, then progressively reduce temperature as ideas are refined. This mirrors simulated annealing.

**Strengths**:
- High temperature naturally produces diverse and unexpected outputs
- Temperature scheduling provides a smooth transition from exploration to exploitation
- Simple to implement

**Weaknesses**:
- High-temperature outputs are often incoherent, not innovative
- Temperature is a blunt instrument — it increases randomness uniformly rather than targeting creative dimensions

**Suitability**: **Moderate**. Useful as a component but not sufficient alone.

### 6.4 Idea Mutation Loops (Conceptual Blending)

**Mechanism**: Start with a set of known architectural patterns. Apply structured transformations: "What if we inverted the data flow?", "What if we merged these two stages?", "What if we replaced this synchronous step with an event-driven one?", "What if we applied [pattern from domain X] to this problem?"

**Strengths**:
- Produces semantically meaningful novelty (not random noise)
- Cross-domain analogy transfer is one of the most powerful innovation mechanisms in human cognition
- Can be implemented as structured prompts to LLM agents

**Weaknesses**:
- Limited by the set of transformation operators
- May not produce truly *paradigm*-shifting ideas, only novel combinations

**Suitability**: **High**. Especially powerful when combined with cross-domain knowledge injection.

### 6.5 Exploration/Exploitation Phase Separation

**Mechanism**: Explicitly separate the system into two phases with different dynamics:

- **Phase 1 (Exploration)**: Maximum divergence. Multiple agents generate radical proposals with no filtering. Reward novelty. No critics. No debate. High temperature. Cross-domain analogies. Mutation operators. The goal is to produce a large, diverse set of candidates.
- **Phase 2 (Exploitation)**: Convergent refinement. Apply critics. Run debates. Evaluate feasibility. Optimize the most promising candidates from Phase 1.

**Strengths**:
- Cleanly separates the innovation objective from the feasibility objective
- Prevents premature convergence by design
- Each phase can use the mechanism best suited to its goal

**Weaknesses**:
- The transition between phases requires careful design
- Risk of Phase 2 discarding all Phase 1 innovations

**Suitability**: **Very high**. This is the foundation of the recommended architecture below.

### 6.6 Comparative Summary

| Mechanism | Novelty Generation | Paradigm Shifts | Feasibility | Convergence Risk |
|---|---|---|---|---|
| Multi-agent debate | Low-Medium | Low | High | High |
| Single-agent reflection | Medium | Medium | Medium | Medium |
| Evolutionary search | High | Medium-High | Medium | Low |
| MAP-Elites / QD | Very High | High | Medium | Very Low |
| Temperature scheduling | Medium | Low-Medium | Low | Low |
| Idea mutation loops | High | Medium | Medium | Low |
| Exploration/exploitation separation | Very High | Very High | High (in Phase 2) | Low |

---

## 7. Recommended System Architecture for Maximum Architectural Innovation

Based on the analysis above, here is the recommended multi-agent architecture. It combines exploration/exploitation phase separation, quality-diversity search, idea mutation, and targeted use of debate.

### 7.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: DIVERGENT EXPLORATION                │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Paradigm  │ │ Paradigm  │ │ Paradigm  │ │ Wildcard  │          │
│  │ Agent A   │ │ Agent B   │ │ Agent C   │ │ Agent     │          │
│  │ (Stream-  │ │ (Event-   │ │ (Graph-   │ │ (Cross-   │          │
│  │  first)   │ │  sourced) │ │  native)  │ │  domain)  │          │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘        │
│        │              │              │              │              │
│        ▼              ▼              ▼              ▼              │
│  ┌────────────────────────────────────────────────────────┐      │
│  │              IDEA MUTATION ENGINE                       │      │
│  │  • Inversion operators ("what if data flows backward?")│      │
│  │  • Merge operators ("combine streaming + graph")       │      │
│  │  • Analogy operators ("apply [biology/economics/etc.]")│      │
│  │  • Abstraction operators ("generalize this pattern")   │      │
│  │  • Decomposition ("split this into micro-patterns")    │      │
│  └────────────────────┬───────────────────────────────────┘      │
│                       │                                           │
│                       ▼                                           │
│  ┌────────────────────────────────────────────────────────┐      │
│  │            DIVERSITY ARCHIVE (MAP-Elites)               │      │
│  │  Axes: paradigm_novelty × complexity × migration_cost  │      │
│  │  Retains best-in-cell across all dimensions             │      │
│  │  Prevents convergence; maintains radical proposals      │      │
│  └────────────────────┬───────────────────────────────────┘      │
│                       │                                           │
└───────────────────────┼───────────────────────────────────────────┘
                        │
                        ▼  TOP-K DIVERSE CANDIDATES
┌───────────────────────┼───────────────────────────────────────────┐
│                    PHASE 2: REFINEMENT & STRESS-TESTING           │
│                       │                                           │
│                       ▼                                           │
│  ┌────────────────────────────────────────────────────────┐      │
│  │           SELF-REFINEMENT LOOPS (per candidate)        │      │
│  │  Each candidate gets N rounds of self-improvement      │      │
│  │  via single-agent reflection before facing critics     │      │
│  └────────────────────┬───────────────────────────────────┘      │
│                       │                                           │
│                       ▼                                           │
│  ┌────────────────────────────────────────────────────────┐      │
│  │           PHYSICS CRITICS (hard constraints only)       │      │
│  │  • CAP theorem compliance                              │      │
│  │  • Computational complexity bounds                     │      │
│  │  • Network physics (latency, bandwidth)                │      │
│  │  Mode: ANNOTATE, not REJECT                            │      │
│  └────────────────────┬───────────────────────────────────┘      │
│                       │                                           │
│                       ▼                                           │
│  ┌────────────────────────────────────────────────────────┐      │
│  │         STRUCTURED DEBATE (surviving candidates)        │      │
│  │  • Each candidate gets an advocate agent                │      │
│  │  • Devil's advocate assigned to status quo              │      │
│  │  • Judge scores on: innovation + feasibility + fit      │      │
│  │  • Mandatory steel-manning of radical proposals         │      │
│  └────────────────────┬───────────────────────────────────┘      │
│                       │                                           │
│                       ▼                                           │
│  ┌────────────────────────────────────────────────────────┐      │
│  │         DOMAIN CRITICS (soft constraints)               │      │
│  │  • Security, cost, org readiness, tooling maturity      │      │
│  │  • Mode: ANNOTATE with severity + mitigation hints      │      │
│  │  • Cannot veto; only score and flag                     │      │
│  └────────────────────┬───────────────────────────────────┘      │
│                       │                                           │
│                       ▼                                           │
│  ┌────────────────────────────────────────────────────────┐      │
│  │         OUTPUT: RANKED PORTFOLIO OF ARCHITECTURES       │      │
│  │  • Conservative option (low risk, incremental)          │      │
│  │  • Moderate innovation option (proven novel patterns)   │      │
│  │  • Radical option (paradigm shift, higher risk)         │      │
│  │  Each with: rationale, risk profile, migration path     │      │
│  └────────────────────────────────────────────────────────┘      │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### 7.2 Key Design Decisions Explained

**Why multiple paradigm agents instead of one general agent?**
Each paradigm agent is primed with a different architectural worldview via its system prompt. Agent A believes streaming is the answer to everything. Agent B thinks in terms of event sourcing and CQRS. Agent C reasons about data as graphs. The wildcard agent is explicitly instructed to draw analogies from non-software domains (biological systems, supply chains, financial markets). This structural diversity is more reliable than hoping a single agent will spontaneously explore multiple paradigms.

**Why a mutation engine?**
LLM agents, even with diverse priming, tend to propose architectures they've seen in training data. The mutation engine applies *structural transformations* to proposals: inverting data flow direction, merging pipeline stages, replacing synchronous with asynchronous patterns, applying abstractions from other domains. This produces candidates that no single agent would propose directly. Critically, the mutation operators are themselves LLM-powered — they understand the semantics of what they're transforming, unlike random mutation in traditional genetic algorithms.

**Why MAP-Elites instead of tournament selection?**
Tournament selection (pick the best) converges. MAP-Elites (fill a grid of diverse niches) explicitly maintains diversity. A radical proposal that scores poorly on "ease of migration" but highly on "paradigm novelty" is preserved in its niche rather than being eliminated. This is essential for ensuring that paradigm shifts survive to Phase 2.

**Why self-refinement before critics?**
A half-formed radical idea will always lose to a well-developed conventional one. Giving each candidate several rounds of self-improvement before critic exposure allows radical ideas to develop their supporting arguments, address obvious objections, and articulate their value proposition. This levels the playing field.

**Why annotate-not-reject critics?**
Critics that can reject proposals create a kill zone for innovation. Critics that annotate ("this has a security concern of severity 3; possible mitigation: X") preserve information without pruning the search tree. The final ranking can weight these annotations, but no single critic can veto.

**Why debate is placed late and structured asymmetrically?**
Debate enters only after proposals are well-developed and after hard-constraint critics have already flagged genuinely impossible ideas. The debate is structured to favor innovation: the devil's advocate argues against the *status quo*, not against the novel proposals. Steel-manning is mandatory — debate participants must articulate the strongest case for each proposal before critiquing it.

**Why the output is a portfolio, not a single recommendation?**
Enterprise architectural decisions involve risk tolerance, organizational context, and strategic vision that the system cannot fully model. Presenting a portfolio with explicit risk/innovation tradeoffs lets human decision-makers choose their position on the innovation-risk frontier.

### 7.3 Prompt Architecture for Paradigm Agents

Each paradigm agent should receive a system prompt structured as:

```
You are an architect who believes deeply that [PARADIGM X] is the 
future of data systems. Your job is NOT to be balanced — it is to 
make the strongest possible case for a [PARADIGM X]-native architecture 
for the given requirements.

You should:
- Challenge every assumption in the current architecture
- Identify where conventional patterns are holding the system back
- Propose the most ambitious version of your paradigm that could work
- Explicitly name what would need to be true for your proposal to succeed
- Ignore "but we've always done it this way" objections

You should NOT:
- Hedge or qualify your proposal with "but the conventional approach 
  might be safer"
- Self-censor radical ideas because they seem impractical
- Optimize for ease of argumentation
```

The wildcard agent gets a different prompt:

```
You are a systems thinker who draws inspiration from non-software 
domains. For the given data pipeline requirements, propose an 
architecture inspired by:
- Biological systems (neural networks, immune systems, evolutionary 
  processes, cellular signaling)
- Economic systems (market mechanisms, auction theory, supply chains)
- Physical systems (thermodynamics, fluid dynamics, network theory)
- Social systems (swarm intelligence, stigmergy, consensus protocols)

Your proposal should be a genuine architectural design, not a metaphor.
Translate the cross-domain insight into concrete technical components,
data flows, and system behaviors.
```

### 7.4 Mutation Operators (Examples for Data Pipeline Architectures)

| Operator | Description | Example |
|---|---|---|
| **Invert** | Reverse the direction of a data flow or control flow | Push-based → Pull-based; Producer-driven → Consumer-driven |
| **Merge** | Combine two previously separate stages | Merge transformation and loading into a single atomic operation |
| **Split** | Decompose a monolithic stage into independent units | Split a single transformation step into a DAG of micro-transforms |
| **Substitute** | Replace a component with one from a different paradigm | Replace message queue with a shared log (Kafka-style) |
| **Abstract** | Generalize a specific pattern into a higher-order one | Replace specific ETL jobs with a declarative pipeline DSL |
| **Analogize** | Apply a pattern from another domain | Apply biological immune system pattern → self-healing pipeline with anomaly detection agents |
| **Eliminate** | Remove a stage entirely and ask "what if this didn't exist?" | What if there's no staging area? What if there's no batch window? |
| **Temporalize** | Change the temporal model of a component | Batch → Streaming; Polling → Event-driven; Synchronous → Eventual |

---

## 8. Risks of Over-Convergence and Mitigation Strategies

### 8.1 Risk: Shared Foundation Model Priors

**Problem**: All agents share the same training data and therefore the same implicit beliefs about what constitutes a good architecture.

**Mitigation**:
- Use different foundation models for different agents where possible (e.g., Claude for some, GPT for others, Gemini for others, open-source models for the wildcard).
- Inject explicit knowledge about unconventional architectures via RAG — feed agents papers, blog posts, and case studies about paradigm-breaking systems.
- Use few-shot examples of radical architectural proposals (not just conventional ones) in agent prompts.

### 8.2 Risk: Evaluation Function Rewards Convention

**Problem**: If the judge or ranking system is itself an LLM, it will tend to rate conventional architectures higher because they match more of its training data.

**Mitigation**:
- Include "paradigm novelty" as an explicit, weighted dimension in the evaluation.
- Calibrate novelty scoring: use embedding distance from a set of known conventional patterns as a proxy for structural novelty.
- Human-in-the-loop for final selection, with the system presenting its innovation score alongside feasibility scores.

### 8.3 Risk: Premature Feasibility Filtering

**Problem**: Hard constraints are applied before ideas are fully developed, killing innovation.

**Mitigation**:
- Phase separation (as described in the architecture above).
- Self-refinement loops before any external evaluation.
- Annotate-not-reject critic design.

### 8.4 Risk: Innovation Theater

**Problem**: The system produces proposals that *appear* novel (different terminology, unfamiliar framing) but are structurally equivalent to conventional architectures.

**Mitigation**:
- Evaluate novelty at the structural level, not the naming level. Use a dedicated "structural analysis" agent that reduces proposals to their fundamental data flow graphs and compares them.
- Define novelty metrics: graph edit distance from conventional patterns, number of novel component types, number of conventional assumptions violated.

### 8.5 Risk: Incoherent Radical Proposals

**Problem**: The system generates ideas that are novel but architecturally incoherent — they sound interesting but couldn't actually work.

**Mitigation**:
- Self-refinement loops (the agent must make its proposal internally consistent before external review).
- "Physics critics" that check hard constraints (CAP, complexity bounds) catch genuine impossibilities.
- Require each proposal to include a concrete data flow diagram, not just prose description. Force structural specificity.

---

## 9. Implementation Recommendations

### 9.1 Minimum Viable Version

If you want to start with a simpler system and iterate:

1. **3 paradigm agents** with strongly differentiated system prompts + 1 wildcard agent
2. **1 mutation round**: take each agent's output, apply 2-3 mutation operators, generate variants
3. **Self-refinement**: 2 rounds of self-critique and improvement per proposal
4. **Physics critic**: single pass, annotate-only
5. **Human ranking** of the resulting portfolio

This gives you most of the innovation benefit without the complexity of MAP-Elites or full evolutionary search.

### 9.2 Full Version

The complete architecture described in Section 7, with:
- 4-6 paradigm agents
- Mutation engine with all operators
- MAP-Elites diversity archive
- 3-5 rounds of self-refinement
- Tiered critics (physics → debate → domain)
- Automated portfolio ranking with human-in-the-loop selection

### 9.3 Instrumentation

To measure whether your system is actually innovating:

- **Structural novelty score**: Graph edit distance of proposed architectures from a library of known patterns.
- **Paradigm violation count**: Number of conventional assumptions explicitly violated by a proposal.
- **Diversity metrics across the portfolio**: Pairwise embedding distance between proposals in a run.
- **Human expert surprise rating**: Have architects rate "did this proposal suggest something I wouldn't have thought of?"

---

## 10. Summary of Core Principles

1. **Separate generation from evaluation.** Innovation requires divergent thinking; evaluation requires convergent thinking. Don't mix them.

2. **Debate is a refinement tool, not a generation tool.** Use it late, use it asymmetrically (devil's advocate against the status quo), and never let it veto radical ideas.

3. **Diversity must be structural, not cosmetic.** Use genuinely different agent priming, mutation operators, and cross-domain analogies — not just different temperatures on the same prompt.

4. **Critics annotate; they don't reject.** Especially domain-specific critics. Only hard physical constraints (CAP theorem, etc.) should have kill authority, and even then, only after self-refinement.

5. **Maintain a portfolio, not a single answer.** The system's job is to present the innovation-risk frontier, not to make the decision.

6. **Measure novelty explicitly.** If you don't measure it, the system will optimize for what it can measure — which will be feasibility, cost, and convention.

7. **The wildcard agent is not optional.** Cross-domain analogy transfer is one of the most reliable mechanisms for genuine paradigm shifts. Dedicate resources to it.
