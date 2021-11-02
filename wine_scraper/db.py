import sqlite3

import click
from flask import current_app, g 
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], 
            # Parse decltypes allows sql to detect what type the data is in.
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # setting row factory attribute to sqlite3.Row tells the connection to 
        # return rows that behave like dicts. This allows acessing collumns
        # by name.
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        # executescript is an sql method. 
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# close_db and init_db_command functions need to be registered with the 
# application instance, otherwise they won't be used by the application. 
# However, since using a factory function, that instance isn't available when 
# writing the functions. Write instead a function that takes an application 
# and does the registration.
def init_app(app):
    # app.teardown_appcontext() tells flask to call that function when cleaning
    # up after returning response.
    app.teardown_appcontext(close_db)
    # app.cli.add_command adds a new command that can be called with the flask 
    # command.
    app.cli.add_command(init_db_command)
