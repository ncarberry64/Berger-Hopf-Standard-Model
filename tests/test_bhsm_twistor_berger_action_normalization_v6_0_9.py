import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import twistor_berger_action_normalization as an


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_twistor_berger_action_normalization_v6_0_9.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / an.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / filename for filename in an.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_package_has_twenty_three_deterministic_claim_safe_artifacts():
    assert len(an.ARTIFACT_FILES) == 23
    assert len(set(an.ARTIFACT_FILES.values())) == 23
    built = an.build_artifact_payloads(ROOT)
    for key, filename in an.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == an.PRIMARY_RESULT, key
        assert payload["fixed_parent_branch"] == "P1", key
        assert payload["p2_p3_used_to_repair_p1"] is False, key
        assert payload["v6_0_8_architecture_preserved"] is True, key
        assert payload["v6_0_7_topological_obstruction_preserved"] is True, key
        assert payload["measured_input_used"] is False, key
        assert payload["frozen_predictions_changed"] is False, key
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == an.deterministic_json(built[key])


def test_physical_measure_round_limit_and_iterated_pushforward():
    v = an.volumes(0.5, 0.5, 0.5)
    assert v["S7"] == pytest.approx(math.pi**4 / 3)
    assert v["S3"] == pytest.approx(v["S1"] * v["S2"])
    assert v["CP3"] * v["S1"] == pytest.approx(v["S7"])
    with pytest.raises(ValueError):
        an.volumes(1, 0, 1)


def test_p1_scalar_curvature_includes_connection_and_round_checks():
    assert an.fiber_scalar_curvature(1, 1) == pytest.approx(1.5)
    assert an.p1_scalar_curvature(0.5, 0.5, 0.5) == pytest.approx(42)
    payload = load("curvature")
    assert "-(1/4) h_ab" in payload["connection_metric_identity"]
    assert payload["status"] == "BHSM_P1_TWISTOR_BERGER_CURVATURE_REDUCTION_DERIVED"


def test_connection_kinetic_matrix_is_exactly_diagonal_positive_and_composes():
    kappa, l2, l1 = 2.0, 3.0, 5.0
    matrix = an.connection_kinetic_matrix(kappa, l2, l1)
    assert matrix[0][0] == pytest.approx(8 * math.pi**2 * kappa * l2**4 * l1)
    assert matrix[1][1] == matrix[0][0]
    assert matrix[2][2] == pytest.approx(8 * math.pi**2 * kappa * l2**2 * l1**3)
    assert all(matrix[i][j] == 0 for i in range(3) for j in range(3) if i != j)
    assert all(value > 0 for value in an.canonical_connection_scales(kappa, l2, l1))
    with pytest.raises(ValueError):
        an.connection_kinetic_matrix(-1, 1, 1)


def test_anisotropic_connection_normalization_is_not_a_physical_sm_coupling():
    payload = load("connection_map")
    assert payload["physical_coupling"] is None
    assert "not one Sp(1)-invariant gauge coupling" in payload["anisotropy_warning"]
    assert load("gauge")["standard_model_coupling"] is None


def test_modulus_dewitt_and_shape_matrices_expose_constrained_conformal_mode():
    assert an.dewit_log_metric() == [[-12, -8, -4], [-8, -2, -2], [-4, -2, 0]]
    shape = an.shape_log_metric()
    assert shape[0] == [-42.0, 0.0, 0.0]
    assert shape[1][1] > 0 and shape[2][2] > 0
    payload = load("moduli")
    assert "lapse-constrained" in payload["conformal_mode"]
    assert "Weyl frame" in payload["einstein_frame_dependency"]


def test_canonical_multiplet_and_interaction_volume_powers_are_not_assumed():
    z, l2, l1 = 3.0, 2.0, 4.0
    vf = 16 * math.pi**2 * l2**2 * l1
    assert an.canonical_multiplet_coefficient(z, l2, l1) == pytest.approx(z * vf)
    cubic = an.canonical_interaction_coefficient(5, 3, 2, z, l2, l1)
    assert cubic == pytest.approx(10 * z ** (-1.5) * vf ** (-0.5))
    assert load("multiplets")["unit_kinetic_assumed_early"] is False


def test_exact_overlap_selection_rules_kill_forbidden_channels():
    assert an.cubic_channel_allowed([(0, 0), (1, 1), (1, -1)])
    assert not an.cubic_channel_allowed([(1, 1), (1, 1), (2, 0)])
    assert not an.cubic_channel_allowed([(0, 0), (0, 0), (2, 0)])
    assert an.quartic_channel_allowed([(1, 1), (1, -1), (1, 1), (1, -1)])
    assert not an.quartic_channel_allowed([(1, 1), (1, 1), (1, 1), (1, -1)])
    with pytest.raises(ValueError):
        an.cubic_channel_allowed([(1, 0), (0, 0), (0, 0)])


