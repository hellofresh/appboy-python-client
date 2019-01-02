from braze.client import BrazeClient

client = BrazeClient(api_key='YOUR_GROUP_ID')

# For create - update users
r = client.user_track(
    attributes=[{
        'external_id': '1',
        'first_name': 'First name',
        'last_name': 'Last name',
        'email': 'email@example.com',
        'status': 'Active',
        # And other fields ...
    }],
    events=None,  # if we don't want to send events we set it to None
    purchases=None,
)
if r['success']:
    # do our magic here
    print('Success!')
    print(r)
else:
    print(r['client_error'])
    print(r['errors'])

# For delete users by external_id or appboy_id
r = client.user_delete(
    external_ids=['1'],
    appboy_ids=None,
)
if r['success']:
    # do our magic here
    print('Success!')
    print(r)
else:
    print(r['client_error'])
    print(r['errors'])
