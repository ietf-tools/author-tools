from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase

import responses

from at.utils.iddiff import (
        get_id_diff, get_latest, IddiffError, LatestDraftNotFound)

TEST_DATA_DIR = './tests/data/'
DRAFT_A = 'draft-smoke-signals-00.txt'
DRAFT_B = 'draft-smoke-signals-01.txt'
DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/doc/rfcdiff-latest-json'


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

    def test_get_latest_not_found_error(self):
        with self.assertRaises(LatestDraftNotFound) as error:
            get_latest('foobar-foobar', DT_LATEST_DRAFT_URL)

        self.assertEqual(str(error.exception),
                         'Can not find the latest draft on datatracker')

    @responses.activate
    def test_get_latest_no_content_url_error(self):
        rfc = 'rfc666'
        responses.add(
                responses.GET,
                '/'.join([DT_LATEST_DRAFT_URL, rfc]),
                json={},
                status=200)
        with self.assertRaises(LatestDraftNotFound) as error:
            get_latest(rfc, DT_LATEST_DRAFT_URL)

        self.assertEqual(
                    str(error.exception),
                    'Can not find url for the latest draft on datatracker')

    def test_get_latest(self):
        rfc = 'rfc666'
        latest_draft_url = get_latest(rfc, DT_LATEST_DRAFT_URL)
        self.assertTrue(latest_draft_url.startswith('https://'))
