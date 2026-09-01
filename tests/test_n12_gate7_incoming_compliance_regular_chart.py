from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_incoming_compliance_regular_chart.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_INCOMING_COMPLIANCE_REGULAR_CHART.json"
)


def test_incoming_compliance_regular_chart() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "INCOMING_COMPLIANCE_REGULAR_CHART_AND_LINEAR_AMPLITUDE_JET_CERTIFIED"
    )
    assert payload["exact_chart"]["incoming_compliance"] == "C_f=M_f^-1=b/d"
    interval = payload["certified_coefficients"]["D_lambda_T_per_lambda_interval"]
    assert 0.0 < interval[0] <= interval[1]
    assert payload["algebra_witness"]["derivative_identity_absolute_residual"] < 1.0e-15
    assert payload["adjudication"]["incoming_M_f_is_zeroed"] is False
    assert payload["adjudication"]["componentwise_KKT_condition_added"] is False
    assert payload["adjudication"]["full_graded_heat_amplitude_bound"].startswith("OPEN")
    assert payload["claim_boundary"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
