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

from bhsm.interface import homogeneous_threading_support_verdict as thread


def test_exact_v625_baseline():
    assert thread.SOURCE_MAIN_SHA == (
        "2236cade321828e26d9a78ecbd5f2a6c67b67982"
    )
    assert thread.V625_SCIENTIFIC_SHA == (
        "df76a3d30a76df90bed2d0aecd0dbaa29af280a0"
    )


def test_frozen_action_multiplicity_and_matcher():
    action = thread.action_ledger()
    assert action["cap_count"] == 2
    assert action["common_B1_count"] == 1
    assert action["matcher_coefficient"] is None
    assert action["new_term_added"] is False
    assert action["total"] == [
        "S_P1,+",
        "S_P1,-",
        "S_GHY,+",
        "S_GHY,-",
        "S_B1",
        "S_match",
        "S_sigma",
    ]


def test_closed_ds4_scale_factor_and_hubble():
    assert thread.a4() == sp.cosh(
        sp.sqrt(thread.X) * (thread.U - thread.U0)
    ) / sp.sqrt(thread.X)
    assert thread.H4() == sp.sqrt(thread.X) * sp.tanh(
        sp.sqrt(thread.X) * (thread.U - thread.U0)
    )
    assert thread.dS4_background_residual() == 0


def test_closed_ds4_connection_coefficients():
    connection = thread.background_ledger()["connection"]
    assert connection["Gamma^u_ij"] == "H4 h_ij"
    assert connection["Gamma^i_uj"] == "H4 delta^i_j"
    assert connection["Gamma^u_uu"] == 0


def test_homogeneous_scalar_hessian():
    hessian = thread.homogeneous_hessian(thread.Q)
    assert hessian["uu"] == sp.diff(thread.Q, thread.U, 2)
    assert hessian["ui"] == 0
    assert hessian["ij_over_hij"] == (
        -thread.H4() * sp.diff(thread.Q, thread.U)
    )


def test_box4_homogeneous_identity():
    expected = (
        -sp.diff(thread.Q, thread.U, 2)
        - 3 * thread.H4() * sp.diff(thread.Q, thread.U)
    )
    assert sp.simplify(thread.box_homogeneous(thread.Q) - expected) == 0


def test_fixed_manifold_B_potential():
    assert thread.B_particular() == (
        -thread.TAU
        * sp.pi
        * thread.CHI_1
        * thread.T
        * thread.Q
        / 16
    )


def test_N_u_normalization():
    assert thread.N_u_particular() == (
        -thread.TAU
        * sp.pi
        * thread.CHI_1
        * thread.T
        * sp.diff(thread.Q, thread.U)
        / 16
    )


def test_covariant_B_derivatives_include_H4():
    derivatives = thread.B_derivatives()
    assert derivatives["D_u_D_u_B"] == (
        -thread.response_coefficient()
        * thread.T
        * sp.diff(thread.Q, thread.U, 2)
    )
    assert derivatives["D_i_D_j_B_over_h_ij"] == (
        thread.response_coefficient()
        * thread.T
        * thread.H4()
        * sp.diff(thread.Q, thread.U)
    )
    assert derivatives["Box4_B"] == (
        thread.response_coefficient()
        * thread.T
        * (
            sp.diff(thread.Q, thread.U, 2)
            + 3 * thread.H4() * sp.diff(thread.Q, thread.U)
        )
    )


def test_delta_K_components_from_coordinate_map():
    curvature = thread.shift_extrinsic_curvature(1)
    alpha = thread.TAU * thread.CHI_1 / 4
    assert curvature["delta_K_uu"] == (
        alpha * sp.diff(thread.Q, thread.U, 2)
    )
    assert curvature["delta_K_ij_over_h_ij"] == (
        -alpha * thread.H4() * sp.diff(thread.Q, thread.U)
    )
    assert curvature["delta_K_ui"] == 0


def test_delta_K_trace():
    curvature = thread.shift_extrinsic_curvature(1)
    assert sp.simplify(
        curvature["delta_K_trace"]
        - thread.TAU
        * thread.CHI_1
        * thread.box_homogeneous(thread.Q)
        / 4
    ) == 0


def test_delta_Q_components():
    curvature = thread.shift_extrinsic_curvature(1)
    alpha = thread.TAU * thread.CHI_1 / 4
    q_dot = sp.diff(thread.Q, thread.U)
    q_ddot = sp.diff(thread.Q, thread.U, 2)
    assert curvature["delta_Q_uu"] == -3 * alpha * thread.H4() * q_dot
    assert curvature["delta_Q_ij_over_h_ij"] == (
        alpha * (q_ddot + 2 * thread.H4() * q_dot)
    )
    assert curvature["delta_Q_ui"] == 0


