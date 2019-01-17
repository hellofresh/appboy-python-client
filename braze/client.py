import time

import requests
from requests.exceptions import RequestException
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_random_exponential

# Max time to wait between API call retries
MAX_WAIT_SECONDS = 1.25


class BrazeRateLimitError(Exception):
    def __init__(self, reset_epoch_s):
        """
        A rate limit error was encountered.

        :param float reset_epoch_s: Unix timestamp for when the API may be called again.
        """
        self.reset_epoch_s = reset_epoch_s
        super(BrazeRateLimitError, self).__init__("BrazeRateLimitError")


class BrazeInternalServerError(Exception):
    pass


def _wait_random_exp_or_rate_limit():
    """Creates a tenacity wait callback that accounts for explicit rate limits."""
    random_exp = wait_random_exponential(multiplier=1, max=MAX_WAIT_SECONDS)

    def check(retry_state):
        """
        Waits with either a random exponential backoff or attempts to obey rate limits
        that Braze returns.

        :param tenacity.RetryCallState retry_state: Info about current retry invocation
        :raises BrazeRateLimitError: If the rate limit reset time is too long
        :returns: Time to wait, in seconds.
        :rtype: float
        """
        exc = retry_state.outcome.exception()
        if isinstance(exc, BrazeRateLimitError):
            sec_to_reset = exc.reset_epoch_s - float(time.time())
            if sec_to_reset >= MAX_WAIT_SECONDS:
                raise exc
            return max(0.0, sec_to_reset)
        return random_exp(retry_state=retry_state)

    return check


class BrazeClient(object):
    """
    Client for Appboy public API. Support user_track.
    usage:
     from braze.client import BrazeClient
     client = BrazeClient(api_key='Place your API key here')
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

    DEFAULT_API_URL = "https://rest.iad-02.braze.com"
    USER_TRACK_ENDPOINT = "/users/track"
    USER_DELETE_ENDPOINT = "/users/delete"
    MAX_RETRIES = 3

    def __init__(self, api_key, api_url=None):
        self.api_key = api_key
        self.api_url = api_url or self.DEFAULT_API_URL
        self.request_url = ""

    def user_track(self, attributes, events, purchases):
        """
        Record custom events, user attributes, and purchases for users.
        :param attributes: dict or list of user attributes dict (external_id, first_name, email)
        :param events: dict or list of user events dict (external_id, app_id, name, time, properties)
        :param purchases: dict or list of user purchases dict (external_id, app_id, product_id, currency, price)
        :return: json dict response, for example: {"message": "success", "errors": [], "client_error": ""}
        """
        self.request_url = self.api_url + self.USER_TRACK_ENDPOINT

        payload = {}

        if events:
            payload["events"] = events

        if attributes:
            payload["attributes"] = attributes

        if purchases:
            payload["purchases"] = purchases

        return self.__create_request(payload=payload)

    def user_delete(self, external_ids, appboy_ids):
        """
        Delete user from braze.
        :param external_ids: dict or list of user external ids
        :param appboy_ids: dict or list of user braze ids
        :return: json dict response, for example: {"message": "success", "errors": [], "client_error": ""}
        """
        self.request_url = self.api_url + self.USER_DELETE_ENDPOINT

        payload = {}

        if external_ids:
            payload["external_ids"] = external_ids

        if appboy_ids:
            payload["appboy_ids"] = appboy_ids

        return self.__create_request(payload=payload)

    def __create_request(self, payload):

        payload["api_key"] = self.api_key

        response = {"errors": []}
        try:
            r = self._post_request_with_retries(payload)
            response.update(r.json())
            response["status_code"] = r.status_code

            message = response["message"]
            if message == "success" or message == "queued":
                if not response["errors"]:
                    response["success"] = True
                else:
                    # Non-Fatal errors
                    pass

        except (RequestException, BrazeRateLimitError, BrazeInternalServerError) as e:
            response["errors"].append(str(e))

        if "success" not in response:
            response["success"] = False

        if "status_code" not in response:
            response["status_code"] = 0

        if "message" not in response:
            response["message"] = ""

        return response

    @retry(
        reraise=True,
        wait=_wait_random_exp_or_rate_limit(),
        stop=stop_after_attempt(MAX_RETRIES),
    )
    def _post_request_with_retries(self, payload):
        """
        :param dict payload:
        :rtype: requests.Response
        """
        r = requests.post(self.request_url, json=payload, timeout=2)
        # https://www.braze.com/docs/developer_guide/rest_api/messaging/#fatal-errors
        if r.status_code == 429:
            reset_epoch_s = float(r.headers.get("X-RateLimit-Reset", 0))
            raise BrazeRateLimitError(reset_epoch_s)
        elif str(r.status_code).startswith("5"):
            raise BrazeInternalServerError("BrazeInternalServerError")
        return r
