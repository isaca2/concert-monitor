from typing import List, Dict
from playwright.sync_api import sync_playwright
from app.scrapers.base import BaseScraper
import time

class DamaiScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        results = []
        # Chinese name is usually better for Damai
        # Try to find a keyword with Chinese characters
        search_term = artist_name
        for k in keywords:
            if any('\u4e00' <= char <= '\u9fff' for char in k):
                search_term = k
                break
                
        url = f"https://search.damai.cn/search.htm?keyword={search_term}"
        
        self.logger.info(f"Attempting to scrape Damai for {search_term}. Warning: Damai has strong anti-bot.")
        
        try:
            with sync_playwright() as p:
                # Using a real browser profile or specific headers might be needed
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=60000)
                
                # Check for captcha or "No results"
                if "验证" in page.content():
                    self.logger.warning("Damai triggered a captcha. Manual intervention or advanced bypass needed.")
                    browser.close()
                    return []
                
                # Try to find items. Selector based on typical Damai structure.
                page.wait_for_selector('.search_items', timeout=5000)
                items = page.query_selector_all('.search_items li')
                
                for item in items[:5]:
                    try:
                        title_el = item.query_selector('.item_title a')
                        link = title_el.get_attribute('href') if title_el else None
                        title = title_el.inner_text() if title_el else ""
                        
                        if link and title:
                            if not link.startswith('http'):
                                link = "https:" + link
                                
                            results.append({
                                "title": title,
                                "date": "See Damai",
                                "venue": "Mainland China",
                                "city": "China",
                                "url": link,
                                "source": "Damai"
                            })
                    except Exception as e:
                        continue
                        
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Playwright error on Damai: {e}")
            
        return results
