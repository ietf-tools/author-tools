from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

import responses

from at import create_app

TEST_DATA_DIR = './tests/data/'
DRAFT_A = 'draft-smoke-signals-00.txt'
DRAFT_B = 'draft-smoke-signals-01.txt'
TEST_UNSUPPORTED_FORMAT = 'draft-smoke-signals-00.odt'
TEMPORARY_DATA_DIR = './tests/tmp/'
DT_APPAUTH_URL = 'https://example.com/'
VALID_API_KEY = 'foobar'


def get_path(filename):
    '''Returns file path'''
    return ''.join([TEST_DATA_DIR, filename])


class TestApiIddiff(TestCase):
    '''Tests for /api/iddiff end point'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
                'UPLOAD_DIR': abspath(TEMPORARY_DATA_DIR),
                'DT_APPAUTH_URL': DT_APPAUTH_URL}

        # mock datatracker api response
        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
                responses.POST,
                DT_APPAUTH_URL,
                json={'success': True},
                status=200)
        self.addCleanup(self.responses.stop)
        self.addCleanup(self.responses.reset)

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
                        '/api/iddiff',
                        data={'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'Missing file(s)')

    def test_missing_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'file_2': (
                                open(get_path(DRAFT_B), 'rb'),
                                ''),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'Filename(s) missing')

    def test_unsupported_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'file_2': (
                                open(get_path(TEST_UNSUPPORTED_FORMAT), 'rb'),
                                TEST_UNSUPPORTED_FORMAT),
                            'apikey': VALID_API_KEY})
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'],
                        'Input file format(s) not supported')

    def test_iddiff(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                        '/api/iddiff',
                        data={
                            'file_1': (
                                open(get_path(DRAFT_A), 'rb'),
                                DRAFT_A),
                            'file_2': (
                                open(get_path(DRAFT_B), 'rb'),
                                DRAFT_B),
                            'apikey': VALID_API_KEY})

                data = result.get_data()

                self.assertEqual(result.status_code, 200)
                self.assertIn(b'<html lang="en">', data)
                self.assertIn(str.encode(DRAFT_A), data)
                self.assertIn(str.encode(DRAFT_B), data)
