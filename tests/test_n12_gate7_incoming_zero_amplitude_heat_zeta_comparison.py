from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_incoming_zero_amplitude_heat_zeta_comparison.py"
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_INCOMING_ZERO_AMPLITUDE_HEAT_ZETA_COMPARISON.json"
)


def test_incoming_zero_amplitude_heat_zeta_comparison() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "FINITE_CORE_ZERO_AMPLITUDE_HEAT_COEFFICIENT_STRICTLY_DOMINATED_BY_ZETA"
    )
    comparison = payload["coefficient_comparison"]
    assert comparison["zeta_minus_heat_logarithmic_margin_lower"] > 0.0
    assert comparison["finite_core_joint_replacement_amplitude_sign_near_zero"] == "STRICTLY_POSITIVE"
    assert comparison["explicit_positive_neighborhood_radius"].startswith("OPEN")
    assert payload["zero_amplitude_Schur_theorem"]["matrix_inverse_formed"] is False
    assert payload["adjudication"]["componentwise_KKT_condition_added"] is False
    assert payload["adjudication"]["entire_certified_amplitude_box_sign"].startswith("OPEN")
    assert payload["claim_boundary"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
