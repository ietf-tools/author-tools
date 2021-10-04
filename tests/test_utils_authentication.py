from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from hypothesis import given
from hypothesis.strategies import text
import responses

from at import create_app

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEMPORARY_DATA_DIR = './tests/tmp/'
AUTHOR_TOOLS_API_TEST_VERSION = '0.0.1'
DT_APPAUTH_URL = 'https://example.com/'
VALID_API_KEY = 'foobar'


def get_path(filename):
    '''Returns file path'''
    return ''.join([TEST_DATA_DIR, filename])


class TestUtilsAuthentication(TestCase):
    '''Tests for at.utils.authentication'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
                'UPLOAD_DIR': abspath(TEMPORARY_DATA_DIR),
                'DT_APPAUTH_URL': DT_APPAUTH_URL,
                'VERSION': AUTHOR_TOOLS_API_TEST_VERSION}

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    @responses.activate
    def test_authentication_missing_api_key(self):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                status=400)

        with self.app.test_client() as client:
            with self.app.app_context():
                filename = get_path(TEST_XML_DRAFT)
                result = client.post(
                            '/api/render/xml',
                            data={'file': (open(filename, 'rb'), filename)})
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
                filename = get_path(TEST_XML_DRAFT)
                result = client.post(
                            '/api/render/xml',
                            data={
                                'file': (open(filename, 'rb'), filename),
                                'apikey': VALID_API_KEY})

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
                filename = get_path(TEST_XML_DRAFT)
                result = client.post(
                            '/api/render/xml',
                            data={
                                'file': (open(filename, 'rb'), filename),
                                'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is invalid')

    @responses.activate
    def test_authentication_valid_api_key_in_headers(self):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                json={'success': True},
                status=200)

        with self.app.test_client() as client:
            with self.app.app_context():
                filename = get_path(TEST_XML_DRAFT)
                result = client.post(
                            '/api/render/xml',
                            headers={'X-API-KEY': VALID_API_KEY},
                            data={'file': (open(filename, 'rb'), filename)})

                self.assertEqual(result.status_code, 200)

    @responses.activate
    @given(text())
    def test_authentication_invalid_api_key_in_headers(self, api_key):
        responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                status=403)

        with self.app.test_client() as client:
            with self.app.app_context():
                filename = get_path(TEST_XML_DRAFT)
                result = client.post(
                            '/api/render/xml',
                            headers={'X-API-KEY': VALID_API_KEY},
                            data={'file': (open(filename, 'rb'), filename)})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is invalid')
