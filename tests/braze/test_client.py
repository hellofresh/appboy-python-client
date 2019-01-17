import time

from braze.client import _wait_random_exp_or_rate_limit
from braze.client import BrazeClient
from braze.client import BrazeClientError
from braze.client import BrazeInternalServerError
from braze.client import BrazeRateLimitError
from braze.client import MAX_RETRIES
from braze.client import MAX_WAIT_SECONDS
from freezegun import freeze_time
import pytest
from pytest import approx
from requests import RequestException
from requests_mock import ANY
from tenacity import Future
from tenacity import RetryCallState


@pytest.fixture
def attributes():
    return {
        "external_id": "123",
        "first_name": "Firstname",
        "email": "mail@example.com",
        "some_key": "some_value",
    }


@pytest.fixture()
def events():
    return {"external_id": "123", "name": "some_name"}


@pytest.fixture()
def purchases():
    return {"external_id": "123", "name": "some_name"}


class TestWaitRandomExpOrRateLimit(object):
    @pytest.fixture
    def retry_state(self):
        retry_state = RetryCallState(object(), lambda x: x, (), {})
        retry_state.outcome = Future(attempt_number=1)
        return retry_state

    @freeze_time()
    def test_raises_if_too_long(self, retry_state):
        callback = _wait_random_exp_or_rate_limit()
        exc = BrazeRateLimitError(time.time() + MAX_WAIT_SECONDS + 1)
        retry_state.outcome.set_exception(exc)

        with pytest.raises(BrazeRateLimitError) as e:
            callback(retry_state)

        assert e.value.reset_epoch_s == exc.reset_epoch_s

    @freeze_time()
    def test_doesnt_allow_negative_waits(self, retry_state):
        callback = _wait_random_exp_or_rate_limit()
        exc = BrazeRateLimitError(time.time() - 1)
        retry_state.outcome.set_exception(exc)

        assert callback(retry_state) == 0.0

    def test_uses_random_exp_for_other_exceptions(self, retry_state):
        callback = _wait_random_exp_or_rate_limit()
        retry_state.outcome.set_exception(Exception())

        for attempt in range(10):
            retry_state.attempt_number = attempt
            for _ in range(100):
                assert 0 <= callback(retry_state) <= 1.5


class TestBrazeClient(object):
    def test_init(self, braze_client):
        assert braze_client.api_key == "API_KEY"
        assert braze_client.request_url == ""

    def test_user_track(
        self, braze_client, requests_mock, attributes, events, purchases
    ):
        headers = {"Content-Type": "application/json"}
        mock_json = {"message": "success", "errors": ""}
        requests_mock.post(ANY, json=mock_json, status_code=200, headers=headers)

        response = braze_client.user_track(
            attributes=attributes, events=events, purchases=purchases
        )
        assert braze_client.api_url + "/users/track" == braze_client.request_url
        assert response["status_code"] == 200
        assert response["errors"] == ""
        assert response["message"] == "success"

    def test_user_track_request_exception(
        self, braze_client, mocker, attributes, events, purchases
    ):
        mocker.patch.object(
            BrazeClient, "_post_request_with_retries", side_effect=RequestException
        )

        with pytest.raises(RequestException):
            braze_client.user_track(
                attributes=attributes, events=events, purchases=purchases
            )

        assert braze_client.api_url + "/users/track" == braze_client.request_url

    @pytest.mark.parametrize(
        "status_code, retry_attempts, error",
        [(500, MAX_RETRIES, BrazeInternalServerError), (401, 1, BrazeClientError)],
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
        error,
    ):
        headers = {"Content-Type": "application/json"}
        error_msg = "Internal Server Error"
        mock_json = {"message": error_msg, "errors": error_msg}
        requests_mock.post(
            ANY, json=mock_json, status_code=status_code, headers=headers
        )

        with pytest.raises(error):
            braze_client.user_track(
                attributes=attributes, events=events, purchases=purchases
            )

        stats = braze_client._post_request_with_retries.retry.statistics
        assert stats["attempt_number"] == retry_attempts

    @freeze_time()
    @pytest.mark.parametrize(
        "reset_delta_seconds, expected_attempts",
        [(0.05, MAX_RETRIES), (MAX_WAIT_SECONDS + 1, 1)],
    )
    def test_retries_for_rate_limit_errors(
        self,
        braze_client,
        requests_mock,
        attributes,
        events,
        purchases,
        reset_delta_seconds,
        expected_attempts,
        no_sleep,
    ):
        headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Reset": str(time.time() + reset_delta_seconds),
        }
        error_msg = "Rate Limit Error"
        mock_json = {"message": error_msg, "errors": error_msg}
        requests_mock.post(ANY, json=mock_json, status_code=429, headers=headers)

        with pytest.raises(BrazeRateLimitError):
            braze_client.user_track(
                attributes=attributes, events=events, purchases=purchases
            )

        stats = braze_client._post_request_with_retries.retry.statistics
        assert stats["attempt_number"] == expected_attempts

        # Ensure the correct wait time is used when rate limited
        for i in range(expected_attempts - 1):
            assert approx(no_sleep.call_args_list[i][0], reset_delta_seconds)
