import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import absolute_unit_anchor_generation as aua
from bhsm.interface import pilot_wave_scale_modulus_dynamics as pw


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_pilot_wave_scale_modulus_dynamics_v5_9.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_v59(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / pw.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in pw.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_9_artifacts_exist_parse_and_preserve_guards():
    for key, filename in pw.ARTIFACT_FILES.items():
        payload = load_v59(key)
        assert (ARTIFACT_DIR / filename).exists(), key
        assert payload["version"] == "v5.9"
        assert payload["sprint"] == "bhsm-pilot-wave-scale-modulus-dynamics-v5-9"
        assert payload["primary_result"] == "BHSM_PILOT_WAVE_DOES_NOT_LIFT_SCALE_MODULUS"
        assert payload["empirical_inputs_used"] is False
        assert payload["observed_mass_or_vev_used"] is False
        assert payload["cosmological_parameter_used"] is False
        assert payload["planck_length_inserted"] is False
        assert payload["wavepacket_width_promoted_to_physical_scale"] is False
        assert payload["regulator_promoted_to_physical_scale"] is False
        assert payload["factor_ordering_selected_to_force_scale"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["numerical_particle_masses_emitted"] is False
        assert payload["physical_couplings_promoted"] is False


def test_materialized_v5_9_artifacts_match_builders():
    built = pw.build_artifact_payloads(ROOT)
    for key, filename in pw.ARTIFACT_FILES.items():
        assert (ARTIFACT_DIR / filename).read_text(encoding="utf-8") == pw.deterministic_json(built[key])


def test_pilot_wave_ontology_separates_wavefunctional_actual_configuration_and_fields():
    ontology = load_v59("wave_equation")["ontology_separation"]
    assert ontology["Psi"] == "universal wavefunctional on configuration space"
    assert ontology["Q_actual"] == "actual configuration guided by Psi"
    assert "not identical to Psi" in ontology["T_and_Phi"]
    assert "amplitude and phase" in ontology["R_and_S"]


def test_configuration_metric_is_scale_covariant():
    metric_1 = pw.configuration_metric(1.0)
    metric_2 = pw.configuration_metric(2.0)
    assert metric_1["G_AB"]["LL"] == pytest.approx(1.0)
    assert metric_1["G_inverse_AB"]["LL"] == pytest.approx(1.0)
    assert metric_1["sqrt_abs_G"] == pytest.approx(1.0)
    assert metric_2["G_AB"]["LL"] == pytest.approx(0.25)
    assert metric_2["G_inverse_AB"]["LL"] == pytest.approx(4.0)
    assert metric_2["determinant"] == pytest.approx(0.25)
    assert metric_2["sqrt_abs_G"] == pytest.approx(0.5)
    assert metric_1["measure"] == "dmu_Q = dL d sigma_scale / L = d(ln L) d sigma_scale"
    assert "L -> lambda L" in metric_1["scale_transformation"]


def test_canonical_dynamics_preserves_v5_8_flat_L_modulus_and_sigma_branch():
    payload = load_v59("canonical_hamiltonian")
    classical = payload["classical_static_limit"]
    assert pw.sigma_force(0.5) == pytest.approx(0.0)
    assert classical["sigma_hessian"] == pytest.approx(4.0)
    assert classical["dU_dL"] == pytest.approx(0.0)
    assert classical["v5_8_flat_L_preserved"] is True
    assert payload["hamiltonian"] == "H_red = N [1/2 L^2 p_L^2 + 1/2 p_sigma^2 + U_BHSM(sigma)]"


def test_wave_equation_uses_laplace_beltrami_without_factor_ordering_scale():
    payload = load_v59("wave_equation")
    assert payload["laplace_beltrami"] == "Delta_G = L^2 partial_L^2 + L partial_L + partial_sigma^2"
    assert payload["ordering"] == "Laplace-Beltrami ordering; no factor ordering selected to force a scale"
    assert payload["ordering_ambiguity"]["status"] == "dimensionless_open_but_not_used_to_select_L"
    assert "timeless Hamiltonian constraint" in payload["internal_time_or_timeless"]


def test_bohmian_quantum_potential_guidance_and_trajectory_do_not_fix_L0():
    assert pw.quantum_potential(1.0, pw.SIGMA_0) == pytest.approx(2.0)
    assert pw.quantum_force_L(1.0, pw.SIGMA_0) == pytest.approx(0.0)
    assert pw.quantum_force_sigma(1.0, pw.SIGMA_0) == pytest.approx(0.0)
    assert pw.guidance_vector(3.0, pw.SIGMA_0) == {"Ldot": 3.0, "sigmadot": 0.0}

    trajectory = pw.trajectory_sample(tau=1.0, L_initial=1.0)
    assert trajectory["L_tau"] == pytest.approx(math.e)
    assert trajectory["guidance_residual_L"] == pytest.approx(0.0)
    assert trajectory["guidance_residual_sigma"] == pytest.approx(0.0)
    assert trajectory["expanding_branch"] is True

    report = load_v59("construction_report")
    assert report["scale_modulus_result"]["finite_L0"] is None
    assert report["scale_modulus_result"]["ell_star"] is None
    assert report["scale_modulus_result"]["M_star"] is None
    assert report["scale_modulus_result"]["M_BH"] is None
    assert report["scale_modulus_result"]["R_BH"] is None


def test_scaling_audit_and_hidden_scale_audit_reject_forced_unit_anchor():
    scaling = load_v59("quantum_scaling")
    assert scaling["global_scale_symmetry_preserved"] is True
    assert scaling["classification"] == "quantum dynamics preserves the flat scale modulus"
    assert scaling["does_not_confuse_wave_packet_with_derived_scale"] is True

    hidden = load_v59("hidden_scale_audit")
    assert hidden["status"] == "NO_HIDDEN_SCALE_PROMOTED"
    assert all(row["promoted_to_physical_scale"] is False for row in hidden["rows"])
    assert hidden["arbitrary_gaussian_width_promoted_to_physical_constant"] is False
    assert hidden["node_divergence_promoted_to_scale"] is False
    rows = {row["item"]: row for row in hidden["rows"]}
    assert rows["regulator"]["classification"] == "not used"
    assert rows["factor-ordering parameter"]["value"] == "xi_order"


def test_boundary_state_is_open_and_relics_remain_physical():
    boundary = load_v59("boundary_state")
    assert boundary["absolute_L_derived"] is False
    assert boundary["turning_point_derived"] is False
    assert boundary["wavefunction_width_derived"] is False
    assert "ell_star" in boundary["boundary_state_does_not_fix"]

    mapping = load_v59("construction_report")["primordial_to_late_time_map"]
    assert mapping["redshifted_relics"] == "physical on-shell relic matter/radiation, not virtual"
    assert mapping["observational_confirmation_claimed"] is False
    assert mapping["redshift_generates_scale"] is False


def test_scalar_topographic_branch_stays_stationary_and_distinct_from_pilot_wave():
    scalar = load_v59("construction_report")["scalar_topographic_effect"]
    assert scalar["classical_vacuum_retained"] is True
    assert scalar["sigma_scale"] == pytest.approx(0.5)
    assert scalar["classical_force_at_sigma0"] == pytest.approx(0.0)
    assert scalar["quantum_force_at_sigma0"] == pytest.approx(0.0)
    assert scalar["combined_force_at_sigma0"] == pytest.approx(0.0)
    assert scalar["classical_action_and_quantum_potential_kept_distinct"] is True


def test_v5_8_scale_modulus_artifact_records_v5_9_no_lift_update():
    scale_modulus = json.loads((ARTIFACT_DIR / aua.ARTIFACT_FILES["scale_modulus"]).read_text(encoding="utf-8"))
    update = scale_modulus["v5_9_pilot_wave_update"]
    assert update["status"] == "BHSM_PILOT_WAVE_DOES_NOT_LIFT_SCALE_MODULUS"
    assert update["boundary_state_status"] == "OPEN_MISSING_PRIMORDIAL_QUANTUM_BOUNDARY_STATE_CLOSURE"
    assert update["nonlinear_backreaction_status"] == "OPEN_MISSING_NONLINEAR_GEOMETRIC_BACKREACTION"
    assert "does not generate ell_star" in update["claim_boundary"]


def test_cli_status_json_and_markdown_are_available():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "pilot-wave-scale-modulus-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_result"] == "BHSM_PILOT_WAVE_DOES_NOT_LIFT_SCALE_MODULUS"
    assert payload["scale_modulus_result"]["finite_L0"] is None

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "pilot-wave-scale-modulus-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.9 Pilot-Wave Scale-Modulus Dynamics" in markdown.stdout


def test_public_ledgers_include_v5_9_claim_boundary_and_open_gates():
    text = focused_text()
    assert "BHSM_PILOT_WAVE_DOES_NOT_LIFT_SCALE_MODULUS" in text
    assert "OPEN_MISSING_PRIMORDIAL_QUANTUM_BOUNDARY_STATE_CLOSURE" in text
    assert "OPEN_MISSING_NONLINEAR_GEOMETRIC_BACKREACTION" in text
    assert "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR" in text
    assert "python -m bhsm.interface pilot-wave-scale-modulus-status --format markdown" in text
    assert "physical on-shell relic matter/radiation, not virtual" in text


def test_forbidden_v5_9_promotions_are_absent():
    text = focused_text()
    forbidden = (
        "v5.9 derives ell_star",
        "v5.9 derives M_star",
        "finite L0 is derived",
        "Planck length is inserted",
        "Hubble rate fixes",
        "CMB temperature fixes",
        "wavepacket width is a BHSM unit anchor",
        "regulator is a BHSM unit anchor",
        "particle masses are derived",
        "gauge couplings are derived",
        "CKM values are derived",
        "rare-B observables are predicted",
        "full BHSM completion is achieved",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    report = load_v59("construction_report")
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
