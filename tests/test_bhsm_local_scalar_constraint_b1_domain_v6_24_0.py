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

from bhsm.interface import local_scalar_constraint_b1_domain as local


def test_exact_action_sectors_and_multiplicities():
    action = local.action_and_background_ledger()["action"]
    assert action["total"] == [
        "S_P1,cap+",
        "S_P1,cap-",
        "S_GHY,cap+",
        "S_GHY,cap-",
        "S_B1",
        "S_match",
        "S_sigma",
    ]
    assert action["cap_count"] == 2
    assert action["common_B1_count"] == 1
    assert action["matcher_coefficient"] is None
    assert action["U_partial"] == "absent (zero in the primary freeze)"


def test_action_coefficient_provenance_is_explicit():
    ledger = local.action_and_background_ledger()
    provenance = ledger["provenance"]
    assert provenance["frozen_action"].startswith(
        "intrinsic_m4_junction_background.py"
    )
    assert provenance["scalar_completion"].startswith(
        "scalar_wall_junction_audit.py"
    )
    action = ledger["action"]
    assert "kappa_1 R5/2" in action["P1"]
    assert action["GHY_each_oriented_cap"].startswith("+kappa_1")
    assert "C_partial R4" in action["B1_primary_freeze"]


def test_critical_background_and_branch_are_not_static_ansatz():
    background = local.action_and_background_ledger()["background"]
    assert background["N0"] == "pi/4"
    assert background["a0"] == "sqrt(2) sin(pi t/4)"
    assert background["sigma0"] == 0
    assert background["X_c"] == 2
    assert background["M4"].startswith("Ric(hbar)=3 X_c")


def test_induced_metric_variation_includes_shape_and_tangential_terms():
    p11, p22, k11, k22, zeta, l11, l22 = sp.symbols(
        "p11 p22 k11 k22 zeta l11 l22"
    )
    result = local.induced_metric_variation(
        sp.diag(p11, p22),
        sp.diag(k11, k22),
        zeta,
        sp.diag(l11, l22),
    )
    assert result == sp.diag(
        p11 + 2 * zeta * k11 + l11,
        p22 + 2 * zeta * k22 + l22,
    )


def test_induced_metric_shape_check_for_constant_umibilic_displacement():
    radius, zeta = sp.symbols("R zeta", positive=True)
    gamma = sp.eye(3) * radius**2
    extrinsic = sp.eye(3) * radius
    result = local.induced_metric_variation(
        sp.zeros(3), extrinsic, zeta
    )
    assert result == sp.diff(
        sp.eye(3) * (radius + sp.Symbol("eps") * zeta) ** 2,
        sp.Symbol("eps"),
    ).subs(sp.Symbol("eps"), 0)
    assert gamma.shape == result.shape


def test_normal_covector_variation_preserves_normalization_and_orthogonality():
    pnn, z1, z2 = sp.symbols("p_nn z1 z2")
    delta_n = local.normal_covector_variation(
        pnn, sp.Matrix([z1, z2])
    )
    assert delta_n == sp.Matrix([pnn / 2, -z1, -z2])
    # delta(g^{AB} n_A n_B)= -p_nn+2 delta n_n.
    assert sp.simplify(-pnn + 2 * delta_n[0]) == 0


def test_extrinsic_curvature_shape_variation():
    zeta = sp.symbols("zeta")
    hessian = sp.diag(*sp.symbols("h1 h2"))
    k2 = sp.diag(*sp.symbols("k1sq k2sq"))
    rann = sp.diag(*sp.symbols("r1 r2"))
    result = local.shape_extrinsic_curvature_variation(
        hessian, k2, rann, zeta
    )
    assert result == -hessian + zeta * (k2 - rann)


def test_trace_shape_variation_contains_induced_inverse_contribution():
    laplacian, norm2, ricnn, zeta = sp.symbols(
        "Delta_zeta norm2 Ric_nn zeta"
    )
    assert sp.simplify(
        local.shape_trace_curvature_variation(
            laplacian, norm2, ricnn, zeta
        )
        - (-laplacian - (norm2 + ricnn) * zeta)
    ) == 0


def test_boundary_measure_variation():
    ptr, mean, zeta, divv = sp.symbols("p_trace K zeta div_v")
    result = local.boundary_measure_fractional_variation(
        ptr, mean, zeta, divv
    )
    assert result == ptr / 2 + mean * zeta + divv


