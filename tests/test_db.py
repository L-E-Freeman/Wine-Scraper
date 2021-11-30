import sqlite3

import pytest 
from wine_scraper.db import get_db

def test_get_close_db(app):
    """
    Within an application context, get_db should return the same connection 
    each time it's called, and after the context, the connection should be 
    closed. 
    """
    # Use app.app_context if you are trying to access current_app outside an 
    # application context. Current_app (the application context) allows you to 
    # access the application handling the current request.
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # pytest.raises allows you to write assertions about raised exceptions.
    with pytest.raises(sqlite3.ProgrammingError) as e: 
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)