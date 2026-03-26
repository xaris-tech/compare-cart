from typing import List
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.product import Product
from app.models.comparison import Comparison

router = APIRouter()


def parse_price(price_str: str) -> float:
    if not price_str:
        return 0.0
    numbers = re.findall(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    if numbers:
        return float(numbers[0])
    return 0.0


def parse_rating(rating_str: str) -> float:
    if not rating_str:
        return 0.0
    numbers = re.findall(r'[\d.]+', rating_str)
    if numbers:
        return float(numbers[0])
    return 0.0


class ComparisonCreate(BaseModel):
    product_ids: List[int]
    name: str = "My Comparison"


class ComparisonResponse(BaseModel):
    id: int
    name: str
    products: List[dict]
    analysis: dict = None

    class Config:
        from_attributes = True


@router.post("/comparisons", response_model=ComparisonResponse)
def create_comparison(comparison: ComparisonCreate, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.id.in_(comparison.product_ids)).all()
    
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    
    db_comparison = Comparison(name=comparison.name)
    db_comparison.set_product_ids(comparison.product_ids)
    db.add(db_comparison)
    db.commit()
    db.refresh(db_comparison)
    
    product_list = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "rating": p.rating,
            "platform": p.platform,
            "image": p.image,
            "link": p.link,
            "sold": p.sold,
            "original_price": p.original_price,
            "location": p.location,
        }
        for p in products
    ]
    
    analysis = analyze_products(product_list)
    
    db_comparison.products = product_list
    db_comparison.analysis = analysis
    
    return db_comparison


def analyze_products(products: List[dict]) -> dict:
    prices = []
    ratings = []
    
    for p in products:
        price = parse_price(p.get('price', ''))
        rating = parse_rating(p.get('rating', ''))
        if price > 0:
            prices.append({'id': p['id'], 'price': price, 'name': p['name']})
        if rating > 0:
            ratings.append({'id': p['id'], 'rating': rating, 'name': p['name']})
    
    lowest_price = min(prices, key=lambda x: x['price']) if prices else None
    highest_rating = max(ratings, key=lambda x: x['rating']) if ratings else None
    
    return {
        "lowest_price": lowest_price,
        "highest_rating": highest_rating,
        "price_range": {
            "min": min(p['price'] for p in prices) if prices else 0,
            "max": max(p['price'] for p in prices) if prices else 0
        },
        "avg_price": sum(p['price'] for p in prices) / len(prices) if prices else 0,
        "product_count": len(products)
    }


@router.get("/comparisons", response_model=List[ComparisonResponse])
def get_comparisons(db: Session = Depends(get_db)):
    comparisons = db.query(Comparison).all()
    for comp in comparisons:
        product_ids = comp.get_product_ids_list()
        products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
        product_list = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "rating": p.rating,
                "platform": p.platform,
                "image": p.image,
                "link": p.link,
                "sold": p.sold,
                "original_price": p.original_price,
                "location": p.location,
            }
            for p in products
        ]
        comp.products = product_list
        comp.analysis = analyze_products(product_list)
    return comparisons


@router.get("/comparisons/{comparison_id}", response_model=ComparisonResponse)
def get_comparison(comparison_id: int, db: Session = Depends(get_db)):
    comparison = db.query(Comparison).filter(Comparison.id == comparison_id).first()
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    product_ids = comparison.get_product_ids_list()
    products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
    comparison.products = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "rating": p.rating,
            "platform": p.platform,
            "image": p.image,
            "link": p.link
        }
        for p in products
    ]
    
    return comparison


@router.delete("/comparisons/{comparison_id}")
def delete_comparison(comparison_id: int, db: Session = Depends(get_db)):
    comparison = db.query(Comparison).filter(Comparison.id == comparison_id).first()
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    db.delete(comparison)
    db.commit()
    return {"message": "Comparison deleted"}
