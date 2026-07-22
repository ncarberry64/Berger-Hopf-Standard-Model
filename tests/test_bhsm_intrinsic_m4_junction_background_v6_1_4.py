import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import intrinsic_m4_junction_background as junction
from bhsm.interface import minimal_equatorial_boundary_action as v613


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_intrinsic_m4_junction_background_v6_1_4.md"
PR156_MERGE = "e4302e1f0fd2cdd597257c1afec9a8a34c90e082"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / junction.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in junction.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_pr156_merge_commit_is_in_history_and_recorded():
    result = subprocess.run(["git", "merge-base", "--is-ancestor", PR156_MERGE, "HEAD"], cwd=ROOT)
    assert result.returncode == 0
    assert load("action")["pr156_merge_commit"] == PR156_MERGE


def test_twenty_five_deterministic_claim_safe_artifacts():
    assert len(junction.ARTIFACT_FILES) == 25
    assert len(set(junction.ARTIFACT_FILES.values())) == 25
    built = junction.build_artifact_payloads(ROOT)
    for key, filename in junction.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == junction.PRIMARY_RESULT, key
        assert payload["frozen_v6_1_3_action_changed"] is False, key
        assert payload["boundary_vacuum_term_added"] is False, key
        assert payload["physical_Dirac_equation_assumed"] is False, key
        assert payload["magnetic_monopole_sector_used"] is False, key
        assert payload["absolute_unit_claimed"] is False, key
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == junction.deterministic_json(built[key])


def test_v613_action_and_provisional_B1_are_unchanged():
    assert v613.PRIMARY_RESULT == "BHSM_MINIMAL_EQUATORIAL_BOUNDARY_ACTION_REQUIRES_MULTIPLE_PRIMITIVES"
    action = load("action")
    assert "C_partial R4" in action["boundary"]
    assert action["terms_added"] == []
    assert action["vacuum"]["U_partial"] == 0
    assert action["boundary_axiom_parent_derived"] is False


def test_bulk_equation_and_ghy_junction_factors_are_explicit():
    payload = load("variation")
    assert payload["bulk_equation"] == "kappa_1 G_AB+(kappa_0/2)g_AB=0"
    assert "kappa_1/2" in payload["canonical_momentum"]
    assert payload["Z2"].startswith("[Q_mu_nu]=2Q_mu_nu^+")
    assert "2C_partial" in payload["junction"]


def test_matching_multiplier_is_exact_nondynamical_and_coefficient_free():
    payload = load("matching")
    assert payload["multiplier_equation"] == "h_mu nu=iota^*g_mu nu"
    assert payload["tunable_matching_coefficient"] is None
    assert payload["propagating_multiplier_mode"] is False
    assert payload["hidden_physical_stress"] is False
    assert "vary independent" in " ".join(payload["variation_order"])


def test_smooth_k0_residual_reproduces_v613_obstruction():
    row = junction.smooth_equator_residual(2, 4, 0.25, -0.01)
    X = 0.25**2 + 1 / 16
    A = -0.01 + 0.25**2
    assert row["X"] == pytest.approx(X)
    assert row["G_t_t"] == pytest.approx(-3 * X)
    assert row["junction_residual_t_t"] == pytest.approx(-12 * X)
    assert row["junction_residual_i_j"] == pytest.approx(-4 * (2 * A + X))
    assert "finite radius" in load("residual")["classification"]


def test_reflection_symmetry_is_not_confused_with_zero_one_sided_curvature():
    payload = load("ansatz")
    assert payload["Z2"].endswith("opposite")
    assert "Z2 does not imply K^+=0" in payload["distinctions"]
    assert payload["one_sided"]["k_s"] == "r_y/r at 0+"


def test_bulk_constant_curvature_has_repository_p1_normalization():
    row = junction.p1_constant_curvature(12, 1)
    assert row == pytest.approx({"lambda_5": 6, "q_5": 1, "bulk_radius": 1})
    equations = load("bulk_equations")
    assert equations["tt"].endswith("-lambda_5=0 after division by n^2")
    assert equations["constraint_propagation"].startswith("nabla^A")


def test_z2_and_one_cap_couplings_keep_the_factor_of_two():
    assert junction.junction_coupling(3, 2, z2=True) == pytest.approx(1.5)
    assert junction.junction_coupling(3, 2, z2=False) == pytest.approx(3)
    payload = load("junction")
    assert payload["bulk_side_count"] == {"one_cap": 1, "Z2_double": 2}


