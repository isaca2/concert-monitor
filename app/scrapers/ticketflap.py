from typing import List, Dict
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
import urllib.parse
import time
import random

class TicketflapScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        url = f"https://www.ticketflap.com/search?q={encoded_term}"
        
        self.logger.info(f"Searching Ticketflap via Playwright for {search_term}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, timeout=60000)
                
                # Ticketflap usually renders list. Wait for it.
                time.sleep(random.uniform(2, 4))
                
                # Check for "no events"
                if "No results found" in page.content():
                    self.logger.info(f"No results on Ticketflap for {search_term}")
                    browser.close()
                    return []

                # Find all links on the search results page
                links = page.query_selector_all('a[href*="/"]')
                
                seen_urls = set()
                for link_el in links:
                    try:
                        title = link_el.inner_text().strip()
                        link = link_el.get_attribute('href')
                        
                        if not link or link in seen_urls:
                            continue
                            
                        if not link.startswith('http'):
                            link = "https://www.ticketflap.com" + link
                        
                        # Ticketflap links often have event-title-slug
                        matches = any(k.lower().replace(' ', '-') in link.lower() for k in keywords) or \
                                  any(k.lower() in title.lower() for k in keywords)
                        
                        if matches and "/events/" in link:
                            results.append({
                                "title": title[:100] if title else f"Event: {search_term}",
                                "date": "Check Website",
                                "venue": "Asia",
                                "city": "Asia",
                                "url": link,
                                "source": "Ticketflap"
                            })
                            seen_urls.add(link)
                    except:
                        continue
                        
                browser.close()
        except Exception as e:
            self.logger.error(f"Ticketflap Playwright error: {e}")
            
        return results
