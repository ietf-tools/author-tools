from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase

import responses

from at.utils.net import (
        get_latest, is_valid_url, is_url, InvalidURL, LatestDraftNotFound)

DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/doc/rfcdiff-latest-json'


class TestUtilsNet(TestCase):
    '''Tests for at.utils.net'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)

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

    def test_get_latest_rfc(self):
        rfc = 'rfc666'
        latest_draft_url = get_latest(rfc, DT_LATEST_DRAFT_URL)
        self.assertTrue(latest_draft_url.startswith('https://'))

    def test_get_latest_id(self):
        draft = 'draft-ietf-quic-http'
        latest_draft_url = get_latest(draft, DT_LATEST_DRAFT_URL)
        self.assertTrue(latest_draft_url.startswith('https://'))

    def test_get_latest_with_original_mismatching(self):
        draft_name = 'draft-ietf-quic-http'
        revision = '23'
        draft = '-'.join([draft_name, revision])
        latest_draft_url = get_latest(draft=draft,
                                      dt_latest_url=DT_LATEST_DRAFT_URL,
                                      original_draft=draft)
        self.assertTrue(latest_draft_url.startswith('https://'))
        self.assertIn(draft_name, latest_draft_url)
        self.assertNotIn(revision, latest_draft_url)
        self.assertNotIn(draft, latest_draft_url)

    def test_get_latest_with_original_matching(self):
        rfc = 'rfc7231'
        previous = 'draft-ietf-httpbis-p2-semantics-26'
        latest_draft_url = get_latest(draft=rfc,
                                      dt_latest_url=DT_LATEST_DRAFT_URL,
                                      original_draft=rfc)
        self.assertTrue(latest_draft_url.startswith('https://'))
        self.assertIn(previous, latest_draft_url)

    def test_invalid_urls(self):
        allowed_domains = ['example.com', ]
        urls = [
                'ftp://example.com/',
                'file://example.com/',
                'example.com',
                '/etc/passwd',
                '../requirements.txt',
                'https://127.0.0.1',
                'https://127.0.0.1:80',
                'https://example.com:80',
                'https://example.com[/',
                'https://example.org']

        for url in urls:
            with self.assertRaises(InvalidURL):
                is_valid_url(url, allowed_domains=allowed_domains)

    def test_valid_url(self):
        allowed_domains = ['example.com', ]
        urls = [
                'http://example.com/',
                'https://example.com/',
                'https://example.com/example.xml',
                'https://example.com/example/example.xml',
                'http://www.example.com/',
                'https://www.example.com/',
                'https://www.example.com/example.xml',
                'https://www.example.com/example/example.xml']

        for url in urls:
            self.assertTrue(is_valid_url(url, allowed_domains=allowed_domains))

    def test_is_url_true(self):
        strings = [
                'http://example.com/',
                'https://example.com/',
                'https://example.com/example.xml',
                'https://example.com/example/example.xml',
                'http://www.example.com/',
                'https://www.example.com/',
                'https://www.example.com/example.xml',
                'https://www.example.com/example/example.xml']

        for string in strings:
            self.assertTrue(is_url(string))

    def test_is_urls_false(self):
        strings = [
                'example.com',
                '/etc/passwd',
                '../requirements.txt',
                'rfc9000',
                'draft-ietf-httpbis-p2-semantics-26']

        for string in strings:
            self.assertFalse(is_url(string))
