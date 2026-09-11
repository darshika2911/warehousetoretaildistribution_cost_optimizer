from transportation_solver import (
    least_cost_method,
    modi_method,
    total_cost,
    compute_dual_values,
    reduced_costs,
)


def solve_transportation_problem(cost, supply, demand):
    """
    Solve the transportation problem using Least Cost Method
    followed by MODI optimization.

    Returns:
        optimal_allocation
        optimal_cost
        dual_values
        reduced_cost_matrix
    """

    initial_allocation = least_cost_method(
        cost,
        supply,
        demand
    )

    optimal_allocation = modi_method(
        cost,
        supply,
        demand,
        initial_allocation
    )

    optimal_cost = total_cost(
        cost,
        optimal_allocation
    )

    u, v = compute_dual_values(
        cost,
        optimal_allocation
    )

    rc = reduced_costs(
        cost,
        optimal_allocation
    )

    return (
        optimal_allocation,
        optimal_cost,
        u,
        v,
        rc
    )


def classify_route(reduced_cost, tolerance=1e-9):
    """
    Classify an unused route using its reduced cost.

    Reduced cost:
        0       -> alternate optimal route
        > 0     -> currently not attractive
    """

    if abs(reduced_cost) <= tolerance:
        return "alternate_optimal"

    return "not_currently_attractive"


def analyze_route_sensitivity(cost, allocation, reduced_cost_matrix):
    """
    Analyze all currently unused transportation routes.

    Returns a list of dictionaries containing:
        route
        current_cost
        reduced_cost
        classification
    """

    routes = []

    rows = len(cost)
    cols = len(cost[0])

    for i in range(rows):
        for j in range(cols):

            # Only analyze unused routes.
            if allocation[i][j] == 0:

                reduced_cost = float(
                    reduced_cost_matrix[i][j]
                )

                routes.append({
                    "warehouse": f"W{i + 1}",
                    "market": f"M{j + 1}",
                    "route": f"W{i + 1} → M{j + 1}",
                    "current_cost": cost[i][j],
                    "reduced_cost": reduced_cost,
                    "classification": classify_route(
                        reduced_cost
                    ),
                })

    # Most competitive unused routes first.
    routes.sort(
        key=lambda x: x["reduced_cost"]
    )

    return routes


def analyze_capacity_sensitivity(u):
    """
    Report warehouse dual values.

    IMPORTANT:
    These are marginal dual values under the current basis.
    They should not automatically be interpreted as guaranteed
    savings for arbitrary capacity changes.

    Returns a list of dictionaries.
    """

    results = []

    for i, value in enumerate(u):

        results.append({
            "warehouse": f"W{i + 1}",
            "dual_value": float(value),
        })

    # Highest absolute marginal value first.
    results.sort(
        key=lambda x: abs(x["dual_value"]),
        reverse=True
    )

    return results


def generate_sensitivity_report(cost, supply, demand):
    """
    Generate a complete sensitivity-analysis result.

    Returns a dictionary so that the results can later be used
    by a dashboard, API, visualization, or frontend.
    """

    (
        optimal_allocation,
        optimal_cost,
        u,
        v,
        rc
    ) = solve_transportation_problem(
        cost,
        supply,
        demand
    )

    route_analysis = analyze_route_sensitivity(
        cost,
        optimal_allocation,
        rc
    )

    capacity_analysis = analyze_capacity_sensitivity(
        u
    )

    alternate_routes = [
        route
        for route in route_analysis
        if route["classification"] == "alternate_optimal"
    ]

    competitive_routes = [
        route
        for route in route_analysis
        if route["classification"] == "not_currently_attractive"
    ]

    return {
        "optimal_cost": optimal_cost,
        "optimal_allocation": optimal_allocation,
        "warehouse_potentials": u,
        "market_potentials": v,
        "capacity_sensitivity": capacity_analysis,
        "route_sensitivity": route_analysis,
        "alternate_optimal_routes": alternate_routes,
        "competitive_unused_routes": competitive_routes,
    }


def print_sensitivity_report(report):
    """
    Print a business-friendly sensitivity report.
    """

    print("=" * 60)
    print("DISTRIBUTION NETWORK SENSITIVITY ANALYSIS")
    print("=" * 60)

    print("\nOPTIMAL DISTRIBUTION COST")
    print("-" * 60)
    print(f"Total distribution cost: ₹{report['optimal_cost']:.0f}")

    print("\nALTERNATE-OPTIMAL ROUTES")
    print("-" * 60)

    alternate_routes = report["alternate_optimal_routes"]

    if not alternate_routes:
        print("No alternate-optimal unused routes identified.")

    else:
        for route in alternate_routes:

            print(
                f"{route['route']}\n"
                f"  Current lane cost : ₹{route['current_cost']}/unit\n"
                f"  Reduced cost      : {route['reduced_cost']:.2f}\n"
                f"  Insight           : Can participate in an "
                f"alternative optimal allocation without "
                f"increasing the objective cost.\n"
            )

    print("\nMOST COMPETITIVE UNUSED ROUTES")
    print("-" * 60)

    competitive_routes = report["competitive_unused_routes"]

    # Show the three smallest positive reduced costs.
    positive_routes = [
        route
        for route in competitive_routes
        if route["reduced_cost"] > 0
    ]

    for route in positive_routes[:3]:

        print(
            f"{route['route']} | "
            f"Current cost: ₹{route['current_cost']}/unit | "
            f"Reduced cost: {route['reduced_cost']:.2f}"
        )

    print(
        "\nInterpretation: Lower positive reduced cost "
        "means the unused lane is closer to becoming "
        "competitive under the current basis."
    )

    print("\nWAREHOUSE CAPACITY SENSITIVITY")
    print("-" * 60)

    for warehouse in report["capacity_sensitivity"]:

        print(
            f"{warehouse['warehouse']} | "
            f"Marginal dual value: "
            f"{warehouse['dual_value']:.2f}"
        )

    print(
        "\nNote: Dual values represent marginal sensitivity "
        "under the current basis and should not be treated "
        "as guaranteed savings for arbitrary capacity changes."
    )


# ------------------------------------------------------------------
# Example dataset
# ------------------------------------------------------------------

COST = [
    [4, 1, 2, 6, 9],
    [6, 4, 3, 5, 7],
    [5, 2, 6, 4, 8],
]

SUPPLY = [100, 120, 120]

DEMAND = [40, 50, 70, 90, 90]


if __name__ == "__main__":

    report = generate_sensitivity_report(
        COST,
        SUPPLY,
        DEMAND
    )

    print_sensitivity_report(report)