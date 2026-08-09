from __future__ import annotations

import json

import numpy as np

from bhsm.interface.completion.eta_knot_color_action_v14_2 import (
    berry_gauge_no_double_counting_payload,
    collective_dirac_action_payload,
    independent_gauss_current_payload,
    topology_sector_payload,
)
from bhsm.interface.completion.eta_knot_color_completion_v14_2 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    HISTORICAL_LIMIT,
    HISTORICAL_VERDICT,
    PRIMARY_VERDICT,
    blocker_falsification_payload,
    cli_status,
    completion_payload,
    lineage_payload,
    materialize,
)
from bhsm.interface.completion.eta_knot_quantization_bundle_v14_2 import (
    boundary_dirac_domain_payload,
    one_particle_hilbert_bundle_payload,
    su3_representation_map_payload,
)
from bhsm.interface.completion.eta_stabilizer_current_v14_2 import (
    VERDICT as SELECTOR_VERDICT,
    covariant_selector_derivative,
    reference_stabilizer_generators,
    selector_current,
    stabilizer_no_current_payload,
)


def test_reference_su3_generators_fix_eta_selector() -> None:
    selector = np.eye(7)[6]
    generators = reference_stabilizer_generators()
    assert len(generators) == 8
    for generator in generators:
        assert np.allclose(generator.T, -generator, atol=1.0e-13)
        assert np.allclose(generator @ selector, 0.0, atol=1.0e-13)


def test_selector_covariant_derivative_equals_partial_derivative() -> None:
    selector = np.eye(7)[6]
    derivative = np.array([0.2, -0.1, 0.3, 0.4, -0.5, 0.1, 0.0])
    result = covariant_selector_derivative(selector, derivative, np.arange(8))
    assert np.allclose(result, derivative, atol=1.0e-13)


def test_selector_color_current_vanishes() -> None:
    selector = np.eye(7)[6]
    derivative = np.array([0.2, -0.1, 0.3, 0.4, -0.5, 0.1, 0.0])
    assert np.allclose(selector_current(selector, derivative, np.arange(8)), 0.0)
    payload = stabilizer_no_current_payload()
    assert payload["validation_passed"]
    assert payload["verdict"] == SELECTOR_VERDICT


def test_hilbert_bundle_fails_closed_at_normalization_and_zero_modes() -> None:
    payload = one_particle_hilbert_bundle_payload()
    assert payload["validation_passed"]
    rows = {row["component"]: row for row in payload["ledger"]}
    assert rows["normalized collective states"]["status"] == "MISSING"
    assert rows["gauge/geometric zero modes"]["status"] == "NOT_SEPARATED_OR_QUOTIENTED"
    assert "NOT_DERIVED" in payload["verdict"]


def test_fr_line_is_recovered_but_not_promoted_to_local_dirac_field() -> None:
    payload = one_particle_hilbert_bundle_payload()
    rows = {row["component"]: row for row in payload["ledger"]}
    assert rows["FR line"]["status"] == "QUANTIZATION_DERIVED"
    assert payload["validation"]["v13_3_admits_physical_bundle_missing"]


def test_rank_three_polarization_is_not_a_physical_triplet_map() -> None:
    payload = su3_representation_map_payload()
    assert payload["validation_passed"]
    assert payload["maps"]["rho_3_or_bar3"] is None
    assert payload["maps"]["transition_map"] is None
    assert payload["classification"].startswith("DIAGNOSTIC_CONDITIONAL")


def test_selector_frame_berry_state_and_physical_connection_are_distinguished() -> None:
    maps = su3_representation_map_payload()["maps"]
    assert "fixed by stabilizer" in maps["stabilizer_selector"]
    assert maps["Berry_connection"].startswith("A^P")
    assert maps["color_charged_knot_state"] is None
    assert maps["independent_connection"].startswith("A on")


