import numpy as np

from transportation_solver import balance_problem


def test_excess_supply_adds_dummy_destination():
    cost = [
        [1, 2],
        [2, 1],
    ]
    supply = [30, 30]
    demand = [20, 30]

    balanced_cost, balanced_supply, balanced_demand, info = balance_problem(
        cost, supply, demand
    )

    assert info["added"] == "dummy_destination"

    assert np.sum(balanced_supply) == np.sum(balanced_demand)

    # Demand should now include 10 units of unused capacity
    assert balanced_demand[-1] == 10

    # Dummy destination has zero transportation cost
    assert all(row[-1] == 0 for row in balanced_cost)


def test_excess_demand_adds_dummy_source():
    cost = [
        [1, 2],
        [2, 1],
    ]
    supply = [20, 30]
    demand = [30, 30]

    balanced_cost, balanced_supply, balanced_demand, info = balance_problem(
        cost, supply, demand
    )

    assert info["added"] == "dummy_source"

    assert np.sum(balanced_supply) == np.sum(balanced_demand)

    # Additional 10 units must come from dummy source
    assert balanced_supply[-1] == 10

    # Dummy source has zero transportation cost
    assert all(value == 0 for value in balanced_cost[-1])


def test_balanced_problem_remains_unchanged():
    cost = [
        [1, 2],
        [2, 1],
    ]
    supply = [30, 30]
    demand = [30, 30]

    balanced_cost, balanced_supply, balanced_demand, info = balance_problem(
        cost, supply, demand
    )

    assert info["added"] is None

    assert balanced_cost == cost
    assert balanced_supply == supply
    assert balanced_demand == demand