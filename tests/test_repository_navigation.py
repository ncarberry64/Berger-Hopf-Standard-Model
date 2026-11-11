"""Navigation controls use a real small Git repository, including sparse paths."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys


SPEC = importlib.util.spec_from_file_location(
    "repository_navigation", Path(__file__).resolve().parents[1] / "tools/audit_repository_navigation.py"
)
NAV = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NAV)


def run_git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def repository(tmp_path: Path, files: dict[str, str]) -> Path:
    run_git(tmp_path, "init", "-q")
    for name, text in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    run_git(tmp_path, "add", ".")
    run_git(tmp_path, "-c", "user.name=Navigation Test", "-c", "user.email=navigation@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
    return tmp_path


def test_missing_target_is_not_hidden_by_untracked_file(tmp_path):
    root = repository(tmp_path, {"README.md": "[lost](docs/lost.md)\n"})
    (root / "docs").mkdir()
    (root / "docs/lost.md").write_text("# Unreviewed", encoding="utf-8")
    result = NAV.audit(root, ("README.md",))
    assert not result["passed"]
    assert result["failures"][0]["reason"] == "missing_local_target"


def test_fragments_duplicate_headings_fences_and_reference_links(tmp_path):
    root = repository(tmp_path, {
        "README.md": "[ok](docs/topic.md#same-heading-1)\n[bad](docs/topic.md#ghost)\n[ref]: docs/topic.md#explicit\n```sh\n[ignored](missing.md)\n```\n",
        "docs/topic.md": '# Same heading\n## Same heading\n<a id="explicit"></a>\n```sh\n# Ghost\n```\n',
    })
    result = NAV.audit(root, ("README.md",))
    assert not result["passed"]
    assert result["markdown_fragments_checked"] == 3
    assert [(f["line"], f["reason"]) for f in result["failures"]] == [(2, "missing_markdown_fragment")]


def test_sparse_targets_are_known_and_unavailable_fragments_are_explicit(tmp_path):
    root = repository(tmp_path, {
        "README.md": "[path](docs/topic.md)\n[heading](docs/topic.md#topic)\n",
        "docs/topic.md": "# Topic\n",
    })
    run_git(root, "sparse-checkout", "set", "--no-cone", "/README.md")
    assert not (root / "docs/topic.md").exists()
    result = NAV.audit(root, ("README.md",))
    assert result["passed"]
    assert not result["validation_complete"]
    assert result["local_links_checked"] == 2
    assert result["markdown_fragments_checked"] == 0
    assert result["unavailable_checks"][0]["reason"] == "fragment_content_not_materialized"


def test_selected_new_navigation_and_encoded_paths(tmp_path):
    root = repository(tmp_path, {"README.md": "[new](docs/New%20Guide.md#guide)\n"})
    (root / "docs").mkdir()
    (root / "docs/New Guide.md").write_text("# Guide\n[home](../README.md)\n", encoding="utf-8")
    result = NAV.audit(root, ("README.md", "docs/New Guide.md"))
    assert result["passed"] and result["validation_complete"]
    assert result["local_links_checked"] == 2


def test_inventory_pins_tree_independently_of_sparse_and_dirty_files(tmp_path):
    root = repository(tmp_path, {"README.md": "start", "docs/topic.md": "topic", "data/value.json": "{}"})
    before = NAV.inventory(root, "HEAD")
    run_git(root, "sparse-checkout", "set", "--no-cone", "/README.md")
    (root / "README.md").write_text("changed", encoding="utf-8")
    (root / "untracked.txt").write_text("local", encoding="utf-8")
    assert NAV.inventory(root, before["source_commit"]) == before
    assert before["total_tracked_paths"] == 3
    assert before["top_level_counts"] == {"[root]": 1, "data": 1, "docs": 1}
    assert before["extension_counts"] == {".json": 1, ".md": 2}


def test_cli_requires_complete_validation_unless_explicitly_allowed(tmp_path, monkeypatch):
    root = repository(tmp_path, {"README.md": "# Home", "docs/guide.md": "# Guide"})
    run_git(root, "sparse-checkout", "set", "--no-cone", "/README.md")
    result = NAV.audit(root, ("docs/guide.md",))
    assert result["passed"] and not result["validation_complete"]
    assert result["local_links_checked"] == 0
    monkeypatch.setattr(NAV, "audit", lambda: result)
    monkeypatch.setattr(sys, "argv", ["audit_repository_navigation.py"])
    assert NAV.main() == 1
    monkeypatch.setattr(sys, "argv", ["audit_repository_navigation.py", "--allow-incomplete"])
    assert NAV.main() == 0
