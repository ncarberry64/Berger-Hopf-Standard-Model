from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface.ae3_reciprocal_join_localization import (
    ACTION_VERSION,
    CARRIER_ID,
    SELECTED_ROUTE,
    current_full_field_attachment_ledger,
    enclosure_transport_square_certificate,
    family_fiber_transport_certificate,
    localization_weight,
    minimal_even_quadratic_coefficients,
    ranked_carrier_candidates,
    reciprocal_join_profile,
    regular_carrier_certificate,
    systems_integration_puzzle,
)
from bhsm.interface.aether_jax_full_local_action import _constants
from scripts.materialize_ae3_reciprocal_join_localization import (
    TARGET,
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_ae3_reciprocal_join_localization.py"


def test_retained_n12_localization_profile_is_promoted_exactly() -> None:
    constants = _constants()
    chi = np.asarray(constants["chi"])
    retained = np.asarray(constants["localization"])
    promoted = localization_weight(reciprocal_join_profile(chi))
    assert np.max(np.abs(retained - promoted)) <= 1.0e-15


def test_reciprocal_join_carrier_has_one_regular_oriented_interface() -> None:
    certificate = regular_carrier_certificate()
    assert certificate["regular_level_set"] is True
    assert certificate["sigma_endpoints"] == [-0.5, 0.5]
    assert abs(certificate["zero_coordinate"] - np.pi / 4.0) <= 1.0e-15
    assert abs(certificate["transversality_at_zero"] - 4.0 / np.pi) <= 1.0e-15
    assert certificate["inside_sign"] == "sigma<0"
    assert certificate["outside_sign"] == "sigma>0"


def test_localized_hopf_weight_is_the_unique_minimal_even_quadratic() -> None:
    a, b = minimal_even_quadratic_coefficients()
    assert a == 1.0
    assert b == -4.0
    assert localization_weight(0.0) == 1.0
    assert localization_weight(-0.5) == 0.0
    assert localization_weight(0.5) == 0.0


def test_candidate_ranking_selects_response_promotion_without_new_physics() -> None:
    rows = ranked_carrier_candidates()
    assert rows[0]["candidate_id"] == CARRIER_ID
    assert rows[0]["result"] == "SELECTED_MINIMAL_POST_AE2_EXTENSION"
    assert rows[0]["new_physical_fields"] == 0
    assert rows[0]["new_continuous_coefficients"] == 0
    assert rows[1]["result"].endswith("NOT_SELECTED_AS_THE_MATERIAL_ACTION")
    assert rows[-1]["candidate_id"] == "SPACETIME_EDGE_TRANSITION"


def test_all_nine_frozen_family_slots_are_real_C2_fibers_and_commute() -> None:
    reset = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    certificate = family_fiber_transport_certificate(reset)
    assert certificate["certificate_passed"] is True
    assert certificate["all_frozen_slots_instantiated_as_real_fibers"] is True
    assert certificate["particle_species_selected_by_geometry"] is False
    assert len(certificate["rows"]) == 9
    assert all(row["commutator_residual"] == 0.0 for row in certificate["rows"])


def test_reset_family_projection_and_enclosure_restriction_square_commutes() -> None:
    reset = np.array([[0.0, 1.0], [-1.0, 0.0]], dtype=complex)
    certificate = enclosure_transport_square_certificate(reset, samples=17)
    assert certificate["certificate_passed"] is True
    assert certificate["smooth_localization_map_is_a_projector"] is False
    assert certificate["time_evolution_intertwiner_claimed"] is False
    assert certificate["reset_restriction_commutator"] == 0.0
    assert certificate["reset_carrier_commutator"] == 0.0
    assert certificate["restriction_idempotency_residual"] == 0.0
    assert len(certificate["rows"]) == 9


def test_historical_zero_source_cycle_is_not_relabelled_as_current_C2_action() -> None:
    ledger = current_full_field_attachment_ledger()
    assert ledger["blocks"]["geometry"]["status"] == "ATTACHED"
    assert ledger["blocks"]["fermion"]["current_C2_action_owned"] is False
    assert ledger["historical_common_superdeterminant_promoted_to_current_C2"] is False
    assert ledger["continuous_coefficient_choice_would_fix_this_mismatch"] is False
    assert ledger["complete_current_full_field_action_attached"] is False


def test_systems_integration_puzzle_advances_sections_without_serial_gates() -> None:
    puzzle = systems_integration_puzzle()
    assert puzzle["serial_gate_order_required"] is False
    assert puzzle["section_updates_allowed_when_locally_compatible"] is True
    assert set(puzzle["sections"]) == {
        "full_field_action",
        "localization_enclosure",
        "particle_identity_transport",
        "family_mass_hierarchy",
        "muon_magnetic_moment",
        "collisions_and_decays",
        "new_particle_and_phenomenon_forecasts",
        "gravity_and_cosmology",
    }
    assert puzzle["sections"]["muon_magnetic_moment"]["prediction_emitted"] is False
    assert puzzle["sections"]["full_field_action"]["complete"] is False
    assert "charged_lepton_family_slot_1_mode_label_(5,2)" in puzzle[
        "sections"
    ]["muon_magnetic_moment"]["fitted_pieces"]


def test_ae3_claim_boundary_closes_carrier_but_not_full_field_balance() -> None:
    payload = build_payload()
    assert payload["action_version"] == ACTION_VERSION
    assert payload["carrier_map"]["route"] == SELECTED_ROUTE
    assert payload["ACTION_OWNED_LOCALIZATION_CARRIER_DERIVED"] is True
    assert payload["BHSM_NATIVE_FAMILY_MODE_STATE_TRANSPORTED_THROUGH_LOCALIZATION"] is True
    assert payload["EXISTING_SM_MANIFESTATION_READOUT_PRESERVED"] is True
    assert payload["physical_transport_square"]["certificate_passed"] is True
    assert payload["nonlinear_completion"][
        "historical_response_constrained_both_ADM_constraints_solved"
    ] is True
    assert payload["PHYSICAL_ENCAPSULATION_IDENTIFIED"] is False
    assert payload["physical_encapsulation_rows"]["PEI_05"] is False
    assert payload["physical_encapsulation_rows"]["PEI_07"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["validation_passed"] is True


def test_materialized_ae3_artifact_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["selected_candidate"] == CARRIER_ID
    assert payload["validation_passed"] is True
