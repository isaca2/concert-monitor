from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
import urllib.parse

class CitylineHKScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Use the first keyword for search
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        url = f"https://search.cityline.com/tc/search?q={encoded_term}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'zh-HK,zh;q=0.9,en;q=0.8'
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch Cityline HK: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cityline HK search results usually have event items
            # We look for result items.
            event_items = soup.select('.event-item, .search-result-item')
            
            if not event_items:
                # Try finding links directly if the structure is different
                event_items = soup.select('a[href*="/event/"]')

            for item in event_items[:10]:
                try:
                    title = item.get_text(strip=True)
                    link = item.get('href')
                    
                    if link and not link.startswith('http'):
                        link = "https://www.cityline.com" + link
                    
                    # Basic validation: check if title contains the artist name or keyword
                    matches = any(k.lower() in title.lower() for k in keywords)
                    
                    if matches and link:
                        results.append({
                            "title": title,
                            "date": "See Website",
                            "venue": "Hong Kong",
                            "city": "Hong Kong",
                            "url": link,
                            "source": "Cityline HK"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Cityline HK: {e}")
            
        return results
