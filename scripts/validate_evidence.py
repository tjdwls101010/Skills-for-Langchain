#!/usr/bin/env python3
"""Validate committed probe evidence, generated-file hashes, and release metadata."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs" / "plans" / "research"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []

    json_paths = sorted(RESEARCH.glob("*.json"))
    parsed = {path.name: load_json(path) for path in json_paths}

    round1 = parsed["probe-round1-tasks.json"]
    round2 = parsed["probe-round2-tasks.json"]
    after = parsed["probe-after-results.json"]
    codex = parsed["probe-codex-results.json"]

    require(len(round1) == 26, "Round 1 must contain 26 tasks", errors)
    require(len(round2) == 12, "Round 2 must contain 12 tasks", errors)

    tasks = round1 + round2
    included = [task for task in tasks if task["include"]]
    excluded = [task for task in tasks if not task["include"]]
    require(len(included) == 27, "Expected 27 included task deltas", errors)
    require(len(excluded) == 11, "Expected 11 measured-correct exclusions", errors)

    baseline = {task["id"]: (task["verdict"], task["include"]) for task in tasks}
    after_tasks = after["tasks"]
    require(len(after_tasks) == 38, "After evidence must contain 38 tasks", errors)
    for task in after_tasks:
        expected = baseline.get(task["id"])
        require(expected is not None, f"Unknown after-task id: {task['id']}", errors)
        if expected is not None:
            observed = (task["baseline_verdict"], task["baseline_include"])
            require(observed == expected, f"Baseline mismatch for {task['id']}", errors)

    final = after["final_reclassified_baseline_result"]
    require(final["include_correct"] == 27 and final["include_total"] == 27, "Final include closure must be 27/27", errors)
    require(final["exclusions_correct"] == 11 and final["exclusion_total"] == 11, "Final exclusion guard must be 11/11", errors)

    generated_hashes = codex["generated_file_sha256"]
    for raw_path, expected_hash in generated_hashes.items():
        path = ROOT / raw_path
        require(path.is_file(), f"Missing generated file: {raw_path}", errors)
        if path.is_file():
            require(sha256(path) == expected_hash, f"Generated-file hash mismatch: {raw_path}", errors)

    attempts = codex["attempts"]
    graders = codex["graders"]
    synthesis = codex["synthesis"]
    require(len(attempts) == 3, "Codex residual evidence must contain 3 attempts", errors)
    require(len(graders) == 6, "Codex residual evidence must contain 6 grader records", errors)
    require(all(record["verdict"] == "correct" for record in graders), "Every residual grader verdict must be correct", errors)
    require(synthesis["pass"] is True, "Residual synthesis must pass", errors)
    require(synthesis["all_current_hashes_match"] is True, "Residual synthesis must confirm current hashes", errors)
    require(synthesis["all_grader_hashes_match"] is True, "Residual synthesis must confirm grader hashes", errors)
    require(all(not task["material_residuals"] for task in synthesis["tasks"]), "Residual synthesis must contain no material residuals", errors)

    plugin_root = ROOT / "plugins" / "skills-for-langchain"
    plugin = load_json(plugin_root / ".claude-plugin" / "plugin.json")
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    version = plugin["version"]
    require(plugin["name"] == "skills-for-langchain", "Unexpected plugin name", errors)
    require(marketplace["name"] == "skills-for-langchain", "Unexpected marketplace name", errors)
    require(marketplace["plugins"][0]["name"] == plugin["name"], "Marketplace and plugin names must match", errors)
    require(marketplace["plugins"][0]["source"] == "./plugins/skills-for-langchain", "Unexpected marketplace plugin source", errors)
    canonical_skill = ROOT / ".claude" / "skills" / "langchain"
    packaged_skill = plugin_root / "skills" / "langchain"
    for relative_path in ("SKILL.md", "references/deepagents.md", "references/langchain-langgraph.md"):
        require(sha256(canonical_skill / relative_path) == sha256(packaged_skill / relative_path), f"Packaged skill drift: {relative_path}", errors)
    require(f"## [{version}]" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), "Plugin version must exist in CHANGELOG.md", errors)

    if errors:
        print("Evidence validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Evidence validation passed: {len(tasks)} tasks, {len(included)} includes, {len(excluded)} exclusions")
    print(f"Plugin release metadata passed: {plugin['name']} v{version}")


if __name__ == "__main__":
    main()
