from decimal import Decimal

## Simulated pricing intelligence using a price elasticity model.
# The idea is that as price increases, demand decreases based on an elasticity coefficient.
# This gives a realistic demand curve without needing a machine learning model.


def get_demand_curve(product, elasticity: float = 1.5)-> list[dict]:
    """
    Price elasticity model:
    units = base_units * (base_price / current_price) ^ elasticity

    When price increases, expected units sold decreases.
    When price decreases, expected units sold increases.
    """

    base_price = float(product.selling_price)
    base_units = product.units_sold or 100

    points = []

    for i in range(20):
        price = base_price * (0.5 + i * 0.1)

        units = base_units * (base_price / price) ** elasticity

        points.append({"price": round(price, 2), "units": round(units, 1)})

    return points


def get_recommendations(product)-> list[dict]:
    """Simple pricing recommendations based on cost price and sales data.
    It generates three scenarios:
    - Conservative: 10% margin, high sales volume
    - Balanced: 30% margin, moderate sales volume
    - Aggressive: 60% margin, low sales volume"""
    cost = float(product.cost_price)
    units_sold = product.units_sold or 100

    scenarios = [
        {
            "scenario": "Conservative",
            "price": round(cost * 1.10, 2),
            "margin_pct": 10.0,
            "revenue_est": round(cost * 1.10 * units_sold, 2),
            "recommended": False,
        },
        {
            "scenario": "Balanced",
            "price": round(cost * 1.30, 2),
            "margin_pct": 30.0,
            "revenue_est": round(cost * 1.30 * units_sold * 0.85, 2),
            "recommended": True,
        },
        {
            "scenario": "Aggressive",
            "price": round(cost * 1.60, 2),
            "margin_pct": 60.0,
            "revenue_est": round(cost * 1.60 * units_sold * 0.60, 2),
            "recommended": False,
        },
    ]

    return scenarios
