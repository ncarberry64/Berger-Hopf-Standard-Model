import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import scalar_wall_junction_audit as wall


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_scalar_wall_junction_audit_v6_1_5.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / wall.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [
        DOC,
        ROOT / "STATUS.md",
        ROOT / "CLAIMS.md",
        ROOT / "ARTIFACT_INDEX.md",
        ROOT / "CLI_REFERENCE.md",
    ]
    paths.extend(ARTIFACTS / name for name in wall.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_fourteen_artifacts_are_deterministic_and_guarded():
    assert len(wall.ARTIFACT_FILES) == 14
    built = wall.build_artifact_payloads(ROOT)
    for key, filename in wall.ARTIFACT_FILES.items():
        payload = load(key)
        assert payload["primary_result"] == wall.PRIMARY_RESULT, key
        assert payload["boundary_tension_inserted"] is False, key
        assert payload["new_scalar_interaction_added"] is False, key
        assert payload["vacuum_energy_silently_subtracted"] is False, key
        assert payload["frozen_predictions_changed"] is False, key
        assert payload["official_prediction_logic_changed"] is False, key
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == wall.deterministic_json(built[key])


def test_vacuum_energy_is_retained_and_shifts_kappa0_exactly():
    vacua = wall.scalar_vacua(-2.0, 8.0)
    assert vacua["stable_double_well"] is True
    assert [row["sigma"] for row in vacua["stationary_points"]] == [0.0, -0.5, 0.5]
    assert vacua["stationary_points"][1]["energy"] == pytest.approx(-0.125)
    assert wall.effective_kappa0(5.0, -2.0, 8.0) == pytest.approx(4.75)
    artifact = load("vacuum")
    assert artifact["constant_subtracted"] is False
    assert artifact["kappa0_eff"] == "kappa_0+2U_vac=kappa_0-A5^2/(2G5)"


def test_direct_and_reduced_equations_have_the_required_factors():
    equations = load("equations")
    reduced = load("reduced")
    assert "6kappa_1" in equations["normal_constraint"]
    assert "3kappa_1" in equations["tangential"]
    assert "4H_rho" in equations["scalar"]
    assert reduced["lapse_retained"] is True
    assert reduced["factor_crosscheck"] is True
    assert "delta_N" in reduced


def test_integral_identity_proves_only_the_declared_sign_domain_no_go():
    identity = load("identity")
    assert "A5>=0" in identity["exact_no_go"]
    assert identity["stable_wall_necessary_sign"] == "A5<0 and G5>0"
    assert identity["global_exclusion_claimed"] is False
    assert load("branch")["not_a_global_theorem"] is True


def test_critical_cap_spectral_threshold_converges():
    branch = load("branch")
    rows = branch["eigenvalue_convergence"]
    assert rows[-1]["mu1_over_q5"] == pytest.approx(29.43091835294, rel=2e-11)
    assert abs(rows[-1]["mu1_over_q5"] - rows[-2]["mu1_over_q5"]) < 1e-8
    assert branch["vacuum_regression"]["junction_residual"] == 0
    assert branch["coupled_backreaction_included"] is False
    assert branch["finite_amplitude_coupled_branch_found"] is False


def test_fixed_background_probe_is_nonzero_but_not_promoted():
    branch = load("branch")
    rows = branch["fixed_background_probe"]["convergence"]
    assert rows[-1]["cap_amplitude"] == pytest.approx(4.0478315253, rel=2e-9)
    assert abs(rows[-1]["cap_amplitude"] - rows[-2]["cap_amplitude"]) < 2e-7
    assert branch["outcome"] == "probe branch found; coupled BVP not found/closed"
    assert wall.PRIMARY_RESULT == "BHSM_MINIMAL_P1_SCALAR_WALL_JUNCTION_NOT_FOUND"


def test_flat_control_tension_and_zero_tension_junction_regression():
    control = wall.flat_control_wall(-2.0, 8.0, 3.0)
    assert control["v"] == pytest.approx(0.5)
    assert control["width"] == pytest.approx(math.sqrt(3.0))
    q = 1.0
    C = 0.5
    assert wall.modified_junction_residual(2.0, q, C, 1.0, 0.0) == pytest.approx(0.0)
    assert load("thin")["curved_BHSM_tension"] is None


def test_minimal_wall_does_not_generate_intrinsic_gravity_or_connection():
    source_map = load("sources")["map"]
    assert source_map["C_partial"]["status"] == "BHSM_SCALAR_WALL_DOES_NOT_GENERATE_CPARTIAL"
    assert source_map["tau_A"]["status"] == "BHSM_SCALAR_WALL_DOES_NOT_GENERATE_TAUA"
    assert source_map["Z_partial"]["status"] == "BHSM_WALL_BENDING_SCALAR_NORMALIZATION_DERIVED_CONDITIONALLY"
    assert load("shape")["stress_difference"] == "p1-p2=0"


def test_mixed_stability_remains_open():
    stability = load("stability")
    assert stability["status"] == "BHSM_SCALAR_WALL_MIXED_STABILITY_OPEN"
    assert stability["full_matrix_constructed"] is False
    assert stability["negative_modes"] is None
    assert stability["stability_claimed"] is False


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "scalar-wall-junction-audit-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == wall.PRIMARY_RESULT
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "v6.1.5 Scalar-Wall Junction Audit" in markdown.stdout


def test_public_claims_keep_result_scope_explicit():
    text = public_text()
    required = [
        wall.PRIMARY_RESULT,
        wall.COMPLETION_GATE,
        "BHSM_SCALAR_VACUUM_ENERGY_SHIFT_DERIVED",
        "BHSM_SCALAR_WALL_DOES_NOT_GENERATE_CPARTIAL",
        "FULL_BHSM_NOT_COMPLETE",
    ]
    assert all(label in text for label in required)
    prohibited = [
        "flat kink is the curved BHSM solution",
        "wall derives C_partial",
        "wall derives tau_A",
        "numerical null proves global exclusion",
    ]
    assert not any(phrase in text for phrase in prohibited)


def test_no_forbidden_inputs_or_repairs():
    hidden = load("hidden")
    assert "measured masses" in hidden["not_imported"]
    for key in wall.ARTIFACT_FILES:
        payload = load(key)
        assert payload["P2_or_P3_repair_used"] is False
        assert payload["hard_coded_wall_thickness_used"] is False
        assert payload["bending_mode_called_sigma_partial"] is False


def test_frozen_predictions_and_official_model_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_invalid_domains_are_rejected():
    with pytest.raises(ValueError):
        wall.effective_kappa0(1, 1, 1)
    with pytest.raises(ValueError):
        wall.vacuum_sectional_curvature(2, 0, -1, 1)
    with pytest.raises(ValueError):
        wall.flat_control_wall(1, 1, 1)
    with pytest.raises(ValueError):
        wall.modified_junction_residual(1, 1, 1, 0, 0)
