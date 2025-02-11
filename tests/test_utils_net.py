from logging import disable as set_logger, INFO, CRITICAL
from unittest import TestCase

import responses

from at.utils.net import (
    get_both,
    get_latest,
    get_previous,
    is_valid_url,
    is_url,
    InvalidURL,
    DocumentNotFound,
)

DT_LATEST_DRAFT_URL = "https://datatracker.ietf.org/api/rfcdiff-latest-json"


class TestUtilsNet(TestCase):
    """Tests for at.utils.net"""

    def setUp(self):
        # susspress logging messages
        set_logger(CRITICAL)

    def tearDown(self):
        # set logging to INFO
        set_logger(INFO)

    def test_get_latest_not_found_error(self):
        with self.assertRaises(DocumentNotFound) as error:
            get_latest("foobar-foobar", DT_LATEST_DRAFT_URL)

        self.assertEqual(
            str(error.exception), "Can not find the latest document on datatracker"
        )

    @responses.activate
    def test_get_latest_no_content_url_error(self):
        rfc = "rfc666"
        responses.add(
            responses.GET, "/".join([DT_LATEST_DRAFT_URL, rfc]), json={}, status=200
        )
        with self.assertRaises(DocumentNotFound) as error:
            get_latest(rfc, DT_LATEST_DRAFT_URL)

        self.assertEqual(
            str(error.exception),
            "Can not find url for the latest document on datatracker",
        )

    def test_get_latest_rfc(self):
        rfc = "rfc666"
        latest_draft_url = get_latest(rfc, DT_LATEST_DRAFT_URL)
        self.assertTrue(latest_draft_url.startswith("https://"))

    def test_get_latest_id(self):
        draft = "draft-ietf-quic-http"
        latest_draft_url = get_latest(draft, DT_LATEST_DRAFT_URL)
        self.assertTrue(latest_draft_url.startswith("https://"))

    def test_invalid_urls(self):
        allowed_domains = [
            "example.com",
        ]
        urls = [
            "ftp://example.com/",
            "file://example.com/",
            "example.com",
            "/etc/passwd",
            "../requirements.txt",
            "https://127.0.0.1",
            "https://127.0.0.1:80",
            "https://example.com:80",
            "https://example.com[/",
            "https://example.org",
        ]

        for url in urls:
            with self.assertRaises(InvalidURL):
                is_valid_url(url, allowed_domains=allowed_domains)

    def test_valid_url(self):
        allowed_domains = [
            "example.com",
        ]
        urls = [
            "http://example.com/",
            "https://example.com/",
            "https://example.com/example.xml",
            "https://example.com/example/example.xml",
            "http://www.example.com/",
            "https://www.example.com/",
            "https://www.example.com/example.xml",
            "https://www.example.com/example/example.xml",
        ]

        for url in urls:
            self.assertTrue(is_valid_url(url, allowed_domains=allowed_domains))

    def test_is_url_true(self):
        strings = [
            "http://example.com/",
            "https://example.com/",
            "https://example.com/example.xml",
            "https://example.com/example/example.xml",
            "http://www.example.com/",
            "https://www.example.com/",
            "https://www.example.com/example.xml",
            "https://www.example.com/example/example.xml",
        ]

        for string in strings:
            self.assertTrue(is_url(string))

    def test_is_urls_false(self):
        strings = [
            "http://example.com[/",
            "example.com",
            "/etc/passwd",
            "../requirements.txt",
            "rfc9000",
            "draft-ietf-httpbis-p2-semantics-26",
        ]

        for string in strings:
            self.assertFalse(is_url(string))

    def test_get_previous_for_rfc(self):
        rfc = "rfc7749"
        previous = "draft-iab-xml2rfcv2-02"
        previous_doc_url = get_previous(rfc, DT_LATEST_DRAFT_URL)
        self.assertTrue(previous_doc_url.startswith("https://"))
        self.assertIn(previous, previous_doc_url)

    def test_get_previous_for_id(self):
        draft = "draft-ietf-sipcore-multiple-reasons-00"
        previous = "draft-sparks-sipcore-multiple-reasons-00"
        previous_doc_url = get_previous(draft, DT_LATEST_DRAFT_URL)
        self.assertTrue(previous_doc_url.startswith("https://"))
        self.assertIn(previous, previous_doc_url)

    def test_get_previous_not_found_error(self):
        with self.assertRaises(DocumentNotFound) as error:
            get_previous("foobar-foobar", DT_LATEST_DRAFT_URL)

        self.assertEqual(
            str(error.exception), "Can not find the previous document on datatracker"
        )

    @responses.activate
    def test_get_previous_no_content_url_error(self):
        rfc = "rfc666"
        responses.add(
            responses.GET, "/".join([DT_LATEST_DRAFT_URL, rfc]), json={}, status=200
        )
        with self.assertRaises(DocumentNotFound) as error:
            get_previous(rfc, DT_LATEST_DRAFT_URL)

        self.assertEqual(
            str(error.exception),
            "Can not find url for the previous document on datatracker",
        )

    def test_get_both_for_rfc(self):
        rfc = "rfc7749"
        previous = "draft-iab-xml2rfcv2-02"
        previous_doc_url, latest_doc_url = get_both(rfc, DT_LATEST_DRAFT_URL)
        self.assertTrue(previous_doc_url.startswith("https://"))
        self.assertIn(previous, previous_doc_url)
        self.assertTrue(latest_doc_url.startswith("https://"))
        self.assertIn(rfc, latest_doc_url)

    def test_get_both_for_id(self):
        draft = "draft-ietf-sipcore-multiple-reasons-00"
        previous = "draft-sparks-sipcore-multiple-reasons-00"
        previous_doc_url, latest_doc_url = get_both(draft, DT_LATEST_DRAFT_URL)
        self.assertTrue(previous_doc_url.startswith("https://"))
        self.assertIn(previous, previous_doc_url)
        self.assertTrue(latest_doc_url.startswith("https://"))
        self.assertIn(draft, latest_doc_url)

    def test_get_both_latest_not_found_error(self):
        with self.assertRaises(DocumentNotFound) as error:
            get_both("foobar-foobar", DT_LATEST_DRAFT_URL)

        self.assertEqual(
            str(error.exception), "Can not find the latest document on datatracker"
        )

    def test_get_both_previous_not_found_error(self):
        draft = "draft-reschke-xml2rfc-00"
        with self.assertRaises(DocumentNotFound) as error:
            get_both(draft, DT_LATEST_DRAFT_URL)

        self.assertEqual(
            str(error.exception),
            "Can not find url for previous document on datatracker",
        )

    @responses.activate
    def test_get_both_no_content_url_error(self):
        rfc = "rfc666"
        responses.add(
            responses.GET, "/".join([DT_LATEST_DRAFT_URL, rfc]), json={}, status=200
        )
        with self.assertRaises(DocumentNotFound) as error:
            get_both(rfc, DT_LATEST_DRAFT_URL)

        self.assertEqual(
            str(error.exception),
            "Can not find url for the latest document on datatracker",
        )
