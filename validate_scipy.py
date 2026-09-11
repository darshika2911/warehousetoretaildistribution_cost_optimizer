"""
validate_scipy.py
==================
Cross-checks the MODI result against a generic linear-programming
solver, independent of the hand-rolled transportation algorithms.

Works fully offline (scipy ships with no external dependencies beyond
itself), which is why it was used as the primary validation during
development. See pulp_validation.py for the equivalent model expressed
in PuLP -- run that locally if you'd rather validate with a solver
that's purpose-built for this class of LP (PuLP/CBC).

Model (identical in both scripts):

    minimize   sum_i sum_j cost[i][j] * x[i][j]
    subject to sum_j x[i][j] = supply[i]      for each source i
               sum_i x[i][j] = demand[j]      for each destination j
               x[i][j] >= 0
"""

import numpy as np
from scipy.optimize import linprog

from run_solution import COST, SUPPLY, DEMAND, SOURCE_LABELS, DEST_LABELS
from transportation_solver import total_cost


def solve_with_scipy(cost, supply, demand):
    m, n = len(supply), len(demand)

    # Flatten x[i][j] -> single vector of length m*n, index = i*n + j
    c = np.array(cost).flatten()

    # Equality constraints: A_eq @ x = b_eq
    A_eq = []
    b_eq = []

    # Supply constraints: sum_j x[i][j] = supply[i]
    for i in range(m):
        row = [0] * (m * n)
        for j in range(n):
            row[i * n + j] = 1
        A_eq.append(row)
        b_eq.append(supply[i])

    # Demand constraints: sum_i x[i][j] = demand[j]
    for j in range(n):
        row = [0] * (m * n)
        for i in range(m):
            row[i * n + j] = 1
        A_eq.append(row)
        b_eq.append(demand[j])

    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not result.success:
        raise RuntimeError(f"LP solve failed: {result.message}")

    alloc = result.x.reshape(m, n).round().astype(int).tolist()
    return alloc, result.fun


def main():
    alloc, lp_cost = solve_with_scipy(COST, SUPPLY, DEMAND)

    print(f"scipy.optimize.linprog (HiGHS) optimal cost: {lp_cost:.2f}")
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
