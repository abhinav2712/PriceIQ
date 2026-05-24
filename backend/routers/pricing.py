from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.product import Product
from models.user import User
from dependencies import require_role
from services.pricing_service import get_demand_curve, get_recommendations

router = APIRouter(prefix="/pricing", tags=["Pricing & Analytics"])


@router.get("/analytics/summary")
def analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    print("ANALYTICS SUMMARY ENDPOINT HIT")
    ## This endpoint provides a summary of pricing analytics across all products. It calculates:
    # - Total number of products
    # - Average profit margin percentage
    # - Total stock value (cost price * stock)
    # - Number of products priced below cost
    products = db.query(Product).filter(Product.is_active == True).all()

    total_products = len(products)
    if total_products == 0:
        return {
            "total_products": 0,
            "avg_margin": 0,
            "total_stock_value": 0,
            "products_below_cost": 0,
        }

    margins = []
    total_stock_value = 0
    products_below_cost = 0

    for product in products:
        cost_price = float(product.cost_price)
        selling_price = float(product.selling_price)

        margin_amount = selling_price - cost_price

        margin_pct = (margin_amount / selling_price) * 100

        margins.append(margin_pct)

        total_stock_value += cost_price * product.stock

        if selling_price < cost_price:
            products_below_cost += 1

    avg_margin = sum(margins) / len(margins)

    response = {
        "total_products": total_products,
        "avg_margin": round(avg_margin, 2),
        "total_stock_value": round(total_stock_value, 2),
        "products_below_cost": products_below_cost,
    }
    print("ANALYTICS SUMMARY ENDPOINT RESPONSE:", response)
    return response


@router.get("/{product_id}/demand-curve")
def demand_curve(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst","viewer")),
):
    ## This endpoint generates a demand curve for a given product based on a price elasticity model.
    ## It retrieves the product from the database, checks if it exists, and then uses the
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    ## The get_demand_curve function simulates how demand changes with price based on an elasticity coefficient.
    # It returns a list of price and expected units sold points that can be used to plot a demand curve on the frontend.
    return {
        "product_id": product.id,
        "product_name": product.name,
        "elasticity": 1.5,
        "data": get_demand_curve(product)
    }


@router.get("/{product_id}/recommendations")
def recommendations(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    ## This endpoint provides pricing recommendations for a given product based on its cost price and sales data.
    ## It retrieves the product from the database, checks if it exists, and then uses the
    # get_recommendations function to generate different pricing scenarios (conservative, balanced, aggressive)
    # with estimated revenue.
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return {
        "product_id": product.id,
        "product_name": product.name,
        "current_price": float(product.selling_price),
        "cost_price": float(product.cost_price),
        "recommendations": get_recommendations(product),
    }
