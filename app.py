from flask import Flask, render_template, request, redirect, url_for, flash
from app.models import db, Artist, Concert, Log
from app.scrapers.manager import ScraperManager
from app.scrapers.livenation_au import LiveNationAUScraper
from app.scrapers.cityline_hk import CitylineHKScraper
from app.scrapers.ticketflap import TicketflapScraper
from app.scrapers.damai import DamaiScraper
from app.scrapers.ticketmaster_au import TicketmasterAUScraper
from app.scrapers.ticketek_au import TicketekAUScraper
from apscheduler.schedulers.background import BackgroundScheduler
import os
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///concerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-key-change-this'

db.init_app(app)

# Initialize Scraper Manager
scraper_manager = ScraperManager()
scraper_manager.register_scraper(LiveNationAUScraper())
scraper_manager.register_scraper(CitylineHKScraper())
scraper_manager.register_scraper(TicketflapScraper())
scraper_manager.register_scraper(DamaiScraper())
scraper_manager.register_scraper(TicketmasterAUScraper())
scraper_manager.register_scraper(TicketekAUScraper())
# Register other scrapers here when ready

def run_scrapers():
    """Run scraping job in app context."""
    with app.app_context():
        print("Running scheduled scrape...")
        scraper_manager.run_all()

scheduler = BackgroundScheduler()
scheduler.add_job(func=run_scrapers, trigger="interval", hours=12)
scheduler.start()

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    concerts = Concert.query.order_by(Concert.found_at.desc()).all()
    logs = Log.query.order_by(Log.timestamp.desc()).limit(10).all()
    return render_template('index.html', concerts=concerts, logs=logs)

@app.route('/scrape-now')
def scrape_now():
    """Manually trigger scraping in a background thread to avoid blocking."""
    thread = threading.Thread(target=run_scrapers)
    thread.start()
    flash('Scraping started in background! Check logs shortly.', 'info')
    return redirect(url_for('index'))

@app.route('/artists', methods=['GET', 'POST'])
def artists():
    if request.method == 'POST':
        name = request.form.get('name')
        keywords = request.form.get('keywords')
        regions = request.form.get('regions')
        
        if name and keywords:
            new_artist = Artist(name=name, keywords=keywords, regions=regions)
            db.session.add(new_artist)
            db.session.commit()
            flash('Artist added successfully!', 'success')
        else:
            flash('Name and Keywords are required.', 'error')
            
    artists = Artist.query.all()
    return render_template('artists.html', artists=artists)

@app.route('/artist/delete/<int:id>')
def delete_artist(id):
    artist = Artist.query.get_or_404(id)
    db.session.delete(artist)
    db.session.commit()
    flash('Artist deleted.', 'success')
    return redirect(url_for('artists'))

@app.route('/artist/edit/<int:id>', methods=['POST'])
def edit_artist(id):
    artist = Artist.query.get_or_404(id)
    artist.name = request.form.get('name')
    artist.keywords = request.form.get('keywords')
    artist.regions = request.form.get('regions')
    db.session.commit()
    flash('Artist updated!', 'success')
    return redirect(url_for('artists'))

@app.route('/clear-mock-concerts')
def clear_mock_concerts():
    """Cleanup any old mock data from the database."""
    count = Concert.query.filter(Concert.source.like('%Mock%')).delete(synchronize_session=False)
    db.session.commit()
    flash(f'Cleared {count} mock concerts from database.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
