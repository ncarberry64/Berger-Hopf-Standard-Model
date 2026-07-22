import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import round_background_gauge_scalar_sector as rb
from bhsm.interface.p1_lorentzian_background_constraint import fixed_shape_solution, hamiltonian_constraint


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_round_background_gauge_scalar_v6_1.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / rb.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in rb.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_package_has_twenty_two_deterministic_claim_safe_artifacts():
    assert len(rb.ARTIFACT_FILES) == 22
    assert len(set(rb.ARTIFACT_FILES.values())) == 22
    built = rb.build_artifact_payloads(ROOT)
    for key, filename in rb.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == rb.PRIMARY_RESULT, key
        assert payload["v6_0_10_round_background_preserved"] is True, key
        assert payload["jensen_selected_as_primary"] is False, key
        assert payload["t0_called_static_universe"] is False, key
        assert payload["effective_base_dimension"] == 5, key
        assert payload["measured_input_used"] is False, key
        assert payload["v5_numbers_used_as_parent_inputs"] is False, key
        assert payload["frozen_predictions_changed"] is False, key
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == rb.deterministic_json(built[key])


def test_selected_round_trajectory_remains_exact_p1_solution():
    for time in (-0.7, 0.0, 0.8):
        row = fixed_shape_solution("round", time, 2, 3)
        assert hamiltonian_constraint(row["a4"], row["a2"], row["a1"], row["H4"], row["H2"], row["H1"], 2, 3) == pytest.approx(0, abs=1e-12)
    assert load("report")["completion_gate"] == "V6_1_M5_BOSONIC_NORMALIZATION_DERIVED_M4_REDUCTION_REQUIRED"


def test_minimum_slice_and_gap_are_exact_but_not_a_static_universe():
    row = rb.round_minimum(2, 3)
    assert row["a_min_squared"] == pytest.approx(63 / 4)
    assert row["gap_at_minimum_radius"] == pytest.approx(1 / 21)
    assert row["acceleration_to_gap"] == pytest.approx(1 / 3)
    payload = load("control")
    assert "not a static universe" in payload["interpretation"]


def test_full_requested_control_parameter_has_irreducible_one_third_floor():
    center = rb.control_ratios(0, 1, 1)
    assert center["epsilon_control"] == pytest.approx(1 / 3)
    assert center["ratios"]["H_squared_over_gap"] == 0
    assert center["ratios"]["gap_adiabaticity"] == 0
    assert rb.control_window(0.1, 1, 1)["exists"] is False
    diagnostic = rb.control_window(0.5, 1, 1)
    assert diagnostic["exists"] is True and diagnostic["epsilon_floor"] == pytest.approx(1 / 3)
    assert "no epsilon_star<<1" in load("control")["strict_result"]


def test_effective_post_fiber_base_is_m5_not_observed_spacetime():
    payload = load("dimension")
    assert payload["M8"] == "I_t x S7"
    assert payload["M5"] == "I_t x S4 after full S3 pushforward"
    assert "not selected" in payload["unresolved_M4"]
    assert payload["s4_identified_as_observed_spacetime"] is False


def test_round_connection_matrix_is_isotropic_with_exact_KR():
    kappa1, a = 3.0, 2.0
    expected = 8 * math.pi**2 * kappa1 * a**5
    assert rb.round_connection_coefficient(kappa1, a) == pytest.approx(expected)
    assert rb.round_geometric_coupling(kappa1, a) == pytest.approx(1 / math.sqrt(expected))
    payload = load("sp1")
    assert payload["matrix"] == "K_ab=K_R delta_ab"
    assert payload["dimensions"]["K_R"] == "L^-1"
    assert payload["dimensions"]["g5_geom"] == "L^1/2"


def test_canonical_connection_redefinition_propagates_to_vertices():
    vertices = rb.gauge_vertex_coefficients(2, 3, hubble=0.4)
    assert vertices["quartic"] == pytest.approx(vertices["cubic"] ** 2)
    assert vertices["canonical_pump_rate"] == pytest.approx(-1)
    payload = load("gauge")
    assert "same g5_geom" in payload["identity"]
    assert payload["RG_running"] is False


def test_nested_u1_is_normalized_without_becoming_an_independent_m5_copy():
    inherited = rb.u1_normalization(2, 3, "inherited_4pi")
    standard = rb.u1_normalization(2, 3, "unit_charge_2pi")
    assert inherited["ratio_to_inherited_Sp1"] == 1
    assert standard["ratio_to_inherited_Sp1"] == 4
    assert standard["canonical_interaction_ratio"] == pytest.approx(0.5)
    payload = load("u1")
    assert payload["double_counted"] is False
    assert "not an additional independent M5 field" in payload["role"]
    assert payload["hypercharge_identification"] is None


