from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase

from hypothesis import given
from hypothesis.strategies import text
import responses

from at import create_app

AUTHOR_TOOLS_API_TEST_VERSION = '0.0.1'
DT_APPAUTH_URL = 'https://example.com/'


class TestUtilsAuthentication(TestCase):
    '''Tests for at.utils.authentication'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)

        config = {
                'DT_APPAUTH_URL': DT_APPAUTH_URL,
                'VERSION': AUTHOR_TOOLS_API_TEST_VERSION}

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)

    @responses.activate
    def test_authentication_missing_api_key(self):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                status=400)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get('/api/version')
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is missing')

    @responses.activate
    def test_authentication_valid_api_key(self):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                json={'success': True},
                status=200)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/version',
                        data={'apikey': 'valid_api_key'})

                self.assertEqual(result.status_code, 200)

    @responses.activate
    @given(text())
    def test_authentication_invalid_api_key(self, api_key):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                status=403)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/version',
                        data={'apikey': api_key})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is invalid')

    @responses.activate
    def test_authentication_valid_api_key_as_query_param(self):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                json={'success': True},
                status=200)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get('/api/version?apikey=valid_api_key')

                self.assertEqual(result.status_code, 200)

    @responses.activate
    @given(text())
    def test_authentication_invalid_api_key_as_query_param(self, api_key):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                status=403)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                        '/api/version?apikey={}'.format(api_key))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is invalid')
