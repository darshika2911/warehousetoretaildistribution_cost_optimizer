"""
make_chart.py
==============
Generates cost_comparison.png -- a bar chart of total distribution cost
across the three stages (NWCR -> LCM -> MODI optimal), showing how much
each method saves over the naive baseline.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from run_solution import COST, SUPPLY, DEMAND
from transportation_solver import north_west_corner, least_cost_method, modi_method, total_cost


def main():
    nwcr = north_west_corner(SUPPLY, DEMAND)
    lcm = least_cost_method(COST, SUPPLY, DEMAND)
    optimal = modi_method(COST, SUPPLY, DEMAND, lcm)

    labels = ["North-West\nCorner Rule", "Least Cost\nMethod", "MODI\n(optimal)"]
    costs = [total_cost(COST, nwcr), total_cost(COST, lcm), total_cost(COST, optimal)]
    colors = ["#c94c4c", "#e0a832", "#3a8f5a"]

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, costs, color=colors, width=0.55)

    for bar, cost in zip(bars, costs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 8,
            f"{cost:,}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    baseline = costs[0]
    savings_pct = (baseline - costs[-1]) / baseline * 100
    ax.set_ylabel("Total distribution cost (₹, arbitrary cost units)")
    ax.set_title(
        f"Warehouse-to-Retail Distribution Cost by Method\n"
        f"MODI cuts cost {savings_pct:.1f}% versus the naive North-West Corner baseline"
    )
    ax.set_ylim(0, max(costs) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig("cost_comparison.png", dpi=150)
    print("Saved cost_comparison.png")
    print(f"NWCR: {costs[0]}  |  LCM: {costs[1]}  |  MODI: {costs[2]}  |  Savings: {savings_pct:.1f}%")


if __name__ == "__main__":
    main()
