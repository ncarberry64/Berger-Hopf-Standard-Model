from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import full_shift_variation_support_closure as close


def test_exact_predecessor_baseline():
    assert close.SOURCE_MAIN_SHA == "7a5de9fc2d9ad75504ed9db40d42b92aa1bc38e6"
    assert close.V626_SCIENTIFIC_SHA == "aa146f05db8d63ef9436b3fc1cf94b79eba4c755"


def test_parent_metric_is_varied_before_reduction():
    ledger = close.provenance_ledger()
    assert ledger["1_arbitrary_symmetric_metric"]["answer"] is True
    assert ledger["2_mixed_component_independent"]["answer"] is True
    assert ledger["5_decomposition_relative_to_EL"]["answer"].startswith("after")


def test_parent_shift_is_arbitrary_one_form():
    full = close.full_shift_ledger()
    assert "N_mu (arbitrary one-form)" in full["independent_variables"]
    assert close.PARENT_RESULT == (
        "BHSM_FULL_SHIFT_VARIATION_IMPOSES_COMPLETE_MOMENTUM_CONSTRAINT"
    )


def test_adm_shift_variation_formula():
    adm = close.full_shift_ledger()["ADM"]
    assert "D_mu delta N_nu+D_nu delta N_mu" in adm["delta_N_K"]
    assert "partial_rho gamma_mu_nu" in adm["K"]


def test_arbitrary_compact_delta_Nu_is_admissible():
    variation = close.full_shift_ledger()["variation"]
    assert "arbitrary smooth compactly supported delta N_mu" in (
        variation["admissible_variations"]
    )
    assert close.provenance_ledger()["6_homogeneous_delta_Nu_excluded"][
        "answer"
    ] is False


def test_no_radial_integration_by_parts_for_shift():
    variation = close.full_shift_ledger()["variation"]
    assert variation["radial_integration_by_parts"] is False


def test_regular_pole_shift_boundary_term_zero():
    assert close.full_shift_ledger()["variation"]["regular_pole_term"] == 0


def test_B1_shift_endpoint_term_zero():
    variation = close.full_shift_ledger()["variation"]
    assert variation["B1_shift_endpoint_term"] == 0
    assert variation["B1_or_matcher_contribution"] == 0


def test_GHY_has_no_independent_shift_endpoint_term():
    assert (
        close.full_shift_ledger()["variation"][
            "GHY_independent_shift_endpoint_term"
        ]
        == 0
    )


def test_two_caps_impose_constraints_without_cancellation():
    rule = close.full_shift_ledger()["variation"]["two_cap_rule"]
    assert "each cap" in rule
    assert "does not cancel constraints" in rule


def test_full_momentum_normalization_matches_v626():
    expected = (
        -3
        * close.KAPPA_1
        * close.X
        / (close.N0 * close.v626.radial_warp() ** 2)
    )
    assert sp.simplify(close.momentum_coefficient() - expected) == 0


def test_full_momentum_homogeneous_components():
    assert close.full_momentum_u().has(sp.diff(close.W, close.U))
    assert close.full_shift_ledger()["linearized_v626"]["homogeneous"]["M_i"] == 0


def test_scalar_equation_is_minus_momentum_divergence():
    assert sp.simplify(
        close.scalar_action_equation()
        - close.v626.minus_divergence_momentum_equation()
    ) == 0


def test_scalar_reduction_is_performed_only_after_parent_audit():
    comm = close.commutativity_ledger()
    assert comm["Route_I"].startswith("vary arbitrary N_mu")
    assert comm["Route_II"].startswith("set N_mu=D_mu B")


def test_reduced_B_variation_only_imposes_divergence():
    assert close.commutativity_ledger()["Route_II_equation"] == "D_mu M^mu=0"


def test_divergence_free_C1_covector_kernel():
    assert close.divergence_free_covector_residual() == 0


def test_C1_parent_momentum_witness_is_nonzero():
    witness = close.c1_momentum_witness()
    assert witness != 0
    assert witness.has(close.C1)
    assert witness.has(close.KAPPA_1)


