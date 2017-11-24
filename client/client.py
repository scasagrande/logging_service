#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import requests as r


class LogClient():
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def store_log(self, clientid, loglevel, msg):
        data = {
            'clientid': clientid,
            'loglevel': loglevel,
            'message': msg
        }
        r.post('{}:{}/messages'.format(self.hostname, self.port), data=data)

    def delete(self):
        r.delete('{}:{}/messages'.format(self.hostname, self.port))

    def get(self, min_level=None):
        route = '{}:{}/messages'.format(self.hostname, self.port)
        if min_level is not None:
            route += '?min_level={}'.format(min_level)
        return r.get(route).json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=''
    )
    parser.add_argument('--clientid', '-c', dest='clientid', help='Client ID')
    parser.add_argument('--loglevel', '-l', dest='loglevel', help='Log level for message')
    parser.add_argument('--message', '-m', dest='message', help='Log message body')
    parser.add_argument('--host', '-H', dest='host', required=True, help='Hostname for logging server')
    parser.add_argument('--port', '-p', dest='port', required=True, help='Port number logging server is hosted on')
    parser.add_argument('--delete', '-d', dest='delete', action='store_const', const=True, default=False, help='')
    parser.add_argument('--get', '-g', dest='get', action='store_const', const=True, default=False, help='')

    args = parser.parse_args()
    client = LogClient(args.host, args.port)

    if args.delete is True:
        client.delete()
        exit()

    if args.get is True:
        print(client.get(min_level=args.loglevel))
        exit()

    client.store_log(args.clientid, args.loglevel, args.message)
