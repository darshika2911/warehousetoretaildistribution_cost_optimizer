"""
transportation_solver.py
=========================
A general-purpose solver for the balanced transportation problem:

    minimize   sum_i sum_j cost[i][j] * x[i][j]
    subject to sum_j x[i][j] = supply[i]   for every source i
               sum_i x[i][j] = demand[j]   for every destination j
               x[i][j] >= 0

This is written generically (any cost matrix / supply / demand), not
hard-coded to a single dataset -- the warehouse/retail-market numbers
used in run_solution.py are just one example problem instance.

Three classical methods are implemented, in the usual teaching order:

  1. north_west_corner()   - naive initial feasible solution (ignores cost)
  2. least_cost_method()   - cost-aware initial feasible solution
  3. modi_method()         - takes ANY feasible solution and iterates it
                              to the true cost-minimum using the
                              u-v (MODI / Modified Distribution) method

modi_method() is deliberately given an `initial_alloc` argument rather
than computing its own starting point, so you can verify path-independence:
starting MODI from north_west_corner() or from least_cost_method() must
converge to the same optimal cost and allocation. run_solution.py does
exactly that as a correctness check.
"""

from copy import deepcopy


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def total_cost(cost, alloc):
    """Total shipping cost of an allocation matrix."""
    return sum(
        cost[i][j] * alloc[i][j]
        for i in range(len(alloc))
        for j in range(len(alloc[0]))
    )


def validate_balanced(supply, demand):
    if sum(supply) != sum(demand):
        raise ValueError(
            f"Unbalanced problem: total supply ({sum(supply)}) != "
            f"total demand ({sum(demand)}). Add a dummy source/destination "
            f"with zero cost before solving, or call balance_problem()."
        )


def balance_problem(cost, supply, demand, dummy_cost=0):
    """
    Real distribution networks are almost never exactly balanced --
    either total capacity exceeds total demand, or total demand exceeds
    what the network can currently supply. Rather than raising an error,
    this inserts a zero-cost dummy source or destination so the problem
    can still be solved with the standard algorithms.

    A dummy destination absorbs *unused* supply (excess capacity that
    ships nowhere); a dummy source covers *unmet* demand (a shortfall
    that a real plan would have to backfill from an outside supplier,
    expedited freight, etc.). Either way, any allocation touching the
    dummy row/column represents a gap in the real network, not an
    actual shipment -- report on it accordingly.

    Returns (cost2, supply2, demand2, info) where info describes what,
    if anything, was added. If the problem was already balanced,
    cost2/supply2/demand2 are unchanged copies and info["added"] is None.
    """
    total_supply, total_demand = sum(supply), sum(demand)
    cost2 = [row[:] for row in cost]
    supply2, demand2 = list(supply), list(demand)

    if total_supply == total_demand:
        return cost2, supply2, demand2, {"added": None}

    if total_supply > total_demand:
        gap = total_supply - total_demand
        demand2.append(gap)
        for row in cost2:
            row.append(dummy_cost)
        info = {"added": "dummy_destination", "index": len(demand2) - 1, "amount": gap}
    else:
        gap = total_demand - total_supply
        supply2.append(gap)
        cost2.append([dummy_cost] * len(demand2))
        info = {"added": "dummy_source", "index": len(supply2) - 1, "amount": gap}

    return cost2, supply2, demand2, info


# ---------------------------------------------------------------------------
# 1. North-West Corner Rule
# ---------------------------------------------------------------------------

def north_west_corner(supply, demand):
    """
    Fast, naive initial feasible solution. Starts at the top-left (north-west)
    cell of the cost matrix and allocates as much as possible, then moves
    right or down. Completely ignores cost -- used only as a baseline and
    as one of two independent starting points for MODI.
    """
    supply = list(supply)
    demand = list(demand)
    m, n = len(supply), len(demand)
    alloc = [[0] * n for _ in range(m)]

    i, j = 0, 0
    while i < m and j < n:
        qty = min(supply[i], demand[j])
        alloc[i][j] = qty
        supply[i] -= qty
        demand[j] -= qty

        if supply[i] == 0 and demand[j] == 0:
            # Both exhausted simultaneously: step diagonally if possible,
            # otherwise the loop terminates naturally.
            if i < m - 1:
                i += 1
            elif j < n - 1:
                j += 1
            else:
                break
        elif supply[i] == 0:
            i += 1
        else:
            j += 1

    return alloc


