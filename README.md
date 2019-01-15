# braze-client
A Python client for the Braze REST API

[![Build Status](https://travis-ci.com/GoodRx/braze-client.svg?branch=master)](https://travis-ci.com/GoodRx/braze-client)
[![Coverage](https://codecov.io/gh/GoodRx/braze-client/branch/master/graph/badge.svg)](https://codecov.io/gh/GoodRx/braze-client)

### How to install

Make sure you have Python 2.7.11+ installed and run:

```
$ git clone git@github.com:hellofresh/appboy-python-client.git
$ cd appboy-python-client
$ python setup.py install
```

### How to use

```python
from braze.client import BrazeClient
client = BrazeClient(api_key='YOUR_API_KEY')

r = client.user_track(
    attributes=[{
        'external_id': '1',
        'first_name': 'First name',
        'last_name': 'Last name',
        'email': 'email@example.com',
        'status': 'Active',
        # And other fields ...
    }],
    events=None,
    purchases=None,
)
if r['success']:
    # do our magic here
    print('Success!')
    print(r)
else:
    print(r['client_error'])
    print(r['errors'])

```
For more examples, check `examples.py`.

### How to test

To run the unit tests, make sure you have the [tox](https://tox.readthedocs.io/en/latest/) module installed and run the following from the repository root directory:

`$ tox`
