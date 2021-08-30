import logging
import unittest
from pathlib import Path
from shutil import rmtree

from faker import Faker
from hypothesis import given, assume
from hypothesis.strategies import text
from werkzeug.datastructures import FileStorage

from at import api

TEST_DATA_DIR = './tests/data/'
TEST_DATA = [
        'draft-smoke-signals-00.xml',
        'draft-smoke-signals-00.txt',
        'draft-smoke-signals-00.md']
TEMPORARY_DATA_DIR = './tests/tmp/'


class TestApi(unittest.TestCase):
    '''Tests for at.api'''

    def setUp(self):
        self.faker = Faker(seed=1985)
        # susspress logging messages
        logging.disable(logging.CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

    def tearDown(self):
        # enable logging messages
        logging.disable(logging.INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    @given(text())
    def test_allowed_file_for_non_supported(self, filename):
        for extension in api.ALLOWED_EXTENSIONS:
            assume(not filename.endswith(extension))

        self.assertFalse(api.allowed_file(filename))

    def test_allowed_file_for_supported(self):
        for extension in api.ALLOWED_EXTENSIONS:
            filename = self.faker.file_name(extension=extension)

            self.assertTrue(api.allowed_file(filename))

    def test_get_filename(self):
        for extension in api.ALLOWED_EXTENSIONS:
            filename = self.faker.file_name()

            self.assertTrue(
                    api.get_filename(filename, extension).endswith(extension))

    def test_get_file(self):
        for extension in api.ALLOWED_EXTENSIONS:
            file_path = self.faker.file_path(extension=extension)
            result = api.get_file(file_path)

            self.assertTrue(result.endswith(extension))
            self.assertNotIn('/', result)

    def test_process_file(self):
        for filename in TEST_DATA:
            with open('/'.join([TEST_DATA_DIR, filename]), 'rb') as file:
                file_object = FileStorage(file, filename=filename)
                dir_path, saved_file = api.process_file(
                        file_object, TEMPORARY_DATA_DIR)

                self.assertTrue(Path(dir_path).is_dir())
                self.assertTrue(Path(saved_file).exists())
                self.assertEqual(Path(saved_file).suffix, '.xml')
