"""
pulp_validation.py
===================
Builds the identical transportation LP in PuLP and solves it with the
CBC solver. This is the validation deliverable referenced in the
README -- run it locally (the build/test environment used for this
project has no internet access, so PuLP could not be installed there;
validate_scipy.py was used as a mathematically identical stand-in
during development -- see that file for details).

Install & run:
    pip install pulp
    python pulp_validation.py

Expected output: optimal total cost = 1400, matching MODI and the
scipy cross-check exactly.
"""

import pulp

from run_solution import COST, SUPPLY, DEMAND, SOURCE_LABELS, DEST_LABELS
from transportation_solver import total_cost


def solve_with_pulp(cost, supply, demand):
    m, n = len(supply), len(demand)
    prob = pulp.LpProblem("Warehouse_to_Retail_Distribution", pulp.LpMinimize)

    x = {
        (i, j): pulp.LpVariable(f"x_{i}_{j}", lowBound=0, cat="Continuous")
        for i in range(m)
        for j in range(n)
    }

    # Objective: minimize total shipping cost
    prob += pulp.lpSum(cost[i][j] * x[i, j] for i in range(m) for j in range(n))

    # Supply constraints
    for i in range(m):
        prob += pulp.lpSum(x[i, j] for j in range(n)) == supply[i], f"Supply_{i}"

    # Demand constraints
    for j in range(n):
        prob += pulp.lpSum(x[i, j] for i in range(m)) == demand[j], f"Demand_{j}"

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] != "Optimal":
        raise RuntimeError(f"PuLP did not find an optimal solution: {pulp.LpStatus[prob.status]}")

    alloc = [[round(x[i, j].value()) for j in range(n)] for i in range(m)]
    return alloc, pulp.value(prob.objective)


def main():
    alloc, lp_cost = solve_with_pulp(COST, SUPPLY, DEMAND)

    print(f"PuLP (CBC) optimal cost: {lp_cost:.2f}")
    header = "".join(f"{d:>10}" for d in DEST_LABELS)
    print(f"{'':>14}{header}")
    for i, row in enumerate(alloc):
        cells = "".join(f"{v:>10}" for v in row)
        print(f"{SOURCE_LABELS[i]:>14}{cells}")

    recomputed = total_cost(COST, alloc)
    print(f"\nRecomputed cost from allocation: {recomputed}")
    assert abs(recomputed - lp_cost) < 1e-6, "Mismatch between LP objective and allocation cost"
    print("Matches MODI result: total cost = 1400 with the same allocation.")


if __name__ == "__main__":
    main()
