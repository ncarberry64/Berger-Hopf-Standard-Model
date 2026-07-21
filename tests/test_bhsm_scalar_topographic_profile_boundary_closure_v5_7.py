import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import physical_scale_generation as psg
from bhsm.interface import scalar_topographic_profile_boundary_closure as stp
from bhsm.interface import scalar_topographic_vacuum_action as stv


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_scalar_topographic_profile_boundary_closure_v5_7.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_v57(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / stp.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def load_v56(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / stv.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def load_v55(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / psg.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in stp.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_7_artifacts_exist_parse_and_preserve_guard_metadata():
    for key, filename in stp.ARTIFACT_FILES.items():
        payload = load_v57(key)
        assert (ARTIFACT_DIR / filename).exists(), key
        assert payload["version"] == "v5.7"
        assert payload["sprint"] == "bhsm-scalar-topographic-profile-boundary-closure-v5-7"
        assert payload["primary_result"] == "SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY"
        assert payload["empirical_inputs_used"] is False
        assert payload["observed_mass_or_vev_used"] is False
        assert payload["pdg_reference_values_used"] is False
        assert payload["w_calibration_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["numerical_particle_masses_emitted"] is False


def test_materialized_v5_7_artifacts_match_deterministic_builders():
    built = stp.build_artifact_payloads(ROOT)
    for key, filename in stp.ARTIFACT_FILES.items():
        assert (ARTIFACT_DIR / filename).read_text(encoding="utf-8") == stp.deterministic_json(built[key])


def test_sigma_scale_and_sigma_profile_are_distinct():
    payload = load_v57("solved_profile")
    rows = {row["symbol"]: row for row in payload["variable_dictionary"]}
    assert rows["sigma_scale"]["definition"] == "normalized vacuum-mode coefficient"
    assert rows["sigma_profile"]["definition"] == "profile width/curvature label"
    assert rows["sigma_profile"]["action_source"] == "not sigma_scale"
    assert payload["profile_solution"]["sigma_profile"] == "infinity for homogeneous lowest mode; no localized width is used"


def test_reduced_bvp_is_deterministic_and_boundary_conditions_close():
    payload = load_v57("solved_profile")
    problem = payload["boundary_problem"]
    assert payload["geometry"]["selected_mode_rule"].startswith("lowest admissible self-adjoint mode")
    assert problem["finite_action"] is True
    assert problem["well_posed"] is True
    assert problem["boundary_variation_cancelled"] is True
    assert problem["level_set_residuals"] == {"Phi_minus_Phi0": 0.0, "T_minus_T0": 0.0}
    assert problem["Robin_residuals"] == {"Phi": 0.0, "T": 0.0}
    assert problem["critical_point_residual_at_y0"] == pytest.approx(0.0)
    assert payload["normalization"]["value"] == pytest.approx(1.0)
    assert payload["normalization"]["residual"] == pytest.approx(0.0)
    assert payload["max_field_residual"] == pytest.approx(0.0)


def test_boundary_coefficients_are_closed_or_marked_conventional_without_fits():
    coeffs = load_v57("solved_profile")["coefficients"]
    assert coeffs["Z_T"]["value"] == pytest.approx(1.0)
    assert coeffs["Z_T"]["status"] == "CONVENTIONAL_CANONICAL_KINETIC_NORMALIZATION"
    assert coeffs["Z_Phi"]["value"] == pytest.approx(1.0)
    assert coeffs["c_K"]["value"] == pytest.approx(0.0)
    assert coeffs["c_K2"]["value"] == pytest.approx(0.0)
    assert coeffs["c_S"]["value"] == pytest.approx(0.0)
    assert coeffs["c_J"]["status"] == "NOT_INDEPENDENT_NO_DOUBLE_COUNT_WITH_COLLAR_JACOBIAN"
    assert coeffs["rho_star"]["status"] == "CONVENTIONAL_NORMALIZED_COLLAR_COORDINATE"
    assert load_v57("construction_report")["empirical_inputs_used"] is False


def test_alpha_beta_and_vacuum_branch_are_evaluated_from_reduced_action():
    payload = load_v57("evaluated_vacuum")
    assert payload["A_ST"] == pytest.approx(-2.0)
    assert payload["C_ST"] == pytest.approx(0.0)
    assert payload["G_ST"] == pytest.approx(8.0)
    assert payload["alpha_scale"] == pytest.approx(2.0)
    assert payload["beta_scale"] == pytest.approx(8.0)
    assert payload["selected_branch"] == pytest.approx(0.5)
    assert payload["vacuum_energy"] == pytest.approx(-0.125)
    assert payload["hessian"] == pytest.approx(4.0)
    assert payload["stable"] is True
    assert payload["global_or_local"] == "global in quartic reduced model when lambda_ST>0"
    assert payload["finite_difference_check"]["passes"] is True


def test_cubic_term_is_retained_or_proven_zero_by_symmetry():
    coeffs = stp.evaluated_coefficients()
    assert coeffs["C_ST"] == pytest.approx(0.0)
    assert "orientation-pair symmetry" in coeffs["cubic_term_retained_or_proven_zero"]
    assert "C_ST=0" in load_v57("evaluated_vacuum")["mode_action"] or load_v57("evaluated_vacuum")["C_ST"] == 0.0


def test_vacuum_profile_satisfies_truncated_field_equations():
    coeffs = stp.evaluated_coefficients()
    residuals = stp.field_residuals(coeffs["sigma_abs"])
    assert residuals["E_T"] == pytest.approx(0.0)
    assert residuals["E_Phi"] == pytest.approx(0.0)
    assert load_v57("solved_profile")["field_equation_residuals"] == pytest.approx(residuals)


def test_hessian_response_is_self_adjoint_invertible_and_stable():
    payload = load_v57("hessian_response")
    flattened = [value for row in payload["hessian_matrix"] for value in row]
    assert flattened == pytest.approx([5.0, -1.0, -1.0, 5.0])
    assert payload["self_adjoint"] is True
    assert payload["zero_modes"] == []
    assert payload["negative_modes"] == []
    assert payload["eigenvalues"] == [4.0, 6.0]
    assert payload["lowest_positive_mode"] == pytest.approx(4.0)
    assert payload["invertible_on_physical_subspace"] is True
    assert payload["green_operator_eigenvalues"] == pytest.approx([0.25, 1.0 / 6.0])
    assert payload["old_curvature_threshold_mass_gap_preserved_invalid"] is True


def test_unit_anchor_remains_open_with_only_dimensionless_ratios():
    unit = load_v57("construction_report")["unit_anchor"]
    assert unit["absolute_scale_fixed"] is False
    assert unit["M_BH_over_M_star"] == pytest.approx(0.5)
    assert unit["R_BH_over_ell_star"] == pytest.approx(2.0)
    assert unit["remaining_unit_input"] == "M_star or ell_star"
    assert unit["absolute_unit_anchor_status"] == "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR"


def test_v5_5_and_v5_6_artifacts_are_updated_with_v5_7_values():
    selected = load_v55("selected_mechanism")["selected_mechanism"]["v5_7_update"]
    v55_report = load_v55("construction_report")["v5_7_update"]
    v56_reduced = load_v56("reduced_vacuum_functional")["v5_7_evaluated_update"]
    v56_solution = load_v56("vacuum_solution")["v5_7_evaluated_update"]
    v56_report = load_v56("construction_report")["v5_7_update"]
    for payload in (selected, v55_report, v56_reduced, v56_solution, v56_report):
        assert payload["status"] == "SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY"
    assert v56_reduced["alpha_scale"] == pytest.approx(2.0)
    assert v56_reduced["beta_scale"] == pytest.approx(8.0)
    assert v56_solution["sigma_scale_vacuum"] == pytest.approx(0.5)
    assert v55_report["scale_potential_action_source_status"] == "CLOSED_CONDITIONALLY_FOR_REDUCED_PROFILE_BVP"


def test_cli_status_json_and_markdown_are_available():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "scalar-topographic-profile-boundary-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_result"] == "SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY"
    assert payload["unit_anchor"]["absolute_scale_fixed"] is False

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "scalar-topographic-profile-boundary-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.7 Scalar/Topographic Profile and Boundary Closure" in markdown.stdout


def test_public_ledgers_include_v5_7_claim_boundary():
    text = focused_text()
    assert "SCALAR_TOPOGRAPHIC_PROFILE_BOUNDARY_CLOSED_CONDITIONALLY" in text
    assert "sigma_scale" in text
    assert "sigma_profile" in text
    assert "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR" in text
    assert "OPEN_MISSING_NONHOMOGENEOUS_BERGER_PROFILE_SOLUTION" in text
    assert "python -m bhsm.interface scalar-topographic-profile-boundary-status --format markdown" in text


def test_forbidden_promotions_are_absent_from_public_v5_7_package():
    text = focused_text()
    forbidden = (
        "numeric eV/GeV scale is derived",
        "particle masses are derived",
        "M_star is derived",
        "ell_star is derived",
        "alpha_i is derived",
        "g2_BH is derived",
        "CKM coefficient value is derived",
        "v5.7 derives CKM exponent",
        "prior mass gap survives",
        "full BHSM completion is achieved",
        "rare-B observables are predicted",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    report = load_v57("construction_report")
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