# ---------------------------------------------------------------------------
# 2. Least Cost Method
# ---------------------------------------------------------------------------

def least_cost_method(cost, supply, demand):
    """
    Cost-aware initial feasible solution. Repeatedly finds the globally
    cheapest remaining cell and allocates as much as that row/column can
    still take, until all supply and demand is exhausted.
    """
    supply = list(supply)
    demand = list(demand)
    m, n = len(supply), len(demand)
    alloc = [[0] * n for _ in range(m)]

    active_rows = set(range(m))
    active_cols = set(range(n))

    while active_rows and active_cols:
        min_cost, min_cell = None, None
        for i in active_rows:
            for j in active_cols:
                if min_cost is None or cost[i][j] < min_cost:
                    min_cost, min_cell = cost[i][j], (i, j)

        i, j = min_cell
        qty = min(supply[i], demand[j])
        alloc[i][j] = qty
        supply[i] -= qty
        demand[j] -= qty

        if supply[i] == 0:
            active_rows.discard(i)
        if demand[j] == 0:
            active_cols.discard(j)

    return alloc


# ---------------------------------------------------------------------------
# 3. MODI (Modified Distribution / u-v) method
# ---------------------------------------------------------------------------

def _basic_cells(alloc, m, n):
    return [(i, j) for i in range(m) for j in range(n) if alloc[i][j] > 0]


