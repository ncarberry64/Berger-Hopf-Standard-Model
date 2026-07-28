from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import x_r4_moduli_tangent_resolution as resolution


def test_x_frw_provenance_and_object_type():
    ledger = resolution.source_ledger()
    x = ledger["symbols"]["X_FRW"]
    assert x["definition"] == "H^2+a^-2"
    assert "homogeneous" in x["type"]
    assert ledger["questions"]["5_X_varied_off_shell"] is False
    assert ledger["questions"]["6_X_eliminated_before_promotion"] is True


def test_fold_control_and_collective_field_are_distinct():
    questions = resolution.source_ledger()["questions"]
    assert questions["1_fold_control_parameter"].startswith("mu=-A5/Z5")
    assert questions["2_collective_field"].startswith("q=r=|epsilon|")
    assert questions["4_q_dimensionless"] is True


def test_delta_x_is_derivative_times_collective_amplitude():
    assert resolution.dx_dq() == resolution.TAU * resolution.CHI_1
    answer = resolution.source_ledger()["questions"]["3_delta_X"]
    assert "dX_FRW/dq|0=tau chi_1" in answer
    assert "delta X_FRW=tau chi_1 q" in answer


def test_action_selected_maximally_symmetric_normalization():
    assert resolution.maximally_symmetric_scalar_curvature() == 12 * resolution.X
    assert (
        resolution.dr4_dq_maximally_symmetric()
        == 12 * resolution.TAU * resolution.CHI_1
    )


def test_static_branch_normalization_is_distinct():
    assert resolution.static_scalar_curvature() == 6 * resolution.X
    assert (
        resolution.dr4_dq_static()
        == 6 * resolution.TAU * resolution.CHI_1
    )
    comparison = resolution.normalization_ledger()["static_comparison"]
    assert "distinct homogeneous branches" in comparison["no_conflict_reason"]


def test_coefficient_one_target_is_superseded_not_rewritten():
    target = resolution.normalization_ledger()["coefficient_one_target"]
    assert target["classification"].startswith(
        "unsupported local-field/right-inverse promotion"
    )
    assert target["implicit_X_R_equals_R4"] is False
    assert target["implicit_x_R_equals_R4_over_12"] is False
    assert target["historical_artifacts_edited"] is False
    assert resolution.RIGHT_INVERSE_RESULT in target["superseded_by"]


def test_fixed_u_raw_ds4_family_derivative():
    raw = resolution.ds4_raw_tangent_fixed_u()
    expected = sp.diff(
        sp.cosh(
            sp.sqrt(resolution.X) * (resolution.U - resolution.U0)
        )
        ** 2
        / resolution.X,
        resolution.X,
    )
    assert raw["uu"] == 0
    assert sp.simplify(raw["S3"] - expected) == 0


def test_fixed_dimensionless_time_is_conformal():
    tangent = resolution.ds4_conformal_tangent_fixed_z()
    assert tangent["zz"] == resolution.X ** -2
    assert tangent["S3"] == -sp.cosh(resolution.Z) ** 2 / resolution.X**2


def test_fixed_u_and_fixed_z_are_explicitly_gauge_related():
    residuals = resolution.ds4_gauge_equivalence_residuals()
    assert residuals == {"uu": 0, "S3": 0}
    assert resolution.ds4_fixed_u_gauge_vector() == (
        resolution.U - resolution.U0
    ) / (2 * resolution.X)


def test_static_family_gauge_relation():
    assert resolution.static_gauge_equivalence_residuals() == {
        "uu": 0,
        "S3": 0,
    }


def test_frechet_normalizations_for_diagnostic_conformal_representatives():
    assert (
        resolution.conformal_dr4(
            resolution.maximally_symmetric_scalar_curvature(),
            -1 / resolution.X,
        )
        == 12
    )
    assert (
        resolution.conformal_dr4(
            resolution.static_scalar_curvature(), -1 / resolution.X
        )
        == 6
    )


def test_boundary_preserving_status_is_not_invented():
    domain = resolution.tangent_ledger()["boundary_and_matcher"]
    assert "preserves the whole B1 and matcher" in domain[
        "intrinsic_B1_diffeomorphism"
    ]
    assert "not boundary-preserving" in domain["regulated_time_boundary"]
    assert domain["repository_regulator_domain"] is None
    assert domain["boundary_admissible_equivalence_proved"] is False
    assert domain["canonical_action_representative"] is None


def test_local_promotion_has_derivative_corrections():
    coeffs = resolution.local_conformal_promotion_coefficients()
    assert coeffs["C1"] == 3 * resolution.ALPHA / resolution.X0
    assert sp.simplify(
        coeffs["C2"]
        - (
            3 * resolution.BETA / resolution.X0
            - sp.Rational(9, 2)
            * resolution.ALPHA**2
            / resolution.X0**2
        )
    ) == 0
    local = resolution.tangent_ledger()["local_promotion"]
    assert "Box ln X" in local["exact_diagnostic_formula"]
    assert local["used_in_action"] is False


