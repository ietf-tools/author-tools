from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from at import create_app

TEMPORARY_DATA_DIR = './tests/tmp/'


class TestApiRender(TestCase):
    '''Tests for /api/render end point'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {'UPLOAD_DIR': './tests/tmp'}
        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_no_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post('/api/render/xml')
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data['error'], 'No file')
