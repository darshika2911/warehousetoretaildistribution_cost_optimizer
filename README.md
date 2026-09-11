# Warehouse-to-Retail Distribution Cost Optimizer
A from-scratch implementation of the classical **transportation problem**,
one of the foundational models in operations research and supply-chain
network design. Given a set of supply points with fixed capacity and a
set of demand points with fixed requirements, the problem is to find the
shipment plan that minimizes total distribution cost while satisfying
every constraint exactly.
 
The code is written generically — any cost matrix, supply vector, and
demand vector can be dropped in — so while the worked example below is
framed as breweries/warehouses shipping to retail markets, the same
solver applies to plant-to-DC allocation, DC-to-store replenishment,
raw-material sourcing across suppliers, or any other bipartite
supply/demand allocation problem with linear per-unit costs.
 
## Why this problem matters
 
Distribution cost is a direct, controllable input to landed cost and
retail competitiveness, and the allocation question — *which warehouse
should serve which market, and how much* — is exactly the kind of
decision that separates a network running near its theoretical cost
floor from one leaking margin to avoidable freight spend.
 
The scale of that leakage is a live, actively debated number in India.
For years, national logistics cost was widely quoted at 13–14% of GDP,
roughly double the 6–8% typical of the US, Europe, and Japan. In 2025,
the first government-commissioned, ground-up study (DPIIT + NCAER,
built on GST network data, RBI data, and over 3,500 industry
respondents) revised that estimate down sharply, to 7.97% of GDP for
FY24, with the government stating explicitly that the older 13–14%
figures came from partial or external estimates rather than a rigorous
national accounting exercise.
 
Whichever figure is the more accurate baseline, the underlying
diagnosis behind the original estimate hasn't gone away: road
transport still dominates the freight mix despite being costlier per
tonne-km than rail or water, small firms sink a much larger share of
output value into logistics than large firms do, and government policy
continues to target single-digit logistics costs partly because
domestic distribution networks remain fragmented and warehouse
allocation is often suboptimal. Fragmented, road-heavy distribution
and suboptimal warehouse-to-retail allocation are a measurable tax on
manufacturing and FMCG competitiveness — and that's the structural
problem this project solves a scaled-down, exactly-solvable version of.
 
*Sources: PIB/DPIIT press release (Nov 2025); Economic Survey 2025–26;
NCAER, "Assessment of Logistics Cost in India."*
 
## Problem statement
 
**Given:**
- `m` supply sources (e.g. warehouses or breweries), each with fixed
  capacity `supply[i]`
- `n` demand destinations (e.g. retail markets), each with fixed
  requirement `demand[j]`
- A balanced problem: total supply = total demand
- A cost matrix `cost[i][j]` giving the per-unit shipping cost from
  source `i` to destination `j`
**Find:** a shipment quantity `x[i][j] ≥ 0` for every source–destination
pair that satisfies every supply and demand constraint exactly and
minimizes total cost `Σ cost[i][j] · x[i][j]`.
 
### Worked example used in this repo
 
| | Market 1 | Market 2 | Market 3 | Market 4 | Market 5 | **Supply** |
|---|---|---|---|---|---|---|
| **Warehouse 1** | 4 | 1 | 2 | 6 | 9 | 100 |
| **Warehouse 2** | 6 | 4 | 3 | 5 | 7 | 120 |
| **Warehouse 3** | 5 | 2 | 6 | 4 | 8 | 120 |
| **Demand** | 40 | 50 | 70 | 90 | 90 | 340 / 340 |
 
## Methods implemented
 
| Step | Method | Role |
|---|---|---|
| 1 | North-West Corner Rule (NWCR) | Fast, naive initial feasible solution — ignores cost entirely |
| 2 | Least Cost Method (LCM) | Cost-aware initial feasible solution — usually much closer to optimal |
| 3 | MODI Method (u-v / Modified Distribution) | Iterates any feasible solution to the true cost-minimum using dual variables and closed-loop reallocation |
| 4 | LP validation | Confirms the MODI answer against a generic linear-programming solver |
| 5 | Chart | Total cost comparison across the three stages |
 
*(Vogel's Approximation Method and the Stepping-Stone method were also
covered in the course this project is based on, but are intentionally
out of scope for this build.)*
 
## Results
 
| Method | Total cost |
|---|---|
| North-West Corner Rule | 1,550 |
| Least Cost Method | 1,410 |
| **MODI (optimal)** | **1,400** |
 
MODI was run starting from *both* the NWCR and the LCM initial
solutions — both converge to the same 1,400 optimal cost and the same
allocation, which is itself a correctness check: the optimum of a
linear program doesn't depend on where you start. `run_solution.py`
runs and prints this check explicitly.
 
**Optimal allocation** (Warehouse → Market, units shipped):
 
| | Market 1 | Market 2 | Market 3 | Market 4 | Market 5 |
|---|---|---|---|---|---|
| **Warehouse 1** | 10 | 50 | 40 | 0 | 0 |
| **Warehouse 2** | 0 | 0 | 30 | 0 | 90 |
| **Warehouse 3** | 30 | 0 | 0 | 90 | 0 |
 
![Cost comparison](cost_comparison.png)
 
## LP validation
 
`pulp_validation.py` builds the identical model in PuLP (minimize
`Σ cost[i][j] · x[i][j]` subject to supply and demand equality
constraints) and solves it with CBC:
 
```bash
pip install pulp
python pulp_validation.py
```
 

 
## Files
 
- `transportation_solver.py` — NWCR, LCM, and MODI implementations
  (fully generic — works with any cost matrix / supply / demand)
- `run_solution.py` — runs all three methods on the example problem
  and prints allocations, including the NWCR-vs-LCM MODI
  path-independence check
- `validate_scipy.py` — LP cross-check used during the build (works
  offline)
- `pulp_validation.py` — the PuLP validation deliverable — run locally
- `make_chart.py` — generates `cost_comparison.png`
- `cost_comparison.png` — NWCR vs LCM vs MODI-optimal chart
## How to run
 
```bash
python run_solution.py       # NWCR, LCM, MODI allocations + costs
python validate_scipy.py     # LP cross-check (works offline)
python make_chart.py         # regenerate the chart
pip install pulp && python pulp_validation.py   # PuLP deliverable validation
```
 
## Using this on a different dataset
 
Swap `COST`, `SUPPLY`, and `DEMAND` at the top of `run_solution.py` for
your own data, or import `transportation_solver` directly:
 
```python
from transportation_solver import north_west_corner, least_cost_method, modi_method, total_cost
 
cost = [[...], [...]]
supply = [...]
demand = [...]
 
initial = least_cost_method(cost, supply, demand)
optimal = modi_method(cost, supply, demand, initial)
print(total_cost(cost, optimal))
```
 
If supply and demand totals don't match, add a dummy source or
destination with zero cost before solving — `validate_balanced()`
will raise an error rather than silently returning a wrong answer.
 
