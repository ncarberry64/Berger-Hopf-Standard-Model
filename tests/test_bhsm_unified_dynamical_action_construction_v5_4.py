import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from bhsm.interface import unified_dynamical_action as uda


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_unified_dynamical_action_construction_v5_4.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_artifact(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / uda.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in uda.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def public_text() -> str:
    paths = [DOC, *(ARTIFACT_DIR / filename for filename in uda.ARTIFACT_FILES.values())]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_4_artifacts_exist_parse_and_preserve_no_fit_metadata():
    for key, filename in uda.ARTIFACT_FILES.items():
        payload = load_artifact(key)
        assert (ARTIFACT_DIR / filename).exists(), key
        assert payload["version"] == "v5.4"
        assert payload["sprint"] == "bhsm-unified-dynamical-action-construction-v5-4"
        assert payload["primary_result"] == "UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY"
        assert payload["empirical_inputs_used"] is False
        assert payload["rare_b_data_fitting_used"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["physics_model_logic_changed"] is False


def test_materialized_artifacts_match_deterministic_builders():
    built = uda.build_artifact_payloads(ROOT)
    for key, filename in uda.ARTIFACT_FILES.items():
        assert (ARTIFACT_DIR / filename).read_text(encoding="utf-8") == uda.deterministic_json(built[key])


def test_configuration_space_separates_dynamical_variables_from_fixed_data():
    payload = load_artifact("configuration_space")
    assert payload["status"] == "UNIFIED_BHSM_CONFIGURATION_SPACE_DEFINED"
    assert "dmu_Sigma,rho" in payload["metric_and_measure"]["measure"]
    assert set(payload["dynamical_variables"]) == {"rho", "A_i", "Psi", "Phi", "J_ch", "N"}
    assert {"h_rho", "P_i", "P_gen"}.issubset(payload["fixed_data"])
    field_rows = {row["symbol"]: row for row in payload["field_content"]}
    assert field_rows["A_i"]["space"] == "Omega^1(Sigma_rho, ad_i), i in {U1,SU2,SU3}"
    assert field_rows["P_i"]["dynamical"] is False


def test_all_action_terms_have_compatible_dimensions_and_symbolic_coefficients():
    payload = load_artifact("coefficient_dimension_table")
    assert payload["all_terms_dimensionless"] is True
    assert uda.validate_action_terms_dimensionless() is True
    assert all(row["dimensionless_action_term"] for row in payload["term_dimension_checks"])
    coeffs = {row["name"]: row for row in payload["coefficients"]}
    assert set(coeffs) == {"kappa_geom", "kappa_g_i", "zeta_psi", "kappa_phi", "g_ch", "g_neu", "kappa_scale"}
    assert all(row["provisional"] is True for row in coeffs.values())
    assert all(row["derivation_status"].startswith("OPEN_") for row in coeffs.values())


def test_action_is_real_or_hermitian_under_declared_conventions():
    payload = load_artifact("action_candidate")
    statuses = {row["name"]: row["hermitian_or_real_status"] for row in payload["terms"]}
    assert "real symmetric" in statuses["geometric_boundary"]
    assert "Hermitian" in statuses["gauge_kinetic"]
    assert "Hermitian" in statuses["fermion_kinetic"]
    assert "real scalar" in statuses["scalar_topographic"]
    assert "Hermitian" in statuses["charged_current"]
    assert "real neutral" in statuses["neutral_response"]
    assert payload["not_a_standard_model_lagrangian_import"] is True


def test_variations_reproduce_stored_operator_equations_and_boundary_conditions():
    payload = load_artifact("variational_equations")
    equations = {row["variable"]: row for row in payload["equations"]}
    assert payload["has_nontrivial_euler_lagrange_equation"] is True
    assert payload["boundary_terms_vanish_under_declared_conditions"] is True
    assert "(1/lambda_i) L_i(rho) A_i" in equations["A_i"]["equation"]
    assert "zeta_psi D_BH Psi" in equations["Psi"]["equation"]
    assert "K_neu N + g_neu R_neu" in equations["N"]["equation"]
    assert all(row["boundary_term"] for row in equations.values())
    assert all(row["boundary_condition"] for row in equations.values())


def test_quadratic_operators_have_domains_adjoints_and_no_invented_inverse():
    payload = load_artifact("quadratic_operators")
    operators = {row["sector"]: row for row in payload["operators"]}
    assert payload["no_invented_inverse"] is True
    assert payload["inverse_response_status"] == "CONDITIONAL_AFTER_DOMAIN_ZERO_MODE_AND_SCALE_GATES"
    assert "gauge-fixed/coexact" in operators["gauge"]["domain"]
    assert "exact gauge modes" in operators["gauge"]["kernel_or_zero_modes"]
    assert operators["gauge"]["response_status"] == "Green operator conditional"
    assert "zero modes" in operators["fermion"]["kernel_or_zero_modes"]


def test_interaction_source_map_traces_interactions_without_promoting_rare_b():
    payload = load_artifact("interaction_source_map")
    interactions = {row["interaction"]: row for row in payload["interactions"]}
    assert payload["rare_b_phenomenology_pursued"] is False
    assert payload["fcnc_status_preserved"] == "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED"
    assert interactions["charged-current transitions"]["status"] == "SUPPORTED_STRUCTURALLY_OPEN_NORMALIZATION"
    assert interactions["neutral-current response"]["status"] == "SUPPORTED_STRUCTURALLY_OPEN_NORMALIZATION"
    assert interactions["current-current composition"]["status"] == "NOT_CLOSED"


def test_dimensionful_scale_remains_explicit_and_open():
    payload = load_artifact("dimensionful_scale_analysis")
    assert payload["physical_scale"] == "Lambda_BH or equivalent conversion scale remains explicit"
    assert payload["universal_scale_parameter_required"] is True
    assert payload["scale_parameter"]["status"] == "OPEN_MISSING_PHYSICAL_SCALE_GENERATION"
    assert payload["scale_parameter"]["not_fit"] is True
    assert payload["does_not_derive_physical_masses_or_couplings"] is True


def test_reduced_model_is_deterministic_stable_and_satisfies_equations():
    payload = load_artifact("reduced_model")
    model = payload["reduced_model"]
    assert payload["status"] == "UNIFIED_ACTION_REDUCED_MODEL_DETERMINISTIC_STABLE"
    assert payload["solution_satisfies_equations"] is True
    assert model["deterministic"] is True
    assert model["physical_fit"] is False
    assert model["max_abs_residual"] <= 1.0e-12
    assert model["stable"] is True
    assert model["determinant"] > 0
    assert all(value > 0 for value in model["eigenvalues"])
    assert uda.validate_reduced_solution()


def test_construction_report_keeps_conditional_status_and_preserved_blockers():
    payload = load_artifact("construction_report")
    assert payload["status"] == "UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY"
    assert payload["dimension_checks_passed"] is True
    assert payload["variational_equations_derived"] is True
    assert payload["quadratic_operators_extracted"] is True
    assert payload["interaction_source_map_constructed"] is True
    assert "OPEN_MISSING_PHYSICAL_SCALE_GENERATION" in payload["still_requiring_new_mathematics"]
    assert "OPEN_MISSING_G2_BH_ACTION_SOURCE" in payload["preserved_blockers"]
    assert payload["recommended_next_construction_sprint"] == "BHSM physical-scale generation"


def test_cli_status_json_and_markdown_are_available():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "unified-dynamical-action-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_result"] == "UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY"
    assert payload["dimension_checks_passed"] is True
    assert payload["frozen_predictions_changed"] is False

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "unified-dynamical-action-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.4 Unified Dynamical Action Construction" in markdown.stdout


def test_public_ledgers_include_v5_4_claim_boundary():
    text = focused_text()
    assert "UNIFIED_BHSM_ACTION_CONSTRUCTED_CONDITIONALLY" in text
    assert "OPEN_MISSING_PHYSICAL_SCALE_GENERATION" in text
    assert "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT" in text
    assert "RARE_B_FCNC_GENERATION_MECHANISM_BLOCKED" in text
    assert "python -m bhsm.interface unified-dynamical-action-status --format markdown" in text


def test_forbidden_promotions_are_absent_from_public_v5_4_package():
    text = public_text()
    forbidden = (
        "alpha_i is derived",
        "g2_BH is derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "Wilson coefficients are derived",
        "q0^2 is predicted",
        "rare-B anomalies are explained",
        "full BHSM completion is achieved",
        "Standard Model Lagrangian imported as BHSM",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    report = load_artifact("construction_report")
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