def test_junction_temporal_and_spatial_curvatures_follow_from_lapse_varied_equations():
    row = junction.junction_extrinsic_curvature(5, 5, 0.2, 1, z2=True)
    assert row["eta"] == pytest.approx(0.2)
    assert row["k_t"] == pytest.approx(-1)
    assert row["k_s"] == pytest.approx(-1)
    assert row["jump_k_t"] == pytest.approx(-2)
    assert row["jump_k_s"] == pytest.approx(-2)


def test_two_constant_curvature_roots_satisfy_gauss_and_junction_exactly():
    roots = junction.boundary_curvature_branches(12, 1, 0.25)
    assert roots == pytest.approx([1.0717967697244912, 14.928203230275509])
    for index, X in enumerate(roots):
        geometry = junction.constant_curvature_branch_geometry(12, 1, 0.25, index)
        assert geometry["boundary_curvature"] == pytest.approx(X)
        assert geometry["gauss_residual"] == pytest.approx(0, abs=1e-14)
        assert geometry["reconstructed_C_partial"] == pytest.approx(0.25)
        assert geometry["one_sided_k"] != 0


def test_coefficient_existence_bound_and_critical_double_root():
    bound = junction.coefficient_bound(12, 1)
    assert bound == pytest.approx(0.5)
    assert junction.boundary_curvature_branches(12, 1, bound) == pytest.approx([2])
    assert junction.boundary_curvature_branches(12, 1, 0.51) == []


def test_regular_offset_hyperplane_caps_exist_for_both_roots():
    for index in (0, 1):
        geometry = junction.constant_curvature_branch_geometry(12, 1, 0.25, index)
        assert 0 < geometry["hyperplane_offset_abs"] < geometry["bulk_radius"]
    caps = load("caps")
    assert caps["status"] == "BHSM_REGULAR_Z2_TWO_CAP_GLOBALIZATION_DERIVED_CONDITIONALLY"
    assert caps["second_junction"] is False
    assert "S4" in caps["spatial_topology"]
    assert "regular pole" in caps["poles"]


def test_boundary_lapse_is_varied_before_proper_time_gauge():
    payload = load("frw")
    assert payload["lapse_policy"] == "N_partial is varied before proper-time gauge N_partial=1"
    assert "X=q_5+eta^2X^2" in payload["Hamiltonian"]
    assert len(payload["sign_branches"]) == 4


def test_shifted_closed_de_sitter_trajectory_is_a_regular_bounce():
    X = junction.boundary_curvature_branches(12, 1, 0.25)[0]
    bounce = junction.closed_de_sitter_trajectory(X, 0)
    late = junction.closed_de_sitter_trajectory(X, 1)
    early = junction.closed_de_sitter_trajectory(X, -1)
    assert bounce["a"] == pytest.approx(1 / math.sqrt(X))
    assert bounce["H"] == 0
    assert late["H"] > 0 > early["H"]
    assert late["X"] == pytest.approx(X)
    assert load("branches")["old_cosh"].endswith("fails for C_partial>0")


def test_critical_coefficient_also_has_a_distinct_exact_static_embedding():
    static = junction.critical_static_geometry(12, 1, 0.5)
    assert static["exists"] is True
    assert static["boundary_radius"] == pytest.approx(1 / math.sqrt(2))
    assert static["X"] == pytest.approx(2)
    assert static["acceleration"] == 0
    assert static["k_t"] == pytest.approx(1)
    assert static["k_s"] == pytest.approx(-1)
    assert junction.critical_static_geometry(12, 1, 0.25)["exists"] is False
    assert "exact R x S3" in load("branches")["static"]


def test_background_relation_is_not_promoted_to_universal_coefficient_derivation():
    payload = load("coefficient")
    assert payload["status"] == "BHSM_BOUNDARY_GRAVITY_COEFFICIENT_BACKGROUND_RELATION_DERIVED"
    assert payload["universal_coefficient_derivation"] is False
    assert payload["primitive_status"].startswith("C_partial remains independent")


def test_vacuum_background_does_not_lock_tau_or_Z():
    payload = load("primitives")
    assert payload["C_partial_removed"] is False
    assert payload["tau_A_constrained_by_vacuum"] is False
    assert payload["Z_partial_constrained_by_vacuum"] is False
    assert payload["potential_primitives"] == 0
    assert payload["continuous_physical_coefficient_combinations"] == 4


def test_connection_vacuum_is_stress_free_and_nonmonopole():
    payload = load("connection")
    assert payload["background"] == "A_mu=0"
    assert payload["stress"] == 0
    assert payload["repair_junction_with_connection"] is False
    assert payload["monopole_status"] == "excluded"


