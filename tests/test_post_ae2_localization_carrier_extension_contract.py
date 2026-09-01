from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from scripts.materialize_post_ae2_localization_carrier_extension_contract import (
    TARGET,
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_post_ae2_localization_carrier_extension_contract.py"


def test_contract_selects_or_authorizes_no_extension() -> None:
    payload = build_payload()
    assert payload["proposed_action_version"] is None
    assert payload["selected_localization_candidate"] is None
    assert payload["selected_enclosure_route"] is None
    assert payload["new_coefficients"] == []
    assert payload["authorization_boundary"]["contract_is_authorization"] is False
    assert payload["authorization_boundary"]["extension_may_be_implemented_now"] is False


def test_contract_has_complete_nonfit_acceptance_boundary() -> None:
    payload = build_payload()
    gates = {row["gate_id"]: row for row in payload["acceptance_gates"]}
    assert set(gates) == {f"LEC_{index:02d}" for index in range(1, 13)}
    assert gates["LEC_04"]["status"] == "OPEN"
    assert gates["LEC_07"]["status"] == "AVAILABLE_UPSTREAM_NOT_YET_ATTACHED"
    assert gates["LEC_11"]["status"] == "OPEN_IF_ANY_COEFFICIENT_IS_PROPOSED"
    assert payload["reusable_subclosures"]["promotion_of_PEI_05_or_PEI_11"] is False


def test_contract_forbids_state_space_to_spacetime_relabelling() -> None:
    forbidden = build_payload()["forbidden_shortcuts"]
    assert "RELABEL_LAMBDA24_ZERO_AS_SIGMA_ENC" in forbidden
    assert "HAND_SELECT_LOCAL_SAME_SPACETIME_ENCLOSURE" in forbidden
    assert "REBUILD_OR_RETUNE_FROZEN_PARTICLE_ASSETS" in forbidden


def test_materialized_contract_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
