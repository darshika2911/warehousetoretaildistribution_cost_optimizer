import pytest
import numpy as np

from sensitivity_analysis import (
    classify_route,
    generate_sensitivity_report,
)


COST = [
    [4, 1, 2, 6, 9],
    [6, 4, 3, 5, 7],
    [5, 2, 6, 4, 8],
]

SUPPLY = [100, 120, 120]
DEMAND = [40, 50, 70, 90, 90]


def test_classify_route():
    assert classify_route(0) == "alternate_optimal"
    assert classify_route(1) == "not_currently_attractive"


def test_classify_route_tolerance():
    assert classify_route(1e-10) == "alternate_optimal"


def test_optimal_cost():
    report = generate_sensitivity_report(COST, SUPPLY, DEMAND)

    assert report["optimal_cost"] == pytest.approx(1400)


def test_alternate_optimal_route():
    report = generate_sensitivity_report(COST, SUPPLY, DEMAND)

    routes = report["alternate_optimal_routes"]

    assert len(routes) >= 1
    assert routes[0]["route"] == "W3 → M2"
    assert routes[0]["reduced_cost"] == pytest.approx(0)


def test_route_sensitivity_sorted():
    report = generate_sensitivity_report(COST, SUPPLY, DEMAND)

    routes = report["route_sensitivity"]

    reduced_costs = [route["reduced_cost"] for route in routes]

    assert reduced_costs == sorted(reduced_costs)


def test_warehouse_potentials():
    report = generate_sensitivity_report(COST, SUPPLY, DEMAND)

    potentials = report["warehouse_potentials"]

    assert np.allclose(potentials, [0, 1, 1])


def test_final_solution_has_no_negative_reduced_cost():
    report = generate_sensitivity_report(COST, SUPPLY, DEMAND)

    for route in report["route_sensitivity"]:
        assert route["reduced_cost"] >= -1e-9