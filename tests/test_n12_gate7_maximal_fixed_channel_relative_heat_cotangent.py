from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / (
    "derive_n12_gate7_maximal_fixed_channel_relative_heat_cotangent.py"
)
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_MAXIMAL_FIXED_CHANNEL_RELATIVE_HEAT_COTANGENT.json"
)


def test_maximal_fixed_channel_relative_heat_cotangent() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "MAXIMAL_FIXED_CHANNEL_INCOMING_RELATIVE_HEAT_COTANGENT_DERIVED"
    )
    assert payload["algebra_witness"]["resolvent_difference_rank"] == 1
    assert payload["algebra_witness"][
        "resolvent_jet_finite_difference_residual"
    ] < 1.0e-9
    assert payload["boundary_triple_theorem"][
        "separate_D_lambda_M_C2_max_required"
    ] is False
    assert payload["adjudication"]["absolute_infinite_volume_heat_trace_required"] is False
    assert payload["adjudication"]["complete_graded_angular_sum"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["actual_projected_KKT_root"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
