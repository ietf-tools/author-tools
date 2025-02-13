from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from werkzeug.datastructures import FileStorage

from at.utils.processor import (
    clean_svg_ids,
    convert_v2v3,
    get_html,
    get_pdf,
    get_text,
    get_xml,
    kramdown2xml,
    md2xml,
    mmark2xml,
    process_file,
    txt2xml,
    rst2xml,
    MmarkError,
    XML2RFCError,
    RstError,
)

TEST_DATA_DIR = "./tests/data/"
TEST_XML_DRAFT = "draft-smoke-signals-00.xml"
TEST_XML_V2_DRAFT = "draft-smoke-signals-00.v2.xml"
TEST_TEXT_DRAFT = "draft-smoke-signals-00.txt"
TEST_KRAMDOWN_DRAFT = "draft-smoke-signals-00.md"
TEST_MMARK_DRAFT = "draft-smoke-signals-00.mmark.md"
TEST_XML_ERROR = "draft-smoke-signals-00.error.xml"
TEST_RST_DRAFT = "draft-doe-smoke-signals-00.rst"
TEST_DATA = [
    TEST_XML_DRAFT,
    TEST_XML_V2_DRAFT,
    TEST_TEXT_DRAFT,
    TEST_KRAMDOWN_DRAFT,
    TEST_MMARK_DRAFT,
    TEST_RST_DRAFT,
]
TEMPORARY_DATA_DIR = "./tests/tmp/"


class TestUtilsProcessor(TestCase):
    """Tests for at.utils.processor"""

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)
        # create copies of test data in temporary data dir
        for file in TEST_DATA:
            original = "".join([TEST_DATA_DIR, file])
            new = "".join([TEMPORARY_DATA_DIR, file])
            copy(original, new)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_process_file(self):
        for filename in TEST_DATA:
            with open("".join([TEST_DATA_DIR, filename]), "rb") as file:
                file_object = FileStorage(file, filename=filename)
                dir_path, saved_file = process_file(file_object, TEMPORARY_DATA_DIR)

                self.assertTrue(Path(dir_path).is_dir())
                self.assertTrue(Path(saved_file).exists())
                self.assertEqual(Path(saved_file).suffix, ".xml")

    def test_md2xml(self):
        for filename in [TEST_KRAMDOWN_DRAFT, TEST_MMARK_DRAFT]:
            saved_file = md2xml("".join([TEMPORARY_DATA_DIR, filename]))

            self.assertTrue(Path(saved_file).exists())
            self.assertEqual(Path(saved_file).suffix, ".xml")

    def test_kramdown2xml(self):
        saved_file = kramdown2xml("".join([TEMPORARY_DATA_DIR, TEST_KRAMDOWN_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")

    def test_mmark2xml(self):
        saved_file = mmark2xml("".join([TEMPORARY_DATA_DIR, TEST_MMARK_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")

    def test_mmark2xml_error(self):
        mmark2xml("foobar")
        self.assertRaises(MmarkError)

    def test_rst2xml(self):
        saved_file = rst2xml("".join([TEMPORARY_DATA_DIR, TEST_RST_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")

    def test_rst2xml_error(self):
        with self.assertRaises(RstError):
            rst2xml("foobar")

    def test_txt2xml(self):
        saved_file = txt2xml("".join([TEMPORARY_DATA_DIR, TEST_TEXT_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")

    def test_convert_v2v3(self):
        saved_file, logs = convert_v2v3(
            "".join([TEMPORARY_DATA_DIR, TEST_XML_V2_DRAFT])
        )

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")
        self.assertIn("errors", logs.keys())
        self.assertIn("warnings", logs.keys())

    def test_convert_v2v3_error(self):
        with self.assertRaises(XML2RFCError):
            saved_file, logs = convert_v2v3(
                "".join([TEMPORARY_DATA_DIR, TEST_XML_ERROR])
            )

    def test_get_xml(self):
        saved_file, logs = get_xml("".join([TEMPORARY_DATA_DIR, TEST_XML_V2_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")
        self.assertIn("errors", logs.keys())
        self.assertIn("warnings", logs.keys())

    def test_get_xml_v3(self):
        saved_file, logs = get_xml("".join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")
        self.assertIsNone(logs)

    def test_get_html(self):
        saved_file, logs = get_html("".join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".html")
        self.assertIn("errors", logs.keys())
        self.assertIn("warnings", logs.keys())

    def test_get_html_error(self):
        with self.assertRaises(XML2RFCError):
            saved_file, logs = get_html("".join([TEMPORARY_DATA_DIR, TEST_XML_ERROR]))

    def test_get_text(self):
        saved_file, logs = get_text("".join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".txt")
        self.assertIn("errors", logs.keys())
        self.assertIn("warnings", logs.keys())

    def test_get_text_error(self):
        with self.assertRaises(XML2RFCError):
            saved_file, logs = get_text("".join([TEMPORARY_DATA_DIR, TEST_XML_ERROR]))

    def test_get_pdf(self):
        saved_file, logs = get_pdf("".join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".pdf")
        self.assertIn("errors", logs.keys())
        self.assertIn("warnings", logs.keys())

    def test_get_pdf_error(self):
        with self.assertRaises(XML2RFCError):
            saved_file, logs = get_pdf("".join([TEMPORARY_DATA_DIR, TEST_XML_ERROR]))

    def test_clean_svg_ids(self):
        saved_file = clean_svg_ids("".join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, ".xml")
