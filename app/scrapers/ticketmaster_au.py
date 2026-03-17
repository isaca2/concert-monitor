from typing import List, Dict
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
import time

class TicketmasterAUScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Use the first keyword for search
        search_term = keywords[0]
        url = f"https://www.ticketmaster.com.au/search?q={search_term}"
        
        self.logger.info(f"Searching Ticketmaster AU for {search_term}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Using a custom user-agent to reduce detection
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, timeout=60000)
                
                # Check for "no results"
                if "No results found" in page.content():
                    self.logger.info(f"No results on Ticketmaster AU for {search_term}")
                    browser.close()
                    return []

                # Wait for event items. Ticketmaster AU uses different selectors occasionally.
                # Try common ones.
                try:
                    page.wait_for_selector('div[data-testid="event-list-item"], .event-listing__item', timeout=10000)
                except:
                    # If selector doesn't appear, maybe no events found or blocked
                    self.logger.warning(f"Timeout waiting for Ticketmaster AU results for {search_term}")
                    browser.close()
                    return []

                # Extract event cards
                items = page.query_selector_all('div[data-testid="event-list-item"], .event-listing__item')
                
                for item in items[:10]:
                    try:
                        title_el = item.query_selector('span[data-testid="event-name"], .event-listing__title')
                        date_el = item.query_selector('span[data-testid="event-date"], .event-listing__date')
                        link_el = item.query_selector('a[href*="/event/"], a[href*="/artist/"]')
                        venue_el = item.query_selector('span[data-testid="venue-name"], .event-listing__venue')
                        
                        if title_el and link_el:
                            title = title_el.inner_text()
                            link = link_el.get_attribute('href')
                            if link and not link.startswith('http'):
                                link = "https://www.ticketmaster.com.au" + link
                            
                            # Validate title against keywords
                            if any(k.lower() in title.lower() for k in keywords):
                                results.append({
                                    "title": title,
                                    "date": date_el.inner_text() if date_el else "Check Website",
                                    "venue": venue_el.inner_text() if venue_el else "Unknown Venue",
                                    "city": "Australia",
                                    "url": link,
                                    "source": "Ticketmaster AU"
                                })
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
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.goto(url, timeout=60000)
                
                # Wait for discovery links or event cards
                try:
                    page.wait_for_selector('a[href*="/event/"], div[data-testid="event-list-item"]', timeout=10000)
                    
                    # Try to find items that look like events
                    items = page.query_selector_all('a[href*="/event/"], div[data-testid="event-list-item"]')
                    
                    seen_urls = set()
                    for item in items[:25]:
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
                            
                            if title:
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
