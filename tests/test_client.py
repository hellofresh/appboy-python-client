from requests import RequestException


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


class TestBrazeClient(object):

    def test_init(self, braze_client):
        assert braze_client.api_key == 'API_KEY'
        assert braze_client.requests is not None
        assert braze_client.request_url == ''
        assert braze_client.headers == {}

    def test_user_track(self, braze_client):
        braze_client.requests = DummyRequest()
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
        assert braze_client.headers['Content-Type'] == 'application/json'
        assert response['status_code'] == 200
        assert response['errors'] == ''
        assert response['client_error'] == ''
        assert response['message'] == 'success'

    def test_user_track_request_exception(self, braze_client):
        braze_client.requests = DummyRequestException()
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
        assert braze_client.headers['Content-Type'] == 'application/json'

        assert response['status_code'] == 0
        assert response['errors'] == ''
        assert response['client_error'] == 'Something went wrong'
