# -*- coding: utf-8 -*-

"""
Logging server written as part of a programming challenge

Many parts borrowed from the flask example on Github:
https://github.com/pallets/flask/tree/0.12-maintenance/examples/flaskr
"""

import os
import json
from datetime import datetime

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, g, request

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'logs.db'),
    DEBUG=True,
    USERNAME='admin',
    PASSWORD='default'
))


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    db = get_db()
    if request.method == 'GET':
        # handle getting and filtering the data
        min_level = request.args.get('min_level', 0) # Default to showing all log messages

        try:
            int(min_level)
        except ValueError:
            min_level = min_level.lower()
            min_level = _convert_log_name_to_id(min_level)
            if min_level is None:
                return json.dumps({'success': False, 'error': 'Bad log level'}, sort_keys=True), 400

        cur = db.execute(
            'select msgs.clientid, l.name, msgs.message, msgs.creation_datetime from messages msgs '
            'inner join loglevels l on msgs.loglevel = l.id '
            'where loglevel >= :min_level;',
            (min_level,)
        )
        entries = cur.fetchall()
        entries = [
            {'clientid': entry[0], 'loglevel': entry[1], 'message': entry[2], 'creation_datetime': entry[3]}
            for entry in entries
        ]
        return json.dumps(entries, sort_keys=True)

    elif request.method == 'POST':
        # handle adding new data to the database
        now = str(datetime.now().utcnow())
        name = request.form['loglevel'].lower()
        loglevel = _convert_log_name_to_id(name)
        if loglevel is None:
            return json.dumps({'success': False, 'error': 'Bad log level'}, sort_keys=True), 400

        db.execute(
            'insert into messages (clientid, loglevel, message, creation_datetime) values (:clientid, :loglevel, :message, :now);',
            (request.form['clientid'], loglevel, request.form['message'], now)
        )
        db.commit()
        return json.dumps({'success': True}), 200


@app.route('/messages', methods=['DELETE'])
def messages_delete_all():
    init_db()
    return json.dumps({'success': True}), 200


def _convert_log_name_to_id(name):
    db = get_db()
    cur = db.execute(
        'select id from loglevels where name = :name;',
        (name,)
    )
    entries = cur.fetchall()
    return None if len(entries) == 0 else entries[0][0]


if __name__ == "__main__":
    app.run(host='0.0.0.0')