from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase
from os.path import abspath
from pathlib import Path
from shutil import rmtree

from at import create_app

API = "/api/yang/validate"
TEMPORARY_DATA_DIR = "./tests/tmp/"
TEST_DATA_DIR = "./tests/data/"
TEST_YANG = "ietf-smoke-signals.yang"
TEST_YANG_ERROR = "ietf-smoke-signals-error.yang"


def get_path(filename):
    """Returns file path"""
    return "".join([TEST_DATA_DIR, filename])


class TestApiYangValidate(TestCase):
    """Tests for /api/yang/validate end point"""

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {"UPLOAD_DIR": abspath(TEMPORARY_DATA_DIR)}

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_no_file(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(API)
                json_data = result.get_json()

                self.assertEqual(result.status_code, 400)
                self.assertEqual(json_data["error"], "No file")

    def test_yang_validate(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                    API, data={"file": (open(get_path(TEST_YANG), "rb"), TEST_YANG)}
                )
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertEqual(json_data["errors"], "")
                self.assertEqual(json_data["pyang"], "YANG file is valid.")

    def test_yang_validate_error(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                    API,
                    data={
                        "file": (
                            open(get_path(TEST_YANG_ERROR), "rb"),
                            TEST_YANG_ERROR,
                        )
                    },
                )
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertGreater(len(json_data["errors"]), 0)
                self.assertIn('type "strng" not found', json_data["errors"])
                self.assertIn("RFC 8407", json_data["errors"])

    def test_yang_validate_no_internal_paths(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                result = client.post(
                    API,
                    data={
                        "file": (
                            open(get_path(TEST_YANG_ERROR), "rb"),
                            TEST_YANG_ERROR,
                        )
                    },
                )
                json_data = result.get_json()

                self.assertEqual(result.status_code, 200)
                self.assertNotIn(TEMPORARY_DATA_DIR, json_data["errors"])
                self.assertNotIn(TEST_YANG_ERROR, json_data["errors"])
