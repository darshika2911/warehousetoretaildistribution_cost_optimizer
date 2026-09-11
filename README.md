# Warehouse-to-Retail Distribution Cost Optimizer

A from-scratch implementation of the classical **Transportation Problem** for optimizing warehouse-to-retail distribution decisions using Operations Research techniques.

The project determines how much product should be shipped from each warehouse to each retail market while satisfying supply and demand constraints and minimizing total distribution cost.

## Key Features

- North-West Corner Rule (NWCR) for an initial feasible solution
- Least Cost Method (LCM) for a cost-efficient initial solution
- MODI (u-v) method for iterative optimization
- Degeneracy handling and explicit basis management
- Automatic balancing of unbalanced supply-demand networks
- Route-level sensitivity analysis
- Warehouse capacity sensitivity analysis
- What-if scenario analysis
- External sourcing / shortage-cost modeling
- Independent LP validation using SciPy and PuLP/CBC
- 22 automated tests

## Why This Problem Matters

Distribution cost directly affects landed cost, margins, and retail competitiveness.

A fundamental supply-chain question is:

> Which warehouse should serve which market, and how much should each warehouse ship?

Poor allocation can create unnecessary transportation costs even when total supply and demand are satisfied. This project models that decision as a classical transportation optimization problem and finds a minimum-cost shipment plan subject to supply and demand constraints.

The model can also evaluate operational changes such as:

- Warehouse capacity reductions
- Demand increases
- Transportation-cost changes
- Warehouse closures
- External sourcing requirements

This extends the project beyond finding a single optimal allocation toward evaluating distribution-network resilience and cost sensitivity.

## Problem Formulation

Given:

- `m` supply sources such as warehouses
- `n` demand destinations such as retail markets
- `supply[i]` as the capacity of source `i`
- `demand[j]` as the requirement of destination `j`
- `cost[i][j]` as the per-unit transportation cost from source `i` to destination `j`

The decision variable is:

$$x_{ij} \geq 0$$

The objective is to minimize:

$$\min \sum_{i=1}^{m}\sum_{j=1}^{n} c_{ij}x_{ij}$$

subject to the supply constraints:

$$\sum_{j=1}^{n}x_{ij}=s_i$$

and demand constraints:

$$\sum_{i=1}^{m}x_{ij}=d_j$$

For a balanced transportation problem:

$$\sum_i s_i = \sum_j d_j$$

If supply and demand are unequal, the project automatically adds a dummy source or destination to balance the network.

## Worked Example

The example uses a 3-warehouse × 5-market network.

|  | Market 1 | Market 2 | Market 3 | Market 4 | Market 5 | Supply |
|---|---:|---:|---:|---:|---:|---:|
| Warehouse 1 | 4 | 1 | 2 | 6 | 9 | 100 |
| Warehouse 2 | 6 | 4 | 3 | 5 | 7 | 120 |
| Warehouse 3 | 5 | 2 | 6 | 4 | 8 | 120 |
| **Demand** | **40** | **50** | **70** | **90** | **90** | **340** |

Total supply = **340 units**  
Total demand = **340 units**

Therefore, the base problem is balanced.

## Optimization Workflow

```text
Input
  │
  ├── Cost Matrix
  ├── Supply
  └── Demand
       │
       ▼
Balance Problem
       │
       ▼
Initial Feasible Solution
       │
       ├── North-West Corner Rule
       └── Least Cost Method
              │
              ▼
        MODI Optimization
              │
        ┌─────┴─────┐
        ▼           ▼
   Degeneracy    Optimality
    Handling       Check
        │           │
        └─────┬─────┘
              ▼
      Optimal Allocation
              │
       ┌──────┴───────┐
       ▼              ▼
LP Validation   Sensitivity Analysis
                       │
                       ▼
                Scenario Analysis
```

## Methods Used

| Method | Purpose |
|---|---|
| **North-West Corner Rule (NWCR)** | Generates an initial feasible transportation solution. |
| **Least Cost Method (LCM)** | Generates a cost-efficient initial feasible solution. |
| **MODI (u-v) Method** | Iteratively improves the solution until no negative reduced cost remains. |
| **Degeneracy Handling** | Maintains a valid transportation basis when fewer than `m+n-1` positive allocations exist. |
| **LP Validation** | Independently validates the custom solver using Linear Programming. |
| **Sensitivity Analysis** | Evaluates route-level and warehouse-capacity sensitivity. |
| **Scenario Analysis** | Quantifies the impact of operational and network changes. |
| **Automatic Balancing** | Handles cases where total supply and demand are unequal. |

## Results

For the worked example:

| Method | Total Cost |
|---|---:|
| North-West Corner Rule | ₹1,550 |
| Least Cost Method | ₹1,410 |
| MODI Optimal Solution | **₹1,400** |

The MODI solution reduces cost by **₹150 (9.7%)** compared with the North-West Corner starting solution.

### Optimal Allocation

|  | Market 1 | Market 2 | Market 3 | Market 4 | Market 5 |
|---|---:|---:|---:|---:|---:|
| Warehouse 1 | 10 | 50 | 40 | 0 | 0 |
| Warehouse 2 | 0 | 0 | 30 | 0 | 90 |
| Warehouse 3 | 30 | 0 | 0 | 90 | 0 |

Total transportation cost:

$$10(4)+50(1)+40(2)+30(3)+90(7)+30(5)+90(4)=₹1,400$$

The solver also reaches the same optimal cost when MODI starts from different feasible solutions, providing a useful path-independence check.

## Cost Comparison

The repository includes `cost_comparison.png`, which compares the initial feasible solutions with the final MODI solution.

![Transportation cost comparison](cost_comparison.png)

## Sensitivity Analysis

The sensitivity module evaluates the optimal network at the route and warehouse levels.

### Alternate-Optimal Route

The worked example identifies:

- **Warehouse 3 → Market 2** with reduced cost `0`

This indicates that the route can participate in an alternate optimal solution under the current model.

One verified alternate optimal allocation is:

|  | Market 1 | Market 2 | Market 3 | Market 4 | Market 5 |
|---|---:|---:|---:|---:|---:|
| Warehouse 1 | 40 | 20 | 40 | 0 | 0 |
| Warehouse 2 | 0 | 0 | 30 | 0 | 90 |
| Warehouse 3 | 0 | 30 | 0 | 90 | 0 |

Its total cost is also **₹1,400**.

### Competitive Unused Routes

Other unused routes with relatively low positive reduced costs include:

| Route | Transportation Cost | Reduced Cost |
|---|---:|---:|
| Warehouse 2 → Market 1 | 6 | 1 |
| Warehouse 2 → Market 4 | 5 | 1 |
| Warehouse 3 → Market 5 | 8 | 1 |

These routes are relatively close to becoming competitive under the current optimal basis. A positive reduced cost does not by itself guarantee that a route will become part of an alternate optimum.

## Scenario Analysis

The project includes a what-if analysis module for evaluating changes in the distribution network.

The following scenarios are evaluated against the base optimal cost of **₹1,400**.

| Scenario | Total Scenario Cost | Cost Change | % Change |
|---|---:|---:|---:|
| Base Network | ₹1,400 | — | — |
| Warehouse 2 capacity reduced by 20% | ₹1,448 | +₹48 | +3.43% |
| Market 5 demand increased by 20% | ₹1,562 | +₹162 | +11.57% |
| Warehouse 1 → Market 3 cost increased by 30% | ₹1,424 | +₹24 | +1.71% |
| Warehouse 3 temporarily closed | ₹1,790 | +₹390 | +27.86% |

For unbalanced scenarios, the model can use a configurable external-sourcing/shortage penalty. In the example scenarios, the penalty is ₹9 per externally sourced unit.

### Example: Warehouse 3 Closure

When Warehouse 3 is temporarily unavailable:

- Transportation cost = **₹710**
- External sourcing = **120 units**
- External sourcing cost = **₹1,080**
- Total scenario cost = **₹1,790**
- Cost increase = **27.86%**

This separates normal transportation cost from the modeled cost of replacing unavailable warehouse capacity.

## Handling Unbalanced Networks

Real supply chains may have situations where total supply does not equal total demand.

The project handles both cases automatically:

### Excess Supply

If:

$$\text{Total Supply} > \text{Total Demand}$$

