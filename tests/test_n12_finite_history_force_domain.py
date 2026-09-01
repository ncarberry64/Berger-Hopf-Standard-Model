from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from scripts.audit_n12_finite_history_force_domain import (
    build_payload,
    zeta_truncation_witness,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_n12_finite_history_force_domain.py"
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"
)


def test_positive_radius_extension_changes_zeta_force() -> None:
    witness = zeta_truncation_witness()
    assert witness["extension_integral"] > 0.0
    assert witness["long_interval_common_scale_zeta_force"] > witness[
        "short_interval_common_scale_zeta_force"
    ]
    assert witness["additivity_residual"] < 1.0e-12


def test_local_existence_is_not_promoted_to_complete_force_domain() -> None:
    payload = build_payload()
    audit = payload["domain_adjudication"]
    assert audit["finite_encapsulation_existence"] == "CLOSED_LOCALLY"
    assert audit["complete_action_owned_force_interval"] == "OPEN"
    assert audit["direct_action_owned_exterior_Weyl_Calderon_response"] == (
        "OPEN_EQUIVALENT_ROUTE"
    )
    assert audit["arbitrary_short_local_branch_is_complete_physical_history"] is False
    assert audit["infinite_tail_analysis_reopened"] is False
    assert audit["post_event_return_required"] is False


def test_force_domain_artifact_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
