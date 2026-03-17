from typing import List, Dict
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
import urllib.parse

class TicketekAUScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        search_term = keywords[0]
        encoded_term = urllib.parse.quote(search_term)
        # Using the direct search URL
        url = f"https://premier.ticketek.com.au/search/SearchResults.aspx?q={encoded_term}"
        
        self.logger.info(f"Searching Ticketek AU via Playwright for {search_term}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, timeout=60000)
                
                # Ticketek often has a loading screen or redirect
                try:
                    page.wait_for_selector('.search-result-item, .event-listing__item, a[href*="show.aspx"]', timeout=10000)
                except:
                    self.logger.warning(f"No results found or timed out on Ticketek AU for {search_term}")
                    browser.close()
                    return []

                items = page.query_selector_all('.search-result-item, .event-listing__item, a[href*="show.aspx"]')
                
                seen_links = set()
                for item in items[:10]:
                    try:
                        title = item.inner_text().strip().split('\n')[0]
                        link = item.get_attribute('href') if item.tag_name() == 'a' else item.query_selector('a').get_attribute('href')
                        
                        if link and link not in seen_links:
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
                        
                browser.close()
        except Exception as e:
            self.logger.error(f"Ticketek AU Playwright error: {e}")
            
        return results
