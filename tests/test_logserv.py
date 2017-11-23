# -*- coding: utf-8 -*-

import os
import tempfile
import pytest

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
    assert b'hello world' in rv.data