def test_connection_ratio_is_scale_independent_but_convention_dependent():
    payload = load("ratio")
    assert payload["scale_dependence"] == "none"
    assert payload["convention_dependence"].startswith("yes")
    assert payload["physical_mixing_candidate_frozen"] is False


def test_associated_charge_operators_keep_geometric_weights_distinct_from_physical_charge():
    row = rb.canonical_charge_operator(3, -1, 2, 4)
    assert row["J"] == 1.5 and row["rank"] == 4
    assert row["integral_u1_weight_q"] == -1 and row["magnetic_weight_m"] == -0.5
    assert row["casimir"] == pytest.approx(15 / 4)
    assert row["physical_charge"] is None
    with pytest.raises(ValueError):
        rb.canonical_charge_operator(3, 0, 1, 1)


def test_gauge_identities_and_zero_mode_firewall_survive_normalization():
    payload = load("gauge")
    assert payload["Bianchi"] == "D_[mu F_nu rho]=0"
    assert "gauge constraints" in payload["longitudinal_modes"]
    assert payload["sp1_identified_as_standard_model_group"] is False


def test_scalar_candidate_ledger_selects_declared_singlet_not_a_rescaled_target():
    sigma = load("sigma")
    assert sigma["status"] == "BHSM_SIGMA_PARENT_FIELD_SELECTED_POTENTIAL_OPEN"
    assert "sigma=1/2" in sigma["not_selection_basis"]
    assert sigma["higgs_identification"] is False
    candidates = load("candidates")["rows"]
    assert candidates[1]["candidate"] == "common rho=ln a"
    assert "constrained" in candidates[1]["result"]


def test_scalar_kinetic_normalization_and_dimensions_are_exact():
    norm = rb.scalar_normalization(2, 3)
    assert norm["fiber_volume"] == pytest.approx(16 * math.pi**2 * 27)
    assert norm["Z5"] == pytest.approx(2 * norm["fiber_volume"])
    payload = load("scalar_kinetic")
    assert payload["dimensions"]["sigma_parent"] == "dimensionless"
    assert payload["dimensions"]["s5"] == "L^-3/2"
    assert payload["t0_pump"] == "-lambda/28"


def test_parent_scalar_coefficients_are_structural_not_imported_from_v5():
    coefficients = rb.scalar_canonical_coefficients(2, -1, 3, 4, 0.5)
    assert coefficients["potential_mass_squared"] == pytest.approx(-0.5)
    assert coefficients["t0_canonical_pump_mass_squared"] == pytest.approx(-0.5 / 28)
    assert coefficients["canonical_cubic_at_sigma_zero"] == 0
    potential = load("potential")
    assert potential["signs_selected"] is False
    assert potential["v5_coefficients_reproduced"] is False
    assert "no direct sigma term" in potential["sources"]["P1_curvature"]


def test_scalar_stationary_points_require_unsourced_sign_conditions():
    assert rb.scalar_stationary_points(1, 2)["points"] == [0]
    broken = rb.scalar_stationary_points(-2, 8)
    assert broken["points"] == pytest.approx([0, -0.5, 0.5])
    assert broken["coefficient_signs_selected"] is False


def test_pure_singlet_polynomial_does_not_source_heavy_tower():
    payload = load("tower")
    assert "J_H=0" in payload["pure_sigma"]
    assert "O_H^-1" in payload["general_retained_modes"]
    assert "1/3" in payload["error"]
    assert payload["extension_outside_interval"] is False


def test_constraint_reduced_scalar_shape_hessian_exposes_open_sigma_sign():
    payload = load("hessian")
    assert "lapse" in payload["removed"]
    assert "Hamiltonian-constrained" in payload["removed"][2]
    assert payload["physical_block_at_sigma_zero_t0"][0].startswith("m_sigma")
    assert "shape block positive" in payload["stability"]
    assert payload["phase_transition_claim"] is False


def test_gauge_scalar_map_has_modulus_vertices_but_no_inserted_sigma_F2():
    payload = load("gauge_scalar")
    assert "a^5" in payload["modulus"]
    assert payload["sigma_F2"] == "absent in the frozen P1 action"
    assert "no connection mass" in payload["selected_sigma"]
    assert payload["electroweak_claim"] is False


def test_aperture_keeps_amplitudes_squares_and_alpha_distinct():
    payload = load("aperture")
    assert "|I_R|^2" in payload["definitions"]["candidate"]
    assert payload["inputs_complete"] is False
    assert "physical collar/boundary domain C" in payload["missing"]
    assert payload["alpha"] is None


