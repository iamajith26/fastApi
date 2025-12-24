from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.session import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import Optional

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product: ProductCreate) -> Product:
        db_product = Product(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def update_product(self, product_id: int, product: ProductUpdate) -> Optional[Product]:
        db_product = self.get_product(product_id)
        if db_product:
            for key, value in product.dict(exclude_unset=True).items():
                setattr(db_product, key, value)
            self.db.commit()
            self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int) -> bool:
        db_product = self.get_product(product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        # Set is_active to False instead of deleting
        db_product.is_active = False
        self.db.commit()
        self.db.refresh(db_product)
        return {"message": "Product deactivated successfully"}

    def get_all_products(self):
        return self.db.query(Product).all()

# Dependency provider
def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)