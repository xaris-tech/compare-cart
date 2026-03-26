from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ComparisonCreate(BaseModel):
    name: str = ""
    product_ids: List[int]

class ComparisonResponse(BaseModel):
    id: int
    name: str
    product_ids: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ComparisonWithProducts(BaseModel):
    id: int
    name: str
    products: List[dict]
    created_at: Optional[datetime] = None