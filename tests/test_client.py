# -*- coding: utf-8 -*-

from client import client  # This imports the actual client.py file for mocking
from client import LogClient


def test_client_init():
    c = LogClient(hostname='http://localhost', port=1234)

    assert c.hostname == 'http://localhost'
    assert c.port == 1234


def test_client_get(mocker):
    """
    Test that the client returns data from the requests call, and also makes the correct
    GET request via requests
    """
    mocker.patch.object(client, 'r')
    client.r.get.return_value.json.return_value = {'foobar': 'hello world'}

    c = LogClient(hostname='http://localhost', port=1234)

    assert c.get() == {'foobar': 'hello world'}
    client.r.get.assert_called_once_with('http://localhost:1234/messages')


def test_client_get_min_log_value(mocker):
    """
    Test that the client passes the minimum log value query parameter correctly onto the
    requests library
    """
    mocker.patch.object(client, 'r')

    c = LogClient(hostname='http://localhost', port=1234)
    _ = c.get(min_level='warning')

    client.r.get.assert_called_once_with('http://localhost:1234/messages?min_level=warning')


def test_client_post(mocker):
    mocker.patch.object(client, 'r')
    client.r.post.return_value.json.return_value = {'success': True}

    c = LogClient(hostname='http://localhost', port=1234)
    assert c.store_log(clientid=100, loglevel='info', msg='hello world') == {'success': True}
    client.r.post.assert_called_once_with(
        'http://localhost:1234/messages',
        data={
            'clientid': 100,
            'loglevel': 'info',
            'message': 'hello world'
        }
    )


def test_client_delete(mocker):
    mocker.patch.object(client, 'r')
    client.r.delete.return_value.json.return_value = {'success': True}

    c = LogClient(hostname='http://localhost', port=1234)
    assert c.delete() == {'success': True}
    client.r.delete.assert_called_once_with('http://localhost:1234/messages')