def test_response_route_d_is_action_selected():
    response = resolution.response_type_ledger()
    assert response["selected_route"] == "D"
    assert response["routes"]["D_independent_metric_plus_collective_field"][
        "selected"
    ]
    assert response["verdict"] == resolution.RESPONSE_RESULT


def test_local_scalar_curvature_right_inverse_is_rejected():
    route = resolution.response_type_ledger()["routes"][
        "B_local_curvature_right_inverse"
    ]
    assert route["required"] is False
    assert route["rejected_by_calculation"] is True
    assert route["verdict"] == resolution.RIGHT_INVERSE_RESULT
    assert any(
        "TT and gauge components" in reason for reason in route["reasons"]
    )


def test_no_local_green_operator_is_emitted():
    response = resolution.response_type_ledger()
    assert response["Green_operator_required"] is False
    assert response["scalar_curvature_right_inverse_emitted"] is False
    assert resolution.GUARDS["generic_green_operator_emitted"] is False


def test_tt_scope_and_family_uniqueness_are_bounded():
    tt = resolution.tangent_ledger()["TT_audit"]
    assert tt["homogeneous_family_TT_component"] == 0
    assert tt["general_DR_kernel_contains_TT"] is True
    assert "one-parameter homogeneous family" in tt["uniqueness"]
    assert tt["general_right_inverse_unique"] is False


def test_affine_moduli_constraint_redefinition_preserves_schur_form():
    assert resolution.schur_affine_shift_residual() == 0
    audit = resolution.double_counting_ledger()
    assert audit["affine_field_redefinition"]["symbolic_residual"] == "0"
    assert audit["Einstein_frame"]["count"] == 1
    assert resolution.GUARDS["K_Weyl_double_counted"] is False


def test_m4_family_tangent_is_not_added_to_independent_metric_variables():
    overlap = resolution.double_counting_ledger()["radial_profile_overlap"]
    assert overlap["M4_X_family_tangent"] == "not added"
    theorem = resolution.double_counting_ledger()[
        "no_double_counting_theorem"
    ]
    assert "never both" in theorem


def test_schur_reduction_stops_at_complete_local_constraint_domain():
    schur = resolution.schur_ledger()
    assert schur["response_type_resolved"] is True
    assert schur["not_reopened"]["full_operator_L"] is None
    assert schur["not_reopened"]["full_source_J"] is None
    assert schur["Schur_complement"] is None
    assert schur["Schur_verdict"] == resolution.SCHUR_RESULT
    assert schur["kinetic_verdict"] == resolution.KINETIC_RESULT


def test_no_schur_or_kinetic_number_is_emitted():
    schur = resolution.schur_ledger()
    assert schur["k_q_E"] is None
    assert schur["kinetic_sign"] is None
    assert resolution.GUARDS["kinetic_number_emitted"] is False


def test_integrity_firewall():
    false_guards = [
        "measured_inputs_used",
        "fitted_coefficients_introduced",
        "new_primitive_introduced",
        "new_scale_introduced",
        "new_action_introduced",
        "arbitrary_boundary_parameter_introduced",
        "chat_only_candidate_imported",
        "local_X_field_invented",
        "physical_mass_claimed",
        "stability_claimed",
        "frozen_predictions_changed",
        "official_prediction_logic_changed",
    ]
    assert all(resolution.GUARDS[key] is False for key in false_guards)


def test_frozen_prediction_hashes():
    expected = {
        "frozen_predictions.md": (
            "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
        ),
        "frozen_predictions.json": (
            "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
        ),
    }
    for filename, digest in expected.items():
        payload = (ROOT / "docs" / filename).read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == digest


def test_artifact_payloads_have_required_sections():
    payloads = resolution.artifact_payloads()
    assert set(payloads) == set(resolution.ARTIFACT_FILES)
    assert "provenance" in payloads["normalization"]
    assert "response_type" in payloads["response"]
    assert "homogeneous_tangent" in payloads["tangent"]
    assert "double_counting" in payloads["double_counting"]
    assert "Schur" in payloads["schur"]


def test_artifacts_are_strict_json_and_match_deterministic_bytes():
    expected = resolution.artifact_bytes()
    for filename, content in expected.items():
        path = ROOT / "artifacts" / filename
        assert path.read_bytes() == content
        decoded = content.decode("utf-8")
        assert decoded.endswith("\n")
        assert "\r" not in decoded
        assert json.loads(decoded)
