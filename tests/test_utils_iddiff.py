from logging import disable as set_logger, INFO, CRITICAL
from pathlib import Path
from shutil import copy, rmtree
from unittest import TestCase

import responses
from werkzeug.datastructures import FileStorage

from at.utils.iddiff import (
        get_id_diff, get_latest, get_text_id, get_text_id_from_file,
        get_text_id_from_url, is_valid_url, IddiffError, InvalidURL,
        LatestDraftNotFound)

TEST_DATA_DIR = './tests/data/'
DRAFT_A = 'draft-smoke-signals-00.txt'
DRAFT_B = 'draft-smoke-signals-01.txt'
TEST_XML_DRAFT = 'draft-smoke-signals-00.xml'
TEST_XML_V2_DRAFT = 'draft-smoke-signals-00.v2.xml'
TEST_KRAMDOWN_DRAFT = 'draft-smoke-signals-00.md'
TEST_MMARK_DRAFT = 'draft-smoke-signals-00.mmark.md'
TEST_XML_ERROR = 'draft-smoke-signals-00.error.xml'
TEST_DATA = [
        TEST_XML_DRAFT, TEST_XML_V2_DRAFT, DRAFT_A, DRAFT_B,
        TEST_KRAMDOWN_DRAFT, TEST_MMARK_DRAFT]
TEMPORARY_DATA_DIR = './tests/tmp/'
DT_LATEST_DRAFT_URL = 'https://datatracker.ietf.org/doc/rfcdiff-latest-json'


class TestUtilsIddiff(TestCase):
    '''Tests for at.utils.iddiff'''

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)
        # create temporary data dir
        Path(TEMPORARY_DATA_DIR).mkdir(exist_ok=True)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)
        # remove temporary data dir
        rmtree(TEMPORARY_DATA_DIR, ignore_errors=True)

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
        self.assertNotIn(previous, rfc)

    def test_get_text_id(self):
        for filename in TEST_DATA:
            original = ''.join([TEST_DATA_DIR, filename])
            new = ''.join([TEMPORARY_DATA_DIR, filename])
            copy(original, new)
            (dir_path, file_path) = get_text_id(TEMPORARY_DATA_DIR, new)
            self.assertTrue(Path(dir_path).exists())
            self.assertTrue(Path(file_path).exists())
            self.assertEqual(Path(file_path).suffix, '.txt')

    def test_get_text_id_error(self):
        filename = TEST_XML_ERROR
        original = ''.join([TEST_DATA_DIR, filename])
        new = ''.join([TEMPORARY_DATA_DIR, filename])
        copy(original, new)

        with self.assertRaises(IddiffError):
            get_text_id(TEMPORARY_DATA_DIR, new)

    def test_get_text_id_from_file(self):
        for filename in TEST_DATA:
            with open(''.join([TEST_DATA_DIR, filename]), 'rb') as file:
                file_object = FileStorage(file, filename=filename)
                (dir_path, file_path) = get_text_id_from_file(
                                            file_object, TEMPORARY_DATA_DIR)
                self.assertTrue(Path(dir_path).exists())
                self.assertTrue(Path(file_path).exists())
                self.assertEqual(Path(file_path).suffix, '.txt')

    def test_get_text_id_from_file_error(self):
        filename = TEST_XML_ERROR
        with open(''.join([TEST_DATA_DIR, filename]), 'rb') as file:
            file_object = FileStorage(file, filename=filename)
            with self.assertRaises(IddiffError):
                get_text_id_from_file(file_object, TEMPORARY_DATA_DIR)

    def test_get_text_id_from_url(self):
        url = 'https://www.ietf.org/archive/id/draft-iab-xml2rfcv2-01.xml'
        (dir_path, file_path) = get_text_id_from_url(url, TEMPORARY_DATA_DIR)
        self.assertTrue(Path(dir_path).exists())
        self.assertTrue(Path(file_path).exists())
        self.assertEqual(Path(file_path).suffix, '.txt')

    def test_get_text_id_from_url_error(self):
        url = 'https://author-tools.ietf.org/sitemap.xml'
        with self.assertRaises(IddiffError):
            get_text_id_from_url(url, TEMPORARY_DATA_DIR)

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
