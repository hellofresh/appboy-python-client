import json
import requests

from requests.exceptions import RequestException


class AppboyClient(object):
    """
    Client for Appboy public API. Support user_track.
    usage:
     from appboy.client import AppboyClient
     client = AppboyClient(app_group_id='Place your app_group_id here')
     r = client.user_track(
            attributes=[{
                'external_id': '1',
                'first_name': 'First name',
                'last_name': 'Last name',
                'email': 'email@example.com',
                'status': 'Active',
            }],
            events=None,
            purchases=None,
     )
    if r['success']:
        print 'Success!'
        print r
    else:
        print r['client_error']
        print r['errors']
    """
    API_URL = 'https://api.appboy.com'

    USER_TRACK_ENDPOINT = '/users/track'

    REQUEST_POST = 'post'

    def __init__(self, app_group_id):
        self.app_group_id = app_group_id
        self.requests = requests
        self.request_url = ''
        self.headers = {}

    def user_track(self, attributes, events, purchases):
        """
        Record custom events, user attributes, and purchases for users.
        :param attributes: dict or list of user attributes dict (external_id, first_name, email)
        :param events: dict or list of user events dict (external_id, app_id, name, time, properties)
        :param purchases: dict or list of user purchases dict (external_id, app_id, product_id, currency, price)
        :return: json dict response, for example: {"message": "success", "errors": [], "client_error": ""}
        """
        self.request_url = self.API_URL + self.USER_TRACK_ENDPOINT

        payload = {}

        if events:
            payload['events'] = events

        if attributes:
            payload['attributes'] = attributes

        if purchases:
            payload['purchases'] = purchases

        return self.__create_request(payload=payload, request_type=self.REQUEST_POST)

    def __create_request(self, payload, request_type):
        self.headers = {
            'Content-Type': 'application/json',
        }

        payload['app_group_id'] = self.app_group_id

        response = {}

        try:
            if request_type == self.REQUEST_POST:
                r = self.requests.post(self.request_url, data=json.dumps(payload), headers=self.headers)
                response = r.json()
                response['status_code'] = r.status_code
                if response['message'] == 'success' and 'errors' not in response:
                    response['success'] = True

        except RequestException as e:
            # handle all requests HTTP exceptions
            response = {'client_error': e.message}
        except Exception as e:
            # handle all exceptions which can be on API side
            response = {'client_error': (e.message + '. Response: ' + r.text)}

        if 'success' not in response:
            response['success'] = False
        if 'errors' not in response:
            response['errors'] = ''
        if 'status_code' not in response:
            response['status_code'] = 0
        if 'message' not in response:
            response['message'] = ''
        if 'client_error' not in response:
            response['client_error'] = ''

        return response
