import cmath
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import harmonic_physicality_coupling_selection as hs


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_harmonic_physicality_coupling_selection_v6_0_4.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / hs.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths += [ARTIFACTS / name for name in hs.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_artifact_package_is_complete_and_claim_guarded():
    assert len(hs.ARTIFACT_FILES) == 20
    for key in hs.ARTIFACT_FILES:
        payload = load(key)
        assert payload["version"] == "v6.0.4", key
        assert payload["primary_result"] == "BHSM_HARMONIC_SELECTION_SOURCE_NOT_DERIVED"
        assert payload["coupling_selection_result"] == "BHSM_PHYSICALITY_COUPLING_SELECTION_BLOCKED"
        assert payload["preserved_results"] == [
            "BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED",
            "BHSM_PHYSICALITY_THRESHOLD_ARCHITECTURE_IDENTIFIED",
        ]
        assert payload["empirical_inputs_used"] is False
        assert payload["preferred_harmonic_ratio_inserted"] is False
        assert payload["particle_or_generation_identification_made"] is False
        assert payload["absolute_unit_generated"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_is_deterministic():
    built = hs.build_artifact_payloads(ROOT)
    for key, name in hs.ARTIFACT_FILES.items():
        assert (ARTIFACTS / name).read_text(encoding="utf-8") == hs.deterministic_json(built[key])


def test_free_orthonormal_quadratic_action_has_no_relative_phase_energy():
    eigenvalues = [2.0, 5.0]
    first = hs.quadratic_modal_action(eigenvalues, [3.0, 4.0])
    second = hs.quadratic_modal_action(eigenvalues, [3.0 * cmath.exp(0.7j), 4.0 * cmath.exp(-1.3j)])
    assert first == pytest.approx(second)
    assert load("linear")["relative_phase_dependence"] is False
    with pytest.raises(ValueError):
        hs.quadratic_modal_action([1.0], [1.0, 2.0])


def test_removable_off_diagonal_quadratic_terms_are_diagonalized_not_called_interactions():
    low, high = hs.symmetric_block_eigenvalues(3.0, 5.0, 2.0)
    assert low + high == pytest.approx(8.0)
    assert low * high == pytest.approx(11.0)
    assert "basis choice" in load("linear")["off_diagonal_rule"]


def test_degenerate_projector_norm_is_basis_independent():
    state = [1.0 + 2.0j, 3.0 - 1.0j, 4.0]
    original = [[1, 0, 0], [0, 1, 0]]
    root2 = 2.0**0.5
    rotated = [[1 / root2, 1 / root2, 0], [-1 / root2, 1 / root2, 0]]
    assert hs.projector_norm(state, original) == pytest.approx(hs.projector_norm(state, rotated))
    assert hs.projector_norm(state, original) >= 0
    with pytest.raises(ValueError):
        hs.projector_norm([1, 2], [[1]])


@pytest.mark.parametrize("level,eigenvalue,degeneracy", [(0, 0, 1), (1, 7, 8), (4, 40, 294), (10, 160, 13013)])
def test_round_s7_scalar_spectrum_is_exact(level, eigenvalue, degeneracy):
    assert hs.round_s7_scalar_eigenvalue(level) == eigenvalue
    assert hs.round_s7_scalar_degeneracy(level) == degeneracy


def test_invalid_round_s7_inputs_are_rejected():
    with pytest.raises(ValueError):
        hs.round_s7_scalar_eigenvalue(-1)
    with pytest.raises(ValueError):
        hs.round_s7_scalar_eigenvalue(1, 0)
    with pytest.raises(ValueError):
        hs.round_s7_scalar_degeneracy(-1)


def test_unique_nonzero_round_s7_octave_pair_is_derived_not_inserted():
    assert hs.exact_octave_pairs(100) == [(4, 10)]
    assert hs.round_s7_scalar_eigenvalue(10) == 4 * hs.round_s7_scalar_eigenvalue(4)
    payload = load("octave")
    assert payload["preferred_harmonic_ratio_inserted"] is False
    assert payload["dyadic_tower"] is False
    assert payload["absolute_scale_fixed"] is False


def test_octave_frequency_and_laplacian_eigenvalue_ratios_are_distinguished():
    payload = load("octave")["distinctions"]
    assert payload["octave"] == "frequency ratio 2"
    assert payload["eigenvalue_ratio"] == "4 for Laplace dispersion omega^2=lambda"


def test_base_ten_order_of_magnitude_is_not_promoted():
    payload = load("octave")
    assert payload["discrete_scale_factor"] is None
    assert payload["base_ten_status"].startswith("bookkeeping only")


def test_parent_field_ledger_does_not_create_a_generic_wave():
    payload = load("fields")
    assert payload["selected_parent_field"] is None
    assert payload["unspecified_wave_field_added"] is False
    rows = {row["field"]: row for row in payload["rows"]}
    assert all(row["inner_product"] and row["boundary_conditions"] and row["berger_s3_relation"] for row in rows.values())
    assert rows["sigma"]["verdict"] == "CIRCULAR_AS_INDEPENDENT_TRIGGER"
    assert rows["top-form flux"]["verdict"] == "NO_LOCAL_HARMONIC_INTERFERENCE"


def test_nested_hopf_structure_is_recorded_without_sm_representation_inference():
    payload = load("spectrum")
    assert payload["quaternionic_Hopf"].startswith("S3 -> S7 -> S4")
    assert payload["complex_Hopf"].startswith("S1 -> S7 -> CP3")
    assert payload["twistor"].startswith("S2 -> CP3 -> S4")
    assert payload["standard_model_representations_inferred"] is False
    assert payload["B8_operator_spectrum_complete"] is False


def test_quartic_tensor_equals_fourth_action_derivative():
    coefficient = 3.0
    overlap = 2.5
    step = 1.0e-3
    values = [hs.quartic_mode_action(k * step, coefficient, overlap) for k in (-2, -1, 0, 1, 2)]
    fourth_difference = (values[0] - 4 * values[1] + 6 * values[2] - 4 * values[3] + values[4]) / step**4
    assert fourth_difference == pytest.approx(hs.quartic_tensor(coefficient, overlap))


def test_interaction_tensor_symmetries_and_sigma_parity_are_explicit():
    payload = load("tensors")
    assert payload["cubic"]["sigma_Z2_value"] == 0
    assert payload["cubic"]["permutation"].startswith("fully symmetric")
    assert payload["quartic"]["permutation"].startswith("fully symmetric")
    assert payload["exact_overlap_values"] is None


def test_u1_selection_rule_matches_explicit_charge_closure():
    assert hs.u1_overlap_allowed([4, -2, -2])
    assert hs.u1_overlap_allowed([3, 1, -2, -2])
    assert not hs.u1_overlap_allowed([4, -2, -1])
    rows = {row["gate"]: row for row in load("rules")["rows"]}
    assert "signed charge sum is zero" in rows["U1/fiber winding"]["condition"]


def test_frequency_commensurability_and_nonzero_coupling_are_independent_gates():
    payload = load("rules")
    assert payload["commensurability_implies_coupling"] is False
    assert payload["coupling_implies_resonance"] is False
    assert "AND" in payload["survival"]


def test_octave_pair_has_no_parity_even_sigma_three_wave_coupling():
    payload = load("resonance")["octave_pair"]
    assert payload["frequency"] == "omega_10=2 omega_4"
    assert payload["sigma_Z2_cubic"] == "zero at sigma=0"
    assert payload["verdict"] == "EXACT_FREQUENCY_RELATION_NO_SIGMA_THREE_WAVE_COUPLING"


def test_zero_mode_quartic_rewrite_is_flagged_as_circular():
    warning = load("resonance")["quartic_warning"]
    assert "zero mode" in warning
    assert "already leaves sigma=0" in warning


def test_resonant_normal_form_is_conservative_and_adds_no_dissipation():
    payload = load("normal_form")
    assert payload["equation"].startswith("i dot A_n")
    assert payload["dissipation_added"] is False
    assert "approximate" in payload["conserved"]["wave_action"]


def test_phase_locking_is_not_prescribed_without_amplitude_equations():
    payload = load("locked")
    assert payload["phases_prescribed"] is False
    assert payload["aligned_selected"] is False
    assert payload["stability_matrix"] is None


def test_coherence_functional_is_basis_invariant_but_phase_blind():
    payload = load("coherence")
    assert payload["basis_independent"] is True
    assert payload["positivity"] == "C2>=0"
    assert payload["phase_sensitivity"].startswith("C2 is phase blind")
    assert payload["arbitrary_basis_subtraction_used"] is False


def test_constrained_variation_uses_only_actual_conserved_quantities():
    payload = load("variational")
    assert payload["principle"].startswith("delta(E-sum_i mu_i Q_i)=0")
    assert payload["arbitrary_coherence_maximized"] is False
    assert payload["second_constrained_variation"] is None


def test_coherent_incoherent_comparison_holds_required_invariants_fixed():
    payload = load("stress")
    assert set(payload["fixed_quantities_required"]) == {"total energy", "all exact charges", "topological number", "mode occupations", "boundary data"}
    assert payload["sigma_eigenvalue_difference"] is None
    assert payload["constructive_binding_claimed"] is False


def test_sigma_hessian_shift_comes_from_actual_interaction_and_sign_is_not_assumed():
    assert hs.independent_field_sigma_shift(-2.0, 3.0) == -6.0
    payload = load("sigma_shift")
    assert payload["coefficient_gamma"] is None
    assert payload["sign"] is None
    assert payload["actual_selected_interaction"] is None


def test_sigma_self_quartic_cannot_trigger_instability_at_zero():
    assert hs.sigma_self_hessian_shift(8.0, 0.0) == 0.0
    assert hs.sigma_self_hessian_shift(8.0, 0.5) == 6.0
    payload = load("sigma_shift")["self_sigma_quartic"]
    assert payload["shift_at_sigma_zero"] == 0
    assert payload["stable_G_positive_sign"] == "nonnegative"


def test_physicality_threshold_has_no_implicit_control_or_critical_value():
    payload = load("threshold")
    assert payload["control_variable"] is None
    assert payload["critical_value"] is None
    assert payload["crossing_direction"] is None
    assert "no stable coherent source" in payload["reason"]


def test_coupled_formed_phase_and_full_hessian_remain_open():
    payload = load("coupled")
    assert len(payload["hessian_sectors"]) == 6
    assert payload["sigma"] is None
    assert payload["negative_modes"] is None
    assert payload["enclosure"] is None


def test_topology_is_not_confused_with_energetic_stability():
    rules = load("rules")["rows"]
    topology = next(row for row in rules if row["gate"] == "orientation/Hopf number")
    assert topology["status"] == "no selected topological sector"
    assert load("variational")["second_constrained_variation"] is None


def test_resonance_does_not_select_metric_or_absolute_scale():
    metric = load("metric")
    assert metric["L4_over_L2"] is None
    assert metric["action_stationarity_satisfied"] is False
    assert metric["overall_scale"] is None
    scale = load("scale")
    assert scale["base_frequency"] is None
    assert scale["absolute_radius"] is None


def test_external_round_container_is_not_called_emergent():
    payload = load("enclosure")
    assert payload["round_S7_container"] == "externally specified spectral diagnostic"
    assert payload["container_called_emergent"] is False
    assert payload["requirements_closed"] is False
    assert payload["finite_container"]["critical_radius"] is None
    assert "1/L" in payload["finite_container"]["mode_spacing"]


def test_parent_to_v5_and_generation_firewall_remain_closed():
    payload = load("v5_map")
    assert payload["admissible_1_2_3"] == "not identified with resonant channels"
    assert payload["sigma_half"] == "not parent-derived"
    assert payload["A_ST"] == "not parent-derived"
    assert payload["G_ST"] == "not parent-derived"
    assert payload["particle_generations_identified"] is False


def test_formation_release_and_de_enveloping_remain_separate_in_public_doctrine():
    text = DOC.read_text(encoding="utf-8")
    for term in ("Physicality formation", "primordial release", "black-hole de-enveloping"):
        assert term.lower() in text.lower()


def test_previous_v603_artifacts_are_not_rewritten():
    paths = list(ARTIFACTS.glob("*v6_0_3.json"))
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    hs.build_artifact_payloads(ROOT)
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    assert paths and before == after


def test_report_routes_to_parent_matter_action_without_manufacturing_interaction():
    report = load("report")
    assert report["status"] == "BHSM_HARMONIC_SELECTION_SOURCE_NOT_DERIVED"
    assert report["selected_parent_field"] is None
    assert report["selected_coupling"] is None
    assert report["completion_gate_status"] == "V6_0_4_STOP_LINEAR_NO_SELECTION_EXACT_OCTAVE_SOURCE_BLOCKED"
    assert report["recommended_next_branch"] == "bhsm-parent-matter-conserved-stress-action-v6-0-5"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "harmonic-physicality-selection-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_HARMONIC_SELECTION_SOURCE_NOT_DERIVED"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "BHSM v6.0.4 Harmonic" in markdown.stdout


def test_public_ledgers_preserve_claim_boundary():
    text = focused_text()
    assert "BHSM_HARMONIC_SELECTION_SOURCE_NOT_DERIVED" in text
    assert "BHSM_PHYSICALITY_COUPLING_SELECTION_BLOCKED" in text
    assert "harmonic-physicality-selection-status" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    forbidden = ["octaves derive particle generations", "harmonic interference binds physical spacetime", "absolute unit is generated", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
