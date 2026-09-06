import unittest
from pathlib import Path
from unittest.mock import patch

from gradio.state_holder import SessionState
import gradio as gr
import app


class DownloadFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_submission_to_download_through_real_gradio_state(self):
        demo = app.demo
        state = SessionState(demo)
        ids = {name: next(i for i, fn in demo.fns.items() if fn.fn and fn.fn.__name__ == name)
               for name in ["prepare", "complete", "download"]}
        prepared = await demo.process_api(ids["prepare"], ["Example", []], state=state)
        with patch.object(app, "analyze_sector", return_value="# Report\n\nFinal result"):
            completed = await demo.process_api(ids["complete"], [prepared["data"][1]], state=state)
        for extension in ["md", "docx", "pdf"]:
            result = await demo.process_api(ids["download"], [None, extension], state=state)
            file = Path(result["data"][0]["value"]["path"])
            self.assertTrue(file.is_file())
            self.assertEqual(file.suffix, "." + extension)
        # Another browser session cannot retrieve this session's report.
        with self.assertRaises(gr.Error):
            await demo.process_api(ids["download"], [None, "md"], state=SessionState(demo))
        # A new query immediately invalidates the old export state.
        await demo.process_api(ids["prepare"], ["Next", completed["data"][1]], state=state)
        with self.assertRaises(gr.Error):
            await demo.process_api(ids["download"], [None, "md"], state=state)
