from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    price = Column(String(50), default="")
    original_price = Column(String(50), default="")
    discount = Column(String(50), default="")
    sold = Column(String(50), default="")
    rating = Column(String(20), default="")
    reviews = Column(Integer, default=0)
    description = Column(Text, default="")
    image = Column(String(500), default="")
    link = Column(String(1000), default="")
    platform = Column(String(50), default="")  # amazon, ebay, walmart
    location = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "original_price": self.original_price,
            "discount": self.discount,
            "sold": self.sold,
            "rating": self.rating,
            "reviews": self.reviews,
            "description": self.description,
            "image": self.image,
            "link": self.link,
            "platform": self.platform,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }