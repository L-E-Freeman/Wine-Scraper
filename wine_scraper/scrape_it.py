import functools

from flask.blueprints import Blueprint

from wine_scraper.db import get_db

# Creates blueprint named 'auth'. 
bp = Blueprint('scrape_it', __name__, url_prefix='/')

