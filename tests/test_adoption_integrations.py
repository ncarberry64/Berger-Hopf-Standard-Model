from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ROOT_INTEGRATION = ROOT / "integrations/cern-root"


def _load_root_adapter():
    path = ROOT_INTEGRATION / "python/bhsm_root.py"
    spec = importlib.util.spec_from_file_location("bhsm_root_test_adapter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeInterpreter:
    def __init__(self) -> None:
        self.declarations: list[str] = []

    def Declare(self, source: str) -> bool:
        self.declarations.append(source)
        return True


class FakeROOT:
    def __init__(self) -> None:
        self.gInterpreter = FakeInterpreter()


class FakeFrame:
    def __init__(self) -> None:
        self.definitions: list[tuple[str, str]] = []

    def Define(self, name: str, expression: str):
        self.definitions.append((name, expression))
        return self


def test_root_adapter_declares_header_and_builds_rdataframe_columns() -> None:
    adapter = _load_root_adapter()
    root = FakeROOT()
    adapter.install(root)
    assert "BHSMCoordinate.hxx" in root.gInterpreter.declarations[0]
    frame = adapter.add_boundary_columns(FakeFrame())
    assert frame.definitions[0] == (
        "bhsm_state",
        "bhsm::root::MapBoundaryState(t, x, y, z)",
    )
    assert [row[0] for row in frame.definitions[1:]] == [
        "bhsm_radius",
        "bhsm_ux",
        "bhsm_uy",
        "bhsm_uz",
        "bhsm_minkowski_interval",
    ]


def test_root_integration_fails_closed_without_runtime_validation() -> None:
    status = json.loads((ROOT_INTEGRATION / "integration_status.json").read_text(encoding="utf-8"))
    assert status["status"] == "OPTIONAL_ROOT_ADAPTER_NOT_RUNTIME_VALIDATED_IN_REPOSITORY_CI"
    assert status["root_runtime_available_during_development"] is False
    assert status["production_hep_tracking_claimed"] is False
    assert status["frozen_predictions_changed"] is False


def test_quickstart_scripts_and_container_use_the_claim_bounded_runner() -> None:
    shell = (ROOT / "run_benchmark.sh").read_text(encoding="utf-8")
    powershell = (ROOT / "run_benchmark.ps1").read_text(encoding="utf-8")
    docker = (ROOT / "integrations/benchmark/Dockerfile").read_text(encoding="utf-8")
    module = "bhsm.interface.benchmarks.coordinate_benchmark"
    assert module in shell
    assert module in powershell
    assert module in docker
    assert "--summary" in shell and "--summary" in powershell and "--summary" in docker
    assert "tmp/coordinate_benchmark/results.json" in shell
    assert "tmp/coordinate_benchmark/results.json" in powershell


def test_summary_cli_runs_without_overwriting_committed_results(tmp_path: Path) -> None:
    pytest.importorskip("matplotlib")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bhsm.interface.benchmarks.coordinate_benchmark",
            "--events",
            "2000",
            "--repeats",
            "1",
            "--summary",
            "--output",
            str(tmp_path / "results.json"),
            "--markdown",
            str(tmp_path / "results.md"),
            "--plot",
            str(tmp_path / "results.png"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "speedup_vs_vectorized_control=" in result.stdout
    assert "SYNTHETIC_MICROBENCHMARK_NOT_PRODUCTION_HEP_VALIDATION" in result.stdout


def test_ci_and_visual_assets_are_discoverable_and_claim_bounded() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    gif = (ROOT / "docs/assets/bhsm_boundary_mapping_explainer.gif").read_bytes()
    assert "python -m pytest -q" in workflow
    assert "audit_frozen_prediction_integrity.py" in workflow
    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert "bhsm_boundary_mapping_explainer.gif" in readme
    assert "not a detector failure" in readme
    assert gif[:6] in (b"GIF87a", b"GIF89a")


def test_frozen_hash_inputs_have_cross_platform_line_ending_contract() -> None:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "docs/frozen_predictions.md text eol=crlf" in attributes
    assert "docs/frozen_predictions.json text eol=crlf" in attributes
