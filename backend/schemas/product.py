from decimal import Decimal
from pydantic import BaseModel, Field, model_validator
from typing import Optional

# ProductCreate       → used when creating a product
# ProductUpdate       → used when editing a product
# ProductResponse     → returned to frontend
# ProductListResponse → returned for paginated product list

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    cost_price: Decimal = Field(..., gt=0)
    selling_price: Decimal = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    units_sold: int = Field(default=0, ge=0)
    rating: Decimal = Field(default=0, ge=0, le=5)

    ## The ProductCreate schema is used for creating new products.
    #  It inherits from ProductBase and does not add any new fields.
    @model_validator(mode="after")
    ## This validator checks that the selling price is greater than the cost price. If not, it raises a ValueError.
    def validate_prices(self):
        if self.selling_price <= self.cost_price:
            raise ValueError("selling_price must be greater than cost_price")
        return self


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    cost_price: Optional[Decimal] = Field(default=None, gt=0)
    selling_price: Optional[Decimal] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    units_sold: Optional[int] = Field(default=None, ge=0)
    rating: Optional[Decimal] = Field(default=None, ge=0, le=5)

    @model_validator(mode="after")
    def validate_prices(self):
        if (
            self.cost_price is not None
            and self.selling_price is not None
            and self.selling_price <= self.cost_price
        ):
            raise ValueError("selling_price must be greater than cost_price")
        return self


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    cost_price: Decimal
    selling_price: Decimal
    stock: int
    units_sold: int
    rating: Decimal
    created_by: Optional[int]
    is_active: bool
    margin_pct: float
    margin_amount: float

    class Config:
        ## The from_attributes = True setting allows Pydantic to create a ProductResponse model
        #  from an ORM object (like a SQLAlchemy model) by reading its attributes.
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    page: int
    limit: int
    products: list[ProductResponse]
