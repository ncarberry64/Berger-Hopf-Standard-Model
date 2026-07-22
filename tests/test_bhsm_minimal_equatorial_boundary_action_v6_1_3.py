import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import m4_lorentz_localization as v612
from bhsm.interface import minimal_equatorial_boundary_action as action


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_minimal_equatorial_boundary_action_v6_1_3.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / action.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in action.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_twenty_three_deterministic_claim_safe_artifacts():
    assert len(action.ARTIFACT_FILES) == 23
    assert len(set(action.ARTIFACT_FILES.values())) == 23
    built = action.build_artifact_payloads(ROOT)
    for key, filename in action.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == action.PRIMARY_RESULT, key
        assert payload["physical_Dirac_equation_assumed"] is False, key
        assert payload["magnetic_monopole_sector_used"] is False, key
        assert payload["measured_mass_or_coupling_used"] is False, key
        assert payload["absolute_unit_claimed"] is False, key
        assert payload["frozen_predictions_changed"] is False, key
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == action.deterministic_json(built[key])


def test_v612_theorem_and_public_documentation_merge_are_preserved():
    assert v612.PRIMARY_RESULT == "BHSM_M4_LORENTZ_SELECTED_LOCALIZATION_DERIVED"
    assert v612.power_collar_closed_form(4)["delta_scalar"] == pytest.approx(1 / 6)
    assert (ROOT / "docs" / "bhsm_in_plain_language.md").is_file()
    assert "#154" in (ROOT / "docs" / "bhsm_scientific_contribution_ledger.md").read_text(encoding="utf-8")


def test_boundary_axiom_is_provisional_and_fields_are_independent():
    payload = load("axiom")
    assert "NOT PARENT-DERIVED" in payload["classification"]
    assert len(payload["fields"]) == 3
    assert all("independent" in value for value in payload["fields"].values())
    assert payload["preferred_representative"] is None
    assert payload["frozen_before_kill_tests"] is True


def test_finite_intrinsic_term_dilutes_but_cannot_cancel_trace_mismatch():
    baseline = action.trace_field_mismatch(2, 3, 0)
    diluted = action.trace_field_mismatch(2, 3, 100)
    assert baseline["bulk_difference"] == diluted["augmented_difference"] == 1
    assert 0 < diluted["augmented_ratio_minus_one"] < baseline["augmented_ratio_minus_one"]
    assert load("trace")["intrinsic_requirement"] == "BHSM_INTRINSIC_BOUNDARY_FIELD_FORMULATION_REQUIRED_FOR_EXACT_M4_LORENTZ"


def test_action_freeze_has_no_post_calculation_additions_and_zero_primary_potential():
    payload = load("freeze")
    assert payload["potential_primary_kill_test"] == "U_partial=0"
    assert payload["fields_added"] == []
    assert "physical fermion action" in payload["prohibited"]
    assert payload["term_added_after_freeze"] is False


def test_exact_metric_multiplier_adds_no_primitive_or_penalty():
    payload = load("matching")
    assert payload["multiplier"]["physical_primitive"] is False
    assert payload["penalty_coefficient"] is None
    assert "no formal overconstraint" in payload["overconstraint"]
    assert "remains intrinsic" in payload["connection"]


def test_one_normalization_ansatz_is_computable_but_not_locked():
    row = action.coefficient_lock_candidate(2, 3, 5, 7, 11)
    assert row == pytest.approx({"C_partial": 6 / 121, "tau_A": 10, "Z_partial": 14 / 121})
    payload = load("lock")
    assert payload["status"] == "BHSM_BOUNDARY_ONE_NORMALIZATION_HYPOTHESIS_UNDERDETERMINED"
    assert payload["spectral_or_Dirac_lock_used"] is False
    assert payload["measured_coupling_used"] is False


def test_primitive_count_separates_raw_coefficients_from_field_conventions():
    free = action.independent_primitive_count()
    sourced = action.independent_primitive_count(scalar_potential=True)
    assert free["raw_coefficients"] == 3
    assert free["physical_invariants_before_potential"] == 2
    assert free["scalar_normalization_physical"] is False
    assert sourced["physical_invariants_with_scalar_source"] == 3
    assert load("primitives")["field_convention_called_prediction"] is False


def test_intrinsic_gravity_sector_has_two_healthy_principal_modes():
    payload = load("gravity")
    assert payload["physical_polarizations"] == 2
    assert payload["tensor_speed_squared"] == 1
    assert payload["Lorentz_mismatch"] == 0
    assert payload["observed_Planck_identification"] is None


def test_canonical_connection_cubic_and_quartic_coefficients_match():
    row = action.canonical_connection_coefficients(8, 2)
    assert row["canonical_factor"] == 4
    assert row["geometric_interaction"] == pytest.approx(0.25)
    assert row["cubic_coefficient"] == pytest.approx(0.25)
    assert row["quartic_coefficient"] == pytest.approx(0.0625)
    assert load("connection")["observed_coupling"] is None


