from pathlib import Path
import sympy as sp

from bhsm.interface import critical_fold_schur_killscreen as kill

ROOT = Path(__file__).resolve().parents[1]


def test_exactly_one_primary_theorem():
    assert kill.PRIMARY_RESULT == "BHSM_FOLD_KINETIC_REQUIRES_ONE_MISSING_ACTION_BLOCK"


def test_critical_background_and_tangent():
    bg = kill.quadratic_form_ledger()["background"]
    assert bg["X_c"] == 2
    assert bg["N_0"] == "pi/4"
    assert bg["sigma_0"] == 0
    assert bg["delta_sigma"] == "q(x)u_1(t)"


def test_variables_are_reduced_by_actual_roles():
    rows = kill.variable_ledger()
    assert rows["zeta"]["reduction"].startswith("zeta=0")
    assert rows["delta_sigma"]["role"] == "genuine fold tangent"
    assert rows["E"]["role"].endswith("gauge")
    assert rows["A"]["role"] == "radial lapse Lagrange multiplier"
    assert rows["surviving_constraint_vector"] == ["A", "psi"]


def test_threading_is_not_quotiented_or_set_zero():
    B = kill.variable_ledger()["B"]
    assert B["invariant_combination"].startswith("S=B-")
    assert "Pi_perp S=-tau" in B["reduction"]
    assert "C_Sigma=0" in B["reduction"]


def test_missing_block_has_saddle_structure():
    matrix = kill.missing_block_matrix()
    assert matrix.shape == (2, 2)
    assert matrix[0, 0] == 0
    assert str(matrix[0, 1]) == "C_H_dagger"
    assert str(matrix[1, 0]) == "C_H"
    assert str(matrix[1, 1]) == "H_psi_psi"


def test_quadratic_form_records_known_direct_terms():
    form = kill.quadratic_form_ledger()
    assert "K_direct(Dq)^2" in form["form"]
    assert form["K_direct_known"]["scalar"].endswith(">=2")
    assert form["K_direct_known"]["Weyl_numeric"] == 1.220620174933802
    assert form["K_direct_complete"] is False


def test_radial_measure_caps_orientation_and_boundary_terms():
    form = kill.quadratic_form_ledger()
    assert form["radial_measure"] == "N_0 a_0^4 dt on t in [0,1]"
    assert form["two_cap_factor"] == "two reflected bulk caps plus one common B1"
    assert "tau odd" in form["orientation"]
    assert form["endpoint"] == "fixed-iota zeta=0"
    assert form["matcher"].startswith("algebraic induced-metric matching")


def test_missing_source_and_operator_are_not_fabricated():
    form = kill.quadratic_form_ledger()
    assert form["J_rad"] == "(J_A(t),J_psi(t))^T is not stored"
    assert form["L_fully_specified"] is False


def test_sequential_elimination_stops_at_first_missing_block():
    reduction = kill.sequential_reduction_ledger()
    assert reduction["step_2_gauge"].startswith("zeta fixed")
    assert reduction["step_3_threading"].startswith("v6.18 response")
    assert reduction["step_4_remaining_radial_constraints"] == "blocked at L_Apsi^crit"
    assert reduction["unresolved_interface_trace_count"] == 0
    assert reduction["threading_domain_nonempty"] is True


def test_formal_schur_complement_has_no_value():
    reduction = kill.sequential_reduction_ledger()
    assert reduction["Schur_complement_formal"] == (
        "K_red=K_direct-<J_rad,(L_Apsi^crit)^-1 J_rad>"
    )
    assert reduction["Schur_complement_value"] is None
    assert reduction["K_shift_endpoint_red"] is None


def test_kill_screen_stops_before_numerics():
    screen = kill.kill_screen_ledger()
    assert screen["L_fully_specified"] is False
    assert screen["domain_complete"] is False
    assert screen["adjoint_domain_known"] is False
    assert screen["kernel_classified"] is False
    assert screen["first_failure"] == "L_Apsi^crit is absent"
    assert screen["numerical_solve_launched"] is False
    assert screen["generic_pseudoinverse_used"] is False


def test_exact_missing_object_formula_type_and_role():
    missing = kill.missing_object_ledger()
    assert missing["name"] == "critical lapse-Weyl radial Hessian block L_Apsi^crit"
    assert "delta^2 S_deriv" in missing["formula"]
    assert missing["tensor_type"].startswith("2x2 formally self-adjoint")
    assert "adjoint domain" in missing["domain_role"]
    assert missing["new_action_needed"] is False


def test_missing_object_has_exact_source_locations():
    locations = kill.missing_object_ledger()["source_locations"]
    assert locations == [
        "src/bhsm/interface/fold_einstein_frame_kinetic_reduction.py:252",
        "src/bhsm/interface/fold_einstein_frame_kinetic_reduction.py:282",
        "src/bhsm/interface/covariant_threading_response.py:295",
    ]


def test_domain_role_is_precise():
    domain = kill.missing_object_ledger()["required_domain"]
    assert domain["pole"].startswith("regular")
    assert "metric matching" in domain["B1"]
    assert domain["gauge"] == "E removed; no seam-slide quotient"


def test_kinetic_result_is_decisively_uncomputed():
    result = kill.kinetic_verdict_ledger()
    assert result["K_scalar"] == ">=2>0"
    assert result["K_Weyl"] == 1.220620174933802
    assert result["K_shift_endpoint_red"] is None
    assert result["k_q_E"] is None
    assert result["sign"] is None
    assert result["fold_field_status"] == "not kinetically classified"
    assert result["physical_mass"] is None


def test_predecessor_results_are_preserved():
    preserved = kill.integrity_ledger()["preserved"]
    assert preserved == [
        "BHSM_INDUCED_THREADING_ACTION_REPRODUCES_CONSTRAINT_RESPONSE",
        "BHSM_FOLD_SOURCE_VANISHING_REPLACES_EXPLICIT_ENERGY_THRESHOLD",
        "BHSM_THREADING_RESPONSE_ACTION_RESTORES_NONEMPTY_FOLD_DOMAIN",
    ]


def test_integrity_guards():
    assert all(value is False for value in kill.GUARDS.values())
    for payload in kill.artifact_payloads().values():
        assert all(payload[key] is False for key in kill.GUARDS)


def test_exactly_two_deterministic_artifacts():
    blobs = kill.artifact_bytes()
    assert len(blobs) == 2
    assert set(blobs) == set(kill.ARTIFACT_FILES.values())
    assert all(blob.endswith(b"\n") for blob in blobs.values())


def test_materialized_artifacts_match():
    for filename, expected in kill.artifact_bytes().items():
        assert (ROOT / "artifacts" / filename).read_bytes() == expected
