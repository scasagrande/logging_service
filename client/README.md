logserv Python Client
=====================

This folder contains an example Python client for interacting with `logserv`. The file is dual purpose; you can either run the file directly from the command line, or you can import the module into your own code.

From the command line
---------------------

With Python 3 installed, first install the dependencies:

```bash
$ pip install -r requirements.txt
```

Then run the script from the command line:

```bash
$ python client.py -h
```

You can get the log messages with a minimum log level:

```bash
$ python client.py --get --loglevel warning --host http://localhost --port 5000
```

Create a new log message:

```bash
$ python client.py --clientid 100 --loglevel info --message hello world -H http://localhost -p 5000
```

Or delete all stored log messages:

```bash
$ python client.py --delete -H http://localhost -p 5000
```

As a module
-----------

Simply import the class into your custom code:

```python
from .client import LogClient
```

Then use it as such

```python
client = LogClient(hostname='http://localhost', port=5000)
_ = client.delete()
_ = client.store_log(
    clientid=100,
    loglevel='info',
    msg='hello world'
)
logs = client.get(min_level='warning')
```
