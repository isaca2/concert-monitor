from app.models import db, Artist, Concert, Log
from app.scrapers.manager import ScraperManager
from app.scrapers.livenation_au import LiveNationAUScraper
from app.scrapers.cityline_hk import CitylineHKScraper
from app.scrapers.ticketflap import TicketflapScraper
from app.scrapers.damai import DamaiScraper
from app.scrapers.ticketmaster_au import TicketmasterAUScraper
from app.scrapers.ticketek_au import TicketekAUScraper
from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    # Use absolute path for SQLite to work in GitHub Actions
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'concerts.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Ensure tables exist
        os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'), exist_ok=True)
        db.create_all()
        
        # Initialize Scraper Manager
        manager = ScraperManager()
        manager.register_scraper(LiveNationAUScraper())
        manager.register_scraper(CitylineHKScraper())
        manager.register_scraper(TicketflapScraper())
        manager.register_scraper(DamaiScraper())
        manager.register_scraper(TicketmasterAUScraper())
        manager.register_scraper(TicketekAUScraper())
        
        print("Starting manual scrape for GitHub Actions...")
        manager.run_all()
        print("Scrape complete.")
