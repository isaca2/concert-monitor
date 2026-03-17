from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.String(200), nullable=False) # Comma-separated
    regions = db.Column(db.String(50), default="AU,CN,HK") # e.g. "AU,CN,HK"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    concerts = db.relationship('Concert', backref='artist', lazy=True, cascade="all, delete-orphan")

class Concert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=True) # Now nullable for "Global Discovery"
    title = db.Column(db.String(200), nullable=False)
    date_str = db.Column(db.String(50)) # Raw string date from source
    venue = db.Column(db.String(100))
    city = db.Column(db.String(50))
    url = db.Column(db.String(500), unique=True, nullable=False)
    source = db.Column(db.String(50)) # e.g. "Ticketmaster"
    is_global_discovery = db.Column(db.Boolean, default=False) # To distinguish from watchlist
    found_at = db.Column(db.DateTime, default=datetime.utcnow)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    level = db.Column(db.String(20), default="INFO")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
