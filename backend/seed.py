from database import SessionLocal
from models.product import Product
from models.user import User
from services.auth_service import hash_password


def seed_data():
    db = SessionLocal()

    try:
        existing_admin = (
            db.query(User).filter(User.email == "admin@priceiq.com").first()
        )

        if not existing_admin:
            admin = User(
                email="admin@priceiq.com",
                password=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        else:
            admin = existing_admin

        products = [
            {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse",
                "category": "Electronics",
                "cost_price": 450,
                "selling_price": 799,
                "stock": 120,
                "units_sold": 80,
                "rating": 4.4,
            },
            {
                "name": "Bluetooth Headphones",
                "description": "Noise cancelling headphones",
                "category": "Electronics",
                "cost_price": 1200,
                "selling_price": 2499,
                "stock": 75,
                "units_sold": 140,
                "rating": 4.6,
            },
            {
                "name": "Yoga Mat",
                "description": "Anti-slip yoga mat",
                "category": "Fitness",
                "cost_price": 300,
                "selling_price": 699,
                "stock": 200,
                "units_sold": 160,
                "rating": 4.3,
            },
            {
                "name": "Water Bottle",
                "description": "Insulated steel water bottle",
                "category": "Lifestyle",
                "cost_price": 250,
                "selling_price": 599,
                "stock": 300,
                "units_sold": 220,
                "rating": 4.5,
            },
            {
                "name": "Running Shoes",
                "description": "Lightweight running shoes",
                "category": "Fashion",
                "cost_price": 1500,
                "selling_price": 3299,
                "stock": 60,
                "units_sold": 95,
                "rating": 4.2,
            },
            {
                "name": "Desk Lamp",
                "description": "LED study desk lamp",
                "category": "Home",
                "cost_price": 550,
                "selling_price": 1199,
                "stock": 90,
                "units_sold": 70,
                "rating": 4.1,
            },
            {
                "name": "Laptop Stand",
                "description": "Adjustable aluminium laptop stand",
                "category": "Office",
                "cost_price": 700,
                "selling_price": 1599,
                "stock": 110,
                "units_sold": 130,
                "rating": 4.7,
            },
            {
                "name": "Phone Case",
                "description": "Shockproof smartphone case",
                "category": "Accessories",
                "cost_price": 120,
                "selling_price": 399,
                "stock": 500,
                "units_sold": 350,
                "rating": 4.0,
            },
            {
                "name": "Coffee Mug",
                "description": "Ceramic coffee mug",
                "category": "Lifestyle",
                "cost_price": 100,
                "selling_price": 299,
                "stock": 250,
                "units_sold": 180,
                "rating": 4.2,
            },
            {
                "name": "Backpack",
                "description": "Water-resistant travel backpack",
                "category": "Fashion",
                "cost_price": 900,
                "selling_price": 1999,
                "stock": 85,
                "units_sold": 105,
                "rating": 4.5,
            },
        ]

        inserted = 0
        reactivated = 0

        for product_data in products:
            existing_product = (
                db.query(Product).filter(Product.name == product_data["name"]).first()
            )

            if existing_product:
                if not existing_product.is_active:
                    existing_product.is_active = True
                    reactivated += 1
                continue

            db.add(Product(**product_data, created_by=admin.id))
            inserted += 1

        db.commit()

        print(f"Seed complete. Inserted {inserted}, reactivated {reactivated}.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
