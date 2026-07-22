import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import p1_lorentzian_background_constraint as lb


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_p1_lorentzian_background_constraint_v6_0_10.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / lb.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in lb.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_package_has_twenty_two_deterministic_claim_safe_artifacts():
    assert len(lb.ARTIFACT_FILES) == 22
    assert len(set(lb.ARTIFACT_FILES.values())) == 22
    built = lb.build_artifact_payloads(ROOT)
    for key, filename in lb.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == lb.PRIMARY_RESULT, key
        assert payload["v6_0_9_normalization_preserved"] is True, key
        assert payload["lapse_set_before_variation"] is False, key
        assert payload["new_field_family_added"] is False, key
        assert payload["arbitrary_supporting_fluid_added"] is False, key
        assert payload["p2_p3_used_in_p1_solution"] is False, key
        assert payload["measured_input_used"] is False, key
        assert payload["frozen_predictions_changed"] is False, key
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == lb.deterministic_json(built[key])


def test_spatial_volume_curvature_and_round_limit_preserve_v609():
    assert lb.spatial_volume(0.5, 0.5, 0.5) == pytest.approx(math.pi**4 / 3)
    assert lb.spatial_curvature(0.5, 0.5, 0.5) == pytest.approx(42)
    with pytest.raises(ValueError):
        lb.spatial_curvature(1, 0, 1)


def test_extrinsic_curvature_reproduces_the_dewitt_kinetic_form():
    rates = (0.3, -0.2, 0.5)
    invariants = lb.extrinsic_invariants(*rates)
    assert lb.adm_kinetic(*rates) == pytest.approx(invariants["KijKij_minus_K2"])
    assert [list(row) for row in lb.DEWITT] == [[-12, -8, -4], [-8, -2, -2], [-4, -2, 0]]
    assert load("action")["dewit"] == [[-12, -8, -4], [-8, -2, -2], [-4, -2, 0]]


def test_lapse_is_retained_and_ghy_removes_second_derivatives():
    payload = load("action")
    assert "(kappa1/N)" in payload["lagrangian"]
    assert "second derivatives" in payload["GHY"]
    assert load("hamiltonian")["lapse_order"] == "vary N first, then choose N=1"


def test_lapse_derivative_equals_volume_times_hamiltonian_constraint():
    n, a4, a2, a1 = 1.7, 2.0, 1.5, 1.2
    qdot = (0.3, -0.1, 0.2)
    k0, k1 = 0.8, 2.3
    h = tuple(value / n for value in qdot)
    volume = lb.spatial_volume(a4, a2, a1)
    analytic_dL_dN = volume * (k1 * (lb.spatial_curvature(a4, a2, a1) - lb.adm_kinetic(*h)) - k0) / 2
    eps = 1e-6
    numeric = (
        lb.homogeneous_lagrangian(n + eps, a4, a2, a1, *qdot, k0, k1)
        - lb.homogeneous_lagrangian(n - eps, a4, a2, a1, *qdot, k0, k1)
    ) / (2 * eps)
    assert numeric == pytest.approx(analytic_dL_dN, rel=1e-8)
    assert analytic_dL_dN == pytest.approx(volume * lb.hamiltonian_constraint(a4, a2, a1, *h, k0, k1))


def test_constraint_matches_tt_equation_and_propagates():
    payload = load("hamiltonian")
    assert payload["status"] == "BHSM_P1_HAMILTONIAN_CONSTRAINT_DERIVED"
    assert "G_tt" in payload["tt_equation"]
    assert lb.constraint_propagation(0.02, 0.1, 0.2, -0.1) == pytest.approx(-0.02 * lb.expansion_scalar(0.1, 0.2, -0.1))


def test_momentum_constraint_is_checked_before_homogeneity():
    payload = load("momentum")
    assert payload["pre_homogeneous"].startswith("C_i=kappa1 D_j")
    assert "time-dependent internal rotations" in payload["not_discarded"]


def test_volume_shape_transform_is_exact_and_nonredundant():
    values = (0.4, -0.2, 0.7)
    transformed = lb.log_shape_coordinates(*values)
    assert lb.logs_from_shape(*transformed) == pytest.approx(values)
    shape = load("equations")["shape_metric"]
    assert shape[0][0] > 0 and shape[1][1] > 0
    assert "constraint" in load("equations")["volume_direction"]


def test_directional_ricci_traces_to_scalar_and_einstein_shapes():
    for scales in [(2.0, 2.0, 2.0), (3.0, 3 / math.sqrt(5), 3 / math.sqrt(5))]:
        ricci = lb.directional_ricci(*scales)
        assert sum(d * r for d, r in zip(lb.DIMENSIONS, ricci, strict=True)) == pytest.approx(lb.spatial_curvature(*scales))
        assert ricci[0] == pytest.approx(ricci[1]) == pytest.approx(ricci[2])


@pytest.mark.parametrize("name", ["round", "jensen"])
def test_fixed_lapse_static_extrema_fail_constraint_and_require_dust_like_support(name):
    branch = lb.static_branch(name, 2.0, 3.0)
    assert branch["vacuum_static_solution"] is False
    assert branch["vacuum_constraint_residual"] == pytest.approx(0.4)
    assert branch["required_stress"]["rho"] == pytest.approx(0.4)
    assert branch["required_stress"]["p4"] == pytest.approx(0, abs=1e-12)
    assert branch["required_stress"]["p2"] == pytest.approx(0, abs=1e-12)
    assert branch["required_stress"]["p1"] == pytest.approx(0, abs=1e-12)


def test_static_exclusion_is_specific_and_does_not_end_dynamic_program():
    assert load("static_round")["status"] == "BHSM_P1_STATIC_PRODUCT_BACKGROUND_EXCLUDED"
    assert load("static_jensen")["status"] == "BHSM_P1_STATIC_PRODUCT_BACKGROUND_EXCLUDED"
    assert load("report")["status"] == "BHSM_P1_FIXED_SHAPE_DYNAMIC_BACKGROUND_DERIVED"
    assert load("support")["matter_model_added"] is False


@pytest.mark.parametrize("name", ["round", "jensen"])
def test_exact_fixed_shape_cosh_solutions_satisfy_constraint(name):
    for time in (-1.2, 0.0, 0.7):
        row = lb.fixed_shape_solution(name, time, 2.0, 3.0)
        residual = lb.hamiltonian_constraint(row["a4"], row["a2"], row["a1"], row["H4"], row["H2"], row["H1"], 2.0, 3.0)
        assert residual == pytest.approx(0, abs=1e-12)
    assert lb.fixed_shape_parameters(name, 2, 3)["expansion_scale_squared"] == pytest.approx((2 / 3) / 42)


def test_round_is_shape_stable_and_jensen_has_one_physical_shape_instability():
    assert lb.constraint_reduced_shape_masses("round", 2) == pytest.approx((1, 1))
    jensen = lb.constraint_reduced_shape_masses("jensen", 2)
    assert jensen[0] > 0 and jensen[1] < 0
    payload = load("stability")
    assert payload["fixed_lapse_hessian_reused_as_final"] is False
    assert "time reparameterization" in payload["reduction"]


def test_general_integrator_preserves_round_invariant_sector_and_refines():
    exact0 = lb.fixed_shape_solution("round", 0, 2, 3)
    q0 = math.log(exact0["a4"])
    initial = (q0, q0, q0, 0, 0, 0)
    coarse = lb.integrate_vacuum(initial, 0.01, 20, 2, 3)
    fine = lb.integrate_vacuum(initial, 0.005, 40, 2, 3)
    exact = lb.fixed_shape_solution("round", 0.2, 2, 3)
    coarse_error = abs(math.exp(coarse["rows"][-1]["state"][0]) - exact["a4"])
    fine_error = abs(math.exp(fine["rows"][-1]["state"][0]) - exact["a4"])
    assert fine_error < coarse_error
    assert fine["maximum_constraint_residual"] < 1e-10
    assert fine["positive_scales"] is True
    final = fine["rows"][-1]["state"]
    assert final[0] == pytest.approx(final[1]) == pytest.approx(final[2])


def test_sigma_uses_existing_isotropic_action_and_cannot_supply_static_dust():
    assert lb.sigma_stress(0, 2.0) == {"rho": 2.0, "p4": -2.0, "p2": -2.0, "p1": -2.0}
    moving = lb.sigma_stress(2, 1, 0.5)
    assert moving["rho"] == 2 and moving["p4"] == 0
    payload = load("sigma")
    assert "cannot supply" in payload["static"]
    assert payload["v5_value_inserted"] is False


def test_geometric_connection_is_not_double_counted_as_support():
    payload = load("connection")
    assert payload["status"] == "BHSM_GEOMETRIC_CONNECTION_BACKGROUND_ALREADY_INCLUDED"
    assert "double counting" in payload["additional_support"]
    assert payload["arbitrary_electric_or_magnetic_field_inserted"] is False


def test_background_connection_matrix_stays_positive_and_time_dependence_is_not_rg():
    data = lb.background_connection_data(2, 3, 4, 0.2, -0.1, 0.3)
    assert data["positive"] is True
    assert data["log_derivative_K12"] == pytest.approx(0.7)
    assert data["log_derivative_K3"] == pytest.approx(0.1)
    assert load("connection_norm")["RG_running_interpretation"] is False


def test_dynamic_tower_control_uses_instantaneous_gap_and_disables_bad_region():
    controlled = lb.dynamic_tower_control(2, 2, 0.01, 0.01, 0.01, 0, energy_squared=1e-5, acceleration_scale=1e-5)
    assert controlled["controlled"] is True
    bad = lb.dynamic_tower_control(100, 100, 0.1, 0.1, 0.1, 0)
    assert bad["controlled"] is False
    payload = load("tower")
    assert payload["through_closing_event_claimed"] is False
    assert "eventually uncontrolled" in payload["late_time"]


def test_multiplet_equation_has_exact_volume_friction_without_particle_claim():
    payload = load("multiplet")
    assert payload["friction"] == "Theta=4H4+2H2+H1"
    assert "lambda_(J,m)(a2,a1)" in payload["equation"]
    assert payload["particle_mass_interpretation"] is False


def test_parent_scale_is_a_primitive_curvature_relation_not_absolute_unit():
    payload = load("scale")
    assert payload["expansion_scale"] == "H_lambda^2=lambda/42"
    assert payload["absolute_unit"] is None
    assert load("parent_v5")["frozen_v5_formulas_changed"] is False


def test_p2_p3_are_not_needed_or_fitted_to_obtain_round_dynamic_branch():
    payload = load("lovelock")
    assert payload["status"] == "BHSM_P1_BACKGROUND_CLOSES_ROUND_DYNAMIC_P2_P3_NOT_REQUIRED"
    assert "not necessary" in payload["necessity"]
    assert payload["coefficient_fit_performed"] is False


def test_report_selects_stable_round_route_without_overclaiming_jensen_or_tower():
    report = load("report")
    assert report["status"] == lb.PRIMARY_RESULT
    assert "round trajectory has no tachyonic homogeneous shape mode" in report["central_answer"]
    assert "Jensen carries one tachyonic shape mode" in report["central_answer"]
    assert report["recommended_next_branch"] == "bhsm-round-background-gauge-scalar-sector-v6-1"
    assert report["full_bhsm_status"] == "FULL_BHSM_NOT_COMPLETE"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "p1-lorentzian-background-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == lb.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.0.10 P1 Lorentzian Background" in markdown.stdout


def test_public_claim_language_and_hidden_inputs_are_guarded():
    text = public_text()
    required = [lb.PRIMARY_RESULT, "BHSM_P1_HAMILTONIAN_CONSTRAINT_DERIVED", "BHSM_P1_STATIC_PRODUCT_BACKGROUND_EXCLUDED", "FULL_BHSM_NOT_COMPLETE"]
    assert all(label in text for label in required)
    forbidden = ["parent solution is the observed universe", "S4 is observed spacetime", "geometric connections are Standard Model gauge fields", "absolute unit is generated", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)
    assert "cosmological parameters" in load("hidden")["not_imported"]


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
