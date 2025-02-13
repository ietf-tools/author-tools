from unittest import TestCase

from at.utils.runner import proc_run, RunnerError


class TestUtilsRunner(TestCase):
    """Tests for at.utils.runner"""

    def test_proc_run_no_timeout(self):
        output = proc_run(args=["echo", "foobar"], timeout=100)
        output.check_returncode()
        self.assertEqual(output.stdout.decode("utf-8").strip(), "foobar")

    def test_proc_run_timeout(self):
        with self.assertRaises(RunnerError):
            output = proc_run(args=["sleep", "100"], timeout=1)
            output.check_returncode()