def _complete_basis_for_degeneracy(alloc, cost, m, n):
    """
    A feasible transportation solution needs exactly m+n-1 basic
    (allocated) cells to compute u/v uniquely. If fewer cells are
    allocated (a degenerate solution), add zero-valued basic cells --
    cheapest first -- that don't close a cycle with the existing basic
    cells, using union-find over the bipartite row/column graph.
    """
    basic = _basic_cells(alloc, m, n)
    parent = list(range(m + n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        parent[rx] = ry
        return True

    for (i, j) in basic:
        union(i, m + j)

    needed = (m + n - 1) - len(basic)
    if needed > 0:
        zero_cells = sorted(
            ((i, j) for i in range(m) for j in range(n) if alloc[i][j] == 0),
            key=lambda c: cost[c[0]][c[1]],
        )
        for (i, j) in zero_cells:
            if needed == 0:
                break
            if union(i, m + j):
                basic.append((i, j))
                needed -= 1

    return basic


def _compute_uv(cost, basic, m, n):
    u = [None] * m
    v = [None] * n
    u[0] = 0
    changed = True
    while changed:
        changed = False
        for (i, j) in basic:
            if u[i] is not None and v[j] is None:
                v[j] = cost[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = cost[i][j] - v[j]
                changed = True
    return u, v


def _find_entering_cell(cost, basic, u, v, m, n):
    """Find the non-basic cell with the most negative reduced cost."""
    basic_set = set(basic)
    entering, best = None, 0
    for i in range(m):
        for j in range(n):
            if (i, j) in basic_set:
                continue
            if u[i] is None or v[j] is None:
                continue  # unreachable cell in a degenerate/disconnected basis
            reduced = cost[i][j] - (u[i] + v[j])
            if reduced < best:
                best, entering = reduced, (i, j)
    return entering


def _find_closed_loop(basic, entering, m, n):
    """
    Find the unique closed loop through `entering` and a subset of the
    basic cells, alternating strictly between horizontal and vertical
    moves (the shape required for a MODI reallocation loop). Standard
    zig-zag depth-first search over the bipartite row/column adjacency.
    """
    cells = set(basic) | {entering}

    def dfs(path, horizontal_next):
        current = path[-1]
        if horizontal_next:
            candidates = [c for c in cells if c[0] == current[0] and c != current]
        else:
            candidates = [c for c in cells if c[1] == current[1] and c != current]

        for nxt in candidates:
            if nxt == entering and len(path) >= 3:
                return path + [nxt]
            if nxt in path:
                continue
            result = dfs(path + [nxt], not horizontal_next)
            if result:
                return result
        return None

    result = dfs([entering], True) or dfs([entering], False)
    if result is None:
        raise RuntimeError(
            "No closed loop found -- the basic-cell set is not a spanning "
            "tree of the transportation graph (check degeneracy handling)."
        )
    return result[:-1]  # drop the repeated starting cell


def compute_dual_values(cost, alloc):
    """
    Recover the MODI dual values (u[i] per source, v[j] per destination)
    for a *final*, optimal allocation. These are the classical
    "shadow prices" of the transportation LP: u[i] + v[j] is what the
    solver believes route (i, j) "should" cost given everything else in
    the plan, and u[0] is pinned to 0 as the reference point (duals are
    only meaningful up to a constant shift -- interpret differences
    between sources/destinations, not the raw numbers).
    """
    m, n = len(alloc), len(alloc[0])
    basic = _complete_basis_for_degeneracy(alloc, cost, m, n)
    return _compute_uv(cost, basic, m, n)


def reduced_costs(cost, alloc):
    """
    For every non-basic (unused) route, the reduced cost is how much
    total cost would change per unit if that route were used instead of
    the current plan -- i.e. cost[i][j] - (u[i] + v[j]). At optimality
    every reduced cost is >= 0, meaning no unused route can improve the
    plan. The size of the smallest positive reduced costs tells you how
    close an alternative route is to becoming worthwhile (e.g. if a
    route's reduced cost is 1, a $1/unit freight-rate change would flip
    the optimal plan to use it).

    Returns a matrix the same shape as `cost`; basic (used) cells are
    reported as 0 by convention.
    """
    m, n = len(alloc), len(alloc[0])
    u, v = compute_dual_values(cost, alloc)
    basic_set = set(_basic_cells(alloc, m, n))
    result = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if (i, j) in basic_set:
                continue
            if u[i] is None or v[j] is None:
                result[i][j] = None  # unreachable in a degenerate basis
            else:
                result[i][j] = cost[i][j] - (u[i] + v[j])
    return result


def modi_method(cost, supply, demand, initial_alloc, max_iter=200, verbose=False):
    """
    Iterate a feasible starting allocation to the cost-minimizing solution
    using the MODI (u-v) method.

    The basis is maintained explicitly across pivots so that degenerate
    solutions (including those created by dummy rows/columns) are handled
    correctly.
    """

    m, n = len(supply), len(demand)
    alloc = deepcopy(initial_alloc)

    # Build an initial spanning-tree basis.
    basic = _complete_basis_for_degeneracy(
        alloc,
        cost,
        m,
        n
    )

    for iteration in range(max_iter):

        # Compute MODI potentials using the current basis.
        u, v = _compute_uv(
            cost,
            basic,
            m,
            n
        )

        # Find the most negative reduced-cost non-basic cell.
        entering = _find_entering_cell(
            cost,
            basic,
            u,
            v,
            m,
            n
        )

        # No negative reduced cost => optimal.
        if entering is None:

            if verbose:
                print(
                    f"Optimal after {iteration} pivot(s)."
                )

            return alloc

        # Find the closed transportation loop.
        loop = _find_closed_loop(
            basic,
            entering,
            m,
            n
        )

        # Alternating + / - cells.
        minus_cells = loop[1::2]

        # Maximum amount that can enter the entering cell.
        theta = min(
            alloc[i][j]
            for (i, j) in minus_cells
        )

        # Determine which minus cell leaves the basis.
        leaving_candidates = [
            cell
            for cell in minus_cells
            if alloc[cell[0]][cell[1]] == theta
        ]

        # Deterministic tie-breaking.
        leaving = leaving_candidates[0]

        # Add entering cell to the basis.
        if entering not in basic:
            basic.append(entering)

        # Perform the pivot.
        for idx, (i, j) in enumerate(loop):

            if idx % 2 == 0:
                alloc[i][j] += theta
            else:
                alloc[i][j] -= theta

        # Remove the leaving cell from the basis.
        if leaving != entering and leaving in basic:
            basic.remove(leaving)

        if verbose:
            print(
                f"Iteration {iteration}: "
                f"entering {entering}, "
                f"leaving {leaving}, "
                f"theta={theta}, "
                f"cost={total_cost(cost, alloc)}"
            )

    raise RuntimeError(
        "MODI did not converge within max_iter iterations."
    )
    
