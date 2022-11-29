from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase

from at.utils.iddiff import get_id_diff, IddiffError

TEST_DATA_DIR = './tests/data/'
DRAFT_A = 'draft-smoke-signals-00.txt'
DRAFT_B = 'draft-smoke-signals-01.txt'


class TestUtilsIddiff(TestCase):
    '''Tests for at.utils.iddiff'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)

    def test_get_id_diff_error(self):
        with self.assertRaises(IddiffError):
            get_id_diff('', '')

    def test_get_id_diff(self):
        id_diff = get_id_diff(''.join([TEST_DATA_DIR, DRAFT_A]),
                              ''.join([TEST_DATA_DIR, DRAFT_B]))

        self.assertIn('<html lang="en">', id_diff)
        self.assertIn(DRAFT_A, id_diff)
        self.assertIn(DRAFT_B, id_diff)

    def test_get_id_diff_with_table_only(self):
        id_diff = get_id_diff(''.join([TEST_DATA_DIR, DRAFT_A]),
                              ''.join([TEST_DATA_DIR, DRAFT_B]),
                              table=True)

        self.assertNotIn('<html lang="en">', id_diff)
        self.assertIn('<table', id_diff)
        self.assertIn('</table>', id_diff)
        self.assertIn(DRAFT_A, id_diff)
        self.assertIn(DRAFT_B, id_diff)

    def test_get_wdiff(self):
        id_diff = get_id_diff(''.join([TEST_DATA_DIR, DRAFT_A]),
                              ''.join([TEST_DATA_DIR, DRAFT_B]),
                              wdiff=True)

        self.assertIn('<html lang="en">', id_diff)
        self.assertIn('<pre>', id_diff)
        self.assertIn('</pre>', id_diff)

    def test_get_chbars(self):
        id_diff = get_id_diff(''.join([TEST_DATA_DIR, DRAFT_A]),
                              ''.join([TEST_DATA_DIR, DRAFT_B]),
                              chbars=True)

        self.assertIn('|Expires:', id_diff)

    def test_get_abdiff(self):
        id_diff = get_id_diff(''.join([TEST_DATA_DIR, DRAFT_A]),
                              ''.join([TEST_DATA_DIR, DRAFT_B]),
                              abdiff=True)

        self.assertIn('OLD:', id_diff)
        self.assertIn('NEW:', id_diff)
