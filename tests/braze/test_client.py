import pytest

from braze.client import BrazeClient
from requests import RequestException
from requests_mock import ANY


@pytest.fixture
def attributes():
    return {
        'external_id': '123',
        'first_name': 'Firstname',
        'email': 'mail@example.com',
        'some_key': 'some_value'
    }


@pytest.fixture()
def events():
    return {
        'external_id': '123',
        'name': 'some_name',
    }


@pytest.fixture()
def purchases():
    return {
        'external_id': '123',
        'name': 'some_name',
    }


class TestBrazeClient(object):

    def test_init(self, braze_client):
        assert braze_client.api_key == 'API_KEY'
        assert braze_client.request_url == ''

    def test_user_track(
            self,
            braze_client,
            requests_mock,
            attributes,
            events,
            purchases,
    ):
        headers = {
            'Content-Type': 'application/json',
        }
        mock_json = {'message': 'success', 'errors': ''}
        requests_mock.post(ANY, json=mock_json, status_code=200, headers=headers)

        response = braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )
        assert braze_client.api_url + '/users/track' == braze_client.request_url
        assert response['status_code'] == 200
        assert response['errors'] == ''
        assert response['message'] == 'success'

    def test_user_track_request_exception(
        self,
        braze_client,
        mocker,
        attributes,
        events,
        purchases,
    ):
        mocker.patch.object(
            BrazeClient,
            '_post_request_with_retries',
            side_effect=RequestException('RequestException Error Message'),
        )

        response = braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )
        assert braze_client.api_url + '/users/track' == braze_client.request_url
        assert response['status_code'] == 0
        assert response['errors'] == 'RequestException Error Message'

    @pytest.mark.parametrize(
        'status_code, attempts', [
            (429, BrazeClient.MAX_RETRIES),
            (500, BrazeClient.MAX_RETRIES),
            (401, 1),
        ],
    )
    def test_retries_for_errors(
        self,
        braze_client,
        requests_mock,
        status_code,
        attempts,
        attributes,
        events,
        purchases,
    ):
        headers = {
            'Content-Type': 'application/json',
        }
        mock_json = {'errors': 'Internal Server Error'}
        requests_mock.post(ANY, json=mock_json, status_code=500, headers=headers)

        braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )

        stats = braze_client._post_request_with_retries.retry.statistics
        assert stats['attempt_number'] == 3
