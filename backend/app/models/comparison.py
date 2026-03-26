import json
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), default="")
    product_ids = Column(Text, default="[]")  # JSON array of IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def get_product_ids_list(self):
        if not self.product_ids:
            return []
        try:
            return json.loads(self.product_ids)
        except:
            return []
    
    def set_product_ids(self, ids: list):
        self.product_ids = json.dumps(ids)