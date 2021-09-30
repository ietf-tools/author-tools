from unittest import TestCase

from at.utils.version import (
        get_id2xml_version, get_goat_version, get_mmark_version,
        get_kramdown_rfc2629_version, get_weasyprint_version,
        get_xml2rfc_version)


class TestUtilsVersion(TestCase):
    '''Tests for at.utils.version'''

    def test_get_kramdown_rfc2629_version(self):
        result = get_kramdown_rfc2629_version()

        self.assertIsNotNone(result)
        self.assertIn('.', result)

    def test_get_id2xml_version(self):
        result = get_id2xml_version()

        self.assertIsNotNone(result)
        self.assertIn('.', result)

    def test_get_xml2rfc_version(self):
        result = get_xml2rfc_version()

        self.assertIsNotNone(result)
        self.assertIn('.', result)

    def test_get_mmark_version(self):
        result = get_mmark_version()

        self.assertIsNotNone(result)
        self.assertIn('.', result)

    def test_get_weasyprint_version(self):
        result = get_weasyprint_version()

        self.assertIsNotNone(result)
        self.assertIn('.', result)

    def test_get_goat_version(self):
        result = get_goat_version()

        self.assertIsNotNone(result)
        self.assertIn('.', result)
