from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_bhsm_encapsulation_realization_ontology.py"
ARTIFACT = ROOT / "artifacts/current_semantics/BHSM_ENCAPSULATION_REALIZATION_ONTOLOGY.json"


def _module():
    spec = importlib.util.spec_from_file_location("bhsm_encapsulation_ontology", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_materialized_ontology_is_deterministic_and_fail_closed() -> None:
    payload = _module().build_payload()
    assert payload == json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["scope_adjudication"]["Gate7_status"] == "ACTIVE_NOT_CLOSED"
    assert payload["validation"]["Gate7_math_and_active_blocker_preserved"]
    assert not any(payload["guardrails"].values())


def test_claims_separate_derived_local_bridge_from_open_physical_volume() -> None:
    claims = {row["id"]: row for row in _module().build_payload()["claim_ledger"]}
    assert claims["ONE_CURRENT_ACTION_OWNER"]["classification"] == "VALIDATED"
    assert claims["LOCAL_CARRIER_STATE_ENCLOSURE_BRIDGE"]["classification"] == "VALIDATED"
    assert claims["COMPLETE_INTERACTING_SPACETIME_VOLUME_ENCLOSURE"]["classification"] == "OPEN"
    assert claims["TOPOLOGICAL_ZERO_INTERIOR_FERMION_CLASS"]["classification"] == "HYPOTHESIS"
    assert claims["HADRON_FIRST_SPACETIME_VOLUME_ONSET"]["classification"] == "HYPOTHESIS"
    assert claims["CURRENT_GATE7_PARTICLE_UNIVERSALITY"]["classification"] == "OPEN"
    assert claims["TWO_ELECTRON_SUPERCONDUCTOR"]["classification"] == "INVALIDATED"


def test_realization_and_decay_dependency_graphs_are_explicit() -> None:
    payload = _module().build_payload()
    assert [row["id"] for row in payload["environment_conditioned_realization_dag"]] == [
        "R1", "R2", "R3", "R4", "R5", "R6"
    ]
    assert [row["id"] for row in payload["stability_to_decay_dependency_dag"]] == [
        "D1", "D2", "D3", "D4", "D5", "D6", "D7"
    ]
    assert all(row["status"] == "OPEN" for row in payload["stability_to_decay_dependency_dag"])
    assert payload["prediction_firewall"]["order"] == [
        "DERIVE", "CERTIFY", "FREEZE_AND_HASH", "PREDICT", "COMPARE"
    ]


def test_authoritative_current_surfaces_reject_explicit_overclaim_sentinels() -> None:
    surfaces = [
        ROOT / "STATUS.md",
        ROOT / "docs/BHSM_CURRENT_ENCAPSULATION_SCOPE.md",
        ROOT / "artifacts/current_semantics/BHSM_ENCAPSULATION_REALIZATION_ONTOLOGY.json",
        ROOT / "artifacts/BHSM_PHYSICAL_COMPLETENESS_MATRIX.json",
        ROOT / "artifacts/current_semantics/BHSM_CURRENT_SYSTEM_INTEGRATION_MAP.json",
    ]
    forbidden = [
        r"ALL_PARTICLES_SHARE_ONE_TRAJECTORY\s*=\s*TRUE",
        r"EVERY_ELEMENTARY_PARTICLE_ENCLOSES_SPACETIME\s*=\s*TRUE",
        r"PROTON_NEUTRON_SPACETIME_ENCLOSURE_DERIVED\s*=\s*TRUE",
        r"TWO_ELECTRONS_ALONE_CONSTITUTE_SUPERCONDUCTIVITY\s*=\s*TRUE",
        r"GATE7_PROVES_ALL_PARTICLE_SPECIFIC_REALIZATIONS\s*=\s*TRUE",
        r"ENCAPSULATION_STABILITY_DERIVES_DECAY_RATES\s*=\s*TRUE",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in surfaces)
    assert not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in forbidden)
