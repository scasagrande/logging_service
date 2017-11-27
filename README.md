Logging Server
==============

[![Travis-CI build status](https://img.shields.io/travis/scasagrande/logging_service/master.svg?maxAge=2592000)](https://travis-ci.org/scasagrande/logging_service)

`logserv` is a basic Flask-based logging server

How to run
----------

This project by default uses `sqlite3` to store the log messages. Follow the directions for your operating system and ensure this is installed before continuing.

Python 3 is also required. This may or may not work on Python 2.7, but was not tested. It is suggested that you setup a virtual Python environment to keep your dependencies separated. I personally use `pyenv` to manage this.

After cloning this repo, navigate your terminal into the root folder of this project

- With Python 3, install the requirements

```bash
$ pip install -r requirements.txt
```

- Install `logserv` (the `--editable` flag will allow you to make changes to your code without having to reinstall)

```bash
$ pip install --editable .
```

- Instruct Flask to use the right application

```bash
$ export FLASK_APP=logserv
```

- Run the app

```bash
$ flask run
```

Server is now running on `localhost:5000` by default. To reset the DB, or apply a new schema, run:

```bash
$ flask initdb
```

How to run with Docker
----------------------

A `Dockerfile` is included if you prefer to use that. To run with docker, first ensure that the Docker daemon is up and running on your system, and that your user account has the correct permissions.

```bash
$ docker build -t logserv .
$ docker run --rm -it -p 5000:5000 logserv
```

This will build the `logserv` docker image, and then run it with port forwarding on localhost 5000. You can access this server in the same way as running the server without docker.

To terminate the server process, simply press `CTRL+c` in the terminal window you started it from.


How to use
----------

Using this server is easy. To read, add, or delete log messages you simply perform a GET, POST, or DELETE HTTP request, with the appropriate data, to the server.

### Reading log entries

Read all stored log entries

`GET /messages`

This returns, as JSON, a list of objects of the following form:

```json
{
  "clientid": 100,
  "loglevel": "info",
  "message": "hello world",
  "creation_datetime": "2017-11-25 03:54:13.054366"
}
```

Where `creation_datetime` is of UTC timezone.

Optional filters for log level

`GET /messages?min_level=VAR`

At time of writing there are 3 logging levels: `info`, `warning`, and `error`. This parameter is case-insensitive. Returned JSON will include stored log messages with the specified minimum level and higher.

### Create new log message

`POST /messages`

Request body:

```
clientid: INT non-null
loglevel: STRING non-null
message: STRING non-null
```

On success this route will return with:

```
{"success": True}
```

If a bad logging level is specified a 400 is returned with this JSON:

```
{"success": False, "error": "Bad log level"}
```

### Clear stored log messages

`DELETE /messages`

This will re-initalize the database, deleting all stored log messages.

Running Tests
-------------

This project uses `pytest` to run the automated tests.

First install the development dependencies:

```bash
$ pip install -r dev-requirements.txt
```

Then with your current working director at the project root, execute `pytest`:

```bash
$ pytest tests/test_logserv.py
```

If you would like to run all the tests (ie, include the client tests) you need to install the dependencies for the client

```bash
$ pip install -r client/requirements.txt
```

Then you can run them all

```bash
$ pytest tests/
```

The majority of the tests for this project are currently integration tests, and thus will require that a sqlite database is able to be created and used.

Several of the tests also make use of the Python fuzz testing library `hypothesis` in order to attempt to cover as many input possibilities as reasonable. However due to all the different input combinations it tries to run through, each test function that uses `hypothesis.given` will take a few seconds.

Client Examples
---------------

Since the server is just a basic CRUD webserver, anything that can make HTTP web requests can interact with it.

### Provided Python client

Please see readme file located in the client directory `client/README.md`

### Curl

```bash
$ curl --data "clientid=100&loglevel=warning&message=hello world" http://localhost:5000/messages
```

```bash
$ curl http://localhost:5000/messages?min_level=warning
```

```bash
$ curl -X DELETE http://localhost:5000/messages
```

Discussion
----------

This approach was taken for simplicity, ease of testing, concurrent request handling, and broad client support.

Alternate approaches could be taken if there was a specific client requirement. For example if existing Python code was logging using the builtin `logging` library, then one could make a http server that handles these requests. Then you would only need to change the client software to direct their output to this server instead of to file. Concurrency support on this server could be done via Twisted or Asyncio.

`logserv` has several shortcomings which I would want to see addressed before being used in production, but are beyond the scope of this challenge.

- Database migrations need to be a thing. You should be able to update this software, and thus the schema, without having to do manual migrations and/or wiping the DB. I know that Django supports this by default, and I'm sure there is a Flask plugin to do this.
- Config file support. This would allow the database to be managed by something more powerful than `sqlite3`, as well as not running the server always in debug mode.
- Authentication is an obvious one. Basic auth is actually really easy to strap onto Flask apps so this would be relatively easy to add, although would require some work to make sure everything is actually secure.
- Super duper vulnerable to SQL injection. Inputs should be sanitized.
- Each request is a blocking action, and thus concurrent requests are blocked and processed serially. Since each request here is pretty light weight, I decided that this was acceptable for now. If there was additional processing logic that took a non-trivial amount of time, I would want to see this addressed. One way to handle this would be to use Django Channels with a few worker processes behind `gunicorn` to handle the requests.
- Additional filtering on log retrieval could be easily added with how the server has been setup.
