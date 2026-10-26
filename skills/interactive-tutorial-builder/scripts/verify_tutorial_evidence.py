#!/usr/bin/env python3
"""Verify that tutorial evidence is complete and bound to one candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


REQUIRED_LAYERS = ("content", "runtime", "browser", "pedagogy")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_digest(artifacts: list[dict[str, str]]) -> str:
    digest = hashlib.sha256()
    for artifact in sorted(artifacts, key=lambda item: item["path"]):
        digest.update(artifact["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(artifact["sha256"].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def safe_relative_path(root: Path, raw_path: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path or "\\" in raw_path:
        errors.append(f"{label}: path must be a non-empty POSIX relative path")
        return None
    logical = PurePosixPath(raw_path)
    if logical.is_absolute() or ".." in logical.parts or logical == PurePosixPath("."):
        errors.append(f"{label}: path must stay inside the manifest directory")
        return None
    try:
        resolved = (root / Path(*logical.parts)).resolve()
    except (OSError, ValueError, UnicodeError):
        errors.append(f"{label}: path cannot be resolved safely")
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        errors.append(f"{label}: path escapes the manifest directory")
        return None
    return resolved


def verify_manifest(manifest_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = manifest_path.resolve()
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "fail", "manifest": str(manifest_path), "errors": [f"manifest: {exc}"]}
    if not isinstance(payload, dict):
        return {"status": "fail", "manifest": str(manifest_path), "errors": ["manifest: expected a JSON object"]}

    if payload.get("version") != 1:
        errors.append("version: expected 1")

    root = manifest_path.parent.resolve()
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict):
        candidate = {}
        errors.append("candidate: expected an object")

    expected_candidate = candidate.get("sha256")
    if not isinstance(expected_candidate, str) or not SHA256_RE.fullmatch(expected_candidate):
        errors.append("candidate.sha256: expected a lowercase SHA-256 digest")

    raw_artifacts = candidate.get("artifacts")
    artifacts: list[dict[str, str]] = []
    if not isinstance(raw_artifacts, list) or not raw_artifacts:
        errors.append("candidate.artifacts: expected at least one artifact")
        raw_artifacts = []

    seen_paths: set[str] = set()
    seen_files: set[Path] = set()
    for index, item in enumerate(raw_artifacts):
        label = f"candidate.artifacts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: expected an object")
            continue
        raw_path = item.get("path")
        expected_sha = item.get("sha256")
        file_path = safe_relative_path(root, raw_path, label, errors)
        if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
            errors.append(f"{label}.sha256: expected a lowercase SHA-256 digest")
            continue
        if isinstance(raw_path, str):
            if raw_path in seen_paths:
                errors.append(f"{label}.path: duplicate artifact path")
            seen_paths.add(raw_path)
        if file_path is None:
            continue
        if file_path in seen_files:
            errors.append(f"{label}.path: aliases another artifact")
        seen_files.add(file_path)
        if not file_path.is_file():
            errors.append(f"{label}.path: file does not exist: {raw_path}")
            continue
        try:
            actual_sha = sha256_file(file_path)
        except OSError as exc:
            errors.append(f"{label}.path: cannot read {raw_path}: {exc}")
            continue
        if actual_sha != expected_sha:
            errors.append(f"{label}.sha256: file digest changed for {raw_path}")
        artifacts.append({"path": raw_path, "sha256": expected_sha})

    if artifacts and len(artifacts) == len(raw_artifacts):
        actual_candidate = candidate_digest(artifacts)
        if expected_candidate != actual_candidate:
            errors.append("candidate.sha256: does not match the declared artifact set")

    layers = payload.get("layers")
    if not isinstance(layers, dict):
        layers = {}
        errors.append("layers: expected an object")

    for layer_name in REQUIRED_LAYERS:
        layer = layers.get(layer_name)
        label = f"layers.{layer_name}"
        if not isinstance(layer, dict):
            errors.append(f"{label}: missing required layer")
            continue
        if layer.get("status") != "pass":
            errors.append(f"{label}.status: expected pass")
        if layer.get("candidate_sha256") != expected_candidate:
            errors.append(f"{label}.candidate_sha256: does not match candidate.sha256")
        report_path = safe_relative_path(root, layer.get("report"), f"{label}.report", errors)
        report_sha = layer.get("report_sha256")
        if not isinstance(report_sha, str) or not SHA256_RE.fullmatch(report_sha):
            errors.append(f"{label}.report_sha256: expected a lowercase SHA-256 digest")
            continue
        if report_path is None:
            continue
        if not report_path.is_file():
            errors.append(f"{label}.report: file does not exist")
            continue
        try:
            report_bytes = report_path.read_bytes()
        except OSError as exc:
            errors.append(f"{label}.report: cannot read report: {exc}")
            continue
        if hashlib.sha256(report_bytes).hexdigest() != report_sha:
            errors.append(f"{label}.report_sha256: report digest changed")
        try:
            report_payload = json.loads(report_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"{label}.report: expected a JSON report: {exc}")
            continue
        if not isinstance(report_payload, dict):
            errors.append(f"{label}.report: expected a JSON object")
            continue
        if report_payload.get("status") != "pass":
            errors.append(f"{label}.report: report status is not pass")
        if report_payload.get("candidate_sha256") != expected_candidate:
            errors.append(f"{label}.report: report candidate does not match candidate.sha256")

    return {
        "status": "fail" if errors else "pass",
        "manifest": str(manifest_path),
        "candidate_sha256": expected_candidate,
        "layers": list(REQUIRED_LAYERS),
        "errors": errors,
        "note": "This verifies evidence integrity, not teaching effectiveness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Path to the tutorial evidence manifest")
    args = parser.parse_args()
    result = verify_manifest(args.manifest)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
