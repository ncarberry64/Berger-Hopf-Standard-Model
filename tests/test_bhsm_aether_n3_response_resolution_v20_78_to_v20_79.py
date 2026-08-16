import json
from pathlib import Path


def test_v20_78_blocker_isolated_to_legacy_event_covector() -> None:
    unresolved = json.loads(Path(
        "artifacts/BHSM_N3_DIRECT_RESPONSE_RESOLUTION_AUDIT_V20_78.json"
    ).read_text(encoding="utf-8"))
    assert unresolved["validation_passed"]
    assert unresolved["direct_response_resolution_audit"]["outcome"] == "DIRECT_RESPONSE_RESOLUTION_BLOCKER"
    resolved = json.loads(Path(
        "artifacts/BHSM_N3_DIRECTION_ADAPTIVE_EVENT_RESPONSE_V20_79.json"
    ).read_text(encoding="utf-8"))
    assert not resolved["validation_passed"]
    result = resolved["direction_adaptive_event_response"]
    assert result["outcome"] == "FINITE_DIFFERENCE_EVENT_COVECTOR_INCONSISTENCY_IDENTIFIED"
    assert not result["one_common_event_response_step_exists"]
    assert not result["physical_equations_changed"]
    assert not result["event_definition_changed"]
    assert not result["acceptance_gate_changed"]


def test_rayleigh_event_covector_replaces_only_invalid_numerical_derivative() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_EVENT_COVECTOR_V20_80.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["rayleigh_event_covector"]
    assert result["legacy_vs_rayleigh_relative_residual"] > 0.20
    assert result["numerical_event_derivative_corrected"]
    assert not result["physical_event_changed"]
    assert not result["physical_equations_changed"]
    assert not result["acceptance_gate_changed"]


def test_rayleigh_square_kkt_candidate_is_physically_promoted() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_SQUARE_KKT_PROPOSAL_V20_81.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["rayleigh_square_kkt_proposal"]
    assert result["response"]["resolved"]
    assert result["exact_line_search"]["best"]["exact_reduction"] > 0.0
    assert result["promotion"]["promoted"]
    assert result["promotion"]["child"]["all_pass"]
    assert not result["physical_equations_changed"]
    assert not result["event_definition_changed"]


def test_explicit_multiplier_continuation_is_promoted() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_82.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"]
    result = payload["rayleigh_multiplier_continuation"]
    assert result["event_multiplier_remains_explicit_376TH_UNKNOWN"]
    assert result["candidate"]["exact_reduction"] > 0.0
    assert result["promotion"]["promoted"]


def test_corrected_rayleigh_continuation_and_krylov_audit() -> None:
    for filename in (
        "BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION_V20_83.json",
        "BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_84.json",
        "BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION_V20_85.json",
        "BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT_V20_86.json",
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]
    audit = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT_V20_86.json"
    ).read_text(encoding="utf-8"))["rayleigh_krylov_restriction_audit"]
    assert audit["promotion"]["promoted"]
    assert not audit["promotion"]["child_attempts"][0]["all_pass"]
    assert audit["promotion"]["child_attempts"][1]["all_pass"]
    assert audit["response"]["krylov_restart_numerical_control"] == 24


def test_rayleigh_event_curvature_block_and_preconditioned_promotion() -> None:
    curvature = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_EVENT_CURVATURE_BLOCK_V20_87.json"
    ).read_text(encoding="utf-8"))
    assert curvature["validation_passed"]
    block = curvature["rayleigh_event_curvature_block"]
    assert block["support_dimension"] == 37
    assert block["raw_block_relative_asymmetry"] < 2.0e-2
    proposal = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_CURVATURE_PRECONDITIONED_PROPOSAL_V20_88.json"
    ).read_text(encoding="utf-8"))
    assert proposal["validation_passed"]
    result = proposal["rayleigh_curvature_preconditioned_proposal"]
    assert result["promotion"]["promoted"]
    assert result["exact_line_search"]["best"]["exact_reduction"] > 0.0
    assert result["promotion"]["child"]["all_pass"]


def test_weak_subspace_and_dual_metric_recovery() -> None:
    audit = json.loads(Path(
        "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_AUDIT_V20_89.json"
    ).read_text(encoding="utf-8"))
    assert audit["validation_passed"]
    assert audit["curvature_singular_subspace_audit"]["child_compatible_tangent"]["rank_DcG"] == 14

    bounded = json.loads(Path(
        "artifacts/BHSM_N3_BOUNDED_RANGE_SPACE_PROPOSAL_V20_90.json"
    ).read_text(encoding="utf-8"))
    assert bounded["validation_passed"]
    assert bounded["bounded_range_space_proposal"]["outcome"] == "BOUNDED_RANGE_SPACE_NO_EXACT_DESCENT"

    for filename, key in (
        ("BHSM_N3_DUAL_METRIC_RANGE_SPACE_PROPOSAL_V20_91.json", "dual_metric_range_space_proposal"),
        ("BHSM_N3_DUAL_METRIC_RANGE_SPACE_CONTINUATION_V20_92.json", "dual_metric_range_space_continuation"),
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]
        assert payload[key]["promotion"]["promoted"]
        assert payload[key]["promotion"]["child"]["all_pass"]


