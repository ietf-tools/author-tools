from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from werkzeug.datastructures import FileStorage
from xml2rfc.parser import XmlRfc

from at.utils.processor import (
        convert_v2v3, get_html, get_pdf, get_text, get_xml, md2xml, prep_xml,
        process_file)

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_XML_V2_DRAFT = 'draft-smoke-signals-00.v2.xml'
TEST_TEXT_DRAFT = 'draft-smoke-signals-00.txt'
TEST_KRAMDOWN_DRAFT = 'draft-smoke-signals-00.md'
TEST_DATA = [
        TEST_XML_DRAFT, TEST_XML_V2_DRAFT, TEST_TEXT_DRAFT,
        TEST_KRAMDOWN_DRAFT]
TEMPORARY_DATA_DIR = './tests/tmp/'


class TestUtilsProcessor(TestCase):
    '''Tests for at.utils.processor'''

    def setUp(self):
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

    def test_process_file(self):
        for filename in TEST_DATA:
            with open(''.join([TEST_DATA_DIR, filename]), 'rb') as file:
                file_object = FileStorage(file, filename=filename)
                dir_path, saved_file = process_file(
                        file_object, TEMPORARY_DATA_DIR)

                self.assertTrue(Path(dir_path).is_dir())
                self.assertTrue(Path(saved_file).exists())
                self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_md2xml(self):
        saved_file = md2xml(
                ''.join([TEMPORARY_DATA_DIR, TEST_KRAMDOWN_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_txt2xml(self):
        saved_file = md2xml(
                ''.join([TEMPORARY_DATA_DIR, TEST_TEXT_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_convert_v2v3(self):
        saved_file = convert_v2v3(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_V2_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_get_xml(self):
        for file in [TEST_XML_DRAFT, TEST_XML_V2_DRAFT]:
            saved_file = get_xml(
                    ''.join([TEMPORARY_DATA_DIR, file]))

            self.assertTrue(Path(saved_file).exists())
            self.assertEqual(Path(saved_file).suffix, '.xml')

    def test_prep_xml(self):
        xml = prep_xml(''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertIsInstance(xml, XmlRfc)

    def test_get_html(self):
        saved_file = get_html(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.html')

    def test_get_text(self):
        saved_file = get_text(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.txt')

    def test_get_pdf(self):
        saved_file = get_pdf(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.pdf')
