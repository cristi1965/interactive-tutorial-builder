from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "skills/interactive-tutorial-builder/scripts/verify_tutorial_evidence.py"
SPEC = importlib.util.spec_from_file_location("verify_tutorial_evidence", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidenceVerifierTest(unittest.TestCase):
    def build_fixture(self, root: Path) -> Path:
        (root / "dist").mkdir()
        (root / "evidence").mkdir()
        artifact = root / "dist/index.html"
        artifact.write_text("<main>lesson</main>\n", encoding="utf-8")
        artifact_record = {"path": "dist/index.html", "sha256": digest(artifact)}
        candidate_sha = MODULE.candidate_digest([artifact_record])

        layers = {}
        for name in MODULE.REQUIRED_LAYERS:
            report = root / f"evidence/{name}.json"
            report.write_text(json.dumps({
                "status": "pass",
                "layer": name,
                "candidate_sha256": candidate_sha,
            }) + "\n", encoding="utf-8")
            layers[name] = {
                "status": "pass",
                "candidate_sha256": candidate_sha,
                "report": f"evidence/{name}.json",
                "report_sha256": digest(report),
            }

        manifest = root / "evidence-manifest.json"
        manifest.write_text(json.dumps({
            "version": 1,
            "candidate": {"sha256": candidate_sha, "artifacts": [artifact_record]},
            "layers": layers,
        }, indent=2) + "\n", encoding="utf-8")
        return manifest

    def test_accepts_complete_bound_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            result = MODULE.verify_manifest(self.build_fixture(Path(directory)))
            self.assertEqual("pass", result["status"], result["errors"])

    def test_rejects_layer_bound_to_another_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.build_fixture(Path(directory))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["layers"]["browser"]["candidate_sha256"] = "0" * 64
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("layers.browser.candidate_sha256" in error for error in result["errors"]))

    def test_rejects_artifact_changed_after_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.build_fixture(root)
            (root / "dist/index.html").write_text("<main>changed</main>\n", encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("file digest changed" in error for error in result["errors"]))

    def test_rejects_missing_required_layer(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.build_fixture(Path(directory))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            del payload["layers"]["pedagogy"]
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("layers.pedagogy" in error for error in result["errors"]))

    def test_rejects_failed_report_body(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.build_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            report = root / payload["layers"]["runtime"]["report"]
            report.write_text(json.dumps({
                "status": "fail",
                "candidate_sha256": payload["candidate"]["sha256"],
            }), encoding="utf-8")
            payload["layers"]["runtime"]["report_sha256"] = digest(report)
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("report status is not pass" in error for error in result["errors"]))

    def test_rejects_report_bound_to_another_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.build_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            report = root / payload["layers"]["content"]["report"]
            report.write_text(json.dumps({
                "status": "pass",
                "candidate_sha256": "0" * 64,
            }), encoding="utf-8")
            payload["layers"]["content"]["report_sha256"] = digest(report)
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("report candidate" in error for error in result["errors"]))

    def test_rejects_invalid_and_non_object_report_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.build_fixture(root)
            for body in ("not-json", "[]"):
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                report = root / payload["layers"]["browser"]["report"]
                report.write_text(body, encoding="utf-8")
                payload["layers"]["browser"]["report_sha256"] = digest(report)
                candidate = root / f"bad-report-{len(body)}.json"
                candidate.write_text(json.dumps(payload), encoding="utf-8")
                result = MODULE.verify_manifest(candidate)
                self.assertEqual("fail", result["status"])
                self.assertTrue(any("expected a JSON" in error for error in result["errors"]))

    def test_returns_structured_failure_for_read_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.build_fixture(Path(directory))
            with mock.patch.object(MODULE, "sha256_file", side_effect=OSError("blocked")):
                result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("cannot read" in error for error in result["errors"]))

    def test_rejects_artifact_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.build_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            first = payload["candidate"]["artifacts"][0]
            alias = {"path": "dist/./index.html", "sha256": first["sha256"]}
            payload["candidate"]["artifacts"].append(alias)
            payload["candidate"]["sha256"] = MODULE.candidate_digest(payload["candidate"]["artifacts"])
            for layer in payload["layers"].values():
                layer["candidate_sha256"] = payload["candidate"]["sha256"]
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("aliases another artifact" in error for error in result["errors"]))

    def test_rejects_non_object_manifest_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            for value in ([], None, 42):
                manifest.write_text(json.dumps(value), encoding="utf-8")
                result = MODULE.verify_manifest(manifest)
                self.assertEqual("fail", result["status"])
                self.assertIn("expected a JSON object", result["errors"][0])

    def test_rejects_wrong_candidate_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.build_fixture(Path(directory))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["candidate"]["sha256"] = "f" * 64
            for layer in payload["layers"].values():
                layer["candidate_sha256"] = "f" * 64
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("declared artifact set" in error for error in result["errors"]))

    def test_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.build_fixture(Path(directory))
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["candidate"]["artifacts"][0]["path"] = "../outside.txt"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            result = MODULE.verify_manifest(manifest)
            self.assertEqual("fail", result["status"])
            self.assertTrue(any("inside the manifest directory" in error for error in result["errors"]))

    def test_rejects_absolute_and_backslash_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.build_fixture(Path(directory))
            for bad_path in ("/tmp/outside.txt", "dist\\index.html"):
                payload = json.loads(manifest.read_text(encoding="utf-8"))
                payload["candidate"]["artifacts"][0]["path"] = bad_path
                candidate = Path(directory) / "bad.json"
                candidate.write_text(json.dumps(payload), encoding="utf-8")
                result = MODULE.verify_manifest(candidate)
                self.assertEqual("fail", result["status"])
                self.assertTrue(any("relative path" in error or "inside" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
