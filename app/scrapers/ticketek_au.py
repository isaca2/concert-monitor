from typing import List, Dict
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
import urllib.parse
import time
import random

class TicketekAUScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        search_term = keywords[0]
        # Direct search URL
        url = f"https://premier.ticketek.com.au/search/SearchResults.aspx?q={urllib.parse.quote(search_term)}"
        
        self.logger.info(f"Searching Ticketek AU for {search_term}...")
        
        try:
            with sync_playwright() as p:
                # Add --disable-http2 to args to potentially fix the ERR_HTTP2_PROTOCOL_ERROR
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-http2', '--no-sandbox', '--disable-setuid-sandbox']
                )
                
                # Use a more modern and specific User-Agent
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = context.new_page()
                
                # To bypass Akamai, sometimes it's better to hit the home page first
                try:
                    page.goto("https://premier.ticketek.com.au/", timeout=30000, wait_until="domcontentloaded")
                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    self.logger.warning(f"Failed to hit Ticketek home page: {e}")
                
                # Now navigate to search
                try:
                    page.goto(url, timeout=60000, wait_until="domcontentloaded")
                except Exception as e:
                    self.logger.error(f"Failed to navigate to search: {e}")
                    browser.close()
                    return []
                
                # Akamai might still block. Check for blocked content or wait for results.
                try:
                    # Give it a bit to load
                    time.sleep(random.uniform(2, 4))
                    
                    # More generic selectors for better matching
                    items = page.query_selector_all('a[href*="show.aspx"], .event-listing__item, .search-result-item')
                    
                    if not items:
                        self.logger.info(f"No results found on Ticketek for {search_term}")
                        browser.close()
                        return []

                    seen_links = set()
                    for item in items[:10]:
                        try:
                            title = item.inner_text().strip().split('\n')[0]
                            link = item.get_attribute('href') if item.tag_name() == 'a' else \
                                   (item.query_selector('a').get_attribute('href') if item.query_selector('a') else None)
                            
                            if link and link not in seen_links and "/shows/" in link:
                                if not link.startswith('http'):
                                    link = "https://premier.ticketek.com.au" + link
                                
                                if any(k.lower() in title.lower() for k in keywords):
                                    results.append({
                                        "title": title[:100],
                                        "date": "Check Website",
                                        "venue": "Australia",
                                        "city": "Australia",
                                        "url": link,
                                        "source": "Ticketek AU"
                                    })
                                    seen_links.add(link)
                        except:
                            continue
                except Exception as e:
                    self.logger.warning(f"Error parsing Ticketek results: {e}")
                        
                browser.close()
        except Exception as e:
            self.logger.error(f"Ticketek AU Playwright error: {e}")
            
        return results
