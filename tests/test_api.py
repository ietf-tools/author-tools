from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from faker import Faker
from hypothesis import given, assume
from hypothesis.strategies import text
from werkzeug.datastructures import FileStorage
from xml2rfc.parser import XmlRfc

from at import api

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_XML_V2_DRAFT = 'draft-smoke-signals-00.v2.xml'
TEST_TEXT_DRAFT = 'draft-smoke-signals-00.txt'
TEST_KRAMDOWN_DRAFT = 'draft-smoke-signals-00.md'
TEST_DATA = [
        TEST_XML_DRAFT, TEST_XML_V2_DRAFT, TEST_TEXT_DRAFT,
        TEST_KRAMDOWN_DRAFT]
TEMPORARY_DATA_DIR = './tests/tmp/'


class TestApi(TestCase):
    '''Tests for at.api'''

    def setUp(self):
        self.faker = Faker(seed=1985)
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)
        # create copies of test data in temporary data dir
        for file in TEST_DATA:
            original = ''.join([TEST_DATA_DIR, file])
            new = ''.join([TEMPORARY_DATA_DIR, file])
            copy(original, new)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
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
            with open(''.join([TEST_DATA_DIR, filename]), 'rb') as file:
                file_object = FileStorage(file, filename=filename)
                dir_path, saved_file = api.process_file(
                        file_object, TEMPORARY_DATA_DIR)

                self.assertTrue(Path(dir_path).is_dir())
                self.assertTrue(Path(saved_file).exists())
                self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_md2xml(self):
        saved_file = api.md2xml(
                ''.join([TEMPORARY_DATA_DIR, TEST_KRAMDOWN_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_txt2xml(self):
        saved_file = api.md2xml(
                ''.join([TEMPORARY_DATA_DIR, TEST_TEXT_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_convert_v2v3(self):
        saved_file = api.convert_v2v3(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_V2_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_get_xml(self):
        for file in [TEST_XML_DRAFT, TEST_XML_V2_DRAFT]:
            saved_file = api.get_xml(
                    ''.join([TEMPORARY_DATA_DIR, file]))

            self.assertTrue(Path(saved_file).exists())
            self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_prep_xml(self):
        xml = api.prep_xml(''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertIsInstance(xml, XmlRfc)

    def test_get_html(self):
        saved_file = api.get_html(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.html')

    def test_get_text(self):
        saved_file = api.get_text(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.txt')

    def test_get_pdf(self):
        saved_file = api.get_pdf(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.pdf')