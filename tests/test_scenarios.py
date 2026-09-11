import pytest

from scenario_analysis import (
    run_scenario,
    warehouse_capacity_scenario,
    demand_scenario,
    route_cost_scenario,
    warehouse_closure_scenario,
)


COST = [
    [4, 1, 2, 6, 9],
    [6, 4, 3, 5, 7],
    [5, 2, 6, 4, 8],
]

SUPPLY = [100, 120, 120]

DEMAND = [40, 50, 70, 90, 90]


def test_base_scenario_cost():
    result = run_scenario(COST, SUPPLY, DEMAND)

    assert result["total_cost"] == pytest.approx(1400)
    assert result["external_sourcing_units"] == 0
    assert result["external_sourcing_cost"] == pytest.approx(0)


def test_capacity_reduction_increases_cost():
    result = warehouse_capacity_scenario(
        COST,
        SUPPLY,
        DEMAND,
        warehouse_index=1,
        reduction=0.20,
    )

    assert result["total_cost"] > 1400
    assert result["external_sourcing_units"] == 24
    assert result["external_sourcing_cost"] == pytest.approx(216)


def test_demand_increase_creates_external_sourcing():
    result = demand_scenario(
        COST,
        SUPPLY,
        DEMAND,
        market_index=4,
        increase=0.20,
    )

    assert result["total_cost"] == pytest.approx(1562)
    assert result["external_sourcing_units"] == 18
    assert result["external_sourcing_cost"] == pytest.approx(162)


def test_route_cost_increase_does_not_reduce_total_cost():
    result = route_cost_scenario(
        COST,
        SUPPLY,
        DEMAND,
        warehouse_index=0,
        market_index=2,
        increase=0.30,
    )

    assert result["total_cost"] >= 1400


def test_warehouse_closure_increases_cost():
    result = warehouse_closure_scenario(
        COST,
        SUPPLY,
        DEMAND,
        warehouse_index=2,
    )

    assert result["total_cost"] == pytest.approx(1790)
    assert result["external_sourcing_units"] == 120
    assert result["external_sourcing_cost"] == pytest.approx(1080)


def test_scenario_cost_components_add_up():
    result = warehouse_closure_scenario(
        COST,
        SUPPLY,
        DEMAND,
        warehouse_index=2,
    )

    assert result["transportation_cost"] + result["external_sourcing_cost"] == pytest.approx(
        result["total_cost"]
    )