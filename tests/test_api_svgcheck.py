from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase
from os.path import abspath
from pathlib import Path
from shutil import rmtree

from at import create_app

API = '/api/svgcheck'
TEMPORARY_DATA_DIR = './tests/tmp/'
TEST_DATA_DIR = './tests/data/'
TEST_SVG = 'ietf.svg'
TEST_INVALID_SVG = 'invalid.svg'
TEST_UNSUPPORTED_FORMAT = 'draft-smoke-signals-00.md'


def get_path(filename):
    '''Returns file path'''
    return ''.join([TEST_DATA_DIR, filename])


class TestApiSvgcheck(TestCase):
    '''Tests for /api/svgcheck end point'''

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
                result = client.post(API)
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'No file')

    def test_missing_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        API,
                        data={
                            'file': (
                                open(get_path(TEST_SVG), 'rb'),
                                '')})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'Filename is missing')

    def test_unsupported_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        API,
                        data={
                            'file': (
                                open(get_path(TEST_UNSUPPORTED_FORMAT), 'rb'),
                                TEST_UNSUPPORTED_FORMAT)})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'],
                        'Input file format not supported')

    def test_svgcheck(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        API,
                        data={
                            'file': (
                                open(get_path(TEST_SVG), 'rb'),
                                TEST_SVG)})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertIn('</svg>', json_data['svg'])
                self.assertIn('File conforms to SVG requirements.',
                              json_data['svgcheck'])
                self.assertIsNone(json_data['errors'])

    def test_svgcheck_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        API,
                        data={
                            'file': (
                                open(get_path(TEST_INVALID_SVG), 'rb'),
                                TEST_INVALID_SVG)})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertIsNone(json_data['svg'])
                self.assertIsNone(json_data['svgcheck'])
                self.assertIn(
                        'ERROR: File does not conform to SVG requirements',
                        json_data['errors'])
