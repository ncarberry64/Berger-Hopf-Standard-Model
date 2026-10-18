"""Exercise the museum's real source assertion against a large scratch index."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
GIT = shutil.which("git")


def _run(arguments, *, cwd, data=None):
    return subprocess.run(arguments, cwd=cwd, input=data, capture_output=True)


@pytest.fixture(scope="module")
def source_index(tmp_path_factory):
    if NODE is None or GIT is None:
        pytest.skip("Node and Git are required for the museum subprocess regression")
    root = tmp_path_factory.mktemp("museum-source-index")
    assert _run([GIT, "init", "-q"], cwd=root).returncode == 0
    blob = _run([GIT, "hash-object", "-w", "--stdin"], cwd=root, data=b"tracked\n")
    assert blob.returncode == 0
    identity = blob.stdout.decode().strip()
    paths = [f"archive/{index:05d}/" + "x" * 125 + ".json" for index in range(14003)]
    paths += ["docs/known.md", "docs/literal[1].md", "docs/literal1.md"]
    entries = "".join(f"100644 {identity}\t{path}\n" for path in paths).encode()
    indexed = _run([GIT, "update-index", "--index-info"], cwd=root, data=entries)
    assert indexed.returncode == 0, indexed.stderr.decode()
    (root / "docs").mkdir()
    for name in ["known.md", "literal[1].md", "untracked.md"]:
        (root / "docs" / name).write_text("source\n", encoding="utf-8")
    return root


def _source_assertion():
    source = (ROOT / "museum/scripts/test-physics-questions.mjs").read_text(encoding="utf-8")
    marker = "test('supporting sources exist in the tracked scientific record', async () => {\n"
    return source.split(marker, 1)[1].split("\n});", 1)[0]


def _check(root, paths, *, body=None):
    questions = [{"id": "fixture", "sources": [{"title": "Fixture", "path": path} for path in paths]}] if paths else []
    body = _source_assertion() if body is None else body
    script = (
        "import assert from 'node:assert/strict';\n"
        "import { access } from 'node:fs/promises';\n"
        "import { execFileSync } from 'node:child_process';\n"
        f"const physicsQuestions = {json.dumps(questions)};\n"
        "await (async () => {\n"
        + body.replace("import.meta.url", json.dumps((root / "museum/scripts/test.mjs").as_uri()))
        + "\n})();\n"
    )
    script_path = root / "execute.mjs"
    script_path.write_text(script, encoding="utf-8")
    return _run([NODE, str(script_path)], cwd=root)


def test_previously_unrestricted_query_exceeds_node_default_buffer(source_index):
    listing = _run([GIT, "ls-files", "-z"], cwd=source_index)
    assert len(listing.stdout) > 1024 * 1024
    body = _source_assertion()
    body = body[body.index("  const repoRoot"):body.index("  const citedPaths")] + body[body.index("  const tracked"):]
    body = body.replace("['--literal-pathspecs', 'ls-files', '-z', '--', ...citedPaths]", "['ls-files', '-z']")
    result = _check(source_index, ["docs/known.md"], body=body)
    assert result.returncode != 0
    assert b"ENOBUFS" in result.stderr


@pytest.mark.parametrize("paths", [["docs/known.md"], ["docs/literal[1].md"], ["docs/known.md", "docs/known.md"]])
def test_bounded_query_accepts_exact_tracked_sources(source_index, paths):
    result = _check(source_index, paths)
    assert result.returncode == 0, result.stderr.decode()[:4000]


@pytest.mark.parametrize("paths", [["docs/untracked.md"], ["docs/*.md"], ["../outside.md"], []])
def test_bounded_query_preserves_rejection(source_index, paths):
    assert _check(source_index, paths).returncode != 0


def test_tracked_but_missing_working_file_still_fails(source_index):
    # This index-only path matches a wildcard for the literal-bracket test above.
    assert _check(source_index, ["docs/literal1.md"]).returncode != 0


def test_longpaths_is_windows_only_and_precedes_checkout():
    workflow = (ROOT / ".github/workflows/institutional.yml").read_text(encoding="utf-8")
    portable = workflow.split("  portable-core:\n", 1)[1].split("  review-container:\n", 1)[0]
    steps = portable.split("    steps:\n", 1)[1]
    longpaths, checkout = steps.split("      - uses: actions/checkout@v4", 1)
    assert "if: runner.os == 'Windows'" in longpaths
    assert "run: git config --global core.longpaths true" in longpaths
    assert "core.longpaths" not in checkout
    assert workflow.count("core.longpaths") == 1
    assert "tests/test_ci_source_tracking.py" in checkout
