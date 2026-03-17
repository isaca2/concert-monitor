from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
import urllib.parse

class LiveNationAUScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Use the first keyword for search
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        url = f"https://www.livenation.com.au/artist-results?keywords={encoded_term}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch Live Nation AU: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Live Nation AU search results usually have event cards
            # We look for result items. The structure often changes, so we'll be broad.
            event_cards = soup.select('.eventcard, .result-item, .artist-result')
            
            if not event_cards:
                # Try another selector if the site layout changed
                event_cards = soup.select('a[href*="/show/"]')

            for card in event_cards[:10]:
                try:
                    title = card.get_text(strip=True)
                    link = card.get('href')
                    
                    if link and not link.startswith('http'):
                        link = "https://www.livenation.com.au" + link
                    
                    # Basic validation: check if title contains the artist name or keyword
                    matches = any(k.lower() in title.lower() for k in keywords)
                    
                    if matches and link:
                        results.append({
                            "title": title,
                            "date": "See Website",
                            "venue": "Various Venues",
                            "city": "Australia",
                            "url": link,
                            "source": "Live Nation AU"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Live Nation AU: {e}")
            
        return results
