import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import m4_lorentz_localization as loc
from bhsm.interface import m5_m4_boundary_reduction as v611


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_m4_lorentz_selected_localization_v6_1_2.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / loc.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in loc.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_twenty_five_deterministic_claim_safe_artifacts():
    assert len(loc.ARTIFACT_FILES) == 25
    assert len(set(loc.ARTIFACT_FILES.values())) == 25
    built = loc.build_artifact_payloads(ROOT)
    for key, filename in loc.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == loc.PRIMARY_RESULT, key
        assert payload["v6_1_1_geometry_preserved"] is True, key
        assert payload["physical_fermion_equation_assumed"] is False, key
        assert payload["magnetic_monopole_sector_used"] is False, key
        assert payload["measured_input_used"] is False, key
        assert payload["frozen_predictions_changed"] is False, key
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == loc.deterministic_json(built[key])


def test_v611_result_and_exact_equatorial_geometry_are_preserved():
    assert v611.PRIMARY_RESULT == "BHSM_ROUND_EQUATORIAL_M4_ZERO_MODE_ARCHITECTURE_DERIVED"
    row = v611.equatorial_geometry(2, 0.1, 0.2)
    assert row["K_trace"] == 0
    assert row["spatial_radius"] == 2


def test_scalar_nonnegative_difference_selects_equatorial_support():
    payload = load("scalar_theorem")
    assert "sin(chi)cos^2(chi)" in payload["functionals"]["difference"]
    assert payload["inequality"].startswith("N_t<=N_s")
    assert payload["physical_equality_support"] == "chi=pi/2"
    assert "strict inequality" in payload["smooth_nonzero_bulk_profile"]


def test_collapsed_poles_do_not_supply_finite_nonzero_m4_support():
    scalar = load("scalar_theorem")
    connection = load("connection_theorem")
    assert "collapses S3" in scalar["pole"]
    assert "diverges" in connection["pole"]


def test_connection_difference_is_nonnegative_and_selects_equator():
    payload = load("connection_theorem")
    assert "cos^2(chi)" in payload["functionals"]["difference"]
    assert payload["inequality"].startswith("N_E<=N_B")
    assert payload["equality_support"] == "chi=pi/2"


def test_power_collar_integrals_match_exact_closed_forms():
    for power in (0.5, 1, 3, 10, 100):
        numerical = loc.power_collar_normalizations(power, 2.3)
        exact = loc.power_collar_closed_form(power)
        assert numerical["delta_scalar"] == pytest.approx(exact["delta_scalar"])
        assert numerical["delta_connection"] == pytest.approx(exact["delta_connection"])
        assert numerical["N_s"] == pytest.approx(numerical["N_E"])


def test_finite_width_mismatch_is_positive_and_distributional_limit_is_zero():
    for power in (1, 10, 1000):
        row = loc.power_collar_normalizations(power, 1)
        assert row["delta_scalar"] > 0
        assert row["delta_connection"] > 0
    assert loc.power_collar_closed_form(1e8)["delta_scalar"] < 2e-8
    assert "distributional" in load("scalar_profile")["exact_limit"]


def test_small_width_coefficients_are_declared_without_measured_bound():
    payload = load("mismatch")
    assert payload["small_width"]["scalar"].startswith("epsilon^2-2epsilon^4")
    assert payload["small_width"]["connection"] == "epsilon^2"
    assert payload["measured_bound_comparison"] is None


def test_finite_boundary_kinetic_term_dilutes_but_cannot_cancel_mismatch():
    baseline = loc.boundary_augmented_mismatch(2, 3, 0)
    diluted = loc.boundary_augmented_mismatch(2, 3, 100)
    assert baseline == pytest.approx(0.5)
    assert 0 < diluted < baseline
    assert "leaves N_s-N_t unchanged" in load("boundary_source")["finite_coefficient_effect"]
    with pytest.raises(ValueError):
        loc.boundary_augmented_mismatch(2, 1, 0)


def test_exact_collar_geometry_does_not_by_itself_create_a_bound_state():
    payload = load("collar")
    assert "cos^2(y)" in payload["metric"]
    assert "a^4 cos^3(y)" in payload["measure"]
    assert payload["bound_state_from_round_geometry"] is False


def test_inverse_power_trap_is_a_diagnostic_not_an_action_source():
    power = 6
    assert loc.inverse_scalar_trap(power, 0, 2) == pytest.approx(-0.75)
    assert loc.inverse_scalar_trap(power, 0.2, 2) > loc.inverse_scalar_trap(power, 0, 2)
    assert load("scalar_profile")["status"].endswith("NOT_ACTION_DERIVED")
    assert load("sturm")["source"] is None


def test_p1_ghy_and_smooth_z2_do_not_generate_intrinsic_boundary_dynamics():
    p1 = load("p1_source")
    z2 = load("z2")
    assert not any(p1["automatic_terms"].values())
    assert p1["Brown_York_background"] == 0
    assert z2["K_jump"] == 0
    assert z2["surface_stress_background"] == 0
    assert z2["independent_boundary_dynamics"] is False


