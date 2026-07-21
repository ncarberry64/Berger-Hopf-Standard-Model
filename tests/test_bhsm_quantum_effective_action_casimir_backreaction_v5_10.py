import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import quantum_effective_action_casimir_backreaction as qe


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_quantum_effective_action_casimir_backreaction_v5_10.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_v510(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / qe.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in qe.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_10_artifacts_exist_parse_and_preserve_guards():
    for key, filename in qe.ARTIFACT_FILES.items():
        path = ARTIFACT_DIR / filename
        assert path.exists(), key
        payload = load_v510(key)
        assert payload["version"] == "v5.10"
        assert payload["sprint"] == "bhsm-quantum-effective-action-casimir-backreaction-v5-10"
        assert payload["primary_result"] == "BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL"
        assert payload["empirical_inputs_used"] is False
        assert payload["cosmological_parameter_used"] is False
        assert payload["planck_length_inserted"] is False
        assert payload["cutoff_promoted_to_physical_scale"] is False
        assert payload["subtraction_point_promoted_to_physical_scale"] is False
        assert payload["casimir_coefficient_assumed"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialized_v5_10_artifacts_match_builders():
    built = qe.build_artifact_payloads(ROOT)
    for key, filename in qe.ARTIFACT_FILES.items():
        actual = (ARTIFACT_DIR / filename).read_text(encoding="utf-8")
        assert actual == qe.deterministic_json(built[key])


def test_retained_and_integrated_modes_are_disjoint():
    payload = load_v510("mode_ownership")
    assert payload["overlap"] == []
    assert payload["double_counting_avoided"] is True
    assert payload["integrated_modes"] == ["homogeneous scalar/topographic orthogonal mode"]
    assert "global size" in payload["retained_collective_modes"]
    assert "scalar/topographic scale" in payload["retained_collective_modes"]

    rows = {row["name"]: row for row in payload["rows"]}
    assert rows["homogeneous scalar/topographic orthogonal mode"]["integrated_out"] is True
    assert rows["homogeneous scalar/topographic orthogonal mode"]["retained_collective"] is False
    assert rows["scalar/topographic scale"]["integrated_out"] is False
    assert rows["scalar/topographic scale"]["retained_collective"] is True


def test_every_requested_fluctuation_class_has_an_ownership_row():
    names = {row.name for row in qe.mode_rows()}
    assert {
        "geometric fluctuations",
        "gauge fluctuations",
        "Faddeev-Popov ghosts",
        "fermion fluctuations",
        "nonhomogeneous scalar/topographic modes",
        "charged-current modes",
        "neutral-response modes",
    } <= names


def test_euclidean_operator_ledger_includes_only_positive_finite_scalar_block():
    payload = load_v510("euclidean_operators")
    assert payload["included_bosonic_operator_positive"] is True
    assert payload["included_bosonic_differential_ellipticity_claimed"] is False
    assert payload["full_bosonic_ellipticity_established"] is False
    rows = {row["sector"]: row for row in payload["operators"]}
    assert rows["scalar/topographic orthogonal homogeneous"]["determinant_status"] == "INCLUDED_EXACT_FINITE_REDUCED"
    for sector in ("gauge", "ghost", "fermion positive determinant", "charged", "neutral", "geometry"):
        assert rows[sector]["determinant_status"] == "EXCLUDED"


def test_gauge_and_ghost_determinants_are_blocked_together():
    payload = load_v510("gauge_ghost")
    assert payload["gauge_fixing_functional"] is None
    assert payload["faddeev_popov_operator"] is None
    assert payload["gauge_determinant_included"] is False
    assert payload["ghost_determinant_included"] is False
    assert payload["candidate_d_dagger_d_promoted_to_final_operator"] is False
    assert payload["gauge_parameter_independence_established"] is False


def test_scalar_hessian_modes_match_v5_7_and_ownership_split():
    assert qe.radial_eigenvalue_hat(0.5) == pytest.approx(4.0)
    assert qe.orthogonal_eigenvalue_hat(0.5) == pytest.approx(6.0)
    spectrum = load_v510("spectral_ledger")
    modes = {row["name"]: row for row in spectrum["modes"]}
    assert modes["delta_parallel"]["integrated_out"] is False
    assert modes["delta_perp"]["integrated_out"] is True
    assert modes["delta_perp"]["degeneracy"] == 1
    assert spectrum["complete_BHSM_spectrum"] is False


def test_spectral_eigenvalue_scales_as_L_inverse_squared_without_fixing_L():
    at_one = qe.orthogonal_eigenvalue(1.0)
    at_two = qe.orthogonal_eigenvalue(2.0)
    assert at_two == pytest.approx(at_one / 4.0)
    with pytest.raises(ValueError):
        qe.orthogonal_eigenvalue(0.0)


def test_exact_zeta_and_direct_determinants_agree_without_cutoff():
    for L, sigma, mu in ((1.0, 0.5, 1.0), (2.0, 0.25, 3.0), (0.75, -0.5, 0.4)):
        direct = qe.reduced_log_determinant(L, sigma, mu)
        zeta = qe.reduced_log_determinant_zeta(L, sigma, mu)
        assert direct == pytest.approx(zeta, abs=1.0e-14)
    payload = load_v510("zeta_determinant")
    assert payload["direct_zeta_residual"] == pytest.approx(0.0)
    assert payload["cutoff_used"] is False
    assert payload["fermionic_contribution"] is None
    assert payload["ghost_contribution"] is None


def test_heat_trace_and_zeta_use_the_same_exact_single_eigenvalue():
    L = 1.3
    sigma = 0.4
    eigen = qe.orthogonal_eigenvalue(L, sigma)
    assert qe.reduced_heat_trace(0.0, L, sigma) == pytest.approx(1.0)
    assert qe.reduced_heat_trace(0.2, L, sigma) == pytest.approx(math.exp(-0.2 * eigen))
    assert qe.reduced_zeta(1.0, L, sigma) == pytest.approx(1.0 / eigen)
    with pytest.raises(ValueError):
        qe.reduced_heat_trace(-0.1)
    payload = load_v510("heat_kernel")
    assert payload["heat_trace_and_zeta_use_same_single_eigenvalue"] is True
    assert payload["coefficients_are_field_theory_Seeley_DeWitt"] is False
    assert payload["full_ultraviolet_divergence_structure_derived"] is False


def test_renormalization_scale_is_explicit_and_not_promoted_to_anchor():
    payload = load_v510("renormalization")
    assert payload["renormalization_scale"] == "mu retained explicitly"
    assert payload["mu_derivative_of_reduced_Gamma_1loop"] == pytest.approx(-1.0)
    assert payload["coefficient_running_available_to_cancel_mu"] is False
    assert payload["renormalization_group_invariance_established"] is False
    assert payload["Lambda_BH"] is None
    assert payload["absolute_unit_from_mu_claimed"] is False

    eps = 1.0e-6
    numeric = (
        qe.reduced_one_loop_action(mu=math.exp(eps))
        - qe.reduced_one_loop_action(mu=math.exp(-eps))
    ) / (2.0 * eps)
    assert numeric == pytest.approx(-1.0, rel=1.0e-9)


def test_coordinate_unit_rescaling_leaves_mu_L_combination_invariant():
    initial = qe.reduced_effective_action(L=1.2, sigma=0.5, mu=0.7)
    scale = 3.5
    rescaled = qe.reduced_effective_action(L=scale * 1.2, sigma=0.5, mu=0.7 / scale)
    assert rescaled == pytest.approx(initial)


def test_casimir_and_total_anomaly_outputs_remain_null():
    payload = load_v510("casimir_anomaly")
    assert payload["total_zero_point_sum"] is None
    assert payload["renormalized_vacuum_energy"] is None
    assert payload["finite_Casimir_remainder"] is None
    assert payload["Casimir_sign"] is None
    assert payload["genuine_BHSM_scale_anomaly_derived"] is False
    assert payload["dimensional_transmutation_derived"] is False


def test_reduced_backreaction_gradients_match_finite_differences():
    L = 1.4
    sigma = 0.37
    eps = 1.0e-6
    analytic = qe.effective_gradients(L, sigma)
    dL = (
        qe.reduced_effective_action(L + eps, sigma)
        - qe.reduced_effective_action(L - eps, sigma)
    ) / (2.0 * eps)
    dsigma = (
        qe.reduced_effective_action(L, sigma + eps)
        - qe.reduced_effective_action(L, sigma - eps)
    ) / (2.0 * eps)
    assert analytic["dGamma_dL"] == pytest.approx(dL, rel=1.0e-9)
    assert analytic["dGamma_dsigma"] == pytest.approx(dsigma, rel=1.0e-9)


def test_partial_system_has_no_finite_L_stationary_point_or_positive_coupled_hessian():
    for L in (0.1, 1.0, 10.0, 1.0e6):
        assert qe.effective_gradients(L, 0.5)["dGamma_dL"] < 0.0
    solution = load_v510("effective_solution")
    stationary = solution["stationary_analysis"]
    assert stationary["finite_L0"] is None
    assert stationary["sigma_equation_real_roots"] == [0.0]
    assert stationary["sigma_half_stationary_after_partial_loop"] is False
    assert stationary["sigma_half_force"] == pytest.approx(2.0 / 3.0)
    assert stationary["sigma_zero_hessian"] == pytest.approx(0.0)
    assert solution["positive_physical_hessian"] is False
    assert solution["absolute_ell_star"] is None


def test_partial_diagnostic_does_not_overwrite_sigma_half():
    solution = load_v510("effective_solution")
    assert solution["v5_7_sigma_half_preserved_as_official_input"] is True
    assert solution["partial_diagnostic_not_promoted_to_v5_7_correction"] is True


def test_pilot_wave_update_avoids_one_loop_double_counting():
    payload = load_v510("pilot_wave_update")
    assert payload["one_loop_mode_included_in_Bohmian_quantum_potential"] is False
    assert payload["double_counting_avoided"] is True
    assert payload["official_v5_9_Hamiltonian_changed"] is False
    assert payload["guidance_recomputed"] is False
    assert payload["finite_attractor_generated"] is False
    assert payload["redshift_generates_unit"] is False
    assert payload["redshifted_relics"] == "physical on-shell relics, not virtual"


def test_uploaded_source_audit_uses_no_legacy_or_cosmology_scale():
    payload = load_v510("uploaded_source_audit")
    assert payload["manuscript_files_present_in_attachment"] == []
    assert payload["K_rho_natural_appearance_in_included_hessian"] is False
    assert payload["K_rho_action_derivation_claimed"] is False
    assert payload["old_curvature_threshold_mass_gap_remains_invalidated"] is True
    assert payload["forbidden_values_used"] == []
    rows = {row["source"]: row for row in payload["rows"]}
    assert rows["fine-structure curvature-projection description"]["alpha_promoted"] is False
    assert rows["local-curvature mass description"]["mass_ansatz_used"] is False


def test_cli_status_json_and_markdown_are_available():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "quantum-effective-action-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_result"] == "BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL"
    assert payload["effective_solution"]["stationary_analysis"]["finite_L0"] is None

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "quantum-effective-action-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.10 Quantum Effective Action and Casimir Backreaction" in markdown.stdout


def test_public_ledgers_preserve_primary_result_and_open_gates():
    text = focused_text()
    assert "BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL" in text
    assert "OPEN_MISSING_FULL_GAUGE_FIXED_DOMAIN" in text
    assert "OPEN_MISSING_FADDEEV_POPOV_GHOST_OPERATOR" in text
    assert "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    assert "python -m bhsm.interface quantum-effective-action-status --format markdown" in text


def test_forbidden_v5_10_promotions_are_absent():
    text = focused_text()
    forbidden = (
        "v5.10 derives a physical Casimir energy",
        "v5.10 derives the total trace anomaly",
        "v5.10 derives ell_star",
        "mu is the BHSM absolute unit",
        "the cutoff fixes L_0",
        "particle masses are derived",
        "gauge couplings are derived",
        "CKM values are derived",
        "rare-B observables are predicted",
        "full BHSM completion is achieved",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    report = load_v510("construction_report")
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["existing_numerical_predictions_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
