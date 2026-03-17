from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
import urllib.parse

class TicketflapScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Use the first keyword for search
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        url = f"https://www.ticketflap.com/search?q={encoded_term}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch Ticketflap: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ticketflap search results usually have event-card classes
            event_cards = soup.select('.event-card, .event-list-item, a[href*="/"]')

            for card in event_cards[:10]:
                try:
                    title = card.get_text(strip=True)
                    link = card.get('href')
                    
                    if link and not link.startswith('http'):
                        link = "https://www.ticketflap.com" + link
                    
                    # Basic validation: check if title contains the artist name or keyword
                    matches = any(k.lower() in title.lower() for k in keywords)
                    
                    if matches and link and "/events/" in link:
                        results.append({
                            "title": title[:100], # Trim long titles
                            "date": "See Website",
                            "venue": "Various",
                            "city": "Asia",
                            "url": link,
                            "source": "Ticketflap"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Ticketflap: {e}")
            
        return results
