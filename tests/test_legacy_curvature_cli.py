from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bhsm.interface", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_all_legacy_curvature_json_commands_work_offline() -> None:
    for command in (
        "legacy-curvature-artifacts",
        "curvature-mass-functional",
        "neutrino-propagation-radius",
        "neutral-curvature-mapping",
        "legacy-neutral-scale",
    ):
        result = run_cli(command, "--format", "json")
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)


def test_legacy_markdown_and_dimensionful_attempt_are_bounded() -> None:
    result = run_cli("legacy-neutral-scale-report", "--format", "markdown")
    assert result.returncode == 0, result.stderr
    assert "ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL" in result.stdout
    assert "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS" in result.stdout
    attempt = run_cli("neutrino-dimensionful-mass", "--format", "json")
    payload = json.loads(attempt.stdout)
    assert payload["legacy_curvature_mass_functional_available"] is True
    assert payload["dimensionful_mass_possible"] is False
    assert payload["dimensionful_mass_output_produced"] is False

