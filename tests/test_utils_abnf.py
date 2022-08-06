from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase

from at.utils.abnf import extract_abnf

TEST_DATA_DIR = './tests/data/'
RFC = 'rfc8855.txt'
DRAFT = 'draft-smoke-signals-00.txt'


class TestUtilsAbnf(TestCase):
    '''Tests for at.utils.abnf'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)

    def test_extract_abnf(self):
        result = extract_abnf(''.join([TEST_DATA_DIR, RFC]))

        self.assertIn('FLOOR-REQUEST-STATUS', result)

    def test_extract_abnf_empty(self):
        result = extract_abnf(''.join([TEST_DATA_DIR, DRAFT]))

        self.assertEqual(result, 'No output from BAP aex.')

    def test_extract_abnf_error(self):
        result = extract_abnf('foobar')

        self.assertIn("Can't open", result)
