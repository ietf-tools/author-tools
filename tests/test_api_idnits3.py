from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase
from urllib.parse import urlencode

import responses

from at import create_app

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_UNSUPPORTED_FORMAT = 'draft-smoke-signals-00.odt'
TEST_XML_ERROR = 'draft-smoke-signals-00.error.xml'
TEST_TEXT_ERROR = 'draft-smoke-signals-00.error.txt'
TEST_KRAMDOWN_ERROR = 'draft-smoke-signals-00.error.md'
TEMPORARY_DATA_DIR = './tests/tmp/'
ALLOWED_DOMAINS = ['ietf.org', 'datatracker.ietf.org']


def get_path(filename):
    '''Returns file path'''
    return ''.join([TEST_DATA_DIR, filename])


class TestApiidnits3(TestCase):
    '''Tests for /api/idnits3 end point'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
                'UPLOAD_DIR': abspath(TEMPORARY_DATA_DIR),
                'REQUIRE_AUTH': False,
                'ALLOWED_DOMAINS': ALLOWED_DOMAINS}

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_no_url(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get('/api/idnits3')
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'URL is missing')

    def test_invalid_url(self):
        url = 'https://www.example.org/draft-example.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits3?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'],
                                 'www.example.org domain is not allowed.')

    def test_download_error(self):
        url = 'https://www.ietf.org/archives/id/draft-404.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits3?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'],
                                 'Error occured while downloading file.')

    def test_idnits3(self):
        url = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.txt'
        id = 'draft-iab-xml2rfcv2-02'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits3?' + urlencode({'url': url}))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(id, data)
                self.assertIn('idnits', data)
                self.assertIn('Comment', data)
                # TODO: Add test for year

    def test_idnits3_options(self):
        url = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.txt'
        id = 'draft-iab-xml2rfcv2-02'
        params = {
                'url': url,
                'year': 2015}

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits3?' + urlencode(params))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(id, data)
                self.assertIn('idnits', data)
                self.assertIn('Comment', data)
                # TODO: Add test for year

    def test_idnits3_submission_check(self):
        url = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.txt'
        id = 'draft-iab-xml2rfcv2-02'
        params = {'url': url, 'submitcheck': True}

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits3?' + urlencode(params))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(id, data)
                self.assertIn('idnits', data)
                self.assertNotIn('warnings', data)
                # submission check
                self.assertIn('Document is VALID.', data)

    def test_no_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post('/api/idnits3')
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'No file')

    def test_missing_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/idnits3',
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                '')})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'Filename is missing')

    def test_unsupported_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/idnits3',
                        data={
                            'file': (
                                open(get_path(TEST_UNSUPPORTED_FORMAT), 'rb'),
                                TEST_UNSUPPORTED_FORMAT)})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'],
                        'Input file format not supported')

    def test_kramdown_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/idnits3',
                        data={
                            'file': (
                                open(get_path(TEST_KRAMDOWN_ERROR), 'rb'),
                                TEST_KRAMDOWN_ERROR)})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertIsNotNone(json_data['error'])

    @responses.activate
    def test_kramdown_error_url(self):
        url = 'https://ietf.org/error.md'
        responses.add(
                responses.GET,
                url,
                body='{::boilerplate foobar}',
                status=200)
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits3?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertIsNotNone(json_data['error'])

    def test_xml_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/idnits3?submission=True',
                        data={
                            'file': (
                                open(get_path(TEST_XML_ERROR), 'rb'),
                                TEST_XML_ERROR)})
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(TEST_XML_ERROR, data)
                self.assertIn('idnits', data)
                self.assertNotIn('Document is VALID.', data)

    def test_text_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/idnits3?submission=True',
                        data={
                            'file': (
                                open(get_path(TEST_TEXT_ERROR), 'rb'),
                                TEST_TEXT_ERROR)})
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(TEST_TEXT_ERROR, data)
                self.assertIn('idnits', data)
                self.assertNotIn('Document is VALID.', data)
