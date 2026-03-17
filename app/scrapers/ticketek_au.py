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
        url = f"https://premier.ticketek.com.au/search/SearchResults.aspx?q={urllib.parse.quote(search_term)}"
        
        self.logger.info(f"Searching Ticketek AU for {search_term}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-http2', 
                        '--no-sandbox', 
                        '--disable-blink-features=AutomationControlled',
                        '--use-fake-ui-for-media-stream',
                        '--use-fake-device-for-media-stream'
                    ]
                )
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"macOS"',
                        "Upgrade-Insecure-Requests": "1"
                    }
                )
                
                page = context.new_page()
                
                # Bypassing "AutomationControlled" flag
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Navigate with a shorter "commit" timeout to avoid hanging on blocked trackers
                try:
                    # We just want the server to accept us. "commit" is enough to start.
                    page.goto(url, timeout=45000, wait_until="commit")
                    
                    # Now wait specifically for content or a timeout
                    time.sleep(random.uniform(5, 8)) # Give it time to render after commit
                    
                    # Try to find items
                    items = page.query_selector_all('a[href*="show.aspx"], .event-listing__item, .search-result-item')
                    
                    if not items:
                        self.logger.info(f"No results or still loading on Ticketek for {search_term}")
                        # Fallback: check if we are blocked
                        if "captcha" in page.content().lower() or "blocked" in page.content().lower():
                            self.logger.warning("Ticketek search appears to be blocked by captcha/Akamai.")
                        browser.close()
                        return []

                    seen_links = set()
                    for item in items[:10]:
                        try:
                            text = item.inner_text().strip()
                            title = text.split('\n')[0]
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
                    self.logger.error(f"Failed to navigate Ticketek: {e}")
                        
                browser.close()
        except Exception as e:
            self.logger.error(f"Ticketek AU Playwright error: {e}")
            
        return results
