from typing import List, Dict
import random
from app.scrapers.base import BaseScraper

class MockScraper(BaseScraper):
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        self.logger.info(f"Mock scraping for {artist_name}...")
        # Simulate finding a concert with 30% chance
        if random.random() < 0.3:
            return [{
                "title": f"{artist_name} World Tour 2026",
                "date": "2026-11-15",
                "venue": "Rod Laver Arena",
                "city": "Melbourne",
                "url": f"https://mock-ticket.com/{artist_name.replace(' ', '-').lower()}",
                "source": "MockSource"
            }]
        return []

    def discover_popular_events(self) -> List[Dict]:
        """Generate a random trending event for Melbourne."""
        if random.random() < 0.2:
            events = [
                {"title": "Lady Gaga: The Chromatica Ball", "venue": "Marvel Stadium", "city": "Melbourne"},
                {"title": "Adele Live 2026", "venue": "MCG", "city": "Melbourne"},
                {"title": "Taylor Swift: The Eras Tour (Encore)", "venue": "MCG", "city": "Melbourne"},
                {"title": "Sydney Opera House Gala", "venue": "Opera House", "city": "Sydney"} # This should be filtered out
            ]
            choice = random.choice(events)
            return [{
                "title": choice["title"],
                "date": "2026-12-01",
                "venue": choice["venue"],
                "city": choice["city"],
                "url": f"https://mock-ticket.com/{choice['title'].replace(' ', '-').lower()}",
                "source": "MockDiscovery"
            }]
        return []
