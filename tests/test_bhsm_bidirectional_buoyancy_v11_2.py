from __future__ import annotations

import json
from math import isclose, pi

import pytest

from bhsm.interface.completion import final_completion_gate_v11_2 as gate
from bhsm.interface.completion.bidirectional_buoyancy_v11_2 import (
    CASIMIR_VERDICT,
    NEXT_OBJECT,
    VERDICT,
    black_hole_payload,
    boundary_pressure_payload,
    casimir_payload,
    casimir_pressure_benchmark,
    displacement_payload,
    exchange_current_payload,
    fixed_encapsulation_payload,
    induced_metric_variation,
    ontology_payload,
    relational_interval,
    spherical_flux_density,
    steering_payload,
)
from bhsm.interface.completion.primitive_support_character_ledger_v11_2 import ledger_payload
from bhsm.interface.completion.support_character_constraint_system_v11_2 import constraint_matrix, constraint_payload


def test_intrinsic_and_extrinsic_geometry_are_separate_and_fail_closed() -> None:
    payload = fixed_encapsulation_payload()
    assert induced_metric_variation(2, -1, 0) == 0
    assert induced_metric_variation(0, 0, 1) != 0
    assert payload["ordinary_motion_invariance_automatic"] is False
    assert payload["action_owned_constraint_or_stability_term"] is None
    assert payload["support_character"]["intrinsic_metric"] == 0


def test_relational_interval_is_covariant_scalar_candidate() -> None:
    assert relational_interval([[-1, 0], [0, 1]], [3, 4]) == 7
    payload = displacement_payload()
    assert "Synge" in payload["global_covariant_candidate"]
    assert payload["q_D_reclassification"].startswith("OPEN")


def test_spherical_flux_has_inverse_square_dilution_but_not_plate_law() -> None:
    assert isclose(spherical_flux_density(8 * pi, 2), 0.5)
    assert isclose(spherical_flux_density(8 * pi, 4), 0.125)
    with pytest.raises(ValueError):
        spherical_flux_density(1, 0)
    payload = displacement_payload()
    assert payload["inverse_square_is_force_law"] is False
    assert payload["plate_casimir_uses_inverse_square"] is False


def test_exchange_current_and_black_hole_transfer_require_conserved_channels() -> None:
    exchange = exchange_current_payload()
    transfer = black_hole_payload()
    assert exchange["action_derived_decomposition"] is None
    assert exchange["new_independent_current_field"] is False
    assert transfer["trigger"] is transfer["transfer_map"] is transfer["Gamma_BH"] is None
    assert transfer["surface_receiving_domain"] is None


def test_casimir_is_external_a_minus_four_benchmark_and_no_double_counting() -> None:
    assert isclose(casimir_pressure_benchmark(2) / casimir_pressure_benchmark(4), 16)
    spectral = boundary_pressure_payload()
    casimir = casimir_payload()
    assert spectral["boundary_operator"] is None
    assert "must be identified or proved independent" in spectral["no_double_counting_rule"]
    assert casimir["exact_coefficient_reproduced_by_bhsm"] is None
    assert casimir["additional_bhsm_contribution"] is None
    assert casimir["verdict"] == CASIMIR_VERDICT


def test_expanded_character_matrix_preserves_prior_result_and_does_not_invent_rows() -> None:
    payload = constraint_payload()
    matrix = constraint_matrix()
    assert matrix.shape == (12, 19)
    assert payload["pre_ontology_result_preserved"] == {"shape": [12, 12], "rank": 7, "nullity": 5}
    assert payload["rank"] == 7 and payload["nullity"] == 12
    assert payload["common_normalization_direction"] is None
    assert payload["inconsistent_rows"] == []
    assert payload["ontology_rows_not_promoted"]


def test_attachment_is_leading_candidate_not_action_owned() -> None:
    rows = {row["object"]: row for row in ledger_payload()["primitive_objects"]}
    assert rows["intrinsic_enclosure_metric"]["candidate_support_character"].startswith("0")
    assert rows["core_surface_attachment"]["candidate_support_character"] == "w_attachment open"
    assert rows["core_surface_attachment"]["existing_action_source"] is None
    assert ontology_payload()["classification"] == "AUTHOR_ONTOLOGY_CLARIFICATION"


def test_gate_materializes_required_artifacts_deterministically_without_promotion(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in gate.materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in gate.materialize(tmp_path)}
    assert first == second
    for filename in [
        "BHSM_bidirectional_topological_buoyancy_ontology_v11_2.json",
        "BHSM_fixed_encapsulation_geometry_v11_2.json",
        "BHSM_relational_spacetime_displacement_v11_2.json",
        "BHSM_core_surface_exchange_current_v11_2.json",
        "BHSM_boundary_spectral_pressure_v11_2.json",
        "BHSM_casimir_reproduction_gate_v11_2.json",
        "BHSM_black_hole_de_envelopment_transfer_v11_2.json",
    ]:
        assert json.loads(first[filename])["validation_passed"]
    result = steering_payload()
    assert result["primary_verdict"] == VERDICT
    assert result["exact_next_object"] == NEXT_OBJECT
    assert result["supported_action"]["complete"] is False
    assert result["physical_outputs_promoted"] == []
    assert result["frozen_predictions_changed"] is False
