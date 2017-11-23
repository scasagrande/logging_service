# -*- coding: utf-8 -*-

import os
import tempfile
import json
import pytest
from hypothesis import given
import hypothesis.strategies as st

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
    """Start with a blank database."""
    rv = client.get('/messages')
    assert b'[]' in rv.data


@given(st.text(min_size=1))
def test_store_retrieve(client, msg):
    rv = client.post('/messages', data=dict({
        'clientid': 100,
        'loglevel': 'info',
        'message': msg
    }))

    assert b'{"success": true}' in rv.data

    rv = client.get('/messages')
    expected = json.dumps({"clientid": 100, "loglevel": 'info', "message": msg}).encode()

    assert expected in rv.data
