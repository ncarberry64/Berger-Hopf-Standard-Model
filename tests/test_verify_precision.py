from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/verify_precision.py"
RESULTS = ROOT / "artifacts/coordinate_benchmark/coordinate_benchmark_results.json"


def _run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "--results", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_committed_coordinate_benchmark_passes_precision_gate() -> None:
    result = _run(RESULTS)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS: precision gate verified" in result.stdout


def test_precision_gate_rejects_degraded_delta(tmp_path: Path) -> None:
    payload = json.loads(RESULTS.read_text(encoding="utf-8"))
    payload["correctness"]["maximum_absolute_difference"] = 1.01e-13
    degraded = tmp_path / "degraded.json"
    degraded.write_text(json.dumps(payload), encoding="utf-8")
    result = _run(degraded)
    assert result.returncode == 1
    assert "exceeds allowable threshold" in result.stdout


def test_precision_gate_rejects_missing_measurement(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text('{"correctness":{"all_kernels_equivalent":true}}', encoding="utf-8")
    result = _run(malformed)
    assert result.returncode == 1
    assert "lacks correctness.maximum_absolute_difference" in result.stdout