def test_m5_dimensionful_and_m4_dimensionless_couplings_are_not_conflated():
    payload = load("coupling_dimension")
    assert "L^1/2" in payload["M5"]
    assert payload["L_eff"] is None
    assert "only for a defined" in payload["conditional_formula"]
    assert payload["observed_coupling"] is None


def test_parent_to_v5_map_advances_without_changing_values():
    payload = load("parent_v5")
    assert "M4 physical map required" in payload["map"]["gauge_kinetic"]
    assert "value not derived" in payload["map"]["A_ST"]
    assert "value not derived" in payload["map"]["G_ST"]
    assert payload["frozen_values_changed"] is False


def test_round_spectrum_at_t0_has_exact_gap_weights_and_degeneracies():
    rows = [rb.round_mode_row(n, 1, 1) for n in range(4)]
    assert rows[0]["eigenvalue_t0"] == 0
    assert rows[1]["eigenvalue_t0"] == pytest.approx(1 / 14)
    assert rows[1]["u1_weights"] == [-1, 1]
    assert [row["total_round_S3_degeneracy"] for row in rows] == [1, 4, 9, 16]
    assert load("spectrum")["particle_map"] is None


def test_spinorial_boundary_inputs_do_not_assume_a_physical_fermion_law():
    payload = load("dirac")
    assert "effective dimension M5" in payload["available"]
    assert "chirality mechanism" in payload["missing"]
    assert "physical M4 boundary/domain reduction" in payload["missing"]
    assert "BHSM-native fermionic action source" in payload["missing"]
    assert payload["physical_fermion_equation"] is None
    assert payload["next_fermionic_action_sprint_ready"] is False
    assert payload["next_Dirac_sprint_ready"] is False


def test_permanent_clifford_and_no_monopole_firewall_is_machine_guarded():
    for payload in (load("dirac"), load("report"), load("hidden")):
        assert payload["physical_fermion_equation_assumed"] is False
        assert payload["magnetic_monopole_sector_used"] is False
        assert payload["monopole_harmonics_used"] is False
        assert payload["chern_data_called_magnetic_charge"] is False
        assert payload["magnetic_charge_quantization_imported"] is False
    assert load("dirac")["monopole_dependency"] is None


def test_public_doctrine_separates_bundle_and_clifford_geometry_from_physics():
    text = public_text()
    assert "BHSM_FERMIONIC_CLIFFORD_AND_NO_MONOPOLE_FIREWALL_FROZEN" in text
    assert "promoted automatically to the physical Dirac equation" in text
    assert "Hopf curvature and Chern data are geometric bundle information" in text
    assert "Monopole harmonic sectors" in text
    assert "magnetic-charge quantization" in text


def test_scale_relations_do_not_reduce_primitive_values_or_generate_units():
    payload = load("scale")
    assert payload["raw_primitives"] == 7
    assert payload["field_normalized_invariants"] == 5
    assert "no primitive value" in payload["primitive_reduction"]
    assert payload["absolute_unit"] is None


def test_report_leads_constructively_and_routes_to_m4_dependency():
    report = load("report")
    assert report["status"] == rb.PRIMARY_RESULT
    assert "isotropic canonical M5 Sp(1) connection" in report["central_answer"]
    assert "no parametrically small tower-control window" in report["central_answer"]
    assert report["recommended_next_branch"] == "bhsm-parent-m5-to-physical-boundary-m4-reduction-v6-1-1"
    assert report["full_bhsm_status"] == "FULL_BHSM_NOT_COMPLETE"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "round-background-gauge-scalar-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == rb.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.1 Round-Background Gauge" in markdown.stdout


def test_public_claim_language_and_hidden_inputs_are_guarded():
    text = public_text()
    required = [rb.PRIMARY_RESULT, "BHSM_ROUND_SP1_CONNECTION_NORMALIZATION_DERIVED", "BHSM_EFFECTIVE_BASE_DIMENSION_5D_CONFIRMED", "BHSM_PHYSICAL_3P1_REDUCTION_REMAINS_REQUIRED", "FULL_BHSM_NOT_COMPLETE"]
    assert all(label in text for label in required)
    forbidden = ["I_t x S4 is observed spacetime", "Sp(1) is the Standard Model", "U(1) is hypercharge", "alpha is derived", "sigma is the Higgs field", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)
    hidden = load("hidden")
    assert "alpha" in hidden["not_imported"] and "measured gauge couplings" in hidden["not_imported"]
    assert hidden["strict_control_window_claimed"] is False


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
