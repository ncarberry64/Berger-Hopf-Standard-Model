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

from bhsm.interface import fixed_action_offshell_radial_family as family


def test_v630_merge_ancestry_pin():
    assert family.SOURCE_MAIN_SHA == (
        "ceaff39ad4c9d2996182407f411a38e6d85ee284"
    )
    assert family.V630_SCIENTIFIC_SHA == (
        "0956941ce156ca30a7dc48369b5efeda00245471"
    )


def test_all_action_controls_are_fixed():
    rows = family.control_rows()
    assert {row["symbol"] for row in rows} == {
        "kappa_0", "kappa_1", "Z5", "A5", "G5", "C_partial"
    }
    assert all(row["derivative_with_respect_to_q"] == 0 for row in rows)
    assert all(row["derivative_with_respect_to_tau"] == 0 for row in rows)


def test_dmu_dq_is_zero():
    assert family.dmu_dq() == 0
    assert family.GUARDS["mu_varied_with_q"] is False


def test_fixed_coordinate_domain_and_regulator():
    ledger = family.regulator_ledger()
    assert ledger["coordinate_manifold"] == "M5=[0,1]_t x M4 on each cap"
    assert ledger["B1"] == "{t=1}"
    assert ledger["coordinate_range_q_dependent"] is False
    assert ledger["M4_regulator_q_dependent"] is False
    assert ledger["vacuum_constant_subtracted"] is False


def test_M4_metric_is_independent():
    ledger = family.m4_metric_ledger()
    assert ledger["metric"] == "independent h_mu_nu"
    assert ledger["d_r_d_q"] == 0
    assert ledger["X_FRW_local_field"] is None
    assert ledger["q_identified_with_curvature"] is False


def test_on_shell_and_off_shell_boundary_residuals_differ():
    assert family.onshell_robin_residual() == (
        family.P_PSI
        + 12 * family.C_PARTIAL * family.LAMBDA * family.PSI_J
    )
    assert family.fixed_h_dirichlet_residual() == family.PSI_J
    assert family.domains_are_equal() is False


def test_metric_modulus_separates_the_domains():
    assert family.metric_modulus_robin_residual_at_zero_derivative() == 0
    assert family.metric_modulus_dirichlet_residual() == 1


def test_matcher_is_not_eliminated_off_shell():
    ledger = family.matcher_variation_ledger()
    assert "Pi_bulk+Lambda=0" in ledger["uneliminated_variations"][
        "bulk_boundary_metric"
    ]
    assert "do not impose delta_h" in ledger["off_shell_fixed_h"]


def test_field_vector_retains_matcher_multiplier():
    vector = family.family_coefficient_ledger()["field_vector_required"]
    assert "independent h_mu_nu" in vector
    assert "matcher multiplier Lambda_mu_nu" in vector


def test_q_normalization_and_kernel():
    ledger = family.family_coefficient_ledger()
    assert "normalized critical scalar Jacobi amplitude" in (
        ledger["coordinates"]["q"]
    )
    assert ledger["kernel"] == (
        "span{u1} after fixed-h Dirichlet data remove metric z"
    )
    assert "u1-orthogonal" in ledger["complement"]


def test_first_order_scalar_kernel_equation_is_retained():
    phi1 = family.family_coefficient_ledger()["Phi1"]
    assert phi1["sigma1"].startswith("u1")
    assert phi1["equation"] == "L0 u1=0 on the scalar Dirichlet domain"


def test_puiseux_metric_tangent_is_not_promoted():
    phi1 = family.family_coefficient_ledger()["Phi1"]
    assert "not promoted" in phi1["a1"]
    assert "not promoted" in phi1["N1"]


def test_second_and_higher_responses_are_not_fabricated():
    ledger = family.family_coefficient_ledger()
    assert ledger["order_reached"] == 1
    assert ledger["Phi2"] is None
    assert ledger["Phi3"] is None
    assert ledger["Phi4"] is None
    assert "Green operator" in ledger["reason"]


def test_absence_of_neighboring_solution_is_not_failure():
    assert family.family_coefficient_ledger()[
        "absence_of_neighboring_solution_is_failure"
    ] is False


def test_F0_and_F1_are_recovered():
    ledger = family.jordan_coefficient_ledger()
    assert ledger["F0"] == "pi/2"
    assert "chi_1" in ledger["F1_plus"]
    assert "chi_1" in ledger["F1_minus"]


def test_F2_and_V2_remain_unresolved_not_zero():
    ledger = family.jordan_coefficient_ledger()
    assert ledger["F2"] is None
    assert ledger["V2"] is None
    assert ledger["v6_30_identity_checked"] is False


def test_common_density_convention_is_declared():
    ledger = family.jordan_coefficient_ledger()
    assert "+F(q)R4/2-V_J(q)" in ledger["common_density_convention"]
    assert ledger["higher_curvature_absorbed_into_F_or_V"] is False


def test_inherited_null_derivatives_preserved():
    ledger = family.potential_ledger()
    assert ledger["V_E_prime_0"] == 0
    assert ledger["V_E_second_0"] == 0
    assert ledger["first_nonzero_higher_derivative"] is None


def test_exactly_one_local_stability_verdict():
    text = json.dumps(family.artifact_payloads())
    assert text.count(family.STABILITY_RESULT) == 1


def test_exactly_one_scale_permission_verdict():
    text = json.dumps(family.artifact_payloads())
    assert text.count(family.SCALE_RESULT) == 1
    assert family.existence_ledger()["scale_phase_permitted"] is False


def test_exactly_one_primary_family_verdict():
    text = json.dumps(family.artifact_payloads())
    # Once in each common artifact plus once inside the existence ledger.
    assert text.count(family.PRIMARY_RESULT) == 6


def test_existence_hypothesis_failure_is_exact():
    ledger = family.existence_ledger()
    assert ledger["local_existence_theorem_emitted"] is False
    assert "Dirichlet operator" in ledger["failed_hypothesis"]
    assert ledger["fatal_inconsistency"] is False


def test_no_wrong_inverse():
    assert family.GUARDS["unprojected_inverse_used"] is False
    assert family.GUARDS["generic_pseudoinverse_used"] is False


def test_empirical_inverse_is_quarantined():
    assert family.GUARDS["empirical_inverse_used"] is False
    assert family.GUARDS["empirical_generation_basis_used"] is False
    text = json.dumps(family.artifact_payloads())
    assert '"m_tau"' not in text
    assert '"m_mu"' not in text
    assert '"m_e"' not in text


def test_integrity_guards():
    for name in (
        "measured_input_used",
        "fitted_parameter_used",
        "chat_only_value_imported",
        "new_action_introduced",
        "new_primitive_introduced",
        "new_scale_introduced",
        "vacuum_constant_subtracted",
        "q_dependent_regulator_used",
        "local_X_FRW_field_created",
        "on_shell_Puiseux_curve_used",
        "frozen_predictions_changed",
        "official_prediction_logic_changed",
        "physical_mass_claimed",
        "global_stability_claimed",
    ):
        assert family.GUARDS[name] is False


def test_artifact_count_and_names():
    assert len(family.ARTIFACT_FILES) == 5
    assert set(family.artifact_payloads()) == set(family.ARTIFACT_FILES)


def test_deterministic_artifact_bytes():
    first = family.artifact_bytes()
    second = family.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_checked_in_artifacts_are_current():
    for name, content in family.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = (
        ROOT
        / "scripts"
        / "materialize_fixed_action_offshell_radial_family_v6_30_1.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in family.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in family.ARTIFACT_FILES.values()
    }
    assert first == second == family.artifact_bytes()