def test_p1_ghy_action_variation_absolute_coefficient():
    assert thread.action_euler_coefficient() == (
        3
        * thread.KAPPA_1
        * thread.X
        / (thread.N0 * thread.radial_warp() ** 2)
    )
    action = thread.threading_ledger()["action_variation"]
    assert action["equation"] == "[-C_M] Box4 W=0"
    assert "GHY cancels" in action["origin"]


def test_momentum_constraint_absolute_coefficient():
    assert thread.momentum_coefficient() == (
        -3
        * thread.KAPPA_1
        * thread.X
        / (thread.N0 * thread.radial_warp() ** 2)
    )
    momentum = thread.threading_ledger()["momentum_constraint"]
    assert momentum["equation"] == "M_mu=C_M D_mu W=0"
    assert momentum["divergence"] == "D^mu M_mu=C_M Box4 W"


def test_action_equation_equals_minus_divergence_of_momentum():
    assert sp.simplify(
        thread.action_shift_equation()
        - thread.minus_divergence_momentum_equation()
    ) == 0
    assert thread.momentum_u_equation().has(sp.diff(thread.W, thread.U))


def test_action_is_divergence_but_not_equivalent_kernelwise():
    rank = thread.action_momentum_kernel_rank()
    assert rank["action_kernel_constants"] == 2
    assert rank["momentum_kernel_constants"] == 1
    assert rank["unfixed_action_only_modes"] == 1


def test_v618_spatial_normalization_is_recovered():
    radius = sp.symbols("a_S", positive=True)
    assert thread.spatial_kernel_eigenvalue(3, radius) == -30 / radius**4
    recovery = thread.threading_ledger()["v6_18_recovery"]
    assert recovery["static_round_S3_operator"] == "(2/a_S^2)Delta_S3"
    assert "pi chi_1/16" in recovery["particular_response"]


def test_local_homogeneous_particular_response():
    solutions = thread.threading_ledger()["solutions"]
    assert solutions["particular"] == "W=0, hence B=-c t q"
    assert thread.threading_ledger()["state_requirement"][
        "local_particular_coefficient_derived"
    ] is True


def test_source_free_lorentzian_mode_solves_action_equation():
    assert thread.source_free_mode_box_residual() == 0
    assert thread.source_free_mode_derivative() != 0


def test_source_free_lorentzian_mode_fails_momentum_constraint():
    assert thread.source_free_momentum_residual() != 0
    assert thread.source_free_momentum_residual().has(thread.C1)


def test_integration_mode_is_not_covered_by_Csigma_axiom():
    scope = thread.threading_ledger()["C_Sigma_axiom_scope"]
    assert scope["fixes_C0"] is True
    assert scope["fixes_C1_Lorentzian_mode"] is False
    assert scope["extension_assumed"] is False


def test_no_global_lorentzian_state_is_selected():
    state = thread.threading_ledger()["state_requirement"]
    assert state["complete_response_unique"] is False
    assert state["selected"] is None
    assert all(
        thread.GUARDS[name] is False
        for name in (
            "arbitrary_Lorentzian_state_selected",
            "retarded_state_selected",
            "advanced_state_selected",
            "Feynman_state_selected",
            "Euclidean_state_selected",
        )
    )


def test_endpoint_invariant_fixed_and_moving_values_agree():
    endpoint = thread.endpoint_ledger()
    assert endpoint["fixed_gauge"]["value"] == (
        "-tau(pi chi_1/16)q(u)+W_h(u)"
    )
    assert endpoint["moving_coordinate"]["value"] == (
        endpoint["fixed_gauge"]["value"]
    )
    assert endpoint["moving_coordinate"]["agreement"] is True
    assert endpoint["gauge_invariant"] is True


def test_endpoint_trace_remains_nonunique_without_becoming_embedding():
    endpoint = thread.endpoint_ledger()
    assert endpoint["particular_trace_derived"] is True
    assert endpoint["unique_endpoint_trace"] is False
    assert "not a physical embedding mode" in endpoint["classification"]
    assert endpoint["result"] == thread.ENDPOINT_RESULT


def test_all_four_B1_scalar_projection_slots_are_recorded():
    projections = thread.b1_ledger()["four_scalar_projections"]
    assert set(projections) == {
        "temporal_threading_piece",
        "scalar_momentum_threading_piece",
        "spatial_trace_threading_piece",
        "traceless_longitudinal_threading_piece",
    }
    assert projections["scalar_momentum_threading_piece"].startswith("0")
    assert projections["traceless_longitudinal_threading_piece"].startswith("0")


def test_two_Ward_dependencies_are_preserved():
    ward = thread.b1_ledger()["Ward"]
    assert ward["projection_count"] == 4
    assert ward["dependency_count"] == 2
    assert ward["expected_independent_count"] == 2
    assert ward["identity"] == "D^mu J_mu nu=-[T_bulk,n nu]"


