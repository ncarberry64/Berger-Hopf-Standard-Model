from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / (
    "derive_n12_gate7_incoming_finite_amplitude_heat_zeta_comparison.py"
)
RESULT = ROOT / "artifacts" / "flagship_integration" / (
    "BHSM_N12_GATE7_INCOMING_FINITE_AMPLITUDE_HEAT_ZETA_COMPARISON.json"
)


def test_incoming_finite_amplitude_heat_zeta_comparison() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "FINITE_CORE_CERTIFIED_AMPLITUDE_BOX_HEAT_STRICTLY_DOMINATED_BY_ZETA"
    )
    bound = payload["finite_amplitude_heat_bound"]
    assert bound["zeta_minus_heat_logarithmic_margin_lower"] > 0.0
    assert bound["low_mode_relative_factor_over_zero_majorant"] > 1.0
    assert bound["high_mode_heat_coefficient_log_upper"] < (
        bound["low_mode_heat_coefficient_log_upper"]
    )
    assert payload["regular_compliance_split"][
        "descriptor_or_kinetic_block_inverse_formed"
    ] is False
    assert payload["adjudication"][
        "finite_core_entire_certified_amplitude_box_sign"
    ] == "STRICTLY_POSITIVE"
    assert payload["adjudication"]["componentwise_KKT_condition_added"] is False
    assert payload["claim_boundary"]["maximal_projected_tail"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
    for relative, digest in payload["inputs"].items():
        path = ROOT / relative
        content = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py"}:
            content = content.replace(b"\r\n", b"\n")
        assert hashlib.sha256(content).hexdigest().upper() == digest