def test_C1_eliminated_by_local_constraint():
    c1 = close.c1_ledger()
    assert c1["C1_status"].startswith("C1=0")
    assert c1["result"] == close.C1_RESULT


def test_C1_is_not_eliminated_by_a_state_prescription():
    c1 = close.c1_ledger()
    assert c1["state_conditions_used"] == []
    assert all(
        close.GUARDS[name] is False
        for name in (
            "arbitrary_Lorentzian_state_selected",
            "retarded_state_selected",
            "advanced_state_selected",
            "Feynman_state_selected",
            "Euclidean_state_selected",
        )
    )


def test_C0_uses_only_inherited_Csigma_scope():
    c0 = close.c1_ledger()["C0_status"]
    assert "only by the inherited v6.18 C_Sigma=0" in c0


def test_unique_threading_response():
    response = close.c1_ledger()["unique_response"]
    assert response["W"] == 0
    assert response["B"] == "-tau(pi chi_1/16)t q"


def test_variation_reduction_noncommutativity_verdict():
    assert close.COMMUTATIVITY_RESULT == (
        "BHSM_SCALAR_REDUCTION_BEFORE_VARIATION_LOSES_C1_MOMENTUM_CONSTRAINT"
    )


def test_static_S3_nonconstant_modes_have_no_kernel():
    radius = sp.symbols("a_S", positive=True)
    assert close.static_s3_scalar_eigenvalue(1, radius) != 0
    assert close.static_s3_scalar_eigenvalue(0, radius) == 0


def test_repair_is_parent_constraint_not_new_physics():
    comm = close.commutativity_ledger()
    assert "already-existing action constraint" in comm["classification"]
    assert close.KILL_SCREEN_RESULT == "BHSM_SHIFT_SECTOR_REPAIRABLE_REDUCTION_ERROR"


def test_endpoint_trace_unique():
    endpoint = close.endpoint_ledger()
    assert endpoint["after_C1_parent_constraint_and_C0_axiom"] == (
        "-tau(pi chi_1/16)q"
    )
    assert endpoint["result"] == close.ENDPOINT_RESULT


def test_four_endpoint_representations_agree():
    endpoint = close.endpoint_ledger()
    values = set(endpoint["representations"].values())
    assert len(values) == 1
    assert endpoint["all_agree"] is True


def test_four_B1_projections_are_retained():
    projections = close.b1_ledger()["four_projections"]
    assert set(projections) == {
        "temporal_H",
        "scalar_momentum",
        "spatial_trace_T",
        "traceless_longitudinal",
    }


def test_B1_threading_source_normalization():
    source = close.b1_threading_source()
    assert sp.simplify(
        source[0]
        - sp.Rational(3, 2)
        * close.KAPPA_1
        * close.TAU
        * close.CHI_1
        * close.v626.H4()
        * sp.diff(close.Q, close.U)
    ) == 0
    assert sp.simplify(
        source[1]
        + close.KAPPA_1
        * close.TAU
        * close.CHI_1
        * (
            sp.diff(close.Q, close.U, 2)
            + 2 * close.v626.H4() * sp.diff(close.Q, close.U)
        )
        / 2
    ) == 0


def test_B1_two_equation_matrix_rank():
    witness = close.b1_rank_witness()
    assert witness["rank"] == 2
    assert witness["canonical_momentum_minor"] == close.KAPPA_1**2


def test_B1_matcher_eliminated_field_vector():
    system = close.b1_ledger()["matcher_eliminated_system"]
    assert system["field_vector"] == [
        "Pi_H",
        "Pi_T",
        "G_H",
        "G_T",
        "T_H",
        "T_T",
    ]
    assert len(system["equations"]) == 2


def test_two_Ward_dependent_rows():
    ward = close.b1_ledger()["Ward"]
    assert len(ward["dependent_rows"]) == 2
    assert len(ward["independent_rows"]) == 2


