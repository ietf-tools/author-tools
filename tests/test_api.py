import logging
import unittest

from faker import Faker
from hypothesis import given, assume
from hypothesis.strategies import text

from at import api


class TestApi(unittest.TestCase):
    '''Tests for at.api'''

    def setUp(self):
        self.faker = Faker(seed=1985)
        logging.disable(logging.CRITICAL)   # susspress logging messages

    def tearDown(self):
        logging.disable(logging.INFO)   # enable logging messages

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
            self.assertTrue(
                    api.get_file(file_path).endswith(extension))
            self.assertNotIn('/', api.get_file(file_path))
