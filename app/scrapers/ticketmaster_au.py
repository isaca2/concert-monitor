from typing import List, Dict
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
import time
import random

class TicketmasterAUScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Use the first keyword for search
        search_term = keywords[0]
        url = f"https://www.ticketmaster.com.au/search?q={search_term}"
        
        self.logger.info(f"Searching Ticketmaster AU for {search_term}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-http2', '--no-sandbox']
                )
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = context.new_page()
                
                # Visit home first for cookies/session
                try:
                    page.goto("https://www.ticketmaster.com.au/", timeout=30000, wait_until="domcontentloaded")
                    time.sleep(random.uniform(1, 2))
                except:
                    pass
                
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                time.sleep(random.uniform(2, 4))
                
                # Check for "no results"
                if "No results found" in page.content():
                    self.logger.info(f"No results on Ticketmaster AU for {search_term}")
                    browser.close()
                    return []

                # Wait for event items
                try:
                    page.wait_for_selector('div[data-testid="event-list-item"], .event-listing__item', timeout=10000)
                except:
                    # Generic link discovery if selector fails
                    pass

                # Extract event cards
                items = page.query_selector_all('div[data-testid="event-list-item"], .event-listing__item, a[href*="/event/"]')
                
                seen_urls = set()
                for item in items[:15]:
                    try:
                        title_el = item.query_selector('span[data-testid="event-name"], .event-listing__title')
                        if not title_el and item.tag_name() == 'a':
                            title_el = item
                            
                        link_el = item.query_selector('a[href*="/event/"], a[href*="/artist/"]')
                        if not link_el and item.tag_name() == 'a':
                            link_el = item
                            
                        if title_el and link_el:
                            title = title_el.inner_text().strip().split('\n')[0]
                            link = link_el.get_attribute('href')
                            
                            if link and link not in seen_urls:
                                if not link.startswith('http'):
                                    link = "https://www.ticketmaster.com.au" + link
                                
                                # Validate title against keywords
                                if any(k.lower() in title.lower() for k in keywords):
                                    results.append({
                                        "title": title[:100],
                                        "date": "Check Website",
                                        "venue": "Australia",
                                        "city": "Australia",
                                        "url": link,
                                        "source": "Ticketmaster AU"
                                    })
                                    seen_urls.add(link)
                    except Exception as e:
                        continue
                        
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Ticketmaster AU error: {e}")
            
        return results

    def discover_popular_events(self) -> List[Dict]:
        results = []
        # Target Melbourne discovery
        url = "https://www.ticketmaster.com.au/discover/concerts/melbourne"
        
        self.logger.info("Discovering popular events in Melbourne on Ticketmaster...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-http2']
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                time.sleep(random.uniform(2, 4))
                
                # Wait for discovery links or event cards
                try:
                    # Try to find items that look like events
                    items = page.query_selector_all('a[href*="/event/"], div[data-testid="event-list-item"]')
                    
                    seen_urls = set()
                    for item in items[:30]:
                        try:
                            # Extract link
                            if item.tag_name() == 'a':
                                link_attr = item.get_attribute('href')
                            else:
                                link_el = item.query_selector('a')
                                link_attr = link_el.get_attribute('href') if link_el else None
                                
                            if not link_attr or link_attr in seen_urls:
                                continue
                                
                            # Extract text/title
                            text = item.inner_text().strip()
                            title = text.split('\n')[0][:100]
                            
                            if title and len(title) > 3:
                                full_url = link_attr if link_attr.startswith('http') else "https://www.ticketmaster.com.au" + link_attr
                                results.append({
                                    "title": title,
                                    "date": "Trending",
                                    "venue": "Melbourne",
                                    "city": "Melbourne",
                                    "url": full_url,
                                    "source": "Ticketmaster Discovery"
                                })
                                seen_urls.add(link_attr)
                        except:
                            continue
                except:
                    self.logger.warning("No trending events found for Melbourne on Ticketmaster")
                        
                browser.close()
        except Exception as e:
            self.logger.error(f"Ticketmaster Discovery error: {e}")
            
        return results
