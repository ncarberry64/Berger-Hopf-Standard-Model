import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import physical_scale_generation as psg
from bhsm.interface import scalar_topographic_vacuum_action as stv


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_scalar_topographic_vacuum_action_derivation_v5_6.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


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
        *(ARTIFACT_DIR / filename for filename in stv.ARTIFACT_FILES.values()),
        *(ARTIFACT_DIR / filename for filename in psg.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def public_text() -> str:
    paths = [DOC, *(ARTIFACT_DIR / filename for filename in stv.ARTIFACT_FILES.values())]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_6_artifacts_exist_parse_and_preserve_no_fit_metadata():
    for key, filename in stv.ARTIFACT_FILES.items():
        path = ARTIFACT_DIR / filename
        assert path.exists(), key
        payload = load_v56(key)
        assert payload["version"] == "v5.6"
        assert payload["sprint"] == "bhsm-scalar-topographic-vacuum-action-derivation-v5-6"
        assert payload["primary_result"] == "SCALAR_TOPOGRAPHIC_VACUUM_ACTION_DERIVED_CONDITIONALLY"
        assert payload["empirical_inputs_used"] is False
        assert payload["observed_mass_or_vev_used"] is False
        assert payload["w_calibration_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["numerical_particle_masses_emitted"] is False


def test_materialized_artifacts_match_deterministic_builders():
    built = stv.build_artifact_payloads(ROOT)
    for key, filename in stv.ARTIFACT_FILES.items():
        assert (ARTIFACT_DIR / filename).read_text(encoding="utf-8") == stv.deterministic_json(built[key])


def test_sigma_scale_is_distinct_from_profile_width():
    payload = load_v56("order_parameter")
    assert payload["symbol"] == "sigma_scale"
    assert payload["not_profile_width"]["profile_width_symbol"] == "sigma_profile"
    assert "dynamical amplitude coefficient" in payload["not_profile_width"]["reason"]
    assert "Q_ST[f_T,f_Phi]=1" in payload["map"]["normalization"]


def test_scalar_topographic_action_source_uses_existing_decomposition():
    payload = load_v56("action_source")
    assert payload["S_ST"] == "S_T_bulk + S_Phi_internal + S_threshold + S_boundary + S_collar"
    assert "U_boundary(T,Phi)" in payload["boundary_term"]
    assert "B_threshold" in payload["collar_term"]
    assert "PO-BH-53 symbolic scalar/topographic boundary variation" in payload["source_chain"]
    assert "Standard Model Higgs potential" not in json.dumps(payload)


def test_variable_dictionary_reconciles_required_symbols():
    payload = load_v56("variable_dictionary")
    rows = {row["symbol"]: row for row in payload["variables"]}
    for symbol in ("T(x)", "T_0", "Phi(y)", "Phi_0", "y_0", "sigma_profile", "sigma_scale", "rho_star", "k_loc", "lambda_T", "lambda_Phi", "alpha_scale", "beta_scale", "M_star", "ell_star"):
        assert symbol in rows
    assert rows["sigma_scale"]["relationship"] == "sets M_BH/M_* after unit anchor"
    assert rows["sigma_profile"]["relationship"] == "distinct from sigma_scale"
    assert rows["alpha_scale"]["definition"] == "negative reduced quadratic Hessian functional"
    assert rows["beta_scale"]["definition"] == "reduced quartic stabilizing functional"


def test_reduced_vacuum_generates_alpha_beta_from_action_functionals():
    payload = load_v56("reduced_vacuum_functional")
    assert payload["status"] == "REDUCED_VACUUM_FUNCTIONAL_DERIVED_CONDITIONALLY"
    assert "second_variation(S_ST)" in payload["alpha_scale"]
    assert "fourth_variation(S_ST)" in payload["beta_scale"]
    assert payload["derivation_source"] == "projection of S_ST onto the normalized scale mode, not a generic quartic ansatz"
    assert "free placeholder" not in payload["alpha_scale"]


def test_vacuum_branches_hessian_and_boundedness_are_consistent():
    payload = load_v56("vacuum_solution")
    assert payload["status"] == "NONZERO_VACUUM_BRANCH_DERIVED_CONDITIONALLY"
    assert "sigma_scale=0" in payload["truncated_branches"]
    assert "sigma_scale=+sqrt(alpha_scale/beta_scale)" in payload["truncated_branches"]
    assert payload["hessian"] == "V_eff''(sigma_scale,0)=2 alpha_scale at the nonzero branch; V_eff''(0)=-alpha_scale"
    assert payload["stable"] is True
    assert payload["boundedness"] == "requires beta_scale>0 for the quartic truncation"


def test_old_curvature_threshold_expansion_has_no_false_mass_term():
    payload = load_v56("curvature_threshold_audit")
    assert payload["expanded_quadratic_lagrangian"] == "L_quad=1/2 etadot^2 - 1/2 |grad eta|^2 - lambda/2 (laplacian eta)^2"
    assert payload["fluctuation_operator"] == "eta_tt - laplacian eta + lambda laplacian^2 eta = 0"
    assert payload["fourier_dispersion"] == "omega^2 = |k|^2 + lambda |k|^4"
    assert payload["mass_term_coefficient"] == 0.0
    assert payload["claimed_prior_mass_gap_survives"] is False
    assert stv.curvature_threshold_expansion(lambda_curv=0.75, mode_k=2.0)["deterministic_check"]["omega_squared"] == pytest.approx(16.0)


def test_unit_anchor_remains_open_while_scale_potential_source_is_conditional():
    payload = load_v56("unit_anchor")
    assert payload["absolute_scale_fixed"] is False
    assert payload["scale_potential_source_status"] == "SCALE_POTENTIAL_ACTION_SOURCE_DERIVED_CONDITIONALLY"
    assert payload["absolute_unit_anchor_status"] == "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR"
    assert payload["M_BH_result"] == "M_BH/M_star = sqrt(alpha_scale/beta_scale)"


def test_reduced_model_satisfies_stationary_and_truncated_field_equations():
    payload = load_v56("reduced_model")
    model = payload["reduced_model"]
    assert payload["stationary_solution_verified"] is True
    assert payload["truncated_field_equations_verified"] is True
    assert payload["hessian_matches_stability"] is True
    assert model["selected_branch"] == pytest.approx(0.5)
    assert model["stationary_residual"] == pytest.approx(0.0)
    assert model["hessian"] == pytest.approx(4.0)
    assert model["vacuum_energy"] == pytest.approx(-0.125)
    assert model["scale_ratio_M_BH_over_M_star"] == pytest.approx(0.5)
    assert model["physical_fit"] is False


def test_v5_5_artifacts_are_updated_to_v5_6_action_functionals():
    selected = load_v55("selected_mechanism")["selected_mechanism"]
    report = load_v55("construction_report")
    assert selected["dimensionless_order_parameter"] == "sigma_scale"
    assert selected["coefficient_source_status"] == "SCALE_POTENTIAL_ACTION_SOURCE_DERIVED_CONDITIONALLY_BY_V5_6"
    assert selected["v5_6_source"] == "artifacts/BHSM_scalar_topographic_vacuum_action_derivation_report_v5_6.json"
    assert report["v5_6_update"]["generic_quartic_ansatz_retired"] is True
    assert "OPEN_MISSING_SCALE_FUNCTIONAL_NUMERIC_INPUTS" in report["still_requiring_new_mathematics"]


def test_cli_status_json_and_markdown_are_available():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "scalar-topographic-vacuum-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_result"] == "SCALAR_TOPOGRAPHIC_VACUUM_ACTION_DERIVED_CONDITIONALLY"
    assert payload["unit_anchor"]["absolute_scale_fixed"] is False

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "scalar-topographic-vacuum-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.6 Scalar/Topographic Vacuum Action Derivation" in markdown.stdout


def test_public_ledgers_include_v5_6_claim_boundary():
    text = focused_text()
    assert "SCALAR_TOPOGRAPHIC_VACUUM_ACTION_DERIVED_CONDITIONALLY" in text
    assert "sigma_scale" in text
    assert "sigma_profile" in text
    assert "CURVATURE_THRESHOLD_MASS_GAP_INVALIDATED_FOR_THIS_ACTION" in text
    assert "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR" in text
    assert "python -m bhsm.interface scalar-topographic-vacuum-status --format markdown" in text


def test_forbidden_promotions_are_absent_from_public_v5_6_package():
    text = public_text()
    forbidden = (
        "Standard Model Higgs potential imported",
        "numeric eV/GeV scale is derived",
        "particle masses are derived",
        "M_star is derived",
        "alpha_i is derived",
        "g2_BH is derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "prior mass gap survives",
        "full BHSM completion is achieved",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    report = load_v56("construction_report")
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
