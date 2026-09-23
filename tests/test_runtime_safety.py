import io
import unittest
from contextlib import redirect_stdout

from runtime_safety import log_failure, public_error_message

class RuntimeSafetyTests(unittest.TestCase):
    def test_messages_and_logs_are_safe(self):
        error = RuntimeError("429 daily quota exhausted person@example.com secret-key")
        self.assertIn("quota", public_error_message(error, "English", "the request").lower())
        self.assertIn("cuota", public_error_message(error, "Español", "la solicitud").lower())
        self.assertIn("unavailable", public_error_message(TimeoutError(), "English", "the request").lower())
        output = io.StringIO()
        with redirect_stdout(output):
            log_failure("demo.failure", error)
        self.assertIn("RuntimeError", output.getvalue())
        self.assertNotIn("person@example.com", output.getvalue())
        self.assertNotIn("secret-key", output.getvalue())
