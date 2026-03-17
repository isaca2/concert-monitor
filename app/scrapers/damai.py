from typing import List, Dict
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
import time
import random

class DamaiScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Chinese name is usually better for Damai
        search_term = artist_name
        for k in keywords:
            if any('\u4e00' <= char <= '\u9fff' for char in k):
                search_term = k
                break
                
        url = f"https://search.damai.cn/search.htm?keyword={search_term}"
        
        self.logger.info(f"Searching Damai via Playwright for {search_term}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                    locale="zh-CN"
                )
                page = context.new_page()
                page.goto(url, timeout=60000)
                
                # Human-like delay
                time.sleep(random.uniform(2, 4))
                
                # Check for captcha or "No results"
                if "验证" in page.content():
                    self.logger.warning("Damai triggered a captcha.")
                    browser.close()
                    return []
                
                # Damai often takes time to render. Wait for elements or specific content.
                try:
                    # Look for search results. Selector might need to be more flexible.
                    page.wait_for_selector('.search_items, .search-result, .items', timeout=15000)
                except:
                    # If selector fails, try getting all links
                    self.logger.info("Search items selector not found on Damai, checking for links...")

                items = page.query_selector_all('li.items, .search_items li, .item__box')
                
                for item in items[:10]:
                    try:
                        title_el = item.query_selector('a.title, .item_title a, h3 a')
                        if not title_el:
                            title_el = item.query_selector('a')
                            
                        link = title_el.get_attribute('href') if title_el else None
                        title = title_el.inner_text().strip() if title_el else ""
                        
                        if link and title:
                            if not link.startswith('http'):
                                link = "https:" + link if link.startswith('//') else "https://www.damai.cn" + link
                                
                            results.append({
                                "title": title[:100],
                                "date": "Check Damai",
                                "venue": "Mainland China",
                                "city": "China",
                                "url": link,
                                "source": "Damai"
                            })
                    except:
                        continue
                        
                browser.close()
        except Exception as e:
            self.logger.error(f"Damai Playwright error: {e}")
            
        return results
