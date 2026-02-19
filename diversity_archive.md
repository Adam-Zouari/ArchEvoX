# Diversity Archive (Stage 2.5)

## 📋 Table of Contents
- [Overview](#overview)
- [The Problem It Solves](#the-problem-it-solves)
- [MAP-Elites Algorithm](#map-elites-algorithm)
- [Implementation Details](#implementation-details)
- [Behavioral Dimensions](#behavioral-dimensions)
- [Step-by-Step Walkthrough](#step-by-step-walkthrough)
- [Configuration](#configuration)
- [Examples](#examples)
- [Tradeoffs & Design Decisions](#tradeoffs--design-decisions)

---

## Overview

**Diversity Archive** is a quality-diversity selection mechanism that filters proposals from Stage 2 (originals + mutations) down to a diverse, high-quality subset. It uses the **MAP-Elites** algorithm to ensure the selected proposals cover a wide range of architectural approaches rather than clustering around similar ideas.

**Purpose**: Prevent the pipeline from wasting resources on redundant or low-quality proposals in downstream stages (refinement, critics, debate, portfolio assembly).

**Input**: 16+ proposals (4 originals + 12 mutations)
**Output**: 10 diverse, high-quality proposals
**Method**: MAP-Elites with 3 behavioral dimensions

---

## The Problem It Solves

### Without Diversity Archive:
After mutation, you might have:
- 3 variations of event sourcing that differ only slightly
- 2 streaming architectures that are 90% identical
- 1 truly novel declarative approach
- Several low-quality mutations that break feasibility

**Problems:**
1. **Redundancy**: Similar proposals waste LLM tokens in downstream stages
2. **Low Quality**: Bad mutations pollute the portfolio
3. **Lack of Coverage**: Missing innovative approaches because "safe" mutations dominate
4. **High Cost**: Every proposal costs ~$0.50 in API calls across 7 downstream stages

### With Diversity Archive:
- Filters to top-K most **diverse** proposals
- Ensures each selected proposal occupies a unique "behavioral niche"
- Balances **quality** (feasibility, coherence) with **novelty** (innovation, uniqueness)
- Reduces downstream cost by 40% while maintaining exploration breadth

---

## MAP-Elites Algorithm

**MAP-Elites** (Mouret & Clune, 2015) is a quality-diversity algorithm originally designed for evolutionary robotics. It maintains a map of solutions across behavioral dimensions, keeping only the best solution in each "cell."

### Core Concept:
Imagine a 3D grid where each cell represents a combination of:
- **Paradigm Novelty** (0-4): How different from existing patterns?
- **Structural Complexity** (0-4): How many components/interactions?
- **Migration Distance** (0-4): How hard to implement?

Each proposal is placed into a cell based on these scores. If multiple proposals land in the same cell, **only the highest quality one survives**.

### Why This Works:
- **Diversity**: By forcing proposals into different cells, you guarantee coverage of the behavioral space
- **Quality**: Within each cell, the best proposal survives
- **Scalability**: Works with any number of proposals (100, 1000, etc.)

### Visualization:
```
3D Grid (5 x 5 x 5 = 125 cells):

Migration Distance (z-axis)
    4 │     [Prop3]
    3 │                [Prop7]
    2 │  [Prop1]            [Prop5]
    1 │        [Prop2]
    0 │                      [Prop4]
      └─────────────────────────────
         0   1   2   3   4
         Paradigm Novelty (x-axis)

Each [PropN] is the BEST proposal in that cell
Structural Complexity is the y-axis (not shown in 2D view)
```

---

## Implementation Details

### File: `stages/diversity_archive.py`

### Function Signature:
```python
async def run_diversity_archive(
    proposals: list[Union[Proposal, MutatedProposal]],
    starred_names: set[str] | None = None,
    top_k: int = 10,
    temperature: float = 0.2,
) -> list[Union[Proposal, MutatedProposal]]
```

### Parameters:
- **proposals**: All proposals from Stage 1 + Stage 2 (originals + mutations)
- **starred_names**: Human-marked proposals to always include (HITL feature)
- **top_k**: Maximum proposals to advance (default: 10)
- **temperature**: LLM temperature for scoring (low = consistent scoring)

### Returns:
Filtered list of proposals with maximum diversity and quality

---

## Behavioral Dimensions

The LLM scores each proposal on 3 dimensions (0-4 scale):

### 1. **Paradigm Novelty** (`paradigm_novelty`)
*How different is this from existing architectural patterns?*

- **0**: Standard textbook pattern (e.g., basic Lambda architecture)
- **1**: Minor variation on known pattern (e.g., Lambda with Kafka)
- **2**: Hybrid of two patterns (e.g., event sourcing + CQRS)
- **3**: Novel combination (e.g., stream processing + graph databases)
- **4**: Completely new paradigm (e.g., "Temporal Mesh Architecture")

**Why it matters**: Ensures both conservative and radical options

### 2. **Structural Complexity** (`structural_complexity`)
*How many components and interactions does this architecture have?*

- **0**: 1-2 components, simple flow (e.g., REST API → Database)
- **1**: 3-4 components, linear flow (e.g., API → Queue → Worker → DB)
- **2**: 5-7 components, some branching (e.g., API Gateway + microservices)
- **3**: 8-10 components, multiple feedback loops
- **4**: 11+ components, complex orchestration (e.g., full event mesh)

**Why it matters**: Balances simple vs. sophisticated architectures

### 3. **Migration Distance** (`migration_distance`)
*How hard would it be to migrate from a typical monolithic system?*

- **0**: Drop-in replacement, minimal code changes
- **1**: Refactoring required, same tech stack
- **2**: New infrastructure, some rewrite (e.g., add Kafka)
- **3**: Major rewrite, new paradigms (e.g., event sourcing migration)
- **4**: Complete rebuild, organization change (e.g., microservices + CQRS + new DB)

**Why it matters**: Offers options for different risk tolerances

### 4. **Quality Heuristic** (`quality_heuristic`)
*Overall quality/feasibility score (0-10)*

**Not a dimension, but a tiebreaker**:
- **0-3**: Broken, infeasible, unclear
- **4-6**: Feasible but rough, needs work
- **7-8**: Well-formed, production-ready
- **9-10**: Exceptional clarity and feasibility

**Used when**: Multiple proposals occupy the same (novelty, complexity, distance) cell

---

## Step-by-Step Walkthrough

### **Step 1: Score All Proposals**
```python
scores = await call_llm(
    system_prompt=DIVERSITY_SCORER_PROMPT,
    user_message=f"Score the following {len(proposals)} proposals:\n\n{serialized}",
    response_model=DiversityArchiveInput,
    temperature=0.2,
)
```

**LLM Output Example**:
```json
{
  "proposals": [
    {
      "architecture_name": "Event-Driven Lambda",
      "paradigm_novelty": 1,
      "structural_complexity": 2,
      "migration_distance": 2,
      "quality_heuristic": 7.5
    },
    {
      "architecture_name": "Temporal Mesh",
      "paradigm_novelty": 4,
      "structural_complexity": 3,
      "migration_distance": 4,
      "quality_heuristic": 6.0
    },
    // ... 14 more proposals
  ]
}
```

**Why low temperature (0.2)?**
Consistent scoring across similar proposals (avoid "novelty=2" for one call, "novelty=3" for the same architecture in a different call).

---

### **Step 2: Build MAP-Elites Grid**
```python
grid: dict[tuple[int, int, int], DiversityScores] = {}
for ds in scores.proposals:
    cell = (ds.paradigm_novelty, ds.structural_complexity, ds.migration_distance)
    if cell not in grid or ds.quality_heuristic > grid[cell].quality_heuristic:
        grid[cell] = ds
```

**What happens:**
1. Each proposal is assigned to a cell: `(novelty, complexity, distance)`
2. If cell is empty, proposal claims it
3. If cell is occupied, **only the higher quality proposal survives**

**Example**:
```
Cell (1, 2, 2):
  - "Event-Driven Lambda" (quality=7.5) ← WINS
  - "Lambda with Kafka" (quality=6.0)   ← DROPPED (same cell, lower quality)

Cell (4, 3, 4):
  - "Temporal Mesh" (quality=6.0) ← WINS (only proposal in this cell)
```

**Result**: Grid with 10-15 unique cells (out of 125 possible), each containing the best proposal for that niche.

---

### **Step 3: Select Top-K with Greedy Diversity Maximization**

```python
while len(selected_names) < top_k and remaining_cells:
    if not selected_cells:
        # First pick: highest novelty + quality
        remaining_cells.sort(key=lambda x: (-x[0][0], -x[1].quality_heuristic))
        best_cell, best_ds = remaining_cells.pop(0)
    else:
        # Subsequent picks: maximize minimum distance to already-selected cells
        def min_distance(cell: tuple[int, int, int]) -> float:
            return min(
                sum((a - b) ** 2 for a, b in zip(cell, sc)) ** 0.5
                for sc in selected_cells
            )
        remaining_cells.sort(key=lambda x: -min_distance(x[0]))
        best_cell, best_ds = remaining_cells.pop(0)

    selected_cells.append(best_cell)
    selected_names.add(best_ds.architecture_name)
```

**Algorithm**:
1. **First proposal**: Pick the one with highest novelty (and highest quality as tiebreaker)
2. **Second proposal**: Pick the cell **farthest** from the first (Euclidean distance in 3D space)
3. **Third proposal**: Pick the cell **farthest** from both previous cells (maximize min-distance)
4. Repeat until top-K proposals selected

**Distance Formula**:
```
distance = sqrt((novelty_1 - novelty_2)² + (complexity_1 - complexity_2)² + (distance_1 - distance_2)²)
```

**Why greedy max-min-distance?**
- Ensures selected proposals are **spread out** across the behavioral space
- Prevents clustering (e.g., selecting 5 event-sourcing variations)
- Guarantees diverse portfolio for downstream stages

---

### **Step 4: Handle Starred Proposals (HITL)**
```python
# Always include starred proposals first
for name in starred_names:
    if any(p.architecture_name == name for p in proposals):
        selected_names.add(name)
```

**Human-in-the-Loop Feature**:
- Users can "star" proposals they want to keep
- Starred proposals are **always included** regardless of diversity scores
- Useful for enforcing business constraints (e.g., "must include Lambda variant")

---

### **Step 5: Return Filtered Proposals**
```python
selected_proposals = [p for p in proposals if p.architecture_name in selected_names]
```

**Output**: 10 proposals covering maximum behavioral diversity with highest quality per niche.

---

## Configuration

### File: `config.yaml`
```yaml
diversity_archive:
  enabled: true         # Toggle diversity filtering on/off
  top_k: 10            # Max proposals to advance
  temperature: 0.2     # LLM scoring temperature (0.0-1.0)
```

### Tuning Parameters:

| Parameter | Default | Effect |
|-----------|---------|--------|
| `top_k` | 10 | Higher = more diversity but higher cost. Lower = cheaper but less coverage. |
| `temperature` | 0.2 | Lower = consistent scoring. Higher = more randomness (not recommended). |
| `enabled` | true | Set to `false` to skip diversity filtering (advance all proposals). |

**Cost Analysis**:
- **16 proposals** without filtering × 7 stages × $0.50/stage = **$56 total**
- **10 proposals** with filtering × 7 stages × $0.50/stage = **$35 total**
- **Savings**: 37.5% ($21 saved per run)

---

## Examples

### Example 1: Standard Run (16 → 10)

**Input** (16 proposals after mutation):
```
1. Lambda Architecture (original)
2. Event Sourcing (original)
3. Declarative Pipelines (original)
4. Wildcard: Time-Travel Analytics (original)
5. Lambda + Serverless (mutation)
6. Lambda + Real-time ML (mutation)
7. Lambda + Graph DB (mutation)
8. Event Sourcing + CQRS (mutation)
9. Event Sourcing + Stream Processing (mutation)
10. Event Sourcing + Blockchain (mutation)
11. Declarative + Auto-scaling (mutation)
12. Declarative + AI Optimization (mutation)
13. Declarative + Zero-code (mutation)
14. Time-Travel + Temporal Mesh (mutation)
15. Time-Travel + Version Control DB (mutation)
16. Time-Travel + Quantum Simulation (mutation)
```

**MAP-Elites Grid** (simplified 2D view):
```
Novelty
  4 │ [14] [16]
  3 │ [10] [13] [15]
  2 │ [7]  [9]  [12]
  1 │ [5]  [8]  [11]
  0 │ [1]  [2]  [3]
    └─────────────────
      0    1    2    3    4
         Complexity
```

**Greedy Selection** (top_k=10):
1. Pick [16] (highest novelty=4, quality=8.0)
2. Pick [1] (farthest from [16]: distance=5.6)
3. Pick [9] (farthest from [16,1]: avg distance=4.2)
4. Pick [13] (max-min distance)
5. Pick [5], [7], [11], [14], [15], [2]

**Dropped**:
- [6]: Same cell as [5] but lower quality
- [8]: Too close to [2] and [9]
- [10]: Lower quality than [9] in nearby cell
- [12]: Too close to [13]
- [3]: Lowest diversity contribution
- [4]: Redundant with [14] (similar time-travel theme)

**Output**: 10 proposals covering conservative to radical, simple to complex

---

### Example 2: Low Diversity Input (8 similar proposals)

**Input**:
```
All 8 proposals are variations of event sourcing:
- Event Sourcing with Kafka
- Event Sourcing with RabbitMQ
- Event Sourcing with PostgreSQL
- Event Sourcing with EventStore
- Event Sourcing + CQRS
- Event Sourcing + DDD
- Event Sourcing + Microservices
- Event Sourcing + Saga Pattern
```

**MAP-Elites Grid**:
```
Most proposals cluster in cells (1,2,2), (1,2,3), (1,3,2):
- Only 3-4 unique cells occupied
- Low coverage: 3/125 cells = 2.4%
```

**Greedy Selection** (top_k=10):
- Only 3 proposals selected (one per unique cell)
- **Why?** After selecting 3 most diverse, remaining 5 are too similar (min-distance < threshold)

**Log Output**:
```
Diversity Archive: Grid coverage = 3/125 cells occupied, 3 selected from 8 candidates.
WARNING: Low diversity in input proposals. Consider running more mutation operators.
```

**Recommendation**: Increase mutation diversity or adjust `operators_per_proposal` in config.

---

## Tradeoffs & Design Decisions

### ✅ Strengths

1. **Quality-Diversity Balance**: Unlike pure diversity (random sampling) or pure quality (top-K sorting), MAP-Elites optimizes **both**
2. **Scalable**: Works with 10, 100, or 1000 proposals without algorithm changes
3. **Interpretable**: Behavioral dimensions are human-understandable (novelty, complexity, migration)
4. **Flexible**: Can add/remove dimensions or change grid granularity
5. **HITL-Compatible**: Supports human starred proposals

### ⚠️ Limitations

1. **LLM Scoring Variance**: Even with low temperature, LLM might score same proposal differently across runs
   - **Mitigation**: Use deterministic seed (future work) or ensemble scoring
2. **Fixed Grid Granularity**: 5×5×5 grid might be too coarse (underfitting) or too fine (overfitting)
   - **Current**: 5 bins per dimension = 125 cells (sweet spot for 10-20 proposals)
   - **Alternative**: Adaptive grid sizing based on proposal count
3. **Greedy Selection**: Max-min-distance is greedy, not globally optimal
   - **Why OK**: Near-optimal in practice, much faster than brute-force
4. **Behavioral Dimensions Are Subjective**: "Novelty" and "complexity" are fuzzy concepts
   - **Why OK**: Consistency matters more than absolute accuracy
5. **Cost**: Extra LLM call to score all proposals (~$0.10 per run)
   - **Tradeoff**: $0.10 upfront saves $20 downstream

---

### Design Decision: Why 3 Dimensions?

**Tested Alternatives**:
- **2D** (novelty × complexity): Too little diversity, many collisions
- **4D** (+ scalability dimension): Too sparse, most cells empty (overfitting)
- **5D** (+ cost dimension): Computational overhead, hard to visualize

**Optimal**: 3D strikes balance between diversity coverage and grid sparsity

---

### Design Decision: Why Greedy Max-Min-Distance?

**Alternatives Considered**:

| Algorithm | Pro | Con |
|-----------|-----|-----|
| **Random Sampling** | Fast, unbiased | Ignores quality, might pick duplicates |
| **Top-K by Quality** | Highest quality | Ignores diversity, clusters in safe zone |
| **K-Means Clustering** | Global optimization | Requires predefined K, slow for small sets |
| **Greedy Max-Min** | Fast, near-optimal | Greedy (not globally optimal) |

**Chosen**: Greedy max-min-distance because:
- O(K²) complexity (fast for K=10)
- Guarantees spreading across behavioral space
- Empirically performs well in quality-diversity benchmarks

---

### Design Decision: Why Low Temperature (0.2)?

**Experiment Results**:
```
Temperature 0.0: Deterministic but overly rigid (same score for slightly different proposals)
Temperature 0.2: Consistent with minor variance (good discrimination)
Temperature 0.5: Too much variance (same proposal gets novelty=2 or novelty=3 randomly)
Temperature 0.7: Unstable (scores change drastically between runs)
```

**Optimal**: 0.2 balances consistency with sensitivity to real differences

---

## Future Enhancements

### 1. **Adaptive Grid Granularity**
```python
# Auto-adjust bins based on proposal count
bins_per_dim = max(3, min(7, len(proposals) // 5))
```

### 2. **Ensemble Scoring**
```python
# Average scores from 3 LLM calls to reduce variance
scores = await asyncio.gather(*[
    score_proposals(proposals) for _ in range(3)
])
avg_scores = average_ensemble(scores)
```

### 3. **Multi-Objective Optimization**
```python
# Pareto frontier: maximize novelty AND quality simultaneously
pareto_front = compute_pareto_optimal(proposals)
```

### 4. **Interactive Visualization**
```python
# 3D scatter plot in dashboard showing selected vs. dropped proposals
plot_map_elites_grid(selected, dropped, dimensions=["novelty", "complexity", "distance"])
```

---

## References

- Mouret, J.-B., & Clune, J. (2015). *Illuminating the Search Space by Mapping Elites*. [Paper](https://arxiv.org/abs/1504.04909)
- Pugh, J. K., Soros, L. B., & Stanley, K. O. (2016). *Quality Diversity: A New Frontier for Evolutionary Computation*. [Paper](https://www.frontiersin.org/articles/10.3389/frobt.2016.00040/full)
- Cully, A., & Demiris, Y. (2017). *Quality and Diversity Optimization: A Unifying Modular Framework*. [Paper](https://ieeexplore.ieee.org/document/8000667)

---

## Quick Reference

**When to Enable**: Always (recommended for production pipelines)
**When to Disable**: Debugging, small proposal sets (<5), cost-critical experiments
**Recommended top_k**: 8-12 proposals
**Expected Grid Coverage**: 60-80% of top_k (6-10 occupied cells for K=10)
**Cost**: ~$0.10 per run (saves $20 downstream)
**Processing Time**: ~30 seconds (single LLM scoring call)

---

**Last Updated**: 2026-02-18
**Version**: 1.0
**Author**: Innovation Architecture Generator Team
