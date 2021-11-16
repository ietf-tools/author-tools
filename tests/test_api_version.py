from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase

from at import create_app

AUTHOR_TOOLS_API_TEST_VERSION = '0.0.1'
DT_APPAUTH_URL = 'https://example.com/'
VERSION_LABELS = (
    'author_tools_api',
    'xml2rfc',
    'kramdown-rfc2629',
    'mmark',
    'id2xml',
    'weasyprint',
    'idnits',
    'iddiff',
    'aasvg',
    'goat')


class TestApiVersion(TestCase):
    '''Tests for /api/version end point'''

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

    def test_version(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.get('/api/version')
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)

                for label in VERSION_LABELS:
                    self.assertIn(label, json_data['versions'])

                self.assertEqual(
                        json_data['versions']['author_tools_api'],
                        AUTHOR_TOOLS_API_TEST_VERSION)
