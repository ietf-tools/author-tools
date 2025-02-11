from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from faker import Faker
from hypothesis import given, assume
from hypothesis.strategies import text
from werkzeug.datastructures import FileStorage

from at.utils.file import (
    allowed_file,
    cleanup_output,
    get_file,
    get_filename,
    get_name,
    get_name_with_revision,
    save_file,
    save_file_from_text,
    save_file_from_url,
    ALLOWED_EXTENSIONS,
    ALLOWED_EXTENSIONS_BY_PROCESS,
    DownloadError,
)

TEST_DATA_DIR = "./tests/data/"
TEST_XML_DRAFT = "draft-smoke-signals-00.xml"
TEST_XML_V2_DRAFT = "draft-smoke-signals-00.v2.xml"
TEST_TEXT_DRAFT = "draft-smoke-signals-00.txt"
TEST_KRAMDOWN_DRAFT = "draft-smoke-signals-00.md"
TEST_MMARK_DRAFT = "draft-smoke-signals-00.mmark.md"
TEST_DATA = [
    TEST_XML_DRAFT,
    TEST_XML_V2_DRAFT,
    TEST_TEXT_DRAFT,
    TEST_KRAMDOWN_DRAFT,
    TEST_MMARK_DRAFT,
]
TEMPORARY_DATA_DIR = "./tests/tmp/"


class TestUtilsFile(TestCase):
    """Tests for at.utils.file"""

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # set faker
        self.faker = Faker(seed=1985)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    @given(text())
    def test_allowed_file_for_non_supported(self, filename):
        for extension in ALLOWED_EXTENSIONS:
            assume(not filename.endswith(extension))

        self.assertFalse(allowed_file(filename))

    def test_allowed_file_for_supported(self):
        for extension in ALLOWED_EXTENSIONS:
            filename = self.faker.file_name(extension=extension)

            self.assertTrue(allowed_file(filename))

    @given(text())
    def test_allowed_file_for_non_supported_with_process(self, filename):
        for process in ALLOWED_EXTENSIONS_BY_PROCESS.keys():
            for extension in ALLOWED_EXTENSIONS_BY_PROCESS[process]:
                assume(not filename.endswith(extension))

            self.assertFalse(allowed_file(filename, process=process))

    def test_allowed_file_for_supported_with_process(self):
        for process in ALLOWED_EXTENSIONS_BY_PROCESS.keys():
            for extension in ALLOWED_EXTENSIONS_BY_PROCESS[process]:
                filename = self.faker.file_name(extension=extension)

                self.assertTrue(allowed_file(filename, process=process))

    def test_get_filename(self):
        for extension in ALLOWED_EXTENSIONS:
            filename = self.faker.file_name()

            self.assertTrue(get_filename(filename, extension).endswith(extension))

    def test_get_file(self):
        for extension in ALLOWED_EXTENSIONS:
            file_path = self.faker.file_path(extension=extension, depth=3)
            result = get_file(file_path)

            self.assertTrue(result.endswith(extension))
            self.assertFalse(result.startswith("/"))
            self.assertTrue(result.count("/"), 1)

    def test_save_file(self):
        for filename in TEST_DATA:
            with open("".join([TEST_DATA_DIR, filename]), "rb") as file:
                file_object = FileStorage(file, filename=filename)
                (dir_path, file_path) = save_file(file_object, TEMPORARY_DATA_DIR)
                self.assertTrue(Path(dir_path).exists())
                self.assertTrue(Path(file_path).exists())

    @given(text())
    def test_save_file_from_text(self, text):
        dir_path, file_path = save_file_from_text(text, TEMPORARY_DATA_DIR)

        self.assertTrue(Path(dir_path).exists())
        self.assertTrue(Path(file_path).exists())

        with open(file_path, "r", newline="") as file:
            self.assertEqual(text, "".join(file.readlines()))

    def test_save_file_from_url_connection_error(self):
        with self.assertRaises(DownloadError) as error:
            save_file_from_url("https://example.foobar/draft.txt", TEMPORARY_DATA_DIR)
        self.assertEqual(str(error.exception), "Error occured while downloading file.")

    def test_save_file_from_url_404_error(self):
        with self.assertRaises(DownloadError) as error:
            save_file_from_url("https://example.com/draft-404.txt", TEMPORARY_DATA_DIR)
        self.assertEqual(str(error.exception), "Error occured while downloading file.")

    def test_save_file_from_url_no_filename(self):
        url = "https://example.com/"
        with self.assertRaises(DownloadError) as error:
            save_file_from_url(url, TEMPORARY_DATA_DIR)
        self.assertEqual(
            str(error.exception), "Can not determine the filename: {}".format(url)
        )

    def test_save_file_from_url_valid(self):
        id_url = "https://www.ietf.org/archive/id/draft-ietf-quic-http-23.txt"
        (dir_path, file_path) = save_file_from_url(id_url, TEMPORARY_DATA_DIR)
        self.assertTrue(Path(dir_path).exists())
        self.assertTrue(Path(file_path).exists())

    @given(text())
    def test_get_name_non_standarded(self, filename):
        for prefix in ["draft-", "rfc"]:
            assume(not filename.startswith(prefix))

        self.assertIsNone(get_name(filename))

    def test_get_name_standarded(self):
        names_dictionary = {
            "rfc3333": "rfc3333",
            "rfc3333.txt": "rfc3333",
            "draft-smoke-signals-00.txt": "draft-smoke-signals",
            "draft-smoke-signals-01": "draft-smoke-signals",
            "draft-smoke-signals": "draft-smoke-signals",
        }

        for filename, name in names_dictionary.items():
            self.assertEqual(get_name(filename), name)

    @given(text())
    def test_get_name_with_revision_non_standarded(self, filename):
        for prefix in ["draft-", "rfc"]:
            assume(not filename.startswith(prefix))

        self.assertIsNone(get_name_with_revision(filename))

    def test_get_name_with_revision_standarded(self):
        names_dictionary = {
            "rfc3333": "rfc3333",
            "rfc3333.txt": "rfc3333",
            "draft-smoke-signals-00.txt": "draft-smoke-signals-00",
            "draft-smoke-signals-01": "draft-smoke-signals-01",
            "draft-smoke-signals": "draft-smoke-signals",
        }

        for filename, name in names_dictionary.items():
            self.assertEqual(get_name_with_revision(filename), name)

    def test_cleanup_output(self):
        rel_dir = TEST_DATA_DIR
        filename = TEST_XML_DRAFT
        rel_path = "".join((TEST_DATA_DIR, TEST_XML_DRAFT))
        abs_path = Path.resolve(Path(rel_path))
        abs_dir = str(abs_path.parent)
        output_0 = "foobar-0"
        output_1 = "foobar-1"
        output_2 = "foobar-2"
        output_3 = "foobar-3"

        log_output = "\n".join(
            (
                output_0,
                ":".join((filename, output_1)),
                ":".join((rel_path, output_2)),
                ":".join((str(abs_path), output_3)),
            )
        )

        result = cleanup_output(abs_path, log_output)

        for output in (output_0, output_1, output_2, output_3):
            self.assertIn(output, result)

        self.assertIn(filename, result)
        self.assertNotIn(rel_dir, result)
        self.assertNotIn(abs_dir, result)

    def test_cleanup_output_when_none(self):
        output = cleanup_output(None, None)

        self.assertIsNone(output)
