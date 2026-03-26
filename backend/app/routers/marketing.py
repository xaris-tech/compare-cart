from typing import List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.marketing import MarketingService

router = APIRouter()

marketing_service = MarketingService()


class MarketingRequest(BaseModel):
    products: List[Dict]


class MarketingResponse(BaseModel):
    success: bool
    marketing_pack: Dict


@router.post("/generate-marketing", response_model=MarketingResponse)
async def generate_marketing(request: MarketingRequest):
    if not request.products:
        raise HTTPException(status_code=400, detail="No products provided")
    
    marketing_pack = marketing_service.generate_marketing_pack(request.products)
    
    return MarketingResponse(
        success=True,
        marketing_pack=marketing_pack
    )


@router.get("/marketing-models")
def get_models():
    return {
        "models": [
            {"id": "openrouter/free", "name": "Llama 3.2 3B (Free)"},
            {"id": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
            {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku"}
        ]
    }
