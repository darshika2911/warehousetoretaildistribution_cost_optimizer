from scenario_analysis import (
    run_scenario,
    compare_scenarios,
    warehouse_capacity_scenario,
    demand_scenario,
    route_cost_scenario,
    warehouse_closure_scenario,
    print_scenario_comparison,
)


COST = [
    [4, 1, 2, 6, 9],
    [6, 4, 3, 5, 7],
    [5, 2, 6, 4, 8],
]

SUPPLY = [100, 120, 120]

DEMAND = [40, 50, 70, 90, 90]


# --------------------------------------------------
# BASE CASE
# --------------------------------------------------

base_result = run_scenario(
    COST,
    SUPPLY,
    DEMAND,
)

print("BASE NETWORK")
print("=" * 60)
print(f"Optimal distribution cost: ₹{base_result['total_cost']:.2f}")


# --------------------------------------------------
# SCENARIO 1: W2 CAPACITY -20%
# --------------------------------------------------

scenario_1 = warehouse_capacity_scenario(
    COST,
    SUPPLY,
    DEMAND,
    warehouse_index=1,
    reduction=0.20,
)

comparison_1 = compare_scenarios(
    base_result,
    scenario_1,
)

print_scenario_comparison(
    "SCENARIO 1 — W2 CAPACITY REDUCED BY 20%",
    comparison_1,
)


# --------------------------------------------------
# SCENARIO 2: M5 DEMAND +20%
# --------------------------------------------------

scenario_2 = demand_scenario(
    COST,
    SUPPLY,
    DEMAND,
    market_index=4,
    increase=0.20,
)

comparison_2 = compare_scenarios(
    base_result,
    scenario_2,
)

print_scenario_comparison(
    "SCENARIO 2 — M5 DEMAND INCREASED BY 20%",
    comparison_2,
)


# --------------------------------------------------
# SCENARIO 3: W1 → M3 COST +30%
# --------------------------------------------------

scenario_3 = route_cost_scenario(
    COST,
    SUPPLY,
    DEMAND,
    warehouse_index=0,
    market_index=2,
    increase=0.30,
)

comparison_3 = compare_scenarios(
    base_result,
    scenario_3,
)

print_scenario_comparison(
    "SCENARIO 3 — W1 → M3 TRANSPORT COST +30%",
    comparison_3,
)


# --------------------------------------------------
# SCENARIO 4: W3 CLOSED
# --------------------------------------------------

scenario_4 = warehouse_closure_scenario(
    COST,
    SUPPLY,
    DEMAND,
    warehouse_index=2,
)

comparison_4 = compare_scenarios(
    base_result,
    scenario_4,
)

print_scenario_comparison(
    "SCENARIO 4 — W3 TEMPORARILY CLOSED",
    comparison_4,
)