from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
import urllib.parse

class TicketekAUScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Use the first keyword for search
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        url = f"https://premier.ticketek.com.au/search/SearchResults.aspx?q={encoded_term}"
        
        self.logger.info(f"Searching Ticketek AU for {search_term}...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch Ticketek AU: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ticketek search results are often in a list with specific classes
            # Selector for search results on Ticketek AU
            items = soup.select('.search-result-item, .event-listing__item')
            
            # Fallback to links if classes differ
            if not items:
                items = soup.select('a[href*="premier.ticketek.com.au/shows/show.aspx"]')

            for item in items[:10]:
                try:
                    # Get title and link
                    if item.name == 'a':
                        title = item.get_text(strip=True)
                        link = item.get('href')
                    else:
                        title_el = item.select_one('.title, h3, a')
                        title = title_el.get_text(strip=True) if title_el else ""
                        link_el = item.select_one('a')
                        link = link_el.get('href') if link_el else ""

                    if link and not link.startswith('http'):
                        link = "https://premier.ticketek.com.au" + link
                    
                    # Basic validation: check if title contains the artist name or keyword
                    matches = any(k.lower() in title.lower() for k in keywords)
                    
                    if matches and link:
                        results.append({
                            "title": title,
                            "date": "See Website",
                            "venue": "Australia",
                            "city": "Australia",
                            "url": link,
                            "source": "Ticketek AU"
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Ticketek AU: {e}")
            
        return results
