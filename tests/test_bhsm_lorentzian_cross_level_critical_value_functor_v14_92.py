import json

from bhsm.interface.completion.lorentzian_cross_level_critical_value_functor_v14_92 import (
    EXACT_NEXT_OBJECT,
    action_and_kkt_ledger,
    bundle_connection_theorem,
    canonical_and_domain_witnesses,
    completion_payload,
    critical_value_witness,
    dirac_domain_theorem,
    historical_architecture,
    materialize,
    metric_gauss_and_coefficient_status,
    nonlinear_reduction,
    reduction_composition_witness,
    reduction_map_ledger,
    retained_repository_provenance_audit,
    tangent_finite_difference,
    weighted_adjoint_witness,
)


def test_historical_chain_requires_m5_and_composes_only_on_admissible_data() -> None:
    history = historical_architecture()
    assert history["M5_is_required"] is True
    assert history["direct_geometric_M8_to_M4_quotient"] is False
    assert history["direct_R_84"].startswith("defined_only")
    assert nonlinear_reduction.__name__ == "nonlinear_reduction"
    assert reduction_composition_witness()["residual"] < 1.0e-13


def test_negative_theorem_is_anchored_to_retained_repository_payloads() -> None:
    audit = retained_repository_provenance_audit()
    assert audit["passed"] is True
    assert all(audit["checks"].values())


def test_reduction_ledger_does_not_fabricate_physical_maps() -> None:
    rows = {row["sector"]: row for row in reduction_map_ledger()}
    assert rows["metric"]["physical_functor"] == "CONDITIONAL"
    assert rows["degree_one_eta"]["R85"] is None
    assert rows["physical_SU3_gauge"]["R85"] is None
    assert rows["Dirac"]["R54"] is None


def test_tangent_and_weighted_adjoint_identities() -> None:
    assert tangent_finite_difference()["error"] < 1.0e-9
    assert weighted_adjoint_witness()["residual"] < 1.0e-13


def test_envelope_and_schur_theorems() -> None:
    witness = critical_value_witness()
    assert witness["parent_stationarity_residual"] < 1.0e-13
    assert witness["envelope_gradient_error"] < 1.0e-9
    assert witness["schur_hessian_error"] < 2.0e-6
    assert min(witness["schur_eigenvalues"]) > 0.0


def test_conditional_symplectic_green_gauge_and_cocycle_witnesses() -> None:
    witness = canonical_and_domain_witnesses()
    assert witness["conditional_cotangent_lift_symplectic_residual"] < 1.0e-13
    assert witness["intrinsic_two_sided_Dirac_Green_residual"] < 1.0e-13
    assert witness["conditional_bundle_cocycle_residual"] < 1.0e-13
    assert witness["conditional_gauge_covariance_residual"] < 1.0e-13
    assert witness["physical_cross_level_symplectic_map"] is None


def test_common_physical_bundle_connection_is_obstructed() -> None:
    theorem = bundle_connection_theorem()
    assert theorem["parent_bundle"].startswith("Sp1")
    assert theorem["explicit_historical_boundary"] == "omega_is_not_the_SM_gauge_field"
    assert theorem["physical_M4_gauge_projection"] is None
    assert theorem["transition_cocycle_intertwiner"] is None


def test_dirac_is_intrinsic_foundational_not_parent_derived() -> None:
    theorem = dirac_domain_theorem()
    assert theorem["M8_parent_Dirac_field"] is None
    assert theorem["cross_level_common_domain"] is None
    assert theorem["self_adjointness_verdict"].startswith("CLOSED_INTRINSICALLY")


def test_stratified_action_is_not_critical_value_of_s8_alone() -> None:
    ledger = action_and_kkt_ledger()
    assert len(ledger["KKT"]) == 5
    assert ledger["is_Crit_of_S8_alone"] is False
    assert ledger["physical_stationarity_commutes_with_reduction"] is False


def test_v14_91_locus_is_not_action_selected() -> None:
    status = metric_gauss_and_coefficient_status()
    assert status["locus_is_exact_stationarity_condition"] is True
    assert status["locus_action_selected"] is False
    assert "do_not_vary_or_select" in status["reason"]


def test_completion_boundary_and_exact_next_object() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["full_coupled_stationary_background"] is None
    assert payload["physical_projector"] is None
    assert payload["DeltaPi"] is None
    assert payload["M_plus_minus"] is None
    assert payload["B_dyn_L2"] is None
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["completion_status"]["FULL_BHSM_COMPLETE"] is False
    assert payload["completion_status"]["USB_SYNCHRONIZATION_ELIGIBLE"] is False


def test_materializer_is_deterministic_and_strict_json(tmp_path) -> None:
    target = tmp_path / "v14_92.json"
    first = materialize(target).read_bytes()
    second = materialize(target).read_bytes()
    assert first == second
    assert json.loads(first) == completion_payload()
