import os 
import tempfile

import pytest

from wine_scraper import create_app
from flaskr.db import get_db, init_db

# Join path to current file with data.sql, 'rb' opens the file in binary 
# format. 
with open (os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():

    # Creates and opens temporary file, returning file descriptor and the 
    # path to it. 
    db_fd, db_path = tempfile.mkstemp()

    # Using create_app from __init__ file. 
    app = create_app({
        'TESTING': True, 
        'DATABASE': db_path,
    })

    # Database created and test data inserted. 
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    # After test finished, temporary file is closed and removed.
    os.close(db_fd)
    os.unlink(db_path)

# Client fixture calls app.test_client() with the application object
# (generator object from yield statement) created by 
# the app fixture. Tests will use the client to make requests to the 
# application without running the server.
@pytest.fixture
def client(app):
    return app.test_client()

# Creates a runner that can call the Click commands registered with app.
# Click is a package that allows you to create neat command line interfaces.
@pytest.fixture
def runner(app):
    return app.test_cli_runner()