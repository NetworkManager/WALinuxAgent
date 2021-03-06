# Copyright Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Requires Python 2.6+ and Openssl 1.0+
#
from azurelinuxagent.common.utils.processutil import format_stdout_stderr, read_output
from tests.tools import *


class TestProcessUtils(AgentTestCase):
    def setUp(self):
        AgentTestCase.setUp(self)
        self.tmp_dir = tempfile.mkdtemp()
        self.stdout = tempfile.TemporaryFile(dir=self.tmp_dir, mode="w+b")
        self.stderr = tempfile.TemporaryFile(dir=self.tmp_dir, mode="w+b")

        self.stdout.write("The quick brown fox jumps over the lazy dog.".encode("utf-8"))
        self.stderr.write("The five boxing wizards jump quickly.".encode("utf-8"))

    def tearDown(self):
        if self.tmp_dir is not None:
            shutil.rmtree(self.tmp_dir)

    def test_read_output_it_should_return_no_content(self):
        with patch('azurelinuxagent.common.utils.processutil.TELEMETRY_MESSAGE_MAX_LEN', 0):
            expected = "[stdout]\n\n\n[stderr]\n"
            actual = read_output(self.stdout, self.stderr)
            self.assertEqual(expected, actual)

    def test_read_output_it_should_truncate_the_content(self):
        with patch('azurelinuxagent.common.utils.processutil.TELEMETRY_MESSAGE_MAX_LEN', 10):
            expected = "[stdout]\nThe quick \n\n[stderr]\nThe five b"
            actual = read_output(self.stdout, self.stderr)
            self.assertEqual(expected, actual)

    def test_read_output_it_should_return_all_content(self):
        with patch('azurelinuxagent.common.utils.processutil.TELEMETRY_MESSAGE_MAX_LEN', 50):
            expected = "[stdout]\nThe quick brown fox jumps over the lazy dog.\n\n" \
                       "[stderr]\nThe five boxing wizards jump quickly."
            actual = read_output(self.stdout, self.stderr)
            self.assertEqual(expected, actual)

    def test_read_output_it_should_handle_exceptions(self):
        with patch('azurelinuxagent.common.utils.processutil.TELEMETRY_MESSAGE_MAX_LEN', "type error"):
            actual = read_output(self.stdout, self.stderr)
            self.assertIn("Cannot read stdout/stderr", actual)

    def test_format_stdout_stderr00(self):
        """
        If stdout and stderr are both smaller than the max length,
        the full representation should be displayed.
        """
        stdout = "The quick brown fox jumps over the lazy dog."
        stderr = "The five boxing wizards jump quickly."

        expected = "[stdout]\n{0}\n\n[stderr]\n{1}".format(stdout, stderr)
        actual = format_stdout_stderr(stdout, stderr, 1000)
        self.assertEqual(expected, actual)

    def test_format_stdout_stderr01(self):
        """
        If stdout and stderr both exceed the max length,
        then both stdout and stderr are trimmed equally.
        """
        stdout = "The quick brown fox jumps over the lazy dog."
        stderr = "The five boxing wizards jump quickly."

        # noinspection SpellCheckingInspection
        expected = '[stdout]\ns over the lazy dog.\n\n[stderr]\nizards jump quickly.'
        actual = format_stdout_stderr(stdout, stderr, 60)
        self.assertEqual(expected, actual)
        self.assertEqual(60, len(actual))

    def test_format_stdout_stderr02(self):
        """
        If stderr is much larger than stdout, stderr is allowed
        to borrow space from stdout's quota.
        """
        stdout = "empty"
        stderr = "The five boxing wizards jump quickly."

        expected = '[stdout]\nempty\n\n[stderr]\ns jump quickly.'
        actual = format_stdout_stderr(stdout, stderr, 40)
        self.assertEqual(expected, actual)
        self.assertEqual(40, len(actual))

    def test_format_stdout_stderr03(self):
        """
        If stdout is much larger than stderr, stdout is allowed
        to borrow space from stderr's quota.
        """
        stdout = "The quick brown fox jumps over the lazy dog."
        stderr = "empty"

        expected = '[stdout]\nr the lazy dog.\n\n[stderr]\nempty'
        actual = format_stdout_stderr(stdout, stderr, 40)
        self.assertEqual(expected, actual)
        self.assertEqual(40, len(actual))

    def test_format_stdout_stderr04(self):
        """
        If the max length is not sufficient to even hold the stdout
        and stderr markers an empty string is returned.
        """
        stdout = "The quick brown fox jumps over the lazy dog."
        stderr = "The five boxing wizards jump quickly."

        expected = ''
        actual = format_stdout_stderr(stdout, stderr, 4)
        self.assertEqual(expected, actual)
        self.assertEqual(0, len(actual))

    def test_format_stdout_stderr05(self):
        """
        If stdout and stderr are empty, an empty template is returned.
        """

        expected = '[stdout]\n\n\n[stderr]\n'
        actual = format_stdout_stderr('', '', 1000)
        self.assertEqual(expected, actual)
