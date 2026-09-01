from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_asymptotic_nhim_angular_force_no_go.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
)


def test_asymptotic_nhim_angular_force_no_go() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["angular_no_go"]["fixed_channel_source_Dini"] == (
        "CLOSED_DO_NOT_REOPEN"
    )
    assert payload["angular_no_go"]["absolute_graded_sum"] == (
        "DIVERGES_TERMS_DO_NOT_TEND_TO_ZERO"
    )
    assert payload["validation"]["zeta_subtraction_is_the_local_optical_integral"] is True
    assert payload["angular_no_go"][
        "finite_direct_zeta_term_repairs_absolute_heat_divergence"
    ] is False
    assert payload["route_adjudication"][
        "NHIM_route_can_close_absolute_graded_Gate7_force"
    ] is False
    assert payload["route_adjudication"]["mathematical_NHIM_preserved"] is True
    assert payload["route_adjudication"]["new_canonical_stop_declared"] is False
    assert payload["claim_boundary"]["actual_finite_stratum"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
