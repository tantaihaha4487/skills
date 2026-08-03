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

COMPACT_SPEC = {
    "i": "compact-page",
    "l": "en",
    "t": "Compact decisions",
    "c": "Keep every visible detail.",
    "q": [
        {
            "i": "mode", "p": "Choose a mode", "w": "It changes behavior.",
            "t": "s", "r": True,
            "o": [
                ["safe", "Safe", "Stable default.", "Lowest risk."],
                ["fast", "Fast", "Faster with tradeoffs."],
            ],
        },
        {
            "i": "speed", "p": "Choose a speed", "w": "Only fast mode needs it.",
            "t": "m", "n": 1, "m": 2, "if": ["mode", "fast"],
            "o": [
                ["quick", "Quick", "Short feedback loop."],
                ["instant", "Instant", "Higher resource cost."],
            ],
        },
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
        self.assertIn('font:200 16px/1.55 "Noto Sans","Noto Sans Thai"', page)
        self.assertIn('id="addQuestion"', page)
        self.assertIn("custom_questions:state.custom", page)

        node = shutil.which("node")
        if node:
            script = page.split("<script>", 1)[1].split("</script>", 1)[0]
            result = subprocess.run(
                [node, "--check", "-"], input=script, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_compact_normalization_preserves_detail(self):
        spec = decision_page.normalize_spec(COMPACT_SPEC)
        decision_page.validate_spec(spec)
        self.assertEqual(spec["id"], "compact-page")
        self.assertEqual(spec["questions"][0]["type"], "single")
        self.assertEqual(spec["questions"][0]["options"][0]["details"], "Stable default.")
        self.assertTrue(spec["questions"][0]["options"][0]["recommended"])
        self.assertEqual(spec["questions"][1]["when"], ["mode", "fast"])

    def test_compact_example_reduces_formatted_authoring_size(self):
        path = Path(__file__).parents[1] / "references" / "example-website.json"
        compact = json.loads(path.read_text(encoding="utf-8"))
        verbose = decision_page.normalize_spec(compact)
        compact_bytes = len(path.read_bytes())
        verbose_bytes = len(json.dumps(verbose, ensure_ascii=False, indent=2).encode())
        self.assertLessEqual(compact_bytes, verbose_bytes * 0.65)

    def test_load_spec_accepts_compact_and_legacy_shapes(self):
        with tempfile.TemporaryDirectory() as directory:
            compact_path = Path(directory) / "compact.json"
            compact_path.write_text(json.dumps(COMPACT_SPEC), encoding="utf-8")
            self.assertEqual(decision_page.load_spec(compact_path)["questions"][1]["type"], "multi")

            legacy_path = Path(directory) / "legacy.json"
            legacy_path.write_text(json.dumps(SPEC), encoding="utf-8")
            self.assertEqual(decision_page.load_spec(legacy_path), SPEC)

    def test_condition_validation_rejects_invalid_dependencies(self):
        valid = decision_page.normalize_spec(COMPACT_SPEC)
        nested = json.loads(json.dumps(valid))
        nested["questions"][1]["when"] = ["all", ["mode", "fast"], ["not", ["mode", "safe"]]]
        decision_page.validate_spec(nested)

        forward = json.loads(json.dumps(valid))
        forward["questions"].reverse()
        with self.assertRaisesRegex(ValueError, "earlier choice"):
            decision_page.validate_spec(forward)

        unknown = json.loads(json.dumps(valid))
        unknown["questions"][1]["when"] = ["mode", "missing"]
        with self.assertRaisesRegex(ValueError, "unknown option"):
            decision_page.validate_spec(unknown)

        malformed = json.loads(json.dumps(valid))
        malformed["questions"][1]["when"] = ["all", ["mode", "fast"]]
        with self.assertRaisesRegex(ValueError, "at least two"):
            decision_page.validate_spec(malformed)

    def test_rejects_duplicate_and_multiple_recommendations(self):
        spec = json.loads(json.dumps(SPEC))
        spec["questions"][0]["options"][1]["id"] = "safe"
        spec["questions"][0]["options"][1]["recommended"] = True
        spec["questions"][0]["options"][1]["recommendation_reason"] = "Also good"
        with self.assertRaisesRegex(ValueError, "duplicated"):
            decision_page.validate_spec(spec)

        boolean_bounds = json.loads(json.dumps(COMPACT_SPEC))
        boolean_bounds["q"][1]["n"] = True
        with self.assertRaisesRegex(ValueError, "min/max"):
            decision_page.validate_spec(decision_page.normalize_spec(boolean_bounds))

    def test_thai_interface_and_unknown_locale(self):
        spec = {**SPEC, "locale": "th"}
        page = decision_page.render_html(spec)
        self.assertIn('<html lang="th">', page)
        self.assertIn("ใช้ตัวเลือกที่แนะนำ", page)
        self.assertIn("บันทึกคำตอบ", page)
        self.assertIn("เพิ่มคำถาม", page)
        with self.assertRaisesRegex(ValueError, "locale"):
            decision_page.validate_spec({**SPEC, "locale": "jp"})

    def test_server_serves_and_saves_matching_response(self):
        with tempfile.TemporaryDirectory() as directory:
            response_path = Path(directory) / "response.json"
            server = decision_page.ThreadingHTTPServer(("127.0.0.1", 0), decision_page.make_handler(b"<p>ok</p>", response_path, SPEC["id"]))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            try:
                self.assertEqual(urllib.request.urlopen(base + "/").read(), b"<p>ok</p>")
                payload = {
                    "format": "boxing-me-response-v1",
                    "spec_id": SPEC["id"],
                    "spec_title": SPEC["title"],
                    "saved_at": "now",
                    "answers": [],
                    "overall_notes": "",
                    "custom_questions": [{"id": "custom", "type": "text"}],
                }
                request = urllib.request.Request(base + "/api/save", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
                result = json.loads(urllib.request.urlopen(request).read())
                self.assertTrue(result["saved"])
                saved = json.loads(response_path.read_text())
                self.assertEqual(saved["spec_id"], SPEC["id"])
                self.assertIn("received_at", saved)
                self.assertEqual(saved["custom_questions"][0]["id"], "custom")

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

                incomplete_request = urllib.request.Request(
                    base + "/api/save",
                    data=json.dumps({"spec_id": SPEC["id"], "answers": []}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(incomplete_request)
                self.assertEqual(caught.exception.code, 400)
                caught.exception.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
