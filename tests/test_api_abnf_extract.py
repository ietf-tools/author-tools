from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from urllib.parse import urlencode

from at import create_app

API = '/api/abnf/extract'
TEMPORARY_DATA_DIR = './tests/tmp/'
DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/api/rfcdiff-latest-json'
ALLOWED_DOMAINS = ['ietf.org', 'rfc-editor.org']


class TestApiAbnfExtract(TestCase):
    '''Tests for /api/abnf/extract end point'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
                'UPLOAD_DIR': abspath(TEMPORARY_DATA_DIR),
                'REQUIRE_AUTH': False,
                'DT_LATEST_DRAFT_URL': DT_LATEST_DRAFT_URL,
                'ALLOWED_DOMAINS': ALLOWED_DOMAINS}

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_no_input(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(API)
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'],
                                 'URL/document name must be provided')

    def test_latest_draft_not_found_error(self):
        doc = 'draft-smoke-signals'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            API + '?' + urlencode({'doc': doc}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(
                        json_data['error'],
                        'Can not find the latest document on datatracker')

    def test_download_error(self):
        url = 'https://www.ietf.org/archives/id/draft-404.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            API + '?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'],
                                 'Error occured while downloading file.')

    def test_text_processing(self):
        url = 'https://datatracker.ietf.org/doc/pdf/draft-iab-xml2rfc-02'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            API + '?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertIn('error', json_data)
                self.assertGreater(len(json_data['error']), 0)

    def test_invalid_url(self):
        url = 'https://www.example.org/draft-example.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            API + '?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'],
                                 'www.example.org domain is not allowed.')

    def test_extract_abnf_empty(self):
        url = 'https://www.rfc-editor.org/rfc/rfc9009.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            API + '?' + urlencode({'url': url}))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertEqual(data, 'No output from BAP aex.')

    def test_extract_abnf_with_url(self):
        url = 'https://www.rfc-editor.org/rfc/rfc9000.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            API + '?' + urlencode({'url': url}))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn('expected_pn  = largest_pn + 1', data)

    def test_extract_abnf_with_docname(self):
        doc = 'RFC 9000'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            API + '?' + urlencode({'doc': doc}))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn('expected_pn  = largest_pn + 1', data)