def test_two_equation_B1_rank_is_not_manufactured_after_stop():
    b1 = thread.b1_ledger()
    assert b1["complete_O_D2q_coefficients"] is False
    assert b1["two_independent_equations"] is None
    assert b1["rank_after_complete_insertion"] is None
    assert b1["compatibility"] is None
    assert b1["result"] == thread.B1_RESULT


def test_matcher_closure_is_retained():
    assert thread.b1_ledger()["matcher_elimination"] == (
        "algebraic and retained"
    )


def test_Rperp_definition_and_invariant_properties():
    residual = thread.residual_ledger()
    assert residual["definition"].startswith(
        "R_perp=(sqrt|h|)^-1 delta_zeta^diag"
    )
    assert residual["gauge_invariant"] is True
    assert residual["affine_invariant"] is True
    assert residual["fixed_moving_invariant"] is True


def test_D00q_residual_coefficient_is_not_assigned():
    coefficients = thread.residual_ledger()["coefficients"]
    assert coefficients["c0"] == 0
    assert coefficients["D_0D_0_q"] is None
    assert coefficients["Box4_q"] is None
    assert "D_0D_0 W_h" in thread.residual_ledger()[
        "why_D_0D_0_coefficient_not_unique"
    ]


def test_noether_rank_and_residual_result_remain_blocked():
    residual = thread.residual_ledger()
    assert residual["Noether_dependency_rank"] is None
    assert residual["proved_zero"] is False
    assert residual["proved_nonzero"] is False
    assert residual["explicit_result"] is None
    assert residual["result"] == thread.RESIDUAL_RESULT


def test_support_verdict_exclusivity_and_dynamic_path_disabled():
    verdict = thread.verdict_ledger()
    assert verdict["selected_support_domain"] is None
    assert verdict["fixed_support_compatible"] is False
    assert verdict["fixed_support_failure_proved"] is False
    assert verdict["dynamical_embedding_required"] is False
    assert verdict["primary_result"] == thread.PRIMARY_RESULT
    assert verdict["one_primary_support_result"] is True
    assert verdict["dynamic_embedding"]["reached"] is False


def test_operator_adjoint_schur_and_kinetic_are_not_emitted():
    verdict = thread.verdict_ledger()
    assert verdict["operator"]["reopened"] is False
    assert verdict["operator"]["inverse"] is None
    assert verdict["operator"]["adjoint_domain"] is None
    assert verdict["Schur"]["constructed"] is False
    assert verdict["Schur"]["k_q_E"] is None
    assert verdict["kinetic"]["coefficient"] is None
    assert verdict["kinetic"]["sign"] is None


def test_hindsight_categories_are_separated():
    hindsight = thread.hindsight_ledger()
    assert set(hindsight) == {"Validated", "Invalidated", "Still active"}
    assert "unique response" in hindsight["Invalidated"][-1]


def test_scientific_integrity_firewall():
    assert all(value is False for value in thread.GUARDS.values())


def test_neither_support_success_string_is_emitted_in_artifacts():
    encoded = json.dumps(thread.artifact_payloads(), sort_keys=True)
    assert "BHSM_FOLD_LOCALIZATION_COMPATIBLE_WITH_FIXED_B1_SUPPORT" not in encoded
    assert (
        "BHSM_DYNAMICAL_B1_EMBEDDING_REQUIRED_BY_LOCAL_FOLD_RESIDUAL"
        not in encoded
    )


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


def test_canonical_json_eol_policy_is_unchanged():
    attributes = (ROOT / ".gitattributes").read_text(
        encoding="utf-8"
    ).splitlines()
    general = "artifacts/*.json text eol=lf"
    nested = "artifacts/**/*.json text eol=lf"
    exception = "artifacts/CKM_no_fit_operator_output_v1.json text eol=crlf"
    assert general in attributes
    assert nested in attributes
    assert exception in attributes
    assert attributes.index(general) < attributes.index(exception)
    assert attributes.index(nested) < attributes.index(exception)


def test_artifact_payloads_have_required_bounded_sections():
    payloads = thread.artifact_payloads()
    assert set(payloads) == set(thread.ARTIFACT_FILES)
    assert {"action", "background", "threading"} <= set(payloads["threading"])
    assert "endpoint" in payloads["endpoint"]
    assert "B1" in payloads["b1"]
    assert "normal_support_residual" in payloads["residual"]
    assert "verdict" in payloads["verdict"]


def test_artifacts_are_strict_json_and_deterministic_lf_bytes():
    expected = thread.artifact_bytes()
    assert len(expected) == 5
    for filename, content in expected.items():
        path = ROOT / "artifacts" / filename
        assert path.read_bytes() == content
        decoded = content.decode("utf-8")
        assert decoded.endswith("\n")
        assert "\r" not in decoded
        assert json.loads(decoded)
