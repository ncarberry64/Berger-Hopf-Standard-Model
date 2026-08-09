from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from bhsm.interface.aether_backward_closure_existing_answer_audit_v15_8 import (
    CLASSIFICATIONS,
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    REPOSITORY_EXISTING_ANSWER_EXHAUSTED,
    backward_closure_payload,
    composition_payload,
    deterministic_json,
    existing_answer_table,
    first_action_source_audit,
    formation_composition_eligible,
    formation_mechanism_payload,
    historical_result_rows,
    mass_and_scale_payload,
    materialize,
    reverse_dependency_rows,
)


ROOT = Path(__file__).resolve().parents[1]


def test_backward_audit_exhausted_existing_answers_but_not_bhsm() -> None:
    assert REPOSITORY_EXISTING_ANSWER_EXHAUSTED is True
    assert FULL_BHSM_COMPLETE is False
    payload = backward_closure_payload()
    assert payload["REPOSITORY_EXISTING_ANSWER_EXHAUSTED"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_required_existing_answer_table_has_every_named_row() -> None:
    rows = {row["requirement"]: row for row in existing_answer_table()}
    assert set(rows) == {
        "Parent surface", "Local physical tangent", "Hessian", "Negative mode",
        "Nonlinear branch", "Self-adjoint domain", "Formation energy ledger",
        "Relative periodic orbit", "Cycle energy", "E=mc^2 readout",
        "Family mass operator", "Absolute scale",
    }
    assert rows["E=mc^2 readout"]["status"] == "ALREADY_PRESENT"
    assert rows["Formation energy ledger"]["classification"] == "CURRENT_DERIVED_CONDITIONAL"


def test_no_existing_action_term_is_promoted_as_formation_trigger() -> None:
    assert first_action_source_audit()["action_owned_formation_trigger_identified"] is False


def test_all_thirteen_atomic_requirements_are_mapped_once() -> None:
    rows = reverse_dependency_rows()
    assert len(rows) == 13
    assert len({row["requirement"] for row in rows}) == 13
    assert rows[0]["requirement"].startswith("A_")
    assert rows[-1]["requirement"].startswith("M_")


def test_every_historical_classification_is_from_closed_vocabulary() -> None:
    allowed = set(CLASSIFICATIONS)
    assert all(row["classification"] in allowed for row in reverse_dependency_rows())
    assert all(row["classification"] in allowed for row in historical_result_rows())


def test_self_adjoint_domain_is_not_globally_called_missing() -> None:
    row = next(row for row in reverse_dependency_rows() if row["requirement"].startswith("F_"))
    assert row["status"] == "DOMAIN_THEOREM_CLASSES_EXIST"
    assert "attachment" in row["missing_only"]


def test_instability_questions_are_separated() -> None:
    payload = composition_payload()
    assert payload["question_A_instability_criterion"] == "YES_CONDITIONALLY"
    assert payload["question_B_unstable_physical_configuration"].startswith("NO_")
    assert payload["question_C_nonlinear_destination"].startswith("NO_")


def test_first_missing_arrow_is_narrower_than_v15_7_chain() -> None:
    assert EXACT_NEXT_OBJECT == composition_payload()["first_missing_arrow"]
    assert "MASS" not in EXACT_NEXT_OBJECT
    assert "CAVITATION" not in EXACT_NEXT_OBJECT
    assert "PERSISTENCE" not in EXACT_NEXT_OBJECT


def test_cavitation_is_only_one_candidate_mechanism() -> None:
    payload = formation_mechanism_payload()
    assert payload["cavitation_role"].startswith("ONE_CANDIDATE")
    assert len(payload["candidate_mechanisms"]) >= 3
    assert payload["action_selected_unique_mechanism"] is None


def test_v14_93_control_is_preserved_but_generalized() -> None:
    control = formation_mechanism_payload()["v14_93_control"]
    assert control["historical_label"] == "ZERO_MODE_WITHOUT_CAVITATION"
    assert control["generic_classification"].endswith("RADIAL_ENCAPSULATION")
    assert control["global_no_go"] is False


def test_mass_energy_readout_is_already_present_and_not_a_trigger() -> None:
    payload = mass_and_scale_payload()
    assert payload["E_EQUALS_MC2_ROLE"] == "ALREADY_PRESENT"
    assert payload["no_mass_energy_equivalence_rederivation"] is True
    assert payload["no_mass_used_as_formation_trigger"] is True


def test_historical_mass_operator_remains_provenance_blocked() -> None:
    payload = mass_and_scale_payload()
    assert payload["HISTORICAL_EXPLICIT_MASS_OPERATOR"].startswith("PROVENANCE_BLOCKED")
    assert "ZERO_INPUT" in payload["ABSOLUTE_SCALE_ACTUAL_STATUS"]


@pytest.mark.parametrize("missing", range(4))
def test_formation_composition_requires_every_arrow(missing: int) -> None:
    gates = [True] * 4
    gates[missing] = False
    assert formation_composition_eligible(
        localized_unstable_configuration=gates[0],
        physical_domain_attached=gates[1],
        same_action_nonlinear_endpoint=gates[2],
        continuous_solution_branch=gates[3],
    ) is False


def test_complete_composition_gate_can_close() -> None:
    assert formation_composition_eligible(
        localized_unstable_configuration=True,
        physical_domain_attached=True,
        same_action_nonlinear_endpoint=True,
        continuous_solution_branch=True,
    ) is True


def test_integrity_firewalls_and_usb_prohibition() -> None:
    certificate = backward_closure_payload()["no_retuning_certificate"]
    assert certificate
    assert all(value is False for value in certificate.values())


def test_json_is_strict_and_deterministic(tmp_path: Path) -> None:
    encoded = deterministic_json(backward_closure_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded
    assert json.loads(encoded)["version"] == "v15.8"
    first = materialize(tmp_path / "a")[0]
    second = materialize(tmp_path / "b")[0]
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()


def test_committed_artifact_matches_materializer(tmp_path: Path) -> None:
    generated = materialize(tmp_path)[0]
    committed = ROOT / "artifacts" / generated.name
    assert generated.read_bytes() == committed.read_bytes()
