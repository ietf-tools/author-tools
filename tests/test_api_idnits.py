from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase
from urllib.parse import urlencode

from at import create_app

TEMPORARY_DATA_DIR = './tests/tmp/'
ALLOWED_DOMAINS = ['ietf.org', 'datatracker.ietf.org']


class TestApiIdnits(TestCase):
    '''Tests for /api/idnits end point'''

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
                result = client.get('/api/idnits')
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'URL is missing')

    def test_text_processing(self):
        url = 'https://datatracker.ietf.org/doc/pdf/draft-iab-xml2rfc-02'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertIn('error', json_data)
                self.assertGreater(len(json_data['error']), 0)

    def test_invalid_url(self):
        url = 'https://www.example.org/draft-example.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'],
                                 'www.example.org domain is not allowed.')

    def test_download_error(self):
        url = 'https://www.ietf.org/archives/id/draft-404.txt'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits?' + urlencode({'url': url}))
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'],
                                 'Error occured while downloading file.')

    def test_idnits(self):
        url = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.txt'
        id = 'draft-iab-xml2rfcv2-02'

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits?' + urlencode({'url': url}))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(id, data)
                self.assertIn('warnings', data)
                self.assertIn('idnits', data)
                # verbose
                self.assertNotIn('Run idnits with the --verbose', data)
                # showtext
                self.assertIn('Internet-Drafts are working documents', data)
                # submission check
                self.assertNotIn('Running in submission checking mode', data)
                # year
                self.assertIn('The copyright year in the IETF', data)

    def test_idnits_options(self):
        url = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.txt'
        id = 'draft-iab-xml2rfcv2-02'
        params = {
                'url': url,
                'verbose': 0,
                'hidetext': True,
                'year': 2015}

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits?' + urlencode(params))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(id, data)
                self.assertIn('warnings', data)
                self.assertIn('idnits', data)
                # verbose
                self.assertIn('Run idnits with the --verbose', data)
                # showtext
                self.assertNotIn('Internet-Drafts are working documents', data)
                # submission check
                self.assertNotIn('Running in submission checking mode', data)
                # year
                self.assertNotIn('The copyright year in the IETF', data)

    def test_idnits_submission_check(self):
        url = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-02.txt'
        id = 'draft-iab-xml2rfcv2-02'
        params = {'url': url, 'submitcheck': True}

        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get(
                            '/api/idnits?' + urlencode(params))
                data = result.get_data(as_text=True)

                self.assertEqual(result.status_code, 200)
                self.assertIn(id, data)
                self.assertIn('warnings', data)
                self.assertIn('idnits', data)
                # submission check
                self.assertIn('Running in submission checking mode', data)