def test_scalar_pullback_and_critical_decoupling():
    dsigma, zeta, normal_gradient = sp.symbols(
        "delta_sigma zeta sigma_n"
    )
    assert local.scalar_pullback_variation(
        dsigma, zeta, normal_gradient
    ) == dsigma + zeta * normal_gradient
    assert local.scalar_pullback_variation(dsigma, zeta, 0) == dsigma
    geometry = local.moving_geometry_ledger()
    assert geometry["critical_scalar_pullback"].endswith(
        "because sigma0=0"
    )


def test_radial_and_m4_scalar_gauge_laws_leave_threading_invariant():
    assert sp.simplify(
        local.transformed_endpoint_shift_invariant()
        - local.endpoint_shift_invariant()
    ) == 0
    assert (
        local.gauge_ledger()["symbolic_threading_invariance"] == "0"
    )


def test_fixed_and_moving_coordinate_endpoint_equivalence_is_bounded():
    gauge = local.gauge_ledger()
    equivalence = gauge["fixed_support_equivalence"]
    assert equivalence["threading_unchanged"] is True
    assert equivalence["physical_support_moved"] is False
    assert gauge["physical_moving_support"][
        "gauge_equivalent_to_fixed_support"
    ] is False


def test_independent_b1_and_matcher_variables_are_kept_before_elimination():
    fields = local.gauge_ledger()["pre_quotient_fields"]
    assert len(fields["independent_B1_before_matching"]) >= 2
    assert len(fields["matcher_before_elimination"]) == 2
    action = local.action_and_background_ledger()["action"]
    assert "h_mu nu-iota^*g_mu nu" in action["matcher"]


def test_embedding_is_not_silently_promoted_to_action_variable():
    obstruction = local.moving_domain_obstruction_ledger()
    assert "fixed iota" in obstruction["fixed_action_fact"]
    assert "one-dimensional cap upper limit" in obstruction[
        "homogeneous_reduced_exception"
    ]
    assert obstruction["stored_homogeneous_endpoint_condition"] == (
        "delta a'_J=delta X/2 in the normalized homogeneous tangent"
    )
    assert obstruction["local_extension_of_homogeneous_condition"] is None
    assert "D_muD_nu q" in obstruction["why_no_local_extension"]
    assert obstruction["physical_zeta_is_action_selected"] is False
    assert obstruction["free_endpoint_equation_derived"] is False
    assert local.GUARDS["embedding_variation_assumed"] is False


def test_smallest_missing_object_includes_double_cap_reflection_extension():
    obstruction = local.moving_domain_obstruction_ledger()
    missing = obstruction["smallest_missing_object"]
    assert "iota_zeta" in missing
    assert "Z2 cap-exchange/reflection extension" in missing
    assert obstruction["verdict"] == local.B1_RESULT


def test_endpoint_noether_identity_is_not_misclassified_as_shape_equation():
    obstruction = local.moving_domain_obstruction_ledger()
    assert "coordinate displacement" in obstruction[
        "Noether_identity_available"
    ]
    assert "does not create a normal free-boundary law" in obstruction[
        "Noether_identity_available"
    ]
    assert obstruction["matcher_fixes_physical_zeta"] is False
    assert obstruction["junction_fixes_physical_zeta"] is False


def test_v620_principal_block_is_recovered_exactly():
    expected = (
        6
        * local.KAPPA_1
        / local.A0**2
        * sp.Matrix([[0, 1], [1, 2]])
    )
    assert local.principal_lapse_weyl_block() == expected
    assert local.operator_ledger()["retained_exact_checks"][
        "principal_A_psi_block"
    ].startswith("(6kappa_1/a0^2)")


def test_critical_radial_measure_is_recovered():
    assert local.critical_radial_measure() == (
        sp.pi * sp.sin(sp.pi * local.T / 4) ** 4
    )
    assert local.operator_ledger()["retained_exact_checks"][
        "radial_measure"
    ] == "N0 a0^4=pi sin^4(pi t/4)"


def test_fixed_cap_ghy_cancellation_and_tensor_junction_are_preserved():
    checks = local.operator_ledger()["retained_exact_checks"]
    assert "cancel capwise" in checks["GHY_fixed_cap"]
    assert checks["tensor_junction"].startswith("kappa_1[Q_ab]")
    assert "h_ab=iota^*g_ab" in checks["matcher"]


def test_full_operator_is_not_manufactured_after_earliest_stop():
    operator = local.operator_ledger()
    assert operator["action_expansion_started"] is False
    assert operator["not_derived"]["complete_quadratic_action"] is None
    assert operator["not_derived"]["L0"] is None
    assert operator["not_derived"]["L1"] is None
    assert operator["not_derived"]["boundary_matrix"] is None
    assert operator["zero_assigned_to_missing_blocks"] is False
    assert operator["operator_verdict"] == local.LOCAL_RESULT


