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

def test_init_db_command(runner, monkeypatch):
    """
    init_db command should call the init_db function and output a message.
    """
    class Recorder(object):
        called = False
    
    def fake_init_db():
        Recorder.called = True

    # monkeypatch fixture replaces init_db function with one that records that
    # it's been called. runner fixture written in conftest used to call 
    # init_db command by name
    monkeypatch.setattr('wine_scraper.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called