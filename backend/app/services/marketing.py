import json
import re
import requests
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "openrouter/free")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class MarketingService:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model
        self.base_url = OPENROUTER_BASE_URL

    def _call_api(self, messages: List[Dict]) -> str:
        if not self.api_key:
            return self._generate_mock_response(messages)
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://comparecart.app",
            "X-Title": "CompareCart"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            if response.status_code != 200:
                return self._generate_mock_response(messages)
            
            result = response.json()
            content = result["choices"][0]["message"].get("content")
            
            if not content:
                reasoning = result["choices"][0]["message"].get("reasoning", "")
                return reasoning if reasoning else self._generate_mock_response(messages)
            
            return content
        except Exception as e:
            return self._generate_mock_response(messages)

    def _generate_mock_response(self, messages: List[Dict]) -> str:
        user_message = messages[-1]["content"] if messages else ""
        
        keyword = "products"
        brands = []
        
        KNOWN_BRANDS = [
            'apple', 'samsung', 'sony', 'bose', 'jbl', 'beats', 'lenovo', 'dell', 'hp', 'asus',
            'acer', 'msi', 'huawei', 'oneplus', 'google', 'pixel', 'nothing', 'razer', 'logitech',
            'anker', 'jabra', 'plantronics', 'sennheiser', 'audio-technica', 'skullcandy',
            'galaxy', 'ideapad', 'thinkpad', 'xps', 'spectre', 'rog', 'surface', 'airpods'
        ]
        
        KNOWN_KEYWORDS = ['laptop', 'earbuds', 'headphones', 'phones', 'phone', 'watch', 'tablet', 'keyboard', 'mouse', 'speaker', 'camera', 'buds', 'buds2', 'buds3']
        
        STOP_WORDS = ['the', 'and', 'for', 'with', 'from', 'free', 'new', 'best', 'top', 'wireless', 'bluetooth', 'premium', 'pro', 'plus', 'max', 'ultra', 'mini', 'gen', '2nd', '3rd', '2024', '2025', '2026']
        
        if "Based on these competitor products" in user_message:
            names = re.findall(r'Name:\s*(.+?)(?:\n|$)', user_message)
            seen_brands = set()
            
            for name in names[:5]:
                name_lower = name.lower()
                
                for kw in KNOWN_KEYWORDS:
                    if kw in name_lower and keyword == "products":
                        keyword = kw
                
                for brand in KNOWN_BRANDS:
                    if brand.lower() in name_lower:
                        brand_clean = brand.strip().title()
                        if brand_clean.lower() not in seen_brands:
                            brands.append(brand_clean)
                            seen_brands.add(brand_clean.lower())
                
                words = name.split()
                for word in words[:5]:
                    word_clean = word.strip()
                    if len(word_clean) > 3:
                        word_lower = word_clean.lower()
                        is_known_keyword = any(kw in word_lower for kw in KNOWN_KEYWORDS)
                        is_stop_word = word_lower in STOP_WORDS
                        is_capitalized = word[0].isupper() if word else False
                        
                        if is_capitalized and not is_known_keyword and not is_stop_word:
                            if word_lower not in seen_brands and len(brands) < 3:
                                brands.append(word_clean)
                                seen_brands.add(word_lower)
        
        brand_str = brands[0] if brands else "Premium"
        brand_list = brands[:3] if brands else ["Premium"]
        
        return json.dumps({
            "seo_titles": {
                "primary": f"{brand_str} {keyword.title()} - Best Quality Online",
                "variations": [
                    f"Top Rated {brand_str} {keyword.title()} at Great Prices",
                    f"Shop {brand_str} {keyword.title()} - Free Shipping",
                    f"Best {brand_str} {keyword.title()} Deals - Limited Time"
                ]
            },
            "description": f"Discover our premium {brand_str.lower()} {keyword}. Designed with quality materials and cutting-edge technology. Perfect for those who demand excellence in performance and style.",
            "google_ads": [
                f"{brand_str} {keyword.title()} - Up to 40% Off",
                f"Premium {brand_str} {keyword.title()} - Best Value",
                f"Shop Top-Rated {brand_str} {keyword.title()} Now"
            ],
            "social_ads": {
                "facebook": [
                    f"Premium Quality {brand_str} {keyword.title()} - Shop Now",
                    f"Don't Miss Our Best {brand_str} {keyword.title()} Deals"
                ],
                "instagram": [
                    f"Elevate Your Style with {brand_str} {keyword.title()}",
                    f"Quality You Can Trust - {brand_str} {keyword.title()}"
                ]
            },
            "keywords": {
                "primary": [keyword, f"best {keyword}", f"{brand_str.lower()} {keyword}"] if brands else [keyword, f"best {keyword}", f"cheap {keyword}"],
                "long_tail": [f"best {keyword} for home", f"affordable {keyword} online", f"top rated {keyword} 2024"],
                "competitor": [f"{brand_str.lower()} alternative", f"best {brand_str.lower()} {keyword}"] if brands else [f"{keyword} alternative", f"best {keyword} brand"]
            },
            "image_prompts": {
                "midjourney": [
                    f"Professional product photography of {brand_str} {keyword} on clean white background, studio lighting, white backdrop --ar 4:5 --v 6",
                    f"Lifestyle shot of person using {brand_str} {keyword} at home, natural lighting, warm atmosphere --ar 16:9 --v 6"
                ],
                "dalle": [
                    f"Professional product photography of {brand_str} {keyword} on white background, soft studio lighting"
                ]
            },
            "brands_detected": brand_list
        })

    def generate_marketing_pack(self, products: List[Dict]) -> Dict:
        products_text = self._format_product_info(products)
        
        messages = [
            {
                "role": "system",
                "content": "You are a JSON generator. Your ONLY output must be valid JSON. Never write any other text."
            },
            {
                "role": "user",
                "content": f"""Create marketing content for these products:
{products_text}

Output this EXACT JSON structure (no additional text):
{{
  "seo_titles": {{"primary": "string", "variations": ["string"]}},
  "description": "string",
  "google_ads": ["string"],
  "social_ads": {{"facebook": ["string"], "instagram": ["string"]}},
  "keywords": {{"primary": ["string"], "long_tail": ["string"]}},
  "image_prompts": {{"midjourney": ["string"], "dalle": ["string"]}}
}}"""
            }
        ]
        
        response = self._call_api(messages)
        
        try:
            if isinstance(response, dict):
                marketing_pack = response
            else:
                marketing_pack = json.loads(response)
            marketing_pack["ai_source"] = "openrouter"
            marketing_pack["model"] = self.model
        except (json.JSONDecodeError, TypeError):
            marketing_pack = json.loads(self._generate_mock_response(messages))
            marketing_pack["ai_source"] = "template"
            
        marketing_pack["generated_at"] = datetime.now().isoformat()
        marketing_pack["source_products"] = len(products)
        
        return marketing_pack

    def _format_product_info(self, products: List[Dict]) -> str:
        formatted = []
        for i, p in enumerate(products[:5], 1):
            formatted.append(f"""
Product {i}:
- Name: {p.get('name', 'N/A')}
- Price: {p.get('price', 'N/A')}
- Rating: {p.get('rating', 'N/A')}
- Platform: {p.get('platform', 'N/A')}
""")
        
        return "\n".join(formatted)