def test_v618_threading_scope_is_separated_by_sector():
    audit = local.threading_coverage_ledger()
    sectors = audit["sector_audit"]
    assert sectors["spatial_nonhomogeneous_ell_ge_1"].startswith("covered")
    assert "C_Sigma=0 axiom" in sectors[
        "spatial_homogeneous_ell_0_time_independent"
    ]
    assert "not covered" in sectors[
        "time_dependent_spatially_homogeneous"
    ]
    assert "not covered" in sectors["general_Lorentzian_M4_scalar"]
    assert "not covered" in sectors["moving_endpoint_trace"]
    assert audit["required_mode_outside_v6_18"] is True


def test_affine_schur_identity_uses_correct_final_argument():
    assert local.affine_schur_identity_residual() == 0
    source = local.source_ledger()
    assert source["affine_identity"] == (
        "K'-<J',L^-1J'>=K-<J,L^-1J>"
    )
    assert source["affine_identity_symbolic_residual"] == "0"


def test_source_bookkeeping_uses_one_affine_convention():
    source = local.source_ledger()
    assert source["bookkeeping_convention"].startswith("A:")
    assert source["no_double_counting_proved_for_available_terms"] is True
    assert source["full_J0"] is None
    assert source["full_J1"] is None
    assert source["source_verdict"] == local.SOURCE_RESULT


def test_operator_pencil_adjoint_and_kernel_remain_undefined():
    schur = local.schur_ledger()
    assert schur["operator_pencil"]["L0"] is None
    assert schur["operator_pencil"]["L1"] is None
    assert schur["domain"] is None
    assert schur["adjoint_domain"] is None
    assert schur["kernel_dimensions"] is None
    assert schur["source_compatibility"] is None
    assert schur["inverse_constructed"] is False


def test_no_arbitrary_global_green_prescription_is_selected():
    schur = local.schur_ledger()
    assert schur["global_green_state_selected"] is False
    assert local.GUARDS["arbitrary_global_green_state_selected"] is False
    assert local.GUARDS["generic_pseudoinverse_emitted"] is False


def test_no_schur_number_kinetic_sign_or_stability_claim_is_emitted():
    schur = local.schur_ledger()
    assert schur["Schur_complement"] is None
    assert schur["K_grav_constraint_J"] is None
    assert schur["k_q_E"] is None
    assert schur["kinetic_sign"] is None
    assert schur["ghost_claim"] is None
    assert schur["stability_claim"] is None
    assert schur["Schur_verdict"] == local.SCHUR_RESULT
    assert schur["kinetic_verdict"] == local.KINETIC_RESULT


def test_integrity_firewall():
    assert all(value is False for value in local.GUARDS.values())


def test_no_local_x_field_or_scalar_curvature_inverse():
    assert local.GUARDS["local_X_field_invented"] is False
    assert local.GUARDS["scalar_curvature_inverse_revived"] is False
    assert local.GUARDS["conformal_tangent_used_as_action_input"] is False


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


def test_deterministic_artifact_checkout_uses_lf_on_all_platforms():
    attributes = (ROOT / ".gitattributes").read_text(
        encoding="utf-8"
    ).splitlines()
    general = "artifacts/*.json text eol=lf"
    nested = "artifacts/**/*.json text eol=lf"
    frozen_exception = (
        "artifacts/CKM_no_fit_operator_output_v1.json text eol=crlf"
    )
    assert general in attributes
    assert nested in attributes
    assert frozen_exception in attributes
    # Git uses the last matching attribute, so the frozen CRLF exception must
    # follow the general canonical-LF materialized-artifact rule.
    assert attributes.index(general) < attributes.index(frozen_exception)
    assert attributes.index(nested) < attributes.index(frozen_exception)


def test_artifact_payloads_have_required_sections():
    payloads = local.artifact_payloads()
    assert set(payloads) == set(local.ARTIFACT_FILES)
    assert "gauge" in payloads["gauge"]
    assert "moving_graph_kinematics" in payloads["gauge"]
    assert "operator" in payloads["operator"]
    assert "domain_obstruction" in payloads["domain"]
    assert "threading_coverage" in payloads["source"]
    assert "Schur" in payloads["schur"]


def test_artifacts_are_strict_json_and_match_deterministic_bytes():
    expected = local.artifact_bytes()
    for filename, content in expected.items():
        path = ROOT / "artifacts" / filename
        assert path.read_bytes() == content
        decoded = content.decode("utf-8")
        assert decoded.endswith("\n")
        assert "\r" not in decoded
        assert json.loads(decoded)
