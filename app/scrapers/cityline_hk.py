from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
import urllib.parse

class CitylineHKScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        # Using the standard website search URL
        url = f"https://www.cityline.com/tc/search.html?keyword={encoded_term}"
        
        self.logger.info(f"Searching Cityline HK for {search_term}...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch Cityline HK: {response.status_code}")
                # Try fallback URL
                url = f"https://www.cityline.com/Events.html?q={encoded_term}"
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cityline uses a dynamic search sometimes, but the base page often lists links
            links = soup.select('a[href*="/event/"], a[href*="detail.html"]')
            
            seen_urls = set()
            for link_el in links:
                try:
                    title = link_el.get_text(strip=True)
                    link = link_el.get('href')
                    
                    if not link or link in seen_urls:
                        continue
                        
                    if not link.startswith('http'):
                        link = "https://www.cityline.com" + link
                    
                    matches = any(k.lower() in title.lower() for k in keywords)
                    
                    if matches:
                        results.append({
                            "title": title,
                            "date": "Check Website",
                            "venue": "Hong Kong",
                            "city": "Hong Kong",
                            "url": link,
                            "source": "Cityline HK"
                        })
                        seen_urls.add(link)
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Cityline HK: {e}")
            
        return results