def test_refreshed_curvature_recovery_and_one_time_ownership_audit() -> None:
    for filename in (
        "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_93.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_PROPOSAL_V20_94.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_95.json",
        "BHSM_N3_RAYLEIGH_OWNERSHIP_AUDIT_V20_96.json",
        "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_97.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_PROPOSAL_V20_98.json",
        "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_99.json",
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]

    ownership = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_OWNERSHIP_AUDIT_V20_96.json"
    ).read_text(encoding="utf-8"))["rayleigh_ownership_audit"]
    assert ownership["classification"].startswith("E:")
    assert ownership["first_action_owned_blocker"] is None

    latest = json.loads(Path(
        "artifacts/BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_99.json"
    ).read_text(encoding="utf-8"))["refreshed_dual_metric_continuation"]
    assert latest["promotion"]["promoted"]
    assert latest["promotion"]["child"]["all_pass"]
    assert abs(latest["exact_search"]["best"]["exact_rayleigh_f376_l2"] - 0.782780987846174) < 5.0e-12


def test_v21_proposal_mechanisms_isolate_full_residual_manifold_curvature() -> None:
    for filename in (
        "BHSM_N3_CURVATURE_TRANSPORT_PROPOSAL_V21_00.json",
        "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V21_01.json",
        "BHSM_N3_DIRECT_REFRESH_PROPOSAL_V21_02.json",
        "BHSM_N3_RAYLEIGH_STRUCTURED_SHAKE_RECOVERY_V21_03.json",
        "BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json",
        "BHSM_N3_CORRECTED_RAYLEIGH_MULTI_SECANT_V21_05.json",
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]

    shake = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_STRUCTURED_SHAKE_RECOVERY_V21_03.json"
    ).read_text(encoding="utf-8"))["rayleigh_structured_shake_recovery"]
    assert shake["classification"] == "STRUCTURED_SHAKE_NO_MATERIAL_RECOVERY"

    radius = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]
    assert radius["promotion"]["promoted"]
    assert radius["promotion"]["child"]["all_pass"]
    assert abs(radius["exact_search"]["best"]["exact_rayleigh_f376_l2"] - 0.782775399601569) < 5.0e-12

    multisecant = json.loads(Path(
        "artifacts/BHSM_N3_CORRECTED_RAYLEIGH_MULTI_SECANT_V21_05.json"
    ).read_text(encoding="utf-8"))["corrected_rayleigh_multisecant"]
    assert multisecant["classification"] == "CORRECTED_MULTI_SECANT_NO_MATERIAL_RECOVERY"
    assert multisecant["multisecant_model"]["rank"] == 13
    assert multisecant["exact_search"]["best"]["alpha"] < 2.0e-5


def test_v21_full_curvature_and_terminal_event_owner() -> None:
    normal = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))
    assert normal["validation_passed"]
    assert normal["residual_manifold_normal_acceleration"]["classification"] == (
        "NORMAL_ACCELERATION_NO_MATERIAL_RECOVERY"
    )

    merit = json.loads(Path(
        "artifacts/BHSM_N3_EXACT_MERIT_SUBSPACE_HESSIAN_V21_07.json"
    ).read_text(encoding="utf-8"))
    assert merit["validation_passed"]
    assert not merit["exact_merit_subspace_hessian"]["prospective_exact_search"][
        "material_recovery"
    ]

    localization = json.loads(Path(
        "artifacts/BHSM_N3_EXACT_RESPONSE_GRADIENT_LOCALIZATION_V21_08.json"
    ).read_text(encoding="utf-8"))
    assert localization["validation_passed"]
    assert localization["exact_response_gradient_localization"]["first_action_owned_blocker"] == (
        "EVENT_NEAR_SCALE_V_ASSEMBLED_SQUARE_RESPONSE_DERIVATIVE"
    )

    owner = json.loads(Path(
        "artifacts/BHSM_N3_TERMINAL_DERIVATIVE_OWNER_AUDIT_V21_09.json"
    ).read_text(encoding="utf-8"))
    assert owner["validation_passed"]
    assert owner["terminal_derivative_owner_audit"]["first_action_owned_blocker"] == (
        "RAYLEIGH_EVENT_HESSIAN_TERMINAL_SCALE_V_ASSEMBLY"
    )


