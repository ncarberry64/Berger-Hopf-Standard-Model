from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_n12_c2_infinite_heat_zeta_compatibility.py"
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY.json"
)


def test_c2_infinite_heat_zeta_compatibility() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["finite_optical_infinite_route"] == "CLOSED_NO_GO"
    assert payload["claim_boundary"]["infinite_optical_common_scale_zeta_criterion"] == "DERIVED"
    assert payload["claim_boundary"]["actual_common_scale_zeta_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["claim_boundary"]["actual_full_graded_heat_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["route_dichotomy"]["finite_later_event_or_canonical_stop"]["infinite_tail_conditions"] == "NOT_REQUIRED"
    assert payload["validation"]["common_scale_is_physical_not_gauge"] is True
    assert payload["claim_boundary"]["chord_03_authorized"] is False


def test_optical_witness_separates_radius_from_modulation() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    witness = payload["sharpness_witness"]
    divergent = witness["persistent_common_scale"]["truncated_zeta_integrals"]
    decaying = witness["decaying_common_scale"]["truncated_zeta_integrals"]
    assert all(a < b for a, b in zip(divergent, divergent[1:]))
    assert all(a < b for a, b in zip(decaying, decaying[1:]))
    assert witness["persistent_common_scale"]["limit"] == "infinity"
    assert witness["decaying_common_scale"]["limit"] == 4.0

