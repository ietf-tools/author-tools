from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from at.utils.yang import validate_yang

TEST_DATA_DIR = "./tests/data/"
TEST_YANG = "ietf-smoke-signals.yang"
TEST_YANG_ERROR = "ietf-smoke-signals-error.yang"
TEST_TEXT_DRAFT = "draft-smoke-signals-00.txt"
TEST_DATA = [TEST_YANG, TEST_YANG_ERROR, TEST_TEXT_DRAFT]
TEMPORARY_DATA_DIR = "./tests/tmp/"


class TestUtilsYang(TestCase):
    """Tests for at.utils.yang"""

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

    def test_validate_yang(self):
        pyang, errors = validate_yang("".join([TEMPORARY_DATA_DIR, TEST_YANG]))

        self.assertEqual(errors, "")
        self.assertEqual(pyang, "YANG file is valid.")

    def test_validate_yang_error(self):
        pyang, errors = validate_yang("".join([TEMPORARY_DATA_DIR, TEST_YANG_ERROR]))

        self.assertGreater(len(errors), 0)
        self.assertIn("error: ", errors)
        self.assertIn('type "strng" not found', errors)

    def test_validate_yang_ietf_guidelines(self):
        pyang, errors = validate_yang("".join([TEMPORARY_DATA_DIR, TEST_YANG_ERROR]))

        self.assertIn("RFC 8407", errors)
        self.assertIn("warning: ", errors)

    def test_validate_yang_non_yang_file(self):
        pyang, errors = validate_yang("".join([TEMPORARY_DATA_DIR, TEST_TEXT_DRAFT]))

        self.assertGreater(len(errors), 0)
        self.assertIn("error: ", errors)

    def test_validate_yang_missing_file(self):
        pyang, errors = validate_yang("foobar.yang")

        self.assertIn("No such file or directory", errors)
        self.assertEqual(pyang, "")

    def test_validate_yang_no_internal_paths(self):
        pyang, errors = validate_yang("".join([TEMPORARY_DATA_DIR, TEST_YANG_ERROR]))

        self.assertNotIn(TEMPORARY_DATA_DIR, errors)
        self.assertNotIn(TEST_YANG_ERROR, errors)
