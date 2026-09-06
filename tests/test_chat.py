"""Regression tests against the real Gradio serialization boundary; no API calls."""
import os
import unittest
from unittest.mock import patch

import gradio as gr

# Do not read a developer's .env or enable provider telemetry in tests.
with patch("dotenv.load_dotenv", return_value=False), patch.dict(
    os.environ, {"CREWAI_TRACING_ENABLED": "false", "OTEL_SDK_DISABLED": "true"}
):
    import app


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.chatbot = gr.Chatbot()

    def round_trip(self, history):
        return self.chatbot.preprocess(self.chatbot.postprocess(history))

    def test_user_and_status_render_before_backend(self):
        with patch.object(app, "analyze_sector") as backend:
            _, history, _ = app.submit_english("  Example  ", [])
        backend.assert_not_called()
        history = self.round_trip(history)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"][0]["text"], "Example")
        self.assertTrue(history[1]["content"][0]["text"])

    def test_bilingual_repeated_turns_survive_gradio_serialization(self):
        for language, submit, finish in [
            ("English", app.submit_english, app.finish_english),
            ("Español", app.submit_spanish, app.finish_spanish),
        ]:
            history = []
            with patch.object(app, "analyze_sector", return_value="Final report") as backend:
                for turn in range(2):
                    original = list(history)
                    _, pending, _ = submit("Example", history)
                    self.assertEqual(history, original)
                    _, history, _ = finish(self.round_trip(pending))
                    backend.assert_called_with("Example", original, language)
                    history = self.round_trip(history)
                    self.assertEqual(len(history), 2 * (turn + 1))
                    self.assertEqual(history[-1]["content"][0]["text"], "Final report")

    def test_blank_input_does_not_start_backend(self):
        with patch.object(app, "analyze_sector") as backend:
            with self.assertRaises(gr.Error):
                app.submit_english("   ", [])
        backend.assert_not_called()

    def test_backend_failure_replaces_status_and_restores_input(self):
        _, pending, _ = app.submit_english("Example", [])
        with patch.object(app, "fallback_llm", return_value=object()), patch.object(
            app, "StockPicker", side_effect=RuntimeError("simulated provider outage")
        ):
            textbox, history, button = app.finish_english(self.round_trip(pending))
        self.assertTrue(textbox.interactive)
        self.assertTrue(button.interactive)
        self.assertEqual(history[-1]["content"], app.UI_TEXT["English"]["error"])


if __name__ == "__main__":
    unittest.main()
