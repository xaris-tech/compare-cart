import cloudscraper
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
import re


class AmazonScraper:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            }
        )

    def get_search_url(self, keyword: str, page: int = 1) -> str:
        keyword_encoded = keyword.replace(' ', '+')
        return f"https://www.amazon.com/s?k={keyword_encoded}&page={page}"

    def scrape(self, keyword: str, num_products: int = 10) -> List[Dict]:
        products = []
        page_num = 1
        max_pages = (num_products // 10) + 2

        while len(products) < num_products and page_num <= max_pages:
            url = self.get_search_url(keyword, page_num)
            print(f"Scraping page {page_num}: {url}")

            try:
                response = self.scraper.get(url, timeout=self.timeout)
                
                print(f"Status: {response.status_code}")

                if response.status_code != 200:
                    print(f"HTTP {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, 'lxml')

                if self._is_blocked(soup):
                    print("Amazon blocked the request")
                    break

                items = soup.select('.s-result-item[data-component-type="s-search-result"]')
                print(f"Found {len(items)} items on page {page_num}")

                if not items:
                    break

                for item in items:
                    if len(products) >= num_products:
                        break

                    product = self._extract_product(item)
                    if product and product.get('name'):
                        products.append(product)
                        print(f"  Extracted: {product['name'][:50]}...")

                page_num += 1
                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"Request error: {e}")
                break

        if not products:
            return [self._error_product(f"No products found for '{keyword}'")]

        print(f"Total products scraped: {len(products)}")
        return products

    def _is_blocked(self, soup: BeautifulSoup) -> bool:
        page_text = soup.get_text().lower()
        return any(blocked in page_text for blocked in ['sorry', 'captcha', 'robot', 'verify', 'blocked', 'unusual traffic'])

    def _extract_product(self, item: BeautifulSoup) -> Dict:
        try:
            title_elem = item.select_one('h2 a') or item.select_one('.a-text-normal')
            title = title_elem.get_text(strip=True) if title_elem else ""

            if not title:
                return None

            price_whole = item.select_one('.a-price-whole')
            price_fraction = item.select_one('.a-price-fraction')
            price = ""
            if price_whole:
                whole = price_whole.get_text().replace(',', '')
                fraction = price_fraction.get_text() if price_fraction else "00"
                try:
                    price = f"${float(whole)}.{fraction}"
                except:
                    price = f"${whole}.{fraction}"

            if not price:
                price_elem = item.select_one('.a-price .a-offscreen')
                if price_elem:
                    price = price_elem.get_text(strip=True)

            original_price_elem = item.select_one('.a-text-price .a-offscreen')
            original_price = original_price_elem.get_text(strip=True) if original_price_elem else ""

            rating_elem = item.select_one('.a-icon-alt')
            rating = ""
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating = rating_text.split()[0] + "★" if rating_text else ""

            review_elem = item.select_one('.a-size-small')
            sold = ""
            if review_elem:
                review_text = review_elem.get_text(strip=True)
                match = re.search(r'\(([\d,]+)\)', review_text)
                if match:
                    sold = match.group(1)

            img_elem = item.select_one('.s-image')
            image = ""
            if img_elem:
                image = img_elem.get('src') or img_elem.get('data-src') or ""

            link_elem = item.select_one('h2 a')
            link = ""
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if href.startswith('http'):
                        link = href
                    elif href.startswith('/'):
                        link = f"https://www.amazon.com{href}"

            return self.create_product_dict(
                name=title,
                price=price,
                original_price=original_price,
                discount="",
                sold=sold,
                rating=rating,
                location="US",
                image=image,
                link=link,
                platform="amazon"
            )
        except Exception as e:
            return None

    def create_product_dict(
        self,
        name: str,
        price: str,
        original_price: str = "",
        discount: str = "",
        sold: str = "",
        rating: str = "",
        location: str = "",
        image: str = "",
        link: str = "",
        platform: str = ""
    ) -> Dict:
        return {
            "name": name,
            "price": price,
            "original_price": original_price,
            "discount": discount,
            "sold": sold,
            "rating": rating,
            "location": location,
            "image": image,
            "link": link,
            "platform": platform
        }

    def _error_product(self, error_msg: str) -> Dict:
        return self.create_product_dict(
            name=f"Error: {error_msg}",
            price="",
            original_price="",
            discount="",
            sold="",
            rating="",
            location="",
            image="",
            link="",
            platform="amazon"
        )