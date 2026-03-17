from jinja2 import Environment, FileSystemLoader
from app.models import db, Artist, Concert, Log
from flask import Flask
import os

def build_static():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'concerts.db')
    db.init_app(app)

    with app.app_context():
        # Load all data
        concerts = Concert.query.order_by(Concert.found_at.desc()).all()
        logs = Log.query.order_by(Log.timestamp.desc()).limit(20).all()
        artists = Artist.query.all()

        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('templates'))
        
        # We need to mock url_for because it's used in templates
        # Since it's a static site, we'll just return '#' for navigation links
        def mock_url_for(endpoint, **values):
            if endpoint == 'index': return 'index.html'
            return '#'

        # Render Index (Dashboard)
        template = env.get_template('index.html')
        # We need to handle the "extends" and "block" manually or just use the same env
        # Actually, Jinja2 handles extends automatically if the loader is set up.
        
        # Mocking the Flask globals/filters that templates use
        html_content = template.render(
            concerts=concerts,
            logs=logs,
            url_for=mock_url_for,
            get_flashed_messages=lambda **kwargs: []
        )

        # Ensure output directory exists
        os.makedirs('dist', exist_ok=True)
        
        with open('dist/index.html', 'w') as f:
            f.write(html_content)
        
        print("Static site generated in dist/index.html")

if __name__ == "__main__":
    build_static()
