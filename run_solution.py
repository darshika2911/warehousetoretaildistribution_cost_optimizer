"""
run_solution.py
================
Runs the full pipeline on the example problem (3 warehouses, 5 retail
markets) and prints:

  1. The North-West Corner Rule initial solution + cost
  2. The Least Cost Method initial solution + cost
  3. MODI run from the NWCR starting point -> optimal solution + cost
  4. MODI run from the LCM starting point -> optimal solution + cost
     (confirms path-independence: both must match)

To solve a DIFFERENT problem, just edit COST / SUPPLY / DEMAND below,
or import transportation_solver and call the functions directly with
your own data.
"""

from transportation_solver import (
    north_west_corner,
    least_cost_method,
    modi_method,
    total_cost,
    validate_balanced,
)

# ---------------------------------------------------------------------------
# Example problem instance
# ---------------------------------------------------------------------------
# Rows = warehouses (sources), columns = retail markets (destinations).
COST = [
    [4, 1, 2, 6, 9],
    [6, 4, 3, 5, 7],
    [5, 2, 6, 4, 8],
]
SUPPLY = [100, 120, 120]
DEMAND = [40, 50, 70, 90, 90]

SOURCE_LABELS = [f"Warehouse {i + 1}" for i in range(len(SUPPLY))]
DEST_LABELS = [f"Market {j + 1}" for j in range(len(DEMAND))]


def print_allocation(title, alloc, cost):
    print(f"\n{title}  (total cost = {total_cost(cost, alloc)})")
    header = "".join(f"{d:>10}" for d in DEST_LABELS)
    print(f"{'':>14}{header}")
    for i, row in enumerate(alloc):
        cells = "".join(f"{v:>10}" for v in row)
        print(f"{SOURCE_LABELS[i]:>14}{cells}")


def main():
    validate_balanced(SUPPLY, DEMAND)

    nwcr = north_west_corner(SUPPLY, DEMAND)
    print_allocation("1) North-West Corner Rule (initial, cost-blind)", nwcr, COST)

    lcm = least_cost_method(COST, SUPPLY, DEMAND)
    print_allocation("2) Least Cost Method (initial, cost-aware)", lcm, COST)

    optimal_from_nwcr = modi_method(COST, SUPPLY, DEMAND, nwcr)
    print_allocation("3) MODI, starting from NWCR -> optimal", optimal_from_nwcr, COST)

    optimal_from_lcm = modi_method(COST, SUPPLY, DEMAND, lcm)
    print_allocation("4) MODI, starting from LCM -> optimal", optimal_from_lcm, COST)

    cost_a = total_cost(COST, optimal_from_nwcr)
    cost_b = total_cost(COST, optimal_from_lcm)
    print("\n--- Path-independence check ---")
    print(f"MODI from NWCR : {cost_a}")
    print(f"MODI from LCM  : {cost_b}")
    if cost_a == cost_b and optimal_from_nwcr == optimal_from_lcm:
        print("PASS: both starting points converge to the same optimal allocation.")
    else:
        print("MISMATCH: check degeneracy handling.")

    print("\n--- Summary ---")
    print(f"{'North-West Corner Rule':<28} {total_cost(COST, nwcr):>8}")
    print(f"{'Least Cost Method':<28} {total_cost(COST, lcm):>8}")
    print(f"{'MODI (optimal)':<28} {cost_a:>8}")


if __name__ == "__main__":
    main()
