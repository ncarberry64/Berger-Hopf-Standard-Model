import json
from pathlib import Path

from boundary_derivation import DerivationStatus, default_boundaries
from boundary_operator_derivation_sprint import (
    STRUCTURALLY_MOTIVATED_NOT_DERIVED,
    derivation_sprint_payload,
)
from mode_selection import EXPECTED_LEDGER, omega_down, omega_lepton, omega_up


ROOT = Path(__file__).resolve().parents[1]


def test_boundary_derivation_sprint_outputs_exist():
    assert ROOT.joinpath("theory/boundary_operator_derivation_sprint.md").exists()
    assert ROOT.joinpath("audits/boundary_operator_derivation_sprint_audit.md").exists()
    assert ROOT.joinpath("audits/boundary_operator_derivation_sprint_audit.json").exists()


def test_boundary_derivation_sprint_classification_is_not_derived():
    payload = json.loads(
        ROOT.joinpath("audits/boundary_operator_derivation_sprint_audit.json").read_text()
    )

    assert payload["p0_blocker"] == "BOUNDARY_OPERATORS_NOT_ACTION_DERIVED"
    assert payload["classification"] == STRUCTURALLY_MOTIVATED_NOT_DERIVED
    assert payload["p0_boundary_blocker_closed"] is False
    assert payload["action_derived"] is False
    assert payload["spectral_derived"] is False
    assert payload["boundary_derived"] is False


def test_existing_boundary_statuses_remain_action_linked_not_action_derived():
    boundaries = default_boundaries()

    assert all(boundary.derivation_status == DerivationStatus.ACTION_LINKED for boundary in boundaries.values())
    assert all(boundary.derivation_status != DerivationStatus.ACTION_DERIVED for boundary in boundaries.values())


def test_sprint_reproduces_operational_values_without_claiming_proof():
    payload = derivation_sprint_payload()
    functions = {
        "lepton": omega_lepton,
        "up": omega_up,
        "down": omega_down,
    }
    expected_targets = {"lepton": 3, "up": 6, "down": 12}

    for finding in payload["findings"]:
        assert finding.target == expected_targets[finding.sector]
        for mode in EXPECTED_LEDGER[finding.sector]:
            assert functions[finding.sector](*mode) == finding.target
        assert finding.selected_modes_satisfy_target is True
        assert finding.derivation_status == "ACTION_LINKED"


def test_sprint_answers_no_help_for_z_or_ckm_exponent():
    payload = json.loads(
        ROOT.joinpath("audits/boundary_operator_derivation_sprint_audit.json").read_text()
    )

    assert payload["helps_derive_z_virt_u2_half"] is False
    assert payload["helps_derive_ckm_exponent_1_16"] is False


def test_frozen_prediction_files_not_repurposed_by_sprint():
    frozen_md = ROOT.joinpath("docs/frozen_predictions.md").read_text()
    frozen_json = ROOT.joinpath("docs/frozen_predictions.json").read_text()

    assert "boundary_operator_derivation_sprint" not in frozen_md
    assert "boundary_operator_derivation_sprint" not in frozen_json


def test_report_names_required_extra_structure_and_limitations():
    text = ROOT.joinpath("theory/boundary_operator_derivation_sprint.md").read_text()

    assert "Classification: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`" in text
    assert "The blocker therefore remains open" in text
    assert "self-adjoint-domain" in text
    assert "does not derive Z_virt" in text
    assert "CKM 1/16" in text
