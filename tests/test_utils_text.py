from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from werkzeug.datastructures import FileStorage

from at.utils.text import (
    get_text_id,
    get_text_id_from_file,
    get_text_id_from_url,
    TextProcessingError,
)

TEST_DATA_DIR = "./tests/data/"
DRAFT_A = "draft-smoke-signals-00.txt"
DRAFT_B = "draft-smoke-signals-01.txt"
TEST_XML_DRAFT = "draft-smoke-signals-00.xml"
TEST_XML_V2_DRAFT = "draft-smoke-signals-00.v2.xml"
TEST_KRAMDOWN_DRAFT = "draft-smoke-signals-00.md"
TEST_MMARK_DRAFT = "draft-smoke-signals-00.mmark.md"
TEST_XML_ERROR = "draft-smoke-signals-00.error.xml"
TEST_DATA = [
    TEST_XML_DRAFT,
    TEST_XML_V2_DRAFT,
    DRAFT_A,
    DRAFT_B,
    TEST_KRAMDOWN_DRAFT,
    TEST_MMARK_DRAFT,
]
TEMPORARY_DATA_DIR = "./tests/tmp/"


class TestUtilsText(TestCase):
    """Tests for at.utils.text"""

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_get_text_id(self):
        for filename in TEST_DATA:
            original = "".join([TEST_DATA_DIR, filename])
            new = "".join([TEMPORARY_DATA_DIR, filename])
            copy(original, new)
            (dir_path, file_path) = get_text_id(TEMPORARY_DATA_DIR, new)
            self.assertTrue(Path(dir_path).exists())
            self.assertTrue(Path(file_path).exists())
            self.assertEqual(Path(file_path).suffix, ".txt")

    def test_get_text_id_error(self):
        filename = TEST_XML_ERROR
        original = "".join([TEST_DATA_DIR, filename])
        new = "".join([TEMPORARY_DATA_DIR, filename])
        copy(original, new)

        with self.assertRaises(TextProcessingError):
            get_text_id(TEMPORARY_DATA_DIR, new)

    def test_get_text_id_from_file(self):
        for filename in TEST_DATA:
            with open("".join([TEST_DATA_DIR, filename]), "rb") as file:
                file_object = FileStorage(file, filename=filename)
                (dir_path, file_path) = get_text_id_from_file(
                    file_object, TEMPORARY_DATA_DIR
                )
                self.assertTrue(Path(dir_path).exists())
                self.assertTrue(Path(file_path).exists())
                self.assertEqual(Path(file_path).suffix, ".txt")

    def test_get_text_id_from_file_error(self):
        filename = TEST_XML_ERROR
        with open("".join([TEST_DATA_DIR, filename]), "rb") as file:
            file_object = FileStorage(file, filename=filename)
            with self.assertRaises(TextProcessingError):
                get_text_id_from_file(file_object, TEMPORARY_DATA_DIR)

    def test_get_text_id_from_url(self):
        url = "https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-01.xml"
        (dir_path, file_path) = get_text_id_from_url(url, TEMPORARY_DATA_DIR)
        self.assertTrue(Path(dir_path).exists())
        self.assertTrue(Path(file_path).exists())
        self.assertEqual(Path(file_path).suffix, ".txt")

    def test_get_text_id_from_url_error(self):
        url = "https://author-tools.ietf.org/sitemap.xml"
        with self.assertRaises(TextProcessingError):
            get_text_id_from_url(url, TEMPORARY_DATA_DIR)

    def test_get_text_id_from_file_raw(self):
        for filename in TEST_DATA:
            suffix = f".{filename.split('.')[-1]}"
            with open("".join([TEST_DATA_DIR, filename]), "rb") as file:
                file_object = FileStorage(file, filename=filename)
                (dir_path, file_path) = get_text_id_from_file(
                    file_object, TEMPORARY_DATA_DIR, raw=True
                )
                self.assertTrue(Path(dir_path).exists())
                self.assertTrue(Path(file_path).exists())
                self.assertEqual(Path(file_path).suffix, suffix)

    def test_get_text_id_from_url_raw(self):
        url = "https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-01.xml"
        (dir_path, file_path) = get_text_id_from_url(url, TEMPORARY_DATA_DIR, raw=True)
        self.assertTrue(Path(dir_path).exists())
        self.assertTrue(Path(file_path).exists())
        self.assertEqual(Path(file_path).suffix, ".xml")

    def test_get_text_id_from_file_text_or_xml(self):
        for filename in TEST_DATA:
            suffix = f".{filename.split('.')[-1]}"
            with open("".join([TEST_DATA_DIR, filename]), "rb") as file:
                file_object = FileStorage(file, filename=filename)
                (dir_path, file_path) = get_text_id_from_file(
                    file_object, TEMPORARY_DATA_DIR, text_or_xml=True
                )
                self.assertTrue(Path(dir_path).exists())
                self.assertTrue(Path(file_path).exists())
                if suffix in [".xml", ".txt"]:
                    self.assertEqual(Path(file_path).suffix, suffix)
                else:
                    self.assertEqual(Path(file_path).suffix, ".txt")

    def test_get_text_id_from_url_text_or_xml(self):
        url = "https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-01.xml"
        (dir_path, file_path) = get_text_id_from_url(
            url, TEMPORARY_DATA_DIR, text_or_xml=True
        )
        self.assertTrue(Path(dir_path).exists())
        self.assertTrue(Path(file_path).exists())
        self.assertEqual(Path(file_path).suffix, ".xml")