def test_Rperp_coefficients_vanish_in_independent_basis():
    assert all(value == 0 for value in close.residual_coefficients_on_shell().values())
    independent = close.residual_ledger()["independent_basis"]
    assert independent == {"ddot_q": 0, "H4_dot_q": 0}


def test_Noether_row_does_not_raise_rank():
    k_h, k_t = sp.symbols("k_H k_T")
    ranks = close.noether_augmented_rank(k_h, k_t)
    assert ranks == {"junction_rank": 2, "with_R_perp_rank": 2}


def test_residual_routes_agree():
    residual = close.residual_ledger()
    assert residual["routes_agree"] is True
    assert residual["result"] == close.RESIDUAL_RESULT


def test_fixed_support_selected_exclusively():
    support = close.support_ledger()
    assert support["fixed_support_compatible"] is True
    assert support["dynamic_embedding"]["required"] is False
    assert support["support_result"] == close.SUPPORT_RESULT


def test_dynamic_path_disabled_when_residual_zero():
    dynamic = close.support_ledger()["dynamic_embedding"]
    assert dynamic["entered"] is False
    assert dynamic["embedding_equation"] is None


def test_operator_reopened_without_inverse():
    operator = close.operator_ledger()
    assert operator["result"] == close.OPERATOR_RESULT
    assert operator["complete_for_inverse"] is False
    assert operator["Schur"]["constructed"] is False
    assert close.GUARDS["operator_inverse_emitted"] is False


def test_operator_field_vector_and_boundary_blocks_recorded():
    operator = close.operator_ledger()
    assert "Y_red=(A,psi,delta_sigma_perp)" in operator["field_vector"]
    assert {"J_H", "J_T", "source_q"} <= set(operator["blocks"])
    assert "regular pole at t=0" in operator["boundary_conditions"]


def test_kinetic_sign_remains_unresolved_for_new_exact_reason():
    kinetic = close.operator_ledger()["kinetic"]
    assert kinetic["sign"] is None
    assert "INCOMPLETE_REOPENED_RADIAL_OPERATOR" in kinetic["result"]


def test_fatal_inconsistency_kill_screen_is_false():
    kill = close.support_ledger()["kill_screen"]
    assert kill["fatal_inconsistency"] is False
    assert kill["repairable_reduction_error"] is True
    assert kill["active_domain_choice"] is False


def test_no_new_inputs_terms_or_claims():
    assert all(value is False for value in close.GUARDS.values())


def test_exactly_one_C1_and_support_verdict_in_payloads():
    payloads = close.artifact_payloads()
    text = json.dumps(payloads)
    assert close.C1_RESULT in text
    assert close.SUPPORT_RESULT in text
    assert "BHSM_LORENTZIAN_C1_MODE_RETAINED" not in text
    assert "BHSM_DYNAMICAL_B1_EMBEDDING_REQUIRED" not in text


def test_artifact_names_and_payload_count():
    assert len(close.ARTIFACT_FILES) == 5
    assert set(close.artifact_payloads()) == set(close.ARTIFACT_FILES)


def test_deterministic_artifact_bytes():
    first = close.artifact_bytes()
    second = close.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest() for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest() for name, content in second.items()
    }


def test_materializer_matches_repository_bytes(tmp_path):
    paths = close.materialize_artifacts(tmp_path)
    assert len(paths) == 5
    expected = close.artifact_bytes()
    for path in paths:
        assert path.read_bytes() == expected[path.name]


def test_checked_in_artifacts_are_current():
    for name, expected in close.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == expected


def test_materializer_is_idempotent_on_checkout():
    script = ROOT / "scripts" / (
        "materialize_full_shift_variation_support_closure_v6_27_0.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {name: (ROOT / "artifacts" / name).read_bytes() for name in close.ARTIFACT_FILES.values()}
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {name: (ROOT / "artifacts" / name).read_bytes() for name in close.ARTIFACT_FILES.values()}
    assert first == second == close.artifact_bytes()