an additional dummy destination is introduced to represent unused capacity.

### Excess Demand

If:

$$\text{Total Demand} > \text{Total Supply}$$

an additional dummy source is introduced to represent external sourcing or the modeled supply gap.

The dummy-source cost can be configured to represent an external procurement or shortage penalty.

## Validation

The custom MODI implementation is independently checked using Linear Programming solvers:

- **SciPy `linprog`**
- **PuLP with CBC**

For the worked example, both validations confirm the optimal cost of **₹1,400**.

The project therefore uses both:

1. A custom Operations Research implementation for algorithmic understanding.
2. Independent LP solvers as a correctness cross-check.

## Testing

The project includes automated tests covering:

- Core transportation solver behavior
- North-West Corner and Least Cost methods
- MODI optimization
- Degenerate transportation problems
- Automatic supply-demand balancing
- Sensitivity analysis
- Alternate-optimal route detection
- Scenario analysis
- External sourcing calculations
- Scenario cost consistency

Run the complete test suite with:

```bash
pytest
```

Expected result:

```text
22 passed
```

## Repository Structure

```text
warehousetoretaildistribution_cost_optimizer/
├── README.md
├── transportation_solver.py       # Core transportation optimization engine
├── sensitivity_analysis.py        # Route and warehouse sensitivity analysis
├── scenario_analysis.py           # What-if scenario modeling
├── run_solution.py                # Main optimization demo
├── run_scenarios.py               # Scenario-analysis demo
├── validate_scipy.py              # SciPy LP validation
├── pulp_validation.py             # PuLP/CBC validation
├── make_chart.py                  # Cost comparison chart
├── cost_comparison.png
├── requirements.txt
├── .gitignore
└── tests/
    ├── test_solver.py
    ├── test_degeneracy.py
    ├── test_balancing.py
    ├── test_sensitivity.py
    └── test_scenarios.py
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/darshika2911/warehousetoretaildistribution_cost_optimizer.git
cd warehousetoretaildistribution_cost_optimizer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the main optimization

```bash
python run_solution.py
```

### 4. Run sensitivity analysis

```bash
python sensitivity_analysis.py
```

### 5. Run scenario analysis

```bash
python run_scenarios.py
```

### 6. Run LP validation

```bash
python validate_scipy.py
python pulp_validation.py
```

### 7. Run automated tests

```bash
pytest
```

## Using a Different Dataset

The solver is designed to work with a generic transportation network.

Provide:

```python
cost = [
    [4, 1, 2, 6, 9],
    [6, 4, 3, 5, 7],
    [5, 2, 6, 4, 8]
]

supply = [100, 120, 120]
demand = [40, 50, 70, 90, 90]
```

The same solver structure can be applied to other allocation problems such as:

- Plant-to-distribution-center allocation
- Supplier-to-factory allocation
- Distribution-center-to-store replenishment
- Warehouse-to-market distribution
- Other supply-demand transportation networks

## Project Outcomes

This project demonstrates the ability to:

- Translate a supply-chain allocation problem into a mathematical optimization model
- Implement classical Operations Research algorithms from scratch
- Handle practical edge cases such as degeneracy and unbalanced networks
- Validate custom optimization logic independently
- Perform route and capacity sensitivity analysis
- Quantify the cost impact of operational disruptions
- Build automated tests around an optimization engine

## Future Enhancements

Potential extensions include:

- Multi-period transportation planning
- Vehicle capacity constraints
- Fixed warehouse-opening costs
- Multiple product categories
- Service-level constraints
- Carbon-emission optimization
- Interactive dashboard for scenario exploration

## Limitations

- The current formulation is a classical single-period transportation model.
- Transportation costs are assumed to be linear and deterministic.
- Vehicle routing and fixed facility-opening costs are outside the current model.
- External sourcing costs in scenario analysis are modeled assumptions and should be replaced with business-specific data for real decision-making.

## Takeaway

The project combines **Operations Research, algorithm implementation, validation, sensitivity analysis, and supply-chain scenario modeling** into a single decision-support framework for warehouse-to-retail distribution optimization.

> This project is intended for educational and portfolio purposes. Real supply-chain decisions require validated business data, operational constraints, and domain-specific assumptions.