def test_nested_u1_is_not_double_counted_or_called_hypercharge():
    payload = load("u1")
    assert payload["independent_boundary_connection"] is False
    assert payload["double_counted"] is False
    assert payload["physical_hypercharge"] is None
    assert payload["magnetic_interpretation"] is None


def test_free_scalar_is_canonical_neutral_and_has_round_s3_spectrum():
    assert action.scalar_mode_mass_squared(0, 2) == 0
    assert action.scalar_mode_mass_squared(2, 2) == 2
    payload = load("sigma")
    assert payload["charge"] == "neutral"
    assert payload["parity"].startswith("Z2 even")
    assert payload["Higgs_identification"] is None
    assert load("potential")["status"] == "BHSM_BOUNDARY_SIGMA_KINETIC_ACTION_DERIVED_POTENTIAL_OPEN"


def test_combined_variation_contains_intrinsic_stress_and_exact_matching():
    payload = load("variation")
    assert "S_GHY" in payload["total_action"]
    assert "2C_partial G_mu nu" in payload["junction"]
    assert payload["metric_constraint"] == "h=iota^*g"
    assert "conditional" in payload["energy_conservation"]


def test_intrinsic_gravity_forces_nonzero_round_equator_junction_residual():
    einstein = action.intrinsic_einstein_tensor(2, 0, 0)
    residual = action.round_equator_junction_residual(3, 2, 0, 0)
    assert einstein["G00"] == pytest.approx(0.75)
    assert residual["residual_00"] == pytest.approx(4.5)
    payload = load("backreaction")
    assert "not an exact solution" in payload["round_status"]
    assert payload["ignored_to_preserve_background"] is False


def test_lorentz_principal_speeds_are_exact_and_full_spectrum_stays_open():
    assert set(load("lorentz")["speeds_squared"].values()) == {1}
    stability = load("stability")
    assert "metric matching multiplier" in stability["removed"]
    assert len(stability["open"]) == 4
    assert stability["physical_negative_mode_claim"] is None


def test_boundary_status_is_conditional_and_no_axis_is_selected():
    payload = load("boundary")
    assert payload["status"] == "BHSM_EQUATORIAL_M4_INTRINSIC_BOUNDARY_DOMAIN_DERIVED_CONDITIONALLY"
    assert payload["parent_derivation"] is False
    assert payload["unique_axis"] is False
    assert payload["background_solution"] == "shifted junction solution required"


def test_currents_and_aperture_do_not_become_observed_charges():
    current = load("current")
    aperture = load("aperture")
    assert current["sigma_current"] == 0
    assert current["observed_charge"] is None
    assert current["magnetic_current"] is None
    assert aperture["e_eff"] is None
    assert aperture["alpha"] is None


def test_parent_map_preserves_v5_values_and_exposes_open_potential():
    payload = load("parent_map")
    assert payload["A_ST"] == "not derived"
    assert payload["G_ST"] == "not derived"
    assert payload["frozen_values_changed"] is False
    assert payload["map"]["scalar_quadratic"] == "unresolved"


def test_fermionic_readiness_never_installs_a_physical_dirac_or_monopole_sector():
    payload = load("fermionic")
    assert payload["physical_first_order_action"] is None
    assert payload["physical_Dirac_equation"] is None
    assert payload["monopole_dependency"] is None


def test_scale_remains_symbolic_and_no_absolute_unit_is_generated():
    payload = load("scale")
    assert payload["a_min_squared"] == "21 kappa_1/(2 kappa_0)"
    assert payload["absolute_unit"] is None
    assert payload["a_min_called_absolute"] is False


def test_report_records_multiple_primitives_and_recommends_source_theorem():
    payload = load("report")
    assert payload["status"] == action.PRIMARY_RESULT
    assert payload["completion_gate"] == action.COMPLETION_GATE
    assert payload["recommended_next_branch"] == "bhsm-boundary-coefficient-source-theorem-v6-1-4"
    assert payload["full_bhsm_status"] == "FULL_BHSM_NOT_COMPLETE"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "minimal-equatorial-boundary-action-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == action.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.1.3 Minimal Equatorial Boundary Action Freeze" in markdown.stdout


def test_public_claim_language_preserves_all_permanent_firewalls():
    text = public_text()
    required = [action.PRIMARY_RESULT, action.COMPLETION_GATE, "FULL_BHSM_NOT_COMPLETE"]
    assert all(label in text for label in required)
    forbidden = ["M4 is observed spacetime", "Sp(1) is the Standard Model", "U(1) is hypercharge", "Chern number is magnetic charge", "alpha is derived", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_invalid_numeric_domains_are_rejected():
    with pytest.raises(ValueError):
        action.trace_field_mismatch(2, 1, 0)
    with pytest.raises(ValueError):
        action.coefficient_lock_candidate(1, 1, 1, 1, 0)
    with pytest.raises(ValueError):
        action.canonical_connection_coefficients(-1, 1)
    with pytest.raises(ValueError):
        action.scalar_mode_mass_squared(-1, 1)
    with pytest.raises(ValueError):
        action.intrinsic_einstein_tensor(0, 0, 0)
