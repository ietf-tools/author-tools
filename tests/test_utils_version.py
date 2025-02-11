from unittest import TestCase

from docker.version import (
    get_aasvg_version,
    get_idnits_version,
    get_idnits3_version,
    get_id2xml_version,
    get_iddiff_version,
    get_mmark_version,
    get_kramdown_rfc_version,
    get_rfcdiff_version,
    get_svgcheck_version,
    get_weasyprint_version,
    get_xml2rfc_version,
)


class TestUtilsVersion(TestCase):
    """Tests for at.utils.version"""

    def test_get_kramdown_rfc_version(self):
        result = get_kramdown_rfc_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_id2xml_version(self):
        result = get_id2xml_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_xml2rfc_version(self):
        result = get_xml2rfc_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_mmark_version(self):
        result = get_mmark_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_weasyprint_version(self):
        result = get_weasyprint_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_idnits_version(self):
        result = get_idnits_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_idnits3_version(self):
        result = get_idnits3_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_aasvg_version(self):
        result = get_aasvg_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_iddiff_version(self):
        result = get_iddiff_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_svgcheck_version(self):
        result = get_svgcheck_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)

    def test_get_rfcdiff_version(self):
        result = get_rfcdiff_version()

        self.assertIsNotNone(result)
        self.assertIn(".", result)
