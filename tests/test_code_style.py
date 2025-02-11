import unittest
import pycodestyle


class TestCodeStyle(unittest.TestCase):
    """Check if all python files follow PEP8 style guide."""

    def test_pep8_conformance(self):
        """Test if files follow PEP8 style guide."""

        paths = ["./at", "./tests/"]

        styleguide = pycodestyle.StyleGuide()
        self.assertEqual(styleguide.check_files(paths).total_errors, 0)
