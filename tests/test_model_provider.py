import unittest

from stock_picker.model_provider import is_repetitive_response, rate_limit_retry_delay


class RepetitiveResponseTests(unittest.TestCase):
    def test_rejects_degenerate_repetition(self):
        result = '"Sunrun". Also "SunPower". ' * 80
        self.assertTrue(is_repetitive_response(result))

    def test_accepts_normal_report(self):
        result = " ".join(f"word{index}" for index in range(150))
        self.assertFalse(is_repetitive_response(result))

    def test_does_not_retry_programming_errors(self):
        self.assertIsNone(rate_limit_retry_delay(TypeError("bad response")))

    def test_uses_provider_requested_rate_limit_delay(self):
        RateLimitError = type("RateLimitError", (Exception,), {})
        delay = rate_limit_retry_delay(RateLimitError("Please try again in 3.5s"))
        self.assertEqual(delay, 4.0)

    def test_skips_daily_quota_retry(self):
        RateLimitError = type("RateLimitError", (Exception,), {})
        error = RateLimitError("GenerateRequestsPerDayPerProjectPerModel-FreeTier")
        self.assertIsNone(rate_limit_retry_delay(error))

    def test_skips_long_rate_limit_wait(self):
        RateLimitError = type("RateLimitError", (Exception,), {})
        self.assertIsNone(rate_limit_retry_delay(RateLimitError("Please try again in 18s")))


if __name__ == "__main__":
    unittest.main()
