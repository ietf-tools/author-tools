from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from at.utils.logs import process_xml2rfc_log
from at.utils.validation import xml2rfc_validation

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_XML_INVALID = 'draft-smoke-signals-00.invalid.xml'
TEST_XML_V2_DRAFT = 'draft-smoke-signals-00.v2.xml'
TEST_DATA = [TEST_XML_DRAFT, TEST_XML_INVALID, TEST_XML_V2_DRAFT]
TEMPORARY_DATA_DIR = './tests/tmp/'


class TestUtilsLogs(TestCase):
    '''Tests for at.utils.logs'''

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

    def test_process_xml2rfc_log(self):
        for file in TEST_DATA:
            output, _ = xml2rfc_validation(''.join([TEMPORARY_DATA_DIR, file]))
            log = process_xml2rfc_log(output)

            self.assertIn('errors', log.keys())
            self.assertIn('warnings', log.keys())
            self.assertGreaterEqual(len(log['errors']), 0)
            self.assertGreaterEqual(len(log['warnings']), 0)
            for error in log['errors']:
                self.assertNotRegex(r'xml2rfc', error)
                self.assertNotRegex(r'Error:', error)
            for warning in log['warnings']:
                self.assertNotRegex(r'xml2rfc', warning)
                self.assertNotRegex(r'Warning:', warning)
