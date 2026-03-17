import logging
from app.models import db, Concert, Artist, Log
from app.scrapers.base import BaseScraper
from app.notifier import EmailNotifier
from typing import List

class ScraperManager:
    def __init__(self):
        self.scrapers: List[BaseScraper] = []
        self.logger = logging.getLogger("ScraperManager")
        self.notifier = EmailNotifier()

    def register_scraper(self, scraper: BaseScraper):
        self.scrapers.append(scraper)

    def run_all(self):
        """Run all scrapers for all artists and also discover global events."""
        artists = Artist.query.all()
        all_new_concerts = []
        
        # 1. Run User-Specific Artist Search
        for artist in artists:
            self.logger.info(f"Scraping for {artist.name}...")
            keywords = [k.strip() for k in artist.keywords.split(',')]
            
            for scraper in self.scrapers:
                try:
                    results = scraper.search_artist(artist.name, keywords)
                    new_concerts = self._save_results(artist, results)
                    all_new_concerts.extend(new_concerts)
                except Exception as e:
                    self.logger.error(f"Error in {scraper.__class__.__name__}: {e}")
                    self._log_db(f"Error scraping {artist.name}: {str(e)}", "ERROR")
        
        # 2. Global Discovery (Trending Events)
        self.logger.info("Running global event discovery for Melbourne...")
        for scraper in self.scrapers:
            try:
                results = scraper.discover_popular_events()
                # Filter for Melbourne
                melbourne_results = []
                for res in results:
                    text_to_check = (res.get('title', '') + res.get('venue', '') + res.get('city', '')).lower()
                    if "melbourne" in text_to_check:
                        melbourne_results.append(res)
                
                new_concerts = self._save_results(None, melbourne_results, is_global=True)
                all_new_concerts.extend(new_concerts)
            except Exception as e:
                self.logger.error(f"Discovery error in {scraper.__class__.__name__}: {e}")

        if all_new_concerts:
            self.notifier.send_notification(all_new_concerts)

    def _save_results(self, artist, results, is_global=False):
        new_concerts_list = []
        for res in results:
            exists = Concert.query.filter_by(url=res['url']).first()
            if not exists:
                concert = Concert(
                    artist_id=artist.id if artist else None,
                    title=res['title'],
                    date_str=res.get('date'),
                    venue=res.get('venue'),
                    city=res.get('city'),
                    url=res['url'],
                    source=res['source'],
                    is_global_discovery=is_global
                )
                db.session.add(concert)
                new_concerts_list.append(concert)
        
        if new_concerts_list:
            db.session.commit()
            target_name = artist.name if artist else "Global Discovery"
            self._log_db(f"Found {len(new_concerts_list)} new concerts for {target_name}", "INFO")
        
        return new_concerts_list

    def _log_db(self, message, level):
        log = Log(message=message, level=level)
        db.session.add(log)
        db.session.commit()
