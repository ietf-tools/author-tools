from logging import disable as set_logger, INFO, CRITICAL
from os.path import abspath
from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from at import create_app

TEST_DATA_DIR = "./tests/data/"
TEST_XML_DRAFT = "draft-smoke-signals-02.xml"
TEST_UNSUPPORTED_FORMAT = "draft-smoke-signals-00.odt"
TEMPORARY_DATA_DIR = "./tests/tmp/"
VALID_API_KEY = "foobar"
SITE_URL = "https://example.org"


def get_path(filename):
    """Returns file path"""
    return "".join([TEST_DATA_DIR, filename])


class TestApiCleanSvgIds(TestCase):
    """Tests for /api/clean_svg_ids end point"""

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
            "UPLOAD_DIR": abspath(TEMPORARY_DATA_DIR),
            "REQUIRE_AUTH": False,
            "SITE_URL": SITE_URL,
        }

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_no_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                    "/api/clean_svg_ids", data={"apikey": VALID_API_KEY}
                )
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data["error"], "No file")

    def test_missing_file_name(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                    "/api/clean_svg_ids",
                    data={
                        "file": (open(get_path(TEST_XML_DRAFT), "rb"), ""),
                        "apikey": VALID_API_KEY,
                    },
                )
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data["error"], "Filename is missing")

    def test_unsupported_file_format(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                    "/api/clean_svg_ids",
                    data={
                        "file": (
                            open(get_path(TEST_UNSUPPORTED_FORMAT), "rb"),
                            TEST_UNSUPPORTED_FORMAT,
                        ),
                        "apikey": VALID_API_KEY,
                    },
                )
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data["error"], "Input file format not supported")

    def test_clean_svg_ids(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                    "/api/clean_svg_ids",
                    data={
                        "file": (open(get_path(TEST_XML_DRAFT), "rb"), TEST_XML_DRAFT),
                        "apikey": VALID_API_KEY,
                    },
                )
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertTrue(json_data["url"].startswith("{}/".format(SITE_URL)))

                # test export
                export_url = json_data["url"].replace(SITE_URL, "")
                export = client.get(export_url)
                self.assertEqual(export.status_code, 200)
                self.assertIsNotNone(export.data)
