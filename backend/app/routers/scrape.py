from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.product import Product
from app.services.scraper import AmazonScraper

router = APIRouter()


class ScrapeRequest(BaseModel):
    keyword: str
    platform: str = "amazon"
    num_products: int = 10


class ScrapeResponse(BaseModel):
    success: bool
    products: List[dict]
    count: int


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_products(request: ScrapeRequest, db: Session = Depends(get_db)):
    if request.platform.lower() != "amazon":
        raise HTTPException(status_code=400, detail="Currently only Amazon platform is supported")
    
    scraper = AmazonScraper()
    products = scraper.scrape(request.keyword, request.num_products)
    
    saved_products = []
    for p in products:
        if not p.get("name", "").startswith("Error:"):
            db_product = Product(
                name=p["name"],
                price=p["price"],
                original_price=p.get("original_price", ""),
                discount=p.get("discount", ""),
                sold=p.get("sold", ""),
                rating=p.get("rating", ""),
                location=p.get("location", ""),
                image=p.get("image", ""),
                link=p.get("link", ""),
                platform=p["platform"]
            )
            db.add(db_product)
            saved_products.append(p)
    
    db.commit()
    
    return ScrapeResponse(
        success=True,
        products=saved_products,
        count=len(saved_products)
    )


@router.get("/platforms")
def get_platforms():
    return {
        "platforms": [
            {"name": "amazon", "label": "Amazon"}
        ]
    }