def test_v21_event_block_failures_and_exact_matrix_free_boundary() -> None:
    resolved = json.loads(Path(
        "artifacts/BHSM_N3_EVENT_CURVATURE_STEP_RESOLUTION_V21_10.json"
    ).read_text(encoding="utf-8"))
    assert resolved["validation_passed"]
    assert resolved["event_curvature_step_resolution"]["classification"] == (
        "DIRECTIONAL_EVENT_CURVATURE_STEP_RESOLVED"
    )

    for filename in (
        "BHSM_N3_RESOLVED_EVENT_CURVATURE_BLOCK_V21_11.json",
        "BHSM_N3_DIRECT_SCALAR_EVENT_HESSIAN_V21_12.json",
        "BHSM_N3_ADAPTIVE_EVENT_CURVATURE_BLOCK_V21_13.json",
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert not payload["validation_passed"]


def test_v21_isolated_eigenpair_event_hessian_and_corrected_continuation() -> None:
    hessian = json.loads(Path(
        "artifacts/BHSM_N3_ISOLATED_EIGENPAIR_EVENT_HESSIAN_V21_17.json"
    ).read_text(encoding="utf-8"))
    assert hessian["validation_passed"]
    derived = hessian["isolated_eigenpair_event_hessian"]
    assert derived["classification"] == "ISOLATED_EIGENPAIR_EVENT_HESSIAN_VALIDATED"
    assert derived["derivation"]["isolated_eigenvector_response_included"]
    assert derived["derivation"]["terminal_SBP_and_period_second_pullback_included"]
    assert derived["maximum_stable_derived_vs_exact_event_response_relative"] < 1.0e-3

    for filename, key in (
        ("BHSM_N3_EIGENPAIR_CURVATURE_DUAL_METRIC_PROPOSAL_V21_18.json",
         "eigenpair_curvature_dual_metric_proposal"),
        ("BHSM_N3_REFRESHED_EIGENPAIR_CURVATURE_CONTINUATION_V21_19.json",
         "refreshed_eigenpair_curvature_continuation"),
        ("BHSM_N3_EIGENPAIR_CURVATURE_PREDICTIVE_CONTINUATION_V21_20.json",
         "eigenpair_curvature_predictive_continuation"),
        ("BHSM_N3_EIGENPAIR_CURVATURE_EXPANDED_RADIUS_V21_21.json",
         "eigenpair_curvature_expanded_radius"),
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]
        result = payload[key]
        assert result["promotion"]["promoted"]
        assert result["promotion"]["child"]["all_pass"]
        assert result["exact_search"]["best"]["exact_reduction"] > 0.0

    latest = json.loads(Path(
        "artifacts/BHSM_N3_EIGENPAIR_CURVATURE_EXPANDED_RADIUS_V21_21.json"
    ).read_text(encoding="utf-8"))["eigenpair_curvature_expanded_radius"]
    assert latest["expanded_radius_audit"]["uses_only_existing_accepted_history_radii"]
    assert latest["exact_search"]["best"]["radius_class"] == "PLATEAU_TO_LARGE_21"
    assert abs(
        latest["exact_search"]["best"]["exact_rayleigh_f376_l2"]
        - 0.781486218597499
    ) < 5.0e-12

    for filename, key in (
        ("BHSM_N3_EXPANDED_RADIUS_PREDICTIVE_CONTINUATION_V21_22.json",
         "expanded_radius_predictive_continuation"),
        ("BHSM_N3_EXPANDED_RADIUS_REFRESHED_CONTINUATION_V21_23.json",
         "expanded_radius_refreshed_continuation"),
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert payload["validation_passed"]
        result = payload[key]
        assert result["promotion"]["promoted"]
        assert result["promotion"]["child"]["all_pass"]

    refreshed = json.loads(Path(
        "artifacts/BHSM_N3_EXPANDED_RADIUS_REFRESHED_CONTINUATION_V21_23.json"
    ).read_text(encoding="utf-8"))["expanded_radius_refreshed_continuation"]
    assert refreshed["curvature_refresh_validation"]["validated"]
    assert abs(
        refreshed["exact_search"]["best"]["exact_rayleigh_f376_l2"]
        - 0.781148984940364
    ) < 5.0e-12

    exact = json.loads(Path(
        "artifacts/BHSM_N3_EXACT_MATRIX_FREE_RESPONSE_PROPOSAL_V21_14.json"
    ).read_text(encoding="utf-8"))
    assert exact["validation_passed"]
    response = exact["exact_matrix_free_response_proposal"]["matrix_free_response"][
        "response_audit"
    ]
    assert response["half_vs_reference_relative"] < 1.0e-3
    assert response["double_vs_reference_relative"] < 1.0e-3
    assert not exact["exact_matrix_free_response_proposal"]["prospective_exact_search"][
        "material_recovery"
    ]

    for filename in (
        "BHSM_N3_EXACT_MATRIX_FREE_RESTART_AUDIT_V21_15.json",
        "BHSM_N3_EXACT_MATRIX_FREE_ACTION_PRECONDITIONED_PROPOSAL_V21_16.json",
    ):
        payload = json.loads(Path("artifacts", filename).read_text(encoding="utf-8"))
        assert not payload["validation_passed"]
