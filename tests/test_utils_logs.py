from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

from at.utils.logs import (get_errors, process_xml2rfc_log, update_logs,
                           XML2RFC_ERROR_REGEX, XML2RFC_LINE_NUMBER_REGEX,
                           XML2RFC_WARN_REGEX)
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

    def test_get_errors_valid(self):
        output, _ = xml2rfc_validation(
                        ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        errors = get_errors(output)

        self.assertIsNone(errors)

    def test_get_errors_invalid(self):
        output, _ = xml2rfc_validation(
                        ''.join([TEMPORARY_DATA_DIR, TEST_XML_INVALID]))
        errors = get_errors(output)

        self.assertIsNotNone(errors)
        self.assertIsInstance(errors, str)
        self.assertGreater(len(errors), 0)

    def test_update_logs(self):
        logs = {
                'errors': ['foo', ],
                'warnings': ['bar', ]}

        new_entries = {
                'errors': ['foobar_error', 'foobar_error_1', ],
                'warnings': ['foobar_warning', 'foobar_warning_1', ]}

        updated_logs = update_logs(logs, new_entries)

        for (key, entries) in logs.items():
            self.assertIn(key, updated_logs.keys())
            for entry in entries:
                self.assertIn(entry, updated_logs[key])

        for (key, entries) in new_entries.items():
            self.assertIn(key, updated_logs.keys())
            for entry in entries:
                self.assertIn(entry, updated_logs[key])

    def test_error_regex(self):
        logs = ('/foo/bar.xml(3): Error: foobar',
                '/foo/bar.xml(3): ERROR: foobar',
                '/foo/bar.xml: Error: foobar',
                'Error: foobar',)

        for log in logs:
            result = XML2RFC_ERROR_REGEX.search(log)
            self.assertEqual('foobar', result.group('message'))

    def test_warning_regex(self):
        logs = ('/foo/bar.xml(3): Warning: foobar',
                '/foo/bar.xml(3): warning: foobar',
                '/foo/bar.xml: Warning: foobar',
                'warning: foobar',)

        for log in logs:
            result = XML2RFC_WARN_REGEX.search(log)
            self.assertEqual('foobar', result.group('message'))

    def test_line_number_regex(self):
        logs = ('/foo/bar.xml(f00): Warning: foobar',
                '/foo/bar.xml(f00): Error: foobar',
                '(f00): Warning: foobar',)

        for log in logs:
            result = XML2RFC_LINE_NUMBER_REGEX.search(log)
            self.assertEqual('f00', result.group('line'))
