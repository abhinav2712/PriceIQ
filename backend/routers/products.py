from decimal import Decimal
from itertools import product
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product
from models.user import User
from schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from dependencies import get_current_user, require_role

## This file contains all the endpoints related to products,
# such as creating, updating, deleting, and listing products.
router= APIRouter(prefix="/products", tags=["products"])


def product_to_response(product: Product) -> ProductResponse:
    ## This function converts a Product SQLAlchemy model instance to a ProductResponse Pydantic model instance.
    cost_price= float(product.cost_price)
    selling_price= float(product.selling_price)
    margin_amount= selling_price - cost_price

    if selling_price > 0:
        margin_pct= (margin_amount / selling_price) * 100
    else:
        margin_pct= 0.0

    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        category=product.category,
        cost_price=product.cost_price,
        selling_price=product.selling_price,
        stock=product.stock,
        units_sold=product.units_sold,
        rating=product.rating,
        created_by=product.created_by,
        is_active=product.is_active,
        margin_pct=round(margin_pct, 2),
        margin_amount=round(margin_amount, 2),
    )


@router.get("", response_model=ProductListResponse)
def list_products(
    search: str | None = None,
    category: str | None = None,
    sort: str | None = Query(default="id"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query=db.query(Product).filter(Product.is_active == True)
    # The search parameter allows users to filter products by name using a case-insensitive partial match.
    # The category parameter allows users to filter products by exact category match.
    # The sort parameter allows users to sort products by id, price, rating, stock,
    # or units_sold in descending order. If no sort parameter is provided, it defaults to sorting by id.

    if search:
        query=query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query=query.filter(Product.category == category)

    allowed_sort_fields = {
        "id": Product.id,
        "price": Product.selling_price,
        "rating": Product.rating,
        "stock": Product.stock,
        "units_sold": Product
    }

    # If the sort parameter is not in the allowed_sort_fields dictionary, it defaults to sorting by Product.id.
    sort_column= allowed_sort_fields.get(sort,Product.id)
    query=query.order_by(sort_column.desc())    

    total = query.count()

    products = (query.offset((page - 1) * limit).limit(limit).all())

    return ProductListResponse(
        total=total,
        page=page,
        limit=limit,
        products=[product_to_response(product) for product in products],
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        category=product_data.category,
        cost_price=product_data.cost_price,
        selling_price=product_data.selling_price,
        stock=product_data.stock,
        units_sold=product_data.units_sold,
        rating=product_data.rating,
        created_by=current_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return product_to_response(product)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product_to_response(product)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    price_fields = {"cost_price", "selling_price"}

    if current_user.role == "analyst":
        if any(field in update_data for field in price_fields):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Analysts are not allowed to update cost_price or selling_price",
            )
    
    new_cost_price = update_data.get("cost_price", product.cost_price)
    new_selling_price = update_data.get("selling_price", product.selling_price)

    if new_selling_price <= new_cost_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selling_price must be greater than cost_price",
        )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product_to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )   

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Instead of deleting the product from the database, we mark it as inactive.
    # This allows us to keep historical data and avoid issues with foreign key constraints.
    product.is_active = False
    db.commit()

    return {"message": "Product deleted successfully"}
