from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from subprocess import CompletedProcess
from unittest import TestCase

from werkzeug.datastructures import FileStorage

from at.utils.validation import (
        convert_v2v3, get_non_ascii_chars, idnits, idnits3, svgcheck,
        validate_draft, validate_xml, xml2rfc_validation)

TEST_DATA_DIR = './tests/data/'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_XML_INVALID = 'draft-smoke-signals-00.invalid.xml'
TEST_XML_V2_DRAFT = 'draft-smoke-signals-00.v2.xml'
TEST_TEXT_DRAFT = 'draft-smoke-signals-00.txt'
TEST_SVG = 'ietf.svg'
TEST_DATA = [TEST_XML_DRAFT, TEST_XML_INVALID, TEST_XML_V2_DRAFT, TEST_SVG]
TEMPORARY_DATA_DIR = './tests/tmp/'


class TestUtilsValidation(TestCase):
    '''Tests for at.utils.validation'''

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

    def test_validate_xml_valid_xml(self):
        log = validate_xml(''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertIn('errors', log.keys())
        self.assertIn('warnings', log.keys())
        self.assertIn('idnits', log.keys())
        self.assertIn('bare_unicode', log.keys())
        self.assertEqual(len(log['errors']), 0)
        self.assertGreater(len(log['idnits']), 0)
        self.assertGreaterEqual(len(log['warnings']), 0)
        self.assertGreaterEqual(len(log['bare_unicode']), 0)

    def test_validate_xml_invalid_xml(self):
        log = validate_xml(''.join([TEMPORARY_DATA_DIR, TEST_XML_INVALID]))

        self.assertIn('errors', log.keys())
        self.assertIn('warnings', log.keys())
        self.assertIn('idnits', log.keys())
        self.assertIn('bare_unicode', log.keys())
        self.assertGreater(len(log['errors']), 0)
        self.assertGreater(len(log['idnits']), 0)
        self.assertGreater(len(log['idnits']), 0)

    def test_xml2rfc_validation(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))

        self.assertTrue(Path(text_file).exists())
        self.assertIsInstance(output, CompletedProcess)

    def test_convert_v2v3(self):
        saved_file, output = convert_v2v3(
                ''.join([TEMPORARY_DATA_DIR, TEST_XML_V2_DRAFT]))

        self.assertTrue(Path(saved_file).exists())
        self.assertEqual(Path(saved_file).suffix, '.xml')
        self.assertIsInstance(output, CompletedProcess)

    def test_idnits(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file)

        self.assertIsNotNone(idnits_log)
        self.assertGreater(len(idnits_log), 0)
        self.assertNotIn('The copyright year in the IETF', idnits_log)
        self.assertNotIn('draft documents valid for a maximum of six months',
                         idnits_log)
        self.assertNotIn('Running in submission checking mode', idnits_log)

    def test_idnits_non_verbose(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file)

        self.assertIsNotNone(idnits_log)
        self.assertGreater(len(idnits_log), 0)
        self.assertIn('Run idnits with the --verbose', idnits_log)
        self.assertNotIn('-->', idnits_log)

    def test_idnits_verbose(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file, verbose='1')

        self.assertIsNotNone(idnits_log)
        self.assertGreater(len(idnits_log), 0)
        self.assertNotIn('Run idnits with the --verbose', idnits_log)
        self.assertNotIn('-->', idnits_log)

    def test_idnits_very_verbose(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file, verbose='2')

        self.assertIsNotNone(idnits_log)
        self.assertGreater(len(idnits_log), 0)
        self.assertNotIn('Run idnits with the --verbose', idnits_log)
        self.assertIn('-->', idnits_log)

    def test_idnits_show_text(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file, show_text=True)

        self.assertIsNotNone(idnits_log)
        self.assertGreater(len(idnits_log), 0)
        self.assertIn('draft documents valid for a maximum of six months',
                      idnits_log)

    def test_idnits_year(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file, year=2000)

        self.assertIsNotNone(idnits_log)
        self.assertGreater(len(idnits_log), 0)
        self.assertIn('The copyright year in the IETF', idnits_log)

    def test_idnits_submit_check(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file, submit_check=True)

        self.assertIsNotNone(idnits_log)
        self.assertGreater(len(idnits_log), 0)
        self.assertIn('Running in submission checking mode', idnits_log)

    def test_idnits_no_internal_paths(self):
        output, text_file = xml2rfc_validation(
                                ''.join([TEMPORARY_DATA_DIR, TEST_XML_DRAFT]))
        idnits_log = idnits(text_file, verbose='2')

        self.assertNotIn(TEMPORARY_DATA_DIR, idnits_log)

    def test_svgcheck_error(self):
        svg, logs, errors = svgcheck('foobar.svg')

        self.assertIsNone(svg)
        self.assertIsNone(logs)
        self.assertIn('No such file', errors)

    def test_svgcheck(self):
        svg, logs, errors = svgcheck(''.join((TEMPORARY_DATA_DIR, TEST_SVG)))

        self.assertIn('</svg>', svg)
        self.assertIn('File conforms to SVG requirements.', logs)
        self.assertIsNone(errors)

    def test_validate_draft(self):
        with open(''.join([TEST_DATA_DIR, TEST_XML_DRAFT]), 'rb') as file:
            file_object = FileStorage(file, filename=TEST_XML_DRAFT)
            log = validate_draft(file_object, TEMPORARY_DATA_DIR)

            self.assertIn('errors', log.keys())
            self.assertIn('warnings', log.keys())
            self.assertIn('idnits', log.keys())
            self.assertIn('bare_unicode', log.keys())
            self.assertIn('non_ascii', log.keys())
            self.assertEqual(len(log['errors']), 0)
            self.assertGreater(len(log['idnits']), 0)
            self.assertGreaterEqual(len(log['warnings']), 0)
            self.assertGreaterEqual(len(log['bare_unicode']), 0)
            self.assertGreaterEqual(len(log['non_ascii']), 0)

    def test_validate_draft_text(self):
        with open(''.join([TEST_DATA_DIR, TEST_TEXT_DRAFT]), 'rb') as file:
            file_object = FileStorage(file, filename=TEST_TEXT_DRAFT)
            log = validate_draft(file_object, TEMPORARY_DATA_DIR)

            self.assertNotIn('errors', log.keys())
            self.assertNotIn('warnings', log.keys())
            self.assertIn('idnits', log.keys())
            self.assertIn('non_ascii', log.keys())
            self.assertGreater(len(log['idnits']), 0)
            self.assertGreaterEqual(len(log['non_ascii']), 0)

    def test_get_non_ascii_chars(self):
        log = get_non_ascii_chars(''.join([TEMPORARY_DATA_DIR,
                                           TEST_XML_DRAFT]))

        self.assertIn('Sinhala', log)

    def test_idnits3(self):
        for draft in TEST_DATA:
            file = ''.join([TEMPORARY_DATA_DIR, draft])
            idnits_log = idnits3(file)
            self.assertIsNotNone(idnits_log)
            self.assertGreater(len(idnits_log), 0)

    def test_idnits3_year(self):
        for draft in TEST_DATA:
            file = ''.join([TEMPORARY_DATA_DIR, draft])
            idnits_log = idnits3(file, year=2023)
            self.assertIsNotNone(idnits_log)
            self.assertGreater(len(idnits_log), 0)

    def test_idnits3_submit_check(self):
        for draft in TEST_DATA:
            file = ''.join([TEMPORARY_DATA_DIR, draft])
            idnits_log = idnits3(file, submit_check=True)
            self.assertIsNotNone(idnits_log)
            self.assertGreater(len(idnits_log), 0)
