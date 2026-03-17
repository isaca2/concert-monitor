from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
import urllib.parse

class LiveNationAUScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        # Live Nation often updates their search endpoint
        url = f"https://www.livenation.com.au/search?keywords={encoded_term}"
        
        self.logger.info(f"Searching Live Nation AU for {search_term}...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                self.logger.error(f"Failed to fetch Live Nation AU: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links that look like show or artist pages
            links = soup.select('a[href*="/show/"], a[href*="/artist/"]')
            
            seen_urls = set()
            for link_el in links:
                try:
                    title = link_el.get_text(strip=True)
                    link = link_el.get('href')
                    
                    if not link or link in seen_urls:
                        continue
                        
                    if not link.startswith('http'):
                        link = "https://www.livenation.com.au" + link
                    
                    # Basic validation: check if title or URL contains the artist name or keyword
                    matches = any(k.lower() in title.lower() or k in link.lower() for k in keywords)
                    
                    if matches and "/artist/" in link:
                        # If it's an artist page, we found the artist profile which likely has show info
                        results.append({
                            "title": f"Live Nation Artist: {title}",
                            "date": "Check Website",
                            "venue": "Australia",
                            "city": "Australia",
                            "url": link,
                            "source": "Live Nation AU"
                        })
                        seen_urls.add(link)
                    elif matches and "/show/" in link:
                        results.append({
                            "title": title,
                            "date": "Check Website",
                            "venue": "Various",
                            "city": "Australia",
                            "url": link,
                            "source": "Live Nation AU"
                        })
                        seen_urls.add(link)
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping Live Nation AU: {e}")
            
        return results
