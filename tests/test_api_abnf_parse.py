from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase
from os.path import abspath
from pathlib import Path
from shutil import rmtree

from at import create_app

API = "/api/abnf/parse"
TEMPORARY_DATA_DIR = "./tests/tmp/"
DT_LATEST_DRAFT_URL = "https://datatracker.ietf.org/doc/rfcdiff-latest-json"
ALLOWED_DOMAINS = ["ietf.org", "rfc-editor.org"]
TEST_DATA_DIR = "./tests/data/"
ABNF = "name.abnf"
ABNF_ERROR = "name-error.abnf"


class TestApiAbnfParse(TestCase):
    """Tests for /api/abnf/parse end point"""

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

        config = {
            "UPLOAD_DIR": abspath(TEMPORARY_DATA_DIR),
            "REQUIRE_AUTH": False,
            "DT_LATEST_DRAFT_URL": DT_LATEST_DRAFT_URL,
            "ALLOWED_DOMAINS": ALLOWED_DOMAINS,
        }

        self.app = create_app(config)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

    def test_abnf_parse(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                file_path = "".join([TEST_DATA_DIR, ABNF])
                with open(file_path, "r", newline="") as file:
                    abnf = "".join(file.readlines())

                    result = client.post(API, data={"input": abnf})
                    json_data = result.get_json()

                    self.assertEqual(result.status_code, 200)
                    self.assertEqual(json_data["errors"], "")
                    self.assertIn("first-name last-name", json_data["abnf"])

    def test_abnf_parse_with_errors(self):
        with self.app.test_client() as client:
            with self.app.app_context():
                file_path = "".join([TEST_DATA_DIR, ABNF_ERROR])
                with open(file_path, "r", newline="") as file:
                    abnf = "".join(file.readlines())

                    result = client.post(API, data={"input": abnf})
                    json_data = result.get_json()

                    self.assertEqual(result.status_code, 200)
                    self.assertIn(
                        "Rule first-name was already defined", json_data["errors"]
                    )
                    self.assertIn("; middle-name UNDEFINED", json_data["abnf"])
