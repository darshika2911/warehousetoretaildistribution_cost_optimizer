import numpy as np

from transportation_solver import (
    north_west_corner,
    modi_method,
    total_cost,
    compute_dual_values,
    reduced_costs,
    _complete_basis_for_degeneracy,
)


def test_nw_corner_produces_degenerate_solution():
    cost = np.array([
        [1, 2],
        [2, 1]
    ], dtype=float)

    supply = np.array([30, 30], dtype=float)
    demand = np.array([30, 30], dtype=float)

    alloc = north_west_corner(supply, demand)

    # NW Corner should produce:
    # [[30, 0],
    #  [ 0, 30]]

    assert np.array_equal(
        alloc,
        np.array([
            [30, 0],
            [0, 30]
        ], dtype=float)
    )

    # Only two cells contain positive allocations.
    positive_cells = sum(
    1
    for row in alloc
    for value in row
    if value > 0
)

    assert positive_cells == 2


def test_degenerate_basis_is_completed():
    cost = np.array([
        [1, 2],
        [2, 1]
    ], dtype=float)

    supply = np.array([30, 30], dtype=float)
    demand = np.array([30, 30], dtype=float)

    alloc = north_west_corner(supply, demand)

    basis = _complete_basis_for_degeneracy(
        alloc,
        cost,
        2,
        2
    )

    # A 2x2 transportation problem requires m+n-1 = 3
    # basic cells.
    assert len(basis) == 3

    # Every basis cell must be unique.
    assert len(set(basis)) == 3


def test_modi_handles_degenerate_initial_solution():
    cost = np.array([
        [1, 2],
        [2, 1]
    ], dtype=float)

    supply = np.array([30, 30], dtype=float)
    demand = np.array([30, 30], dtype=float)

    initial_alloc = north_west_corner(supply, demand)

    solution = modi_method(
        cost,
        supply,
        demand,
        initial_alloc
    )

    # The diagonal allocation is optimal.
    expected = np.array([
        [30, 0],
        [0, 30]
    ], dtype=float)

    assert np.array_equal(solution, expected)

    assert total_cost(cost, solution) == 60


def test_dual_values_exist_for_degenerate_solution():
    cost = np.array([
        [1, 2],
        [2, 1]
    ], dtype=float)

    supply = np.array([30, 30], dtype=float)
    demand = np.array([30, 30], dtype=float)

    alloc = north_west_corner(supply, demand)

    u, v = compute_dual_values(cost, alloc)

    # All row and column potentials should be determined.
    assert all(value is not None for value in u)
    assert all(value is not None for value in v)


def test_reduced_costs_show_optimality():
    cost = np.array([
        [1, 2],
        [2, 1]
    ], dtype=float)

    supply = np.array([30, 30], dtype=float)
    demand = np.array([30, 30], dtype=float)

    alloc = north_west_corner(supply, demand)

    # NW solution is already optimal for this particular example.
    rc = reduced_costs(cost, alloc)

    # No negative reduced cost should exist.
    non_basic_reduced_costs = [
    rc[i][j]
    for i in range(2)
    for j in range(2)
    if alloc[i][j] == 0
]

    assert all(value >= -1e-9 for value in non_basic_reduced_costs)

def test_modi_improves_degenerate_initial_solution():
        cost = np.array([
        [5, 1],
        [1, 5]
        ], dtype=float)

        supply = np.array([30, 30], dtype=float)
        demand = np.array([30, 30], dtype=float)

    # NW Corner produces a degenerate solution:
    #
    # [30,  0]
    # [ 0, 30]
    #
        initial_alloc = north_west_corner(supply, demand)

        initial_cost = total_cost(cost, initial_alloc)

        assert initial_cost == 300

    # MODI should recognize that the off-diagonal routes
    # are cheaper and pivot to the optimal solution.
        solution = modi_method(
            cost,
            supply,
            demand,
            initial_alloc
        )

        expected = np.array([
            [0, 30],
            [30, 0]
        ], dtype=float)

        assert np.array_equal(solution, expected)

    # Optimal cost = 30(1) + 30(1) = 60
        assert total_cost(cost, solution) == 60

    # Confirm that MODI actually improved the initial solution.
        assert total_cost(cost, solution) < initial_cost
