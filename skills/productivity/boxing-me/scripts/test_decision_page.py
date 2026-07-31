#!/usr/bin/env python3
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import decision_page


SPEC = {
    "id": "test-page",
    "title": "Test decisions",
    "context": "Test context",
    "questions": [
        {
            "id": "mode",
            "prompt": "Choose a mode",
            "why": "It changes behavior.",
            "type": "single",
            "required": True,
            "options": [
                {"id": "safe", "label": "Safe", "details": "Stable default.", "recommended": True, "recommendation_reason": "Lowest risk."},
                {"id": "fast", "label": "Fast", "details": "Faster with tradeoffs."},
            ],
        }
    ],
}


class DecisionPageTests(unittest.TestCase):
    def test_validation_and_safe_embedding(self):
        spec = {**SPEC, "context": "</script><script>alert(1)</script>"}
        decision_page.validate_spec(spec)
        page = decision_page.render_html(spec)
        self.assertNotIn("</script><script>alert(1)</script>", page)
        self.assertIn("\\u003c/script>", page)
        self.assertIn("Apply recommendations", page)

        node = shutil.which("node")
        if node:
            script = page.split("<script>", 1)[1].split("</script>", 1)[0]
            result = subprocess.run(
                [node, "--check", "-"], input=script, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_duplicate_and_multiple_recommendations(self):
        spec = json.loads(json.dumps(SPEC))
        spec["questions"][0]["options"][1]["id"] = "safe"
        spec["questions"][0]["options"][1]["recommended"] = True
        spec["questions"][0]["options"][1]["recommendation_reason"] = "Also good"
        with self.assertRaisesRegex(ValueError, "duplicated"):
            decision_page.validate_spec(spec)

    def test_server_serves_and_saves_matching_response(self):
        with tempfile.TemporaryDirectory() as directory:
            response_path = Path(directory) / "response.json"
            server = decision_page.ThreadingHTTPServer(("127.0.0.1", 0), decision_page.make_handler(b"<p>ok</p>", response_path, SPEC["id"]))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                self.assertEqual(urllib.request.urlopen(base + "/").read(), b"<p>ok</p>")
                payload = {"spec_id": SPEC["id"], "answers": [], "saved_at": "now"}
                request = urllib.request.Request(base + "/api/save", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
                result = json.loads(urllib.request.urlopen(request).read())
                self.assertTrue(result["saved"])
                saved = json.loads(response_path.read_text())
                self.assertEqual(saved["spec_id"], SPEC["id"])
                self.assertIn("received_at", saved)

                bad_request = urllib.request.Request(
                    base + "/api/save",
                    data=json.dumps({"spec_id": "another-page", "answers": []}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(bad_request)
                self.assertEqual(caught.exception.code, 400)
                caught.exception.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
