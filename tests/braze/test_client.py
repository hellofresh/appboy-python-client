import pytest

from braze.client import BrazeClient
from braze.client import BrazeInternalServerError
from requests import RequestException
from requests_mock import ANY


class TestBrazeClient(object):

    def test_init(self, braze_client):
        assert braze_client.api_key == 'API_KEY'
        assert braze_client.request_url == ''

    def test_user_track(self, braze_client, requests_mock):
        headers = {
            'Content-Type': 'application/json',
        }
        mock_json = {'message': 'success', 'errors': ''}
        requests_mock.post(ANY, json=mock_json, status_code=200, headers=headers)
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

        response = braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )
        assert braze_client.api_url + '/users/track' == braze_client.request_url
        assert response['status_code'] == 200
        assert response['errors'] == ''
        assert response['message'] == 'success'

    def test_user_track_request_exception(self, braze_client, mocker):
        mocker.patch.object(
            BrazeClient,
            '_post_request_with_retries',
            side_effect=RequestException('RequestException Error Message'),
        )
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

        response = braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )
        assert braze_client.api_url + '/users/track' == braze_client.request_url
        assert response['status_code'] == 0
        assert response['errors'] == 'RequestException Error Message'

    def test__post_request_with_retries(self, braze_client, mocker):
        spy = mocker.patch.object(
            BrazeClient,
            '_post_request_with_retries',
            side_effect=BrazeInternalServerError('Error 500'),
        )
        with pytest.raises(BrazeInternalServerError):
            braze_client._post_request_with_retries()

        # TODO
