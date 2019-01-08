import pytest

from braze.client import BrazeClient
from freezegun import freeze_time
from requests import RequestException
from requests_mock import ANY
import time


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
        error_msg = 'RequestException Error Message'
        mocker.patch.object(
            BrazeClient,
            '_post_request_with_retries',
            side_effect=RequestException(error_msg),
        )

        response = braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )
        assert braze_client.api_url + '/users/track' == braze_client.request_url
        assert response['status_code'] == 0
        assert error_msg in response['errors']

    @pytest.mark.parametrize(
        'status_code, retry_attempts', [
            (500, BrazeClient.MAX_RETRIES),
            (401, 1),
        ],
    )
    def test_retries_for_errors(
        self,
        braze_client,
        requests_mock,
        status_code,
        retry_attempts,
        attributes,
        events,
        purchases,
    ):
        headers = {
            'Content-Type': 'application/json',
        }
        error_msg = 'Internal Server Error'
        mock_json = {'message': error_msg, 'errors': error_msg}
        requests_mock.post(
            ANY,
            json=mock_json,
            status_code=status_code,
            headers=headers,
        )

        response = braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )

        stats = braze_client._post_request_with_retries.retry.statistics
        assert stats['attempt_number'] == retry_attempts
        assert response['success'] is False

    @freeze_time()
    @pytest.mark.parametrize('reset_delta_seconds, expected_attempts', [
        (0.05, 1 + BrazeClient.MAX_RETRIES),
        (BrazeClient.MAX_WAIT_SECONDS + 1, 1),
    ])
    def test_retries_for_rate_limit_errors(
        self,
        braze_client,
        mocker,
        requests_mock,
        attributes,
        events,
        purchases,
        reset_delta_seconds,
        expected_attempts,
    ):
        headers = {
            'Content-Type': 'application/json',
            'X-RateLimit-Reset': str(time.time() + reset_delta_seconds),
        }
        error_msg = 'Rate Limit Error'
        mock_json = {'message': error_msg, 'errors': error_msg}
        requests_mock.post(
            ANY,
            json=mock_json,
            status_code=429,
            headers=headers,
        )

        spy = mocker.spy(braze_client, "_post_request_with_retries")
        response = braze_client.user_track(
            attributes=attributes,
            events=events,
            purchases=purchases,
        )
        assert spy.call_count == expected_attempts
        assert response['success'] is False
        assert 'BrazeRateLimitError' in response['errors']