def test_collective_dirac_action_is_not_reused_from_eft_as_provenance() -> None:
    payload = collective_dirac_action_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["existing_fermion_term_not_reused_as_eta_derivation"]
    assert "NOT_DERIVED" in payload["verdict"]


def test_no_new_elementary_fermion_is_added() -> None:
    payload = collective_dirac_action_payload()
    assert "NOT_ADDED_AS_AN_INDEPENDENT_UV_FIELD" in payload["effective_field_status"]


def test_gauss_variation_is_typed_conditionally_but_not_promoted() -> None:
    payload = independent_gauss_current_payload()
    assert payload["validation_passed"]
    assert payload["conditional_derivation"]["conditional_equation"] == "D_nu F^{nu mu a}=g3^2 J_eta^{mu a}"
    assert payload["retained_action_result"]["eta_knot_current"] is None
    assert payload["retained_action_result"]["eta_sourced_independent_Gauss_equation"] is None


def test_gauss_contract_preserves_yang_mills_and_topology() -> None:
    validation = independent_gauss_current_payload()["validation"]
    assert validation["YM_principal_symbol_preserved"]
    assert validation["independent_c2_sectors_preserved"]
    assert validation["new_continuous_coefficient_absent"]


def test_color_remains_family_central_and_does_not_insert_kud() -> None:
    payload = independent_gauss_current_payload()
    assert payload["flavor_factorization"] == "rho_color(A) tensor I_C3"
    assert payload["charged_current"] == "J_+^family=I3"
    assert payload["K_ud"] is None


def test_berry_and_independent_color_are_not_double_counted() -> None:
    payload = berry_gauge_no_double_counting_payload()
    assert payload["validation_passed"]
    assert payload["local_same_bundle_identity"].startswith("A=A^P+a")
    assert "cannot be a global reference" in payload["global_warning"]


def test_eta_topology_does_not_remove_independent_instanton_sectors() -> None:
    payload = topology_sector_payload()
    assert payload["validation_passed"]
    assert payload["validation"]["EP_c2_zero"]
    assert payload["validation"]["independent_color_c2_unrestricted"]


def test_boundary_dirac_and_index_fail_closed() -> None:
    payload = boundary_dirac_domain_payload()
    assert payload["validation_passed"]
    assert payload["contract"]["self_adjoint_domain"] is None
    assert payload["contract"]["Euclidean_continuation"] is None
    assert payload["Index_D_rel"] is None
    assert payload["eta_invariant"] is None


def test_recovered_v7_architecture_and_limit_are_preserved_exactly() -> None:
    payload = lineage_payload()
    assert payload["validation_passed"]
    assert payload["historical_verdict"] == HISTORICAL_VERDICT
    assert payload["historical_limit"] == HISTORICAL_LIMIT


def test_falsification_contract_is_constructive_and_no_proxy_is_accepted() -> None:
    payload = blocker_falsification_payload()
    assert payload["validation_passed"]
    assert len(payload["criteria"]) == 6
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_completion_issues_exactly_outcome_c() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["primary_result"] == PRIMARY_VERDICT
    assert payload["Mark_III"] == "NOT_REACHED"
    assert payload["BHSM_physical_completion"] is False
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_completion_preserves_scientific_safeguards() -> None:
    validation = completion_payload()["validation"]
    assert validation["frozen_predictions_unchanged"]
    assert validation["official_prediction_logic_unchanged"]
    assert validation["measured_inputs_not_used"]
    assert validation["new_fields_not_introduced"]
    assert validation["new_continuous_coefficients_not_introduced"]
    assert validation["gauge_dressed_BVP_not_attempted"]


def test_cli_status_matches_completion_gate() -> None:
    status = cli_status()
    assert status["version"] == "v14.2"
    assert status["primary_result"] == PRIMARY_VERDICT
    assert status["exact_next_object"] == EXACT_NEXT_OBJECT


def test_materialization_is_deterministic_and_valid_json(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
    assert len(first) == 11
    for blob in first.values():
        assert json.loads(blob)["validation_passed"]