def test_low_mode_overlap_normalizations_are_exact_and_volume_explicit():
    assert load("cubic")["exact_low_modes"] == {"I_000": 1, "I_0_A_Abar": 1}
    assert load("quartic")["exact_low_modes"]["I_0000"] == 1
    assert load("quartic")["physical_basis_values"]["Q_0000"] == "Vol(F)^(-1)"


def test_branching_dimension_checks_extend_through_ell_twelve():
    rows = an.branching_checks(12)
    assert len(rows) == 13
    assert all(row["branch_dimension_sum"] == row["so8_harmonic_dimension"] for row in rows)


def test_exact_singlet_tower_gap_and_level_crossing():
    round_gap = an.spectral_gap(1, 1)
    assert round_gap["gap"] == pytest.approx(0.75)
    assert "J=1/2" in round_gap["lowest_channel"]
    below = an.spectral_gap(1, 0.1)
    assert below["gap"] == pytest.approx(2)
    assert below["lowest_channel"] == "(J=1,m=0)"
    crossing = an.spectral_gap(1, 1 / math.sqrt(6))
    assert crossing["gap"] == pytest.approx(2)
    assert crossing["lowest_channel"].startswith("degenerate")


def test_tower_resolvent_is_controlled_only_below_the_gap():
    result = an.tower_error_bound(0.1, 1.0, 0.2)
    assert result["controlled"] is True
    assert result["resolvent_norm_bound"] == pytest.approx(1 / 0.9)
    assert result["derivative_remainder_bound"] == pytest.approx(1 / 9)
    failed = an.tower_error_bound(1.0, 1.0)
    assert failed["controlled"] is False
    assert math.isinf(failed["resolvent_norm_bound"])
    assert load("tower")["one_loop_computed"] is False


def test_p1_fixed_lapse_extrema_do_not_become_parent_vacua_or_absolute_units():
    branches = an.fixed_lapse_stationary_branches(2, 3)
    assert branches[0]["L4_squared"] == pytest.approx(45 / 4)
    assert branches[1]["L2_over_L4"] == pytest.approx(1 / math.sqrt(5))
    scale = load("scale")
    assert "violates" in scale["lorentzian_constraint"]
    assert scale["absolute_unit_anchor"] is None
    stability = load("stability")
    assert stability["round_leading_principal_minors"] == [24, 224, 960]
    assert "saddle" in stability["classification"]


def test_sigma_is_a_candidate_not_a_reverse_engineered_v5_identification():
    payload = load("sigma")
    assert payload["status"] == "BHSM_SIGMA_PARENT_CANDIDATE_SELECTED"
    assert payload["new_field_added"] is False
    assert "identification with the v5" in payload["not_derived"][0]
    assert load("parent_v5")["reverse_engineering_used"] is False


def test_p2_p3_are_not_added_after_p1_calculation_begins():
    payload = load("lovelock")
    assert payload["included_in_P1_result"] is False
    assert payload["role"] == "possible higher-curvature correction study only"


def test_final_result_leads_with_progress_and_retains_the_real_blocker():
    report = load("report")
    assert report["status"] == an.PRIMARY_RESULT
    assert "exact physical measure" in report["central_answer"]
    assert "does not yet supply a full Lorentzian stationary parent background" in report["central_answer"]
    assert report["full_bhsm_status"] == "FULL_BHSM_NOT_COMPLETE"
    assert report["recommended_next_branch"] == "bhsm-p1-lorentzian-background-constraint-closure-v6-0-10"


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "twistor-berger-action-normalization-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == an.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.0.9 Twistor--Berger Action Normalization" in markdown.stdout


def test_public_claim_language_and_forbidden_inputs_are_guarded():
    text = public_text()
    required = [an.PRIMARY_RESULT, "BHSM_PHYSICAL_FIBER_MEASURE_DERIVED", "BHSM_BERGER_TOWER_SPECTRAL_GAP_DERIVED", "FULL_BHSM_NOT_COMPLETE"]
    assert all(label in text for label in required)
    forbidden = ["Standard Model gauge group is derived", "physical gauge coupling is derived", "absolute scale is generated", "full BHSM completion is achieved"]
    assert not any(claim in text for claim in forbidden)
    assert load("hidden")["not_imported"] == ["Planck length", "Hubble rate", "CMB temperature", "measured masses", "PDG values", "W calibration", "CKM fitting", "neutrino limits", "cosmological parameters"]


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