def test_sigma_zero_vacuum_imports_no_v5_values_or_constant_energy():
    payload = load("sigma")
    assert payload["background"] == "sigma_partial=0"
    assert payload["potential"].startswith("U_partial=0")
    assert payload["junction_contribution"] == 0
    assert payload["v5_values_imported"] is False


def test_no_boundary_vacuum_term_is_inserted_to_close_the_background():
    payload = load("missing")
    assert payload["required_term"] is None
    assert payload["boundary_tension_added"] is False
    assert payload["parent_potential_constant_added"] is False
    assert payload["candidate_if_triggered"]["coefficient_assigned"] is False


def test_bulk_boundary_conservation_holds_on_retained_vacuum():
    payload = load("conservation")
    assert "T_bulk,n nu" in payload["identity"]
    assert "zero normal flux" in payload["retained_vacuum"]
    assert "Lambda elimination" in payload["matching"]


def test_negative_modes_are_not_claimed_before_full_constraint_reduction():
    payload = load("stability")
    assert "matching multiplier" in payload["constraints_removed"]
    assert payload["negative_modes"] is None
    assert len(payload["open"]) == 4
    assert payload["status"].endswith("FULL_MIXED_STABILITY_OPEN")


def test_tensor_sector_is_mixed_and_normal_spectrum_remains_open():
    payload = load("tensor")
    assert payload["classification"].startswith("mixed bulk-boundary")
    assert payload["normal_spectrum"] == "not solved"
    assert payload["observed_graviton_status"] is None


def test_intrinsic_lorentz_cones_survive_without_causal_overclaims():
    payload = load("lorentz")
    assert set(payload["speeds_squared"].values()) == {1}
    assert payload["superluminal_claim"] is None
    assert payload["acausal_claim"] is None
    assert "well-posedness proof" in payload["matching"]


def test_coefficient_source_and_parent_maps_preserve_open_physical_interpretation():
    sources = load("sources")
    parent = load("parent_map")
    assert sources["tau_A"].startswith("independent")
    assert sources["U_partial"].startswith("absent")
    assert sources["broad_survey_performed"] is False
    assert parent["v5_coefficients_changed"] is False
    assert parent["reverse_engineered_from_v5"] is False


def test_fermionic_readiness_has_no_physical_dirac_or_monopole_dependency():
    payload = load("fermionic")
    assert payload["physical_first_order_action"] is None
    assert payload["physical_Dirac_equation"] is None
    assert payload["monopole_dependence"] is None
    assert payload["self_adjoint_domain"] == "not selected"


def test_scale_is_derived_only_in_terms_of_unsourced_primitives():
    payload = load("scale_hidden")
    assert payload["bulk_radius"] == "L5=sqrt(12kappa_1/kappa_0)"
    assert payload["absolute_unit"] is None
    assert "Planck length" in payload["not_imported"]


def test_report_leads_with_constructed_background_and_keeps_stability_gate_open():
    payload = load("report")
    assert payload["status"] == junction.PRIMARY_RESULT
    assert payload["missing_vacuum_term"] is None
    assert payload["completion_gate"] == junction.COMPLETION_GATE
    assert payload["recommended_next_branch"] == "bhsm-junction-mixed-stability-closure-v6-1-5"
    assert payload["full_bhsm_status"] == "FULL_BHSM_NOT_COMPLETE"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "intrinsic-m4-junction-background-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == junction.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.1.4 Intrinsic M4 Junction-Supported" in markdown.stdout


def test_public_claim_language_preserves_firewalls():
    text = public_text()
    required = [junction.PRIMARY_RESULT, junction.COMPLETION_GATE, "FULL_BHSM_NOT_COMPLETE"]
    assert all(label in text for label in required)
    forbidden = ["M4 is observed spacetime", "intrinsic connection is a Standard Model gauge field", "alpha is derived", "physical Dirac equation is derived", "monopoles exist", "absolute unit is generated", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_invalid_numeric_domains_and_missing_roots_are_rejected():
    with pytest.raises(ValueError):
        junction.p1_constant_curvature(0, 1)
    with pytest.raises(ValueError):
        junction.junction_coupling(1, -1)
    with pytest.raises(ValueError):
        junction.constant_curvature_branch_geometry(12, 1, 0.25, 2)
    with pytest.raises(ValueError):
        junction.closed_de_sitter_trajectory(0, 1)
