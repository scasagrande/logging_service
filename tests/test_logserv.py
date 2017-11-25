# -*- coding: utf-8 -*-

import os
import tempfile
import json
import pytest
from hypothesis import given
import hypothesis.strategies as st
from datetime import datetime

from logserv import logserv


@pytest.fixture
def client(request):
    db_fd, logserv.app.config['DATABASE'] = tempfile.mkstemp()
    logserv.app.config['TESTING'] = True
    client = logserv.app.test_client()
    with logserv.app.app_context():
        logserv.init_db()

    def teardown():
        os.close(db_fd)
        os.unlink(logserv.app.config['DATABASE'])
    request.addfinalizer(teardown)

    return client


def test_empty_db(client):
    """
    Starting with a new server, the messages GET route should return an empty
    list
    """
    rv = client.get('/messages')
    assert b'[]' in rv.data
    assert rv.status_code == 200


@given(st.text(min_size=1))
def test_store_retrieve(mocker, client, msg):
    """
    A log message stored via the POST route should be retrievable via the GET
    route.

    A wide variety of log messages are tested via Hypothesis to cover all
    common string cases
    """
    mocker.patch.object(logserv, 'datetime')
    logserv.datetime.now.return_value.utcnow.return_value = datetime(2017, 11, 25, 1, 2, 3)

    rv = client.post('/messages', data=dict({
        'clientid': 100,
        'loglevel': 'info',
        'message': msg
    }))

    assert b'{"success": true}' in rv.data
    assert rv.status_code == 200

    rv = client.get('/messages')
    expected = json.dumps({
        "clientid": 100,
        "loglevel": 'info',
        "message": msg,
        'creation_datetime': '2017-11-25 01:02:03'
    }).encode()

    assert expected in rv.data
    assert rv.status_code == 200


def test_store_delete_retrieve(client):
    """
    After storing a message in the log, the DELETE route is called,
    and then the GET route should return an empty list
    """
    rv = client.post('/messages', data=dict({
        'clientid': 100,
        'loglevel': 'info',
        'message': 'foobar'
    }))

    assert b'{"success": true}' in rv.data
    assert rv.status_code == 200

    rv = client.delete('/messages')

    assert b'{"success": true}' in rv.data
    assert rv.status_code == 200

    rv = client.get('/messages')
    assert b'[]' in rv.data
    assert rv.status_code == 200


def test_retrieve_min_level(mocker, client):

    # Mock datetime object
    mocker.patch.object(logserv, 'datetime')
    logserv.datetime.now.return_value.utcnow.return_value = datetime( 2017, 11, 25, 1, 2, 3)

    # Create test data
    messages = [
        {
            "clientid": 100,
            "loglevel": "info",
            "message": "business as usual"
        },
        {
            "clientid": 101,
            "loglevel": "warning",
            "message": "take a look when you have time"
        },
        {
            "clientid": 102,
            "loglevel": "error",
            "message": "danger danger!!"
        }
    ]

    # Post the messages to the server
    for msg in messages:
        _ = client.post('/messages', data=msg)

    # Modify our local data to include the mocked datetime creation
    for msg in messages:
        msg['creation_datetime'] = str(datetime(2017, 11, 25, 1, 2, 3))

    # Get the log messages back from the server
    rv = client.get('/messages')
    for msg in messages:
        assert json.dumps(msg).encode() in rv.data

    for idx, level in enumerate(('info', 'warning', 'error')):
        # Check that filtering by both the log level name, or the associated
        # log level ID works
        rv_name = client.get('/messages?min_level={}'.format(level))
        rv_num = client.get('/messages?min_level={}'.format(level))
        if idx == 0:
            for msg in messages:
                assert json.dumps(msg).encode() in rv_name.data
                assert json.dumps(msg).encode() in rv_num.data
            continue
        for msg in messages[:idx-1]:
            assert json.dumps(msg).encode() not in rv_name.data
            assert json.dumps(msg).encode() not in rv_num.data
        for msg in messages[idx:]:
            assert json.dumps(msg).encode() in rv_name.data
            assert json.dumps(msg).encode() in rv_num.data


def test_bad_loglevel_post(client):
    rv = client.post('/messages', data=dict({
        'clientid': 100,
        'loglevel': 'onfire',
        'message': 'foobar'
    }))

    assert b'{"success": false, "error": "Bad log level"}' in rv.data
    assert rv.status_code == 400


def test_bad_loglevel_get(client):
    rv = client.get('/messages?min_level=foobar')

    assert b'{"success": false, "error": "Bad log level"}' in rv.data
    assert rv.status_code == 400
