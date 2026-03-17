from abc import ABC, abstractmethod
from typing import List, Dict
import logging

class BaseScraper(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def search_artist(self, artist_name: str, keywords: List[str]) -> List[Dict]:
        """Search for a specific artist and return found concerts."""
        pass

    def discover_popular_events(self) -> List[Dict]:
        """Optionally override to find trending/popular events without keywords."""
        return []
