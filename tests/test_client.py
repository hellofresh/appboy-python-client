import unittest

from requests import RequestException

from appboy.client import AppboyClient


class DummyRequest(object):
    def __init__(self):
        self.status_code = 200
        self.text = 'Some text'

    def post(self, request_url, data, headers):
        return self

    @staticmethod
    def json():
        return {'message': 'success', 'errors': ''}


class DummyRequestException(object):
    def __init__(self):
        self.status_code = 200

    def post(self, request_url, data, headers):
        raise RequestException('Something went wrong')

    @staticmethod
    def json():
        return {'message': 'success', 'errors': ''}


class TestAppboyClient(unittest.TestCase):
    def setUp(self):
        self.client = AppboyClient(app_group_id='APP_GROUP_ID')

    def test_init(self):
        self.assertEqual(self.client.app_group_id, 'APP_GROUP_ID')
        self.assertIsNotNone(self.client.requests)
        self.assertEqual(self.client.request_url, '')
        self.assertEqual(self.client.headers, {})

    def test_user_track(self):
        self.client.requests = DummyRequest()
        attributes = {
            'external_id': '123',
            'first_name': 'Firstname',
            'email': 'mail@example.com',
            'some_key': 'some_value'
        }
        events = {
            'external_id': '123',
            'name': 'some_name'
        }
        purchases = {
            'external_id': '123',
            'name': 'some_name'
        }

        response = self.client.user_track(attributes=attributes, events=events, purchases=purchases)

        self.assertEqual('https://api.appboy.com/users/track', self.client.request_url)
        self.assertEqual(self.client.headers['Content-Type'], 'application/json')

        self.assertEqual(response['status_code'], 200)
        self.assertEqual(response['errors'], '')
        self.assertEqual(response['client_error'], '')
        self.assertEqual(response['message'], 'success')

    def test_user_track_request_exception(self):
        self.client.requests = DummyRequestException()
        attributes = {
            'external_id': '123',
            'first_name': 'Firstname',
            'email': 'mail@example.com',
            'some_key': 'some_value'
        }
        events = {
            'external_id': '123',
            'name': 'some_name'
        }
        purchases = {
            'external_id': '123',
            'name': 'some_name'
        }

        response = self.client.user_track(attributes=attributes, events=events, purchases=purchases)

        self.assertEqual('https://api.appboy.com/users/track', self.client.request_url)
        self.assertEqual(self.client.headers['Content-Type'], 'application/json')

        self.assertEqual(response['status_code'], 0)
        self.assertEqual(response['errors'], '')
        self.assertEqual(response['client_error'], 'Something went wrong')
