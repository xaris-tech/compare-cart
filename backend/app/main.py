import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from app.database import init_db
from app.routers import products, scrape, comparison, marketing

app = FastAPI(
    title="CompareCart API",
    description="E-commerce Product Comparison & Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(scrape.router, prefix="/api", tags=["Scrape"])
app.include_router(comparison.router, prefix="/api", tags=["Comparison"])
app.include_router(marketing.router, prefix="/api", tags=["Marketing"])


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "CompareCart API - E-commerce Intelligence Platform"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
