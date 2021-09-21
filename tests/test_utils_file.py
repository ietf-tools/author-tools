from unittest import TestCase

from faker import Faker
from hypothesis import given, assume
from hypothesis.strategies import text

from at.utils.file import (
        ALLOWED_EXTENSIONS, allowed_file, get_file, get_filename)


class TestUtilsFile(TestCase):
    '''Tests for at.utils.file'''

    def setUp(self):
        self.faker = Faker(seed=1985)

    @given(text())
    def test_allowed_file_for_non_supported(self, filename):
        for extension in ALLOWED_EXTENSIONS:
            assume(not filename.endswith(extension))

        self.assertFalse(allowed_file(filename))

    def test_allowed_file_for_supported(self):
        for extension in ALLOWED_EXTENSIONS:
            filename = self.faker.file_name(extension=extension)

            self.assertTrue(allowed_file(filename))

    def test_get_filename(self):
        for extension in ALLOWED_EXTENSIONS:
            filename = self.faker.file_name()

            self.assertTrue(
                    get_filename(filename, extension).endswith(extension))

    def test_get_file(self):
        for extension in ALLOWED_EXTENSIONS:
            file_path = self.faker.file_path(extension=extension)
            result = get_file(file_path)

            self.assertTrue(result.endswith(extension))
            self.assertNotIn('/', result)
