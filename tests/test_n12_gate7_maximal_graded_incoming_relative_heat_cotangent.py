from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / (
    "derive_n12_gate7_maximal_graded_incoming_relative_heat_cotangent.py"
)
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT.json"
)


def test_maximal_graded_incoming_relative_heat_cotangent() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT_SUMMABLE"
    )
    split = payload["low_high_spectral_split"]
    assert split["net_low_energy_linear_decay_rate"] > 0.0
    assert split["high_energy_quadratic_decay_rate"] > 0.0
    assert payload["root_test_witness"]["sample_rows_strictly_decrease"] is True
    assert payload["adjudication"]["unknown_far_C2_tail_used_in_angular_majorant"] is False
    assert payload["adjudication"]["interior_log_radius_source_counterexample_reopened"] is False
    assert payload["claim_boundary"][
        "maximal_incoming_full_graded_relative_heat_cotangent"
    ] == "CERTIFIED_SUMMABLE"
    assert payload["claim_boundary"]["actual_projected_KKT_root"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
