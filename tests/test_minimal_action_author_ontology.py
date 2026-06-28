from __future__ import annotations

import json
from pathlib import Path

from bhsm.interface.minimal_action import load_author_ontology, require_author_axiom


ROOT = Path(__file__).resolve().parents[1]


def test_author_ontology_is_machine_readable_and_controlling() -> None:
    payload = load_author_ontology(ROOT)
    assert payload["source_status"] == "DISCOVERED"
    assert payload["author_supplied"] is True
    assert payload["ontology_status"] == "ACTIVE_CONTROLLING_THEORY_DICTIONARY"
    assert payload["public_status"] == "structural architecture integrated conditional; numerical closure open"
    assert len(payload["axioms"]) == 4


def test_ontology_records_exact_cp_x_ch_and_neutrino_semantics() -> None:
    payload = load_author_ontology(ROOT)
    cp = require_author_axiom(payload, "CP_IS_Z6_BOUNDARY_HOLONOMY_CONSTRAINT")
    x_ch = require_author_axiom(payload, "X_CH_IS_CHARGED_BOUNDARY_RESPONSE_OPERATOR")
    neutrino = require_author_axiom(
        payload, "NEUTRINO_MASS_IS_PROPAGATION_LOCKED_CURVATURE_RESPONSE"
    )
    assert cp.maximum_status == "ARTIFACT_BACKED"
    assert cp.standalone_target_status == "RETIRED_TARGET"
    assert x_ch.maximum_status == "CONDITIONAL_ACTION_THEOREM"
    assert "P_ch" in x_ch.definitions["sector_projector"]
    assert neutrino.maximum_status == "CONDITIONAL_PROPAGATION_THEOREM"
    assert "secondary" in neutrino.definitions["dirac_majorana_role"]


def test_ontology_guardrails_forbid_empirical_or_runtime_promotion() -> None:
    raw = json.loads((ROOT / "artifacts/BHSM_author_ontology_v0_8.json").read_text())
    assert all(value is False for value in raw["guardrails"].values())
    text = json.dumps(raw).lower()
    for forbidden in ("observed masses", "pdg theorem input", "w calibration theorem input"):
        assert forbidden not in text
