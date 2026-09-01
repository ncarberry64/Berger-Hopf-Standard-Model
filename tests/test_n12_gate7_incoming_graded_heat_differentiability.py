from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_incoming_graded_heat_differentiability.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_INCOMING_GRADED_HEAT_DIFFERENTIABILITY.json"
)


def test_incoming_graded_heat_differentiability() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "INCOMING_SHRINKING_ARM_GRADED_HEAT_DIFFERENTIABILITY_CERTIFIED"
    )
    theorem = payload["domination_theorem"]
    assert theorem["spatial_quadratic_coefficient"] > 0.0
    assert theorem["root_test_limit"] == "minus_infinity"
    assert theorem["differentiation_through_graded_supertrace"] == "CERTIFIED"
    assert payload["absolute_angular_derivative_majorants"]["total"] > 0.0
    assert payload["adjudication"]["uniform_graded_heat_amplitude_differentiability"] == "CLOSED"
    assert payload["adjudication"]["heat_amplitude_coefficient_value"].startswith("OPEN")
    assert payload["adjudication"]["componentwise_KKT_condition_added"] is False
    assert payload["claim_boundary"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
