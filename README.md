<p align="center">
  <a href="https://hellofresh.com">
    <img width="120" src="https://www.hellofresh.de/images/hellofresh/press/HelloFresh_Logo.png">
  </a>
</p>

# appboy-python-client
A Python client for the Appboy REST API

[ ![Codeship build](https://codeship.com/projects/d92ace70-056d-0134-ffb9-566313bcba78/status?branch=master)](https://codeship.com/projects/154416)
### Owner
[Alexander Zhilyaev](mailto:azh@hellofresh.com)

### How to install

Make sure you have Python 2.7.11+ installed and run:

```
$ git clone git@github.com:hellofresh/appboy-python-client.git
$ cd appboy-python-client
$ python setup.py install
```

### How to use

```python
from appboy.client import AppboyClient

client = AppboyClient(app_group_id='YOUR_GROUP_ID')

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
    print 'Success!'
    print r
else:
    print r['client_error']
    print r['errors']

```
For more examples, check `examples.py`.

### How to test

To run the unit tests, make sure you have the [nose](http://nose.readthedocs.org/) module instaled and run the following from the repository root directory:

`$ nosetests`