def test_great_s3_orbit_is_selected_but_no_representative_is_preferred():
    payload = load("orbit")
    assert "great S3" in payload["selection"]
    assert "SO(5)" in payload["orbit"]
    assert payload["unique_representative"] is False
    assert load("report")["preferred_equator_invented"] is False


def test_sigma_kink_is_conditional_and_frozen_p1_lacks_localizing_couplings():
    row = loc.sigma_kink_conditions(2, -4, 1)
    assert row["exists_algebraically"] is True
    assert row["vacuum_magnitude"] == 2
    assert row["flat_wall_width"] == 1
    assert row["round_S4_profile_stability_derived"] is False
    assert loc.sigma_stationary_points(1, 1) == [0.0]
    assert len(load("sigma_coupling")["absent"]) >= 4
    assert load("sigma_coupling")["inserted"] is False


def test_p2_p3_and_tree_bulk_induction_do_not_close_localization():
    lovelock = load("lovelock")
    assert lovelock["selected"] is False
    assert "independent kappa2" in lovelock["P2"]
    assert "independent kappa3" in lovelock["P3"]
    induced = load("bulk_induction")
    assert "J_H=0" in induced["pure_constant_sigma"]
    assert induced["local_boundary_primitive"] is False
    assert induced["quantum_loop_included"] is False


def test_minimal_boundary_action_family_is_identified_but_unsourced():
    payload = load("boundary_source")
    assert payload["independent_primitives_minimum"] == 3
    assert {row["coefficient"] for row in payload["terms"]} == {"C_partial", "tau_A", "Z_partial"}
    assert all(row["source"] is None for row in payload["terms"])
    assert payload["coefficient_lock_theorem"] is None


def test_tensor_result_is_principal_symbol_only():
    payload = load("gravity")
    assert "principal-symbol" in payload["mismatch"]
    assert "full gauge-fixed tensor Hessian remains required" in payload["constraints"]
    assert payload["observed_Planck_scale"] is None


def test_localized_operator_domain_and_gauge_constraints_are_not_skipped():
    sturm = load("sturm")
    connection = load("connection_profile")
    assert "real V, eta, r" in sturm["self_adjoint"]
    assert "eta u" in sturm["delta_matching"]
    assert "gauge-compatible" in connection["gauge_covariance"]
    assert connection["K4"] is None


def test_currents_aperture_and_fermions_remain_open_and_nonmagnetic():
    currents = load("currents")
    aperture = load("aperture")
    fermionic = load("fermionic")
    assert currents["canonical_coupling"] is None
    assert currents["magnetic_charge"] is None
    assert aperture["alpha"] is None
    assert fermionic["physical_equation"] is None
    assert fermionic["monopole_dependency"] is None


def test_scale_and_parent_maps_add_no_absolute_unit_or_observed_inputs():
    scale = load("scale")
    assert scale["added_primitives_this_sprint"] == 0
    assert scale["absolute_unit"] is None
    assert load("parent_v5")["historical_values_changed"] is False
    assert "Planck scale" in load("hidden")["not_imported"]
    report = load("report")
    assert report["L_eff_invented"] is False
    assert report["standard_model_group_or_charge_assigned"] is False
    assert report["delta_boundary_term_added"] is False
    assert report["boundary_kinetic_term_added"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["existing_numerical_predictions_changed"] is False


def test_report_leads_with_the_derived_selection_and_keeps_action_gate_open():
    payload = load("report")
    assert payload["status"] == loc.PRIMARY_RESULT
    assert payload["action_status"] == "BHSM_M4_EQUATORIAL_LOCALIZATION_SOURCE_SELECTED_ACTION_OPEN"
    assert "selects support" in payload["central_answer"]
    assert payload["completion_gate"] == loc.COMPLETION_GATE
    assert payload["recommended_next_branch"] == "bhsm-minimal-equatorial-boundary-action-freeze-v6-1-3"
    assert payload["full_bhsm_status"] == "FULL_BHSM_NOT_COMPLETE"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "m4-lorentz-localization-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == loc.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.1.2 M4 Lorentz-Selected" in markdown.stdout


def test_public_claim_language_preserves_firewalls():
    text = public_text()
    required = [loc.PRIMARY_RESULT, loc.COMPLETION_GATE, "BHSM_FERMIONIC_CLIFFORD_AND_NO_MONOPOLE_FIREWALL_FROZEN", "FULL_BHSM_NOT_COMPLETE"]
    assert all(label in text for label in required)
    forbidden = ["M4 is observed spacetime", "Sp(1) is the Standard Model", "U(1) is hypercharge", "Chern number is magnetic charge", "alpha is derived", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_invalid_numeric_domains_are_rejected():
    with pytest.raises(ValueError):
        loc.cosine_power_integral(-1)
    with pytest.raises(ValueError):
        loc.power_collar_normalizations(0, 1)
    with pytest.raises(ValueError):
        loc.inverse_scalar_trap(2, math.pi / 2, 1)
