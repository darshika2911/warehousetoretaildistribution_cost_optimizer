from copy import deepcopy

from transportation_solver import balance_problem
from sensitivity_analysis import solve_transportation_problem

def run_scenario(cost, supply, demand, shortage_cost=None):
    """
    Balance and solve a transportation scenario.

    Returns both transportation cost and external sourcing impact.
    """

    if shortage_cost is None:
        shortage_cost = max(max(row) for row in cost)

    original_supply = list(supply)
    original_demand = list(demand)

    balanced_cost, balanced_supply, balanced_demand, balance_info = balance_problem(
        cost,
        supply,
        demand,
        dummy_cost=shortage_cost
    )

    allocation, total_cost, u, v, rc = solve_transportation_problem(
        balanced_cost,
        balanced_supply,
        balanced_demand
    )

    # Calculate real warehouse-to-market transportation cost
    transportation_cost = 0

    for i in range(len(original_supply)):
        for j in range(len(original_demand)):
            transportation_cost += cost[i][j] * allocation[i][j]

    # Calculate external sourcing
    external_sourcing_units = 0

    if balance_info["added"] == "dummy_source":
        dummy_row = balance_info["index"]
        external_sourcing_units = sum(allocation[dummy_row])

    external_sourcing_cost = external_sourcing_units * shortage_cost

    return {
        "allocation": allocation,
        "total_cost": total_cost,
        "transportation_cost": transportation_cost,
        "external_sourcing_units": external_sourcing_units,
        "external_sourcing_cost": external_sourcing_cost,
        "shortage_cost": shortage_cost,
        "balance_info": balance_info,
        "u": u,
        "v": v,
        "reduced_costs": rc
    }


def compare_scenarios(base_result, scenario_result):
    base_cost = base_result["total_cost"]
    scenario_cost = scenario_result["total_cost"]

    cost_change = scenario_cost - base_cost

    if base_cost != 0:
        percentage_change = (cost_change / base_cost) * 100
    else:
        percentage_change = 0

    return {
        "base_cost": base_cost,
        "scenario_cost": scenario_cost,
        "cost_change": cost_change,
        "percentage_change": percentage_change,
        "transportation_cost": scenario_result["transportation_cost"],
        "external_sourcing_units": scenario_result["external_sourcing_units"],
        "external_sourcing_cost": scenario_result["external_sourcing_cost"]
    }


def warehouse_capacity_scenario(cost, supply, demand, warehouse_index, reduction):
    """
    Reduce the capacity of one warehouse by a given percentage.

    Example:
        reduction = 0.20
        means 20% capacity reduction.
    """

    scenario_supply = deepcopy(supply)

    original_capacity = scenario_supply[warehouse_index]

    scenario_supply[warehouse_index] = (
        original_capacity * (1 - reduction)
    )

    return run_scenario(cost, scenario_supply, demand)


def demand_scenario(cost, supply, demand, market_index, increase):
    """
    Increase demand at one market by a given percentage.

    Example:
        increase = 0.20
        means 20% increase in demand.
    """

    scenario_demand = deepcopy(demand)

    original_demand = scenario_demand[market_index]

    scenario_demand[market_index] = (
        original_demand * (1 + increase)
    )

    return run_scenario(cost, supply, scenario_demand)


def route_cost_scenario(
    cost,
    supply,
    demand,
    warehouse_index,
    market_index,
    increase,
):
    """
    Increase transportation cost on one route by a given percentage.

    Example:
        increase = 0.30
        means 30% increase in lane cost.
    """

    scenario_cost = deepcopy(cost)

    original_cost = scenario_cost[warehouse_index][market_index]

    scenario_cost[warehouse_index][market_index] = (
        original_cost * (1 + increase)
    )

    return run_scenario(cost=scenario_cost, supply=supply, demand=demand)


def warehouse_closure_scenario(
    cost,
    supply,
    demand,
    warehouse_index,
):
    """
    Simulate temporary closure of a warehouse.

    The warehouse capacity is reduced to zero.
    """

    scenario_supply = deepcopy(supply)

    scenario_supply[warehouse_index] = 0

    return run_scenario(cost, scenario_supply, demand)


def print_scenario_comparison(title, comparison):
    print("=" * 60)
    print(title)
    print("=" * 60)

    print(f"Base optimal cost:          ₹{comparison['base_cost']:.2f}")
    print(f"Transportation cost:        ₹{comparison['transportation_cost']:.2f}")
    print(f"External sourcing units:    {comparison['external_sourcing_units']}")
    print(f"External sourcing cost:     ₹{comparison['external_sourcing_cost']:.2f}")
    print(f"Total scenario cost:        ₹{comparison['scenario_cost']:.2f}")

    if comparison["cost_change"] >= 0:
        print(
            f"Cost increase:              "
            f"₹{comparison['cost_change']:.2f} "
            f"({comparison['percentage_change']:.2f}%)"
        )
    else:
        print(
            f"Cost reduction:             "
            f"₹{-comparison['cost_change']:.2f} "
            f"({-comparison['percentage_change']:.2f}%)"
        )