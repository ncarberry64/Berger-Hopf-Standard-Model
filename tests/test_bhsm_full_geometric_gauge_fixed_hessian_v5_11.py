import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import full_geometric_gauge_fixed_hessian as fh


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_full_geometric_gauge_fixed_hessian_v5_11.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / fh.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md"]
    paths += [ARTIFACTS / name for name in fh.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_artifacts_parse_and_preserve_guards():
    for key, filename in fh.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["version"] == "v5.11", key
        assert payload["primary_result"] == "BHSM_QUADRATIC_OPERATOR_COMPLEX_PARTIAL"
        assert payload["empirical_inputs_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_round_trip_is_deterministic():
    built = fh.build_artifact_payloads(ROOT)
    for key, filename in fh.ARTIFACT_FILES.items():
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == fh.deterministic_json(built[key])


def test_complete_field_and_symmetry_inventory_has_no_invented_scalar_gauge():
    payload = load("field_symmetry")
    names = {row["name"] for row in payload["fields"]}
    assert {"metric/collar geometry", "internal gauge connections", "fermions", "T", "Phi", "charged current", "neutral response", "collective moduli", "geometric ghosts", "internal ghosts"} <= names
    symmetries = {row["name"]: row for row in payload["gauge_symmetries"]}
    assert symmetries["scalar shift"]["status"] == "ABSENT"
    assert symmetries["collar/embedding redundancy"]["status"] == "NOT_ESTABLISHED_NO_NEW_GAUGE_INTRODUCED"


def test_background_is_honestly_off_shell_except_reduced_scalar():
    payload = load("background_stationarity")
    rows = {row["component"]: row for row in payload["rows"]}
    assert payload["full_background_on_shell"] is False
    assert rows["T,Phi,sigma"]["stationarity"] == "ZERO_EXACTLY_IN_DECLARED_REDUCED_MODEL"
    assert rows["geometry"]["stationarity"] == "UNRESOLVED_OFF_SHELL"
    assert rows["global scale"]["stationarity"] == "FLAT_CLASSICALLY_NOT_FIXED"
    assert "tadpole" in payload["tadpole_rule"].lower() or "first variations" in payload["tadpole_rule"]


def test_all_second_variation_blocks_and_adjoint_pairs_are_present():
    payload = load("second_variation")
    assert payload["shape"] == [6, 6]
    assert len(payload["blocks"]) == 36
    blocks = {(row["row"], row["column"]): row for row in payload["blocks"]}
    for row in payload["field_order"]:
        for col in payload["field_order"]:
            assert (row, col) in blocks
            assert blocks[(row, col)]["domain_codomain"]
            assert blocks[(row, col)]["adjoint_relation"]
    assert blocks[("g", "ST")]["status"] == "NONZERO_FORMULA_OPEN"
    assert blocks[("ST", "g")]["formula"].endswith("^dagger")


def test_geometric_fp_operator_follows_declared_candidate_variation_but_domain_stays_open():
    payload = load("geometric_gauge_ghost")
    assert "delta_xi h_AB" in payload["ghost_derivation"]
    assert "-nabla^2" in payload["ghost_operator"]
    assert payload["gamma"].startswith("1/2 conventional")
    assert payload["boundary_condition"] is None
    assert payload["conformal_mode"].startswith("unresolved")
    assert payload["determinant_ready"] is False


def test_boundary_vacuum_value_is_retained_without_becoming_physical_tension():
    payload = load("boundary_tension_surface")
    tension = payload["boundary_tension_candidate"]
    assert fh.reduced_vacuum_value() == pytest.approx(-0.125)
    assert tension["normalized_total_reduced_vacuum_value"] == pytest.approx(-0.125)
    assert tension["normalized_value_automatically_subtracted"] is False
    assert tension["U_boundary_identified_with_entire_reduced_value"] is False
    assert tension["absolute_density_value"] is None
    assert tension["physical_sign"].startswith("unresolved")


def test_shape_equation_contains_every_requested_surface_contribution():
    payload = load("boundary_tension_surface")
    equation = payload["normal_shape_equation"]
    for key in ("tension", "K", "K2", "TrS2", "collar_jacobian", "scalar_topographic_pressure", "external_pressure_jump"):
        assert equation[key], key
    assert "E_quantum" in equation["formula"]
    assert equation["stationarity"].startswith("OPEN_OFF_SHELL")
    stress = payload["boundary_stress_tensor"]
    assert stress["definition"].startswith("T_Sigma^ab=")
    assert stress["fully_evaluated"] is False


def test_v5_7_shape_coefficient_zeros_are_not_promoted_to_geometric_zeros():
    provenance = load("boundary_tension_surface")["coefficient_provenance"]
    assert "not a geometric zero" in provenance["c_K"]
    assert "not set to zero" in provenance["c_K2"]
    assert "not set to zero" in provenance["c_S"]
    assert "remains active" in provenance["c_J"]


def test_surface_scaling_model_can_have_a_conditional_root_but_current_Lc_is_open():
    assert fh.surface_scaling_eigenvalue(1.0, 1.0, 0.0, -1.0, 0.0) == pytest.approx(0.0)
    assert fh.surface_scaling_critical_lengths(1.0, 0.0, -1.0, 0.0) == pytest.approx([1.0])
    assert fh.surface_scaling_critical_lengths(1.0, 0.0, 1.0, 0.0) == []
    with pytest.raises(ValueError):
        fh.surface_scaling_eigenvalue(0.0, 1.0, 0.0, 0.0, 0.0)
    payload = load("boundary_tension_surface")
    assert payload["lowest_mode"]["L_c"] is None
    classification = payload["critical_scale_classification"]
    assert classification["fixed_completely_by_current_action"] is False
    assert classification["current_result"] == "STILL_SCALE_COVARIANT"
    assert classification["absolute_scale_claimed"] is False


def test_xi_perp_is_a_physical_candidate_not_silently_gauge_removed():
    geometry = load("geometric_gauge_ghost")
    assert "xi_perp" in geometry["normal_mode"]
    principal = {row["sector"]: row for row in load("principal_ellipticity")["rows"]}
    assert "normal displacement xi_perp" in principal
    assert principal["normal displacement xi_perp"]["strong_ellipticity_with_boundary"] is False
    modes = {row["mode"]: row for row in load("zero_negative")["zero_modes"]}
    assert modes["lowest xi_perp surface mode"]["type"] == "physical boundary-shape candidate"
    negatives = {row["sector"]: row for row in load("zero_negative")["negative_modes"]}
    assert negatives["normal displacement xi_perp"]["discarded"] is False


def test_v5_10_quantum_term_is_only_a_uniform_partial_diagnostic():
    quantum = load("boundary_tension_surface")["quantum_term"]
    assert quantum["uniform_scale_derivatives"] == {"dGamma_dL": "-1/L", "d2Gamma_dL2": "1/L^2"}
    assert quantum["local_shape_stress_available"] is False
    assert quantum["included_in_official_surface_operator"] is False


def test_primordial_release_sequence_is_preserved_with_explicit_statuses():
    stages = load("boundary_tension_surface")["preserved_primordial_interpretation"]
    assert [row["stage"] for row in stages] == [
        "stable compact state",
        "lambda_surface reaches zero",
        "outward instability",
        "guided compact-to-expanding trajectory",
        "primordial hot plasma",
    ]
    assert "not derived" in stages[-1]["status"]


def test_internal_ghosts_follow_gauge_variation_and_no_couplings_inserted():
    payload = load("internal_gauge_ghost")
    assert [row["raw_adjoint_rank"] for row in payload["sectors"]] == [1, 3, 8]
    assert payload["ghost_operator"].startswith("M_i=D_i^dagger D_i")
    assert payload["numerical_gauge_couplings"] is None
    assert payload["selected_boundary_condition"] is None


def test_fermion_symbol_square_current_and_eta_status_are_explicit():
    payload = load("fermion")
    assert payload["principal_symbol"] == "i gamma^A k_A"
    assert "Laplace type" in payload["square"]
    assert "gamma(n)" in payload["boundary_form"]
    assert payload["normal_current_controlled"] is False
    assert payload["eta_invariant"] is None
    assert payload["determinant_phase_controlled"] is False
    assert payload["determinant_ready"] is False


def test_scalar_full_form_recovers_v5_10_six_over_L_squared():
    payload = load("scalar")
    assert payload["homogeneous_hessian"] == [[5, -1], [-1, 5]]
    assert payload["parallel_mode"]["eigenvalue"] == "4/L^2"
    assert payload["orthogonal_mode"]["eigenvalue"] == "6/L^2"
    assert payload["v5_10_eigenvalue_recovered"] is True
    assert payload["homogeneous_zero_modes"] == []
    assert payload["homogeneous_negative_modes"] == []
    assert payload["full_determinant_ready"] is False


def test_charged_is_composite_and_neutral_determinant_ownership_stays_open():
    payload = load("charged_neutral")
    assert payload["charged"]["independent_field_space"] is None
    assert payload["charged"]["determinant_ownership"] == "NO_INDEPENDENT_ZERO_POINT_DETERMINANT"
    assert payload["charged"]["mediator_invented"] is False
    assert payload["neutral"]["quadratic_operator"] == "K_neu symbolic"
    assert payload["neutral"]["determinant_ownership"] == "UNRESOLVED"
    assert payload["neutral"]["ev_values_inserted"] is False


def test_only_reduced_scalar_boundary_form_is_closed():
    payload = load("boundary_self_adjoint")
    rows = {row["sector"]: row for row in payload["rows"]}
    assert rows["scalar homogeneous"]["variation_vanishes"] is True
    assert rows["scalar homogeneous"]["adjoint_domain_matches"] is True
    assert rows["geometry+geometric ghost"]["selected"] is None
    assert rows["internal gauge+ghost"]["selected"] is None
    assert payload["full_self_adjoint_operator_complex"] is False


def test_principal_symbols_match_orders_without_false_strong_ellipticity():
    payload = load("principal_ellipticity")
    rows = {row["sector"]: row for row in payload["rows"]}
    assert rows["fermion D"]["order"] == 1
    assert rows["fermion D"]["principal_symbol"] == "i gamma^A k_A"
    assert rows["internal gauge"]["order"] == 2
    assert "|k|^2" in rows["internal gauge"]["principal_symbol"]
    assert all(row["strong_ellipticity_with_boundary"] is False for row in payload["rows"])
    assert payload["determinant_ready"] is False


def test_collective_modes_are_not_removed_or_owned_twice_and_jacobian_is_recorded():
    payload = load("zero_negative")
    zeros = {row["mode"]: row for row in payload["zero_modes"]}
    assert zeros["global L"]["type"] == "physical classical modulus/collective coordinate"
    assert "retain" in zeros["global L"]["treatment"]
    assert payload["jacobian"]["L_sigma"] == "dL/L d sigma_scale"
    assert payload["negative_modes_silently_removed"] is False


def test_negative_modes_are_explicitly_unresolved_not_discarded():
    payload = load("zero_negative")
    rows = {row["sector"]: row for row in payload["negative_modes"]}
    assert rows["geometry conformal"]["count"] is None
    assert rows["geometry conformal"]["discarded"] is False
    assert rows["scalar homogeneous"]["count"] == 0
    assert all(row["discarded"] is False for row in payload["negative_modes"])


def test_heat_kernel_inputs_are_not_promoted_to_total_coefficients():
    payload = load("heat_kernel")
    assert payload["requested_coefficients"] == ["a_0", "a_1/2", "a_1", "a_3/2", "a_2"]
    assert payload["total_coefficients_calculated"] is False
    assert all(row["readiness"] != "EXACT_SPECTRUM_READY" for row in payload["rows"])


def test_reduced_hessian_is_second_variation_of_stored_finite_action():
    xi_g, xi_i = 1.7, 2.3
    hessian = fh.gauge_fixed_reduced_hessian(xi_g, xi_i)
    eps = 1.0e-5
    origin = [0.0] * 6
    for i in range(6):
        for j in range(6):
            ei, ej = origin.copy(), origin.copy()
            ei[i] = eps
            ej[j] = eps
            eij = [ei[k] + ej[k] for k in range(6)]
            numerical = (fh.reduced_quadratic_action(eij, xi_g, xi_i) - fh.reduced_quadratic_action(ei, xi_g, xi_i) - fh.reduced_quadratic_action(ej, xi_g, xi_i)) / eps**2
            assert numerical == pytest.approx(hessian[i][j], abs=1e-12)


def test_gauge_fixing_removes_only_gauge_zeros_and_physical_projection_is_xi_independent():
    raw = fh.raw_reduced_hessian()
    assert raw[1][1] == raw[3][3] == 0
    for xi_g, xi_i in ((0.25, 0.5), (1.0, 1.0), (4.0, 9.0)):
        fixed = fh.gauge_fixed_reduced_hessian(xi_g, xi_i)
        assert fixed[1][1] > 0 and fixed[3][3] > 0
        assert fh.physical_reduced_hessian() == [[2,0,0,0],[0,3,0,0],[0,0,5,-1],[0,0,-1,5]]
        assert fh.physical_reduced_eigenvalues() == [2,3,4,6]


def test_finite_ghost_normalization_cancels_gauge_parameters():
    for xi_g, xi_i in ((0.25, 0.5), (1.0, 1.0), (4.0, 9.0)):
        assert fh.reduced_determinant_quotient(xi_g, xi_i) == pytest.approx(144.0)
    payload = load("reduced_complex")
    assert payload["normalized_gauge_ghost_quotient"] == payload["physical_determinant"]
    assert payload["physical_casimir_assigned"] is False


def test_v5_10_remains_partial_and_no_full_loop_is_permitted():
    update = load("construction_report")["v5_10_update"]
    assert update["historical_result"] == "BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL"
    assert update["historical_one_mode_determinant_preserved"] is True
    assert update["promoted_to_official_effective_action"] is False
    assert update["full_one_loop_permitted"] is False


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "full-geometric-gauge-fixed-hessian-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_QUADRATIC_OPERATOR_COMPLEX_PARTIAL"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "BHSM v5.11 Full Geometric and Gauge-Fixed Hessian" in markdown.stdout


def test_public_ledgers_and_forbidden_claims():
    text = focused_text()
    assert "BHSM_QUADRATIC_OPERATOR_COMPLEX_PARTIAL" in text
    assert "OPEN_MISSING_ACTION_DERIVED_GEOMETRIC_HESSIAN" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    assert "full-geometric-gauge-fixed-hessian-status" in text
    forbidden = ["v5.11 derives a physical Casimir energy", "v5.11 derives particle masses", "v5.11 derives gauge couplings", "v5.11 completes BHSM", "the old curvature-threshold mass gap is valid"]
    assert not any(phrase in text for phrase in forbidden)


def test_old_mass_gap_remains_invalidated_and_relative_results_preserved():
    report = load("construction_report")
    assert any("curvature-threshold mass-gap" in row for row in report["invalidated_or_ruled_out"])
    assert report["preserved_relative_results"] == {"sigma_scale":"1/2", "M_BH_over_M_star":"1/2", "R_BH_over_ell_star":"2"}


def test_frozen_prediction_and_official_logic_files_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
