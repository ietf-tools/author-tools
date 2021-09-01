from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from hypothesis import given, assume
from hypothesis.strategies import text

from at import create_app

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_XML_V2_DRAFT = 'draft-smoke-signals-00.v2.xml'
TEST_TEXT_DRAFT = 'draft-smoke-signals-00.txt'
TEST_KRAMDOWN_DRAFT = 'draft-smoke-signals-00.md'
TEST_UNSUPPORTED_FORMAT = 'draft-smoke-signals-00.odt'
TEST_XML_ERROR = 'draft-smoke-signals-00.error.xml'
TEST_TEXT_ERROR = 'draft-smoke-signals-00.error.txt'
TEST_KRAMDOWN_ERROR = 'draft-smoke-signals-00.error.md'
TEST_DATA = [
        TEST_XML_DRAFT, TEST_XML_V2_DRAFT, TEST_TEXT_DRAFT,
        TEST_KRAMDOWN_DRAFT]
TEMPORARY_DATA_DIR = './tests/tmp/'
VALID_API_KEY = 'foobar'


def get_path(filename):
    '''Returns file path'''
    return ''.join([TEST_DATA_DIR, filename])


class TestApiRender(TestCase):
    '''Tests for /api/render end point'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
                'UPLOAD_DIR': abspath('./tests/tmp'),
                'API_KEYS': [VALID_API_KEY, ]}

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_no_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'No file')

    def test_missing_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                ''),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'Filename is missing')

    def test_unsupported_render_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/flac',
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                TEST_XML_DRAFT),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'], 'Render format not supported')

    def test_unsupported_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={
                            'file': (
                                open(get_path(TEST_UNSUPPORTED_FORMAT), 'rb'),
                                TEST_UNSUPPORTED_FORMAT),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'],
                        'Input file format not supported')

    def test_render_xml(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                for filename in TEST_DATA:
                    result = client.post(
                            '/api/render/xml',
                            data={
                                'file': (
                                    open(get_path(filename), 'rb'), filename),
                                'apikey': VALID_API_KEY})

                    self.assertEqual(result.status_code, 200)
                    self.assertIsNotNone(result.data)

    def test_render_text(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                for filename in TEST_DATA:
                    result = client.post(
                            '/api/render/text',
                            data={
                                'file': (
                                    open(get_path(filename), 'rb'), filename),
                                'apikey': VALID_API_KEY})

                    self.assertEqual(result.status_code, 200)
                    self.assertIsNotNone(result.data)

    def test_render_html(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                for filename in TEST_DATA:
                    result = client.post(
                            '/api/render/html',
                            data={
                                'file': (
                                    open(get_path(filename), 'rb'), filename),
                                'apikey': VALID_API_KEY})

                    self.assertEqual(result.status_code, 200)
                    self.assertIsNotNone(result.data)

    def test_render_pdf(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                for filename in TEST_DATA:
                    result = client.post(
                            '/api/render/pdf',
                            data={
                                'file': (
                                    open(get_path(filename), 'rb'), filename),
                                'apikey': VALID_API_KEY})

                    self.assertEqual(result.status_code, 200)
                    self.assertIsNotNone(result.data)

    def test_kramdown_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={
                            'file': (
                                open(get_path(TEST_KRAMDOWN_ERROR), 'rb'),
                                TEST_KRAMDOWN_ERROR),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertTrue(json_data['error'].startswith(
                    'kramdown-rfc2629 error:'))

    def test_text_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={
                            'file': (
                                open(get_path(TEST_TEXT_ERROR), 'rb'),
                                TEST_TEXT_ERROR),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertTrue(json_data['error'].startswith(
                    'id2xml error:'))

    def test_xml_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={
                            'file': (
                                open(get_path(TEST_XML_ERROR), 'rb'),
                                TEST_XML_ERROR),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertTrue(json_data['error'].startswith(
                    'xml2rfc error:'))

    def test_authentication_missing_api_key(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post('/api/render/xml')
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is missing')

    def test_authentication_valid_api_key(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                TEST_XML_DRAFT),
                            'apikey': VALID_API_KEY})

                self.assertEqual(result.status_code, 200)

    @given(text())
    def test_authentication_invalid_api_key(self, api_key):
        assume(api_key != VALID_API_KEY)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml',
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                TEST_XML_DRAFT),
                            'apikey': api_key})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is invalid')

    def test_authentication_valid_api_key_as_query_param(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml?apikey={}'.format(VALID_API_KEY),
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                TEST_XML_DRAFT)})

                self.assertEqual(result.status_code, 200)

    @given(text())
    def test_authentication_invalid_api_key_as_query_param(self, api_key):
        assume(api_key != VALID_API_KEY)

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/render/xml?apikey={}'.format(api_key),
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                TEST_XML_DRAFT)})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 401)
                self.assertEqual(json_data['error'], 'API key is invalid')
