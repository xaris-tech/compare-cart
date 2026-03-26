from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    price: str = ""
    original_price: str = ""
    discount: str = ""
    sold: str = ""
    rating: str = ""
    reviews: int = 0
    description: str = ""
    image: str = ""
    link: str = ""
    platform: str = ""
    location: str = ""

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int