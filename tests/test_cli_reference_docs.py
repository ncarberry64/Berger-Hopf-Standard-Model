from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cli_reference_is_a_readable_markdown_table() -> None:
    text = (ROOT / "CLI_REFERENCE.md").read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| `")]
    assert len(rows) >= 20
    assert all(row.count("|") == 6 for row in rows)
    assert all("| no | no |" in row for row in rows)


def test_cli_index_matches_required_current_commands() -> None:
    payload = json.loads(
        (ROOT / "artifacts/BHSM_cli_command_index_v0_7.json").read_text(encoding="utf-8")
    )
    commands = {row["command"] for row in payload["commands"]}
    required = {
        "registry",
        "status",
        "gallery",
        "artifact-sources",
        "formula-registry",
        "compute-artifact",
        "artifact-report",
        "cp-o-int-field-action",
        "theorem-blockers",
    }
    assert required <= commands
    assert payload["internet_required"] is False
    assert payload["pdg_required"] is False
    assert payload["external_hep_tools_required"] is False


def test_representative_cli_commands_run_offline() -> None:
    commands = (
        ("registry", "--format", "json"),
        ("formula-registry", "--format", "json"),
        ("theorem-blockers",),
        ("cp-o-int-field-action", "--format", "json"),
    )
    for args in commands:
        result = subprocess.run(
            [sys.executable, "-m", "bhsm.interface", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)

