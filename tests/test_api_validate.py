from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from at import create_app

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_XML_V2_DRAFT = 'draft-smoke-signals-00.v2.xml'
TEST_XML_INVALID = 'draft-smoke-signals-00.invalid.xml'
TEST_TEXT_DRAFT = 'draft-smoke-signals-00.txt'
TEST_KRAMDOWN_DRAFT = 'draft-smoke-signals-00.md'
TEST_MMARK_DRAFT = 'draft-smoke-signals-00.mmark.md'
TEST_UNSUPPORTED_FORMAT = 'draft-smoke-signals-00.odt'
TEST_XML_ERROR = 'draft-smoke-signals-00.error.xml'
TEST_KRAMDOWN_ERROR = 'draft-smoke-signals-00.error.md'
TEST_DATA = [
        TEST_XML_DRAFT, TEST_XML_V2_DRAFT, TEST_KRAMDOWN_DRAFT,
        TEST_MMARK_DRAFT]
TEMPORARY_DATA_DIR = './tests/tmp/'
VALID_API_KEY = 'foobar'


def get_path(filename):
    '''Returns file path'''
    return ''.join([TEST_DATA_DIR, filename])


class TestApiValidate(TestCase):
    '''Tests for /api/validate end point'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
                'UPLOAD_DIR': abspath(TEMPORARY_DATA_DIR),
                'REQUIRE_AUTH': False}

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
                        '/api/validate',
                        data={'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'No file')

    def test_missing_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/validate',
                        data={
                            'file': (
                                open(get_path(TEST_XML_DRAFT), 'rb'),
                                ''),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'Filename is missing')

    def test_unsupported_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/validate',
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

    def test_validate(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                for filename in TEST_DATA:
                    result = client.post(
                            '/api/validate',
                            data={
                                'file': (
                                    open(get_path(filename), 'rb'), filename),
                                'apikey': VALID_API_KEY})
                    json_data = result.get_json()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn('errors', json_data)
                    self.assertIn('warnings', json_data)
                    self.assertIn('idnits', json_data)
                    self.assertEqual(len(json_data['errors']), 0)
                    self.assertGreaterEqual(len(json_data['warnings']), 0)
                    self.assertGreater(len(json_data['idnits']), 0)

    def test_validate_text(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/validate',
                        data={
                            'file': (
                                open(get_path(TEST_TEXT_DRAFT), 'rb'),
                                TEST_TEXT_DRAFT),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertNotIn('errors', json_data)
                self.assertNotIn('warnings', json_data)
                self.assertIn('idnits', json_data)
                self.assertGreater(len(json_data['idnits']), 0)

    def test_validate_invalid_id(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/validate',
                        data={
                            'file': (
                                open(get_path(TEST_XML_INVALID), 'rb'),
                                TEST_XML_INVALID),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertIn('errors', json_data)
                self.assertIn('warnings', json_data)
                self.assertIn('idnits', json_data)
                self.assertGreater(len(json_data['errors']), 0)
                self.assertGreater(len(json_data['warnings']), 0)
                self.assertGreater(len(json_data['idnits']), 0)

    def test_kramdown_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/validate',
                        data={
                            'file': (
                                open(get_path(TEST_KRAMDOWN_ERROR), 'rb'),
                                TEST_KRAMDOWN_ERROR),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertTrue(json_data['error'].startswith(
                    'kramdown-rfc error:'))

    def test_xml_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/validate',
                        data={
                            'file': (
                                open(get_path(TEST_XML_ERROR), 'rb'),
                                TEST_XML_ERROR),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertTrue(json_data['error'].startswith(
                    'xml2rfc error:'))
