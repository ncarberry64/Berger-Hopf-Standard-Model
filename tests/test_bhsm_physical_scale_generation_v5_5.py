import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import physical_scale_generation as psg


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_physical_scale_generation_v5_5.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_artifact(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / psg.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in psg.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def public_text() -> str:
    paths = [DOC, *(ARTIFACT_DIR / filename for filename in psg.ARTIFACT_FILES.values())]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_5_artifacts_exist_parse_and_preserve_no_fit_metadata():
    for key, filename in psg.ARTIFACT_FILES.items():
        path = ARTIFACT_DIR / filename
        assert path.exists(), key
        payload = load_artifact(key)
        assert payload["version"] == "v5.5"
        assert payload["sprint"] == "bhsm-physical-scale-generation-v5-5"
        assert payload["primary_result"] == "BHSM_PHYSICAL_SCALE_GENERATED_CONDITIONALLY"
        assert payload["empirical_inputs_used"] is False
        assert payload["pdg_reference_values_used"] is False
        assert payload["w_calibration_used"] is False
        assert payload["charged_mass_fitting_used"] is False
        assert payload["ckm_fitting_used"] is False
        assert payload["neutrino_limits_used"] is False
        assert payload["legacy_threshold_tables_used"] is False
        assert payload["numerical_particle_masses_emitted"] is False


def test_materialized_artifacts_match_deterministic_builders():
    built = psg.build_artifact_payloads(ROOT)
    for key, filename in psg.ARTIFACT_FILES.items():
        assert (ARTIFACT_DIR / filename).read_text(encoding="utf-8") == psg.deterministic_json(built[key])


def test_scale_inventory_does_not_mislabel_dimensionless_quantities_as_physical_scales():
    payload = load_artifact("scale_inventory")
    assert payload["dimensionless_quantities_not_physical_scales"] is True
    rows = {row["symbol"]: row for row in payload["scale_objects"]}
    for symbol in ("q_B", "Vol_hat(Sigma_rho)", "lambda_n_hat", "omega_n_hat^2"):
        assert rows[symbol]["can_set_absolute_scale"] is False
    assert rows["sigma"]["can_set_absolute_scale"] is True
    assert rows["sigma"]["reason"].endswith("absolute M_* anchor remains open")


def test_free_radius_is_not_reported_as_dynamically_generated():
    payload = load_artifact("candidate_comparison")
    candidates = {row["name"]: row for row in payload["candidates"]}
    radius = candidates["geometric radius"]
    assert radius["status"] == "PARTIAL_REJECT_FREE_RADIUS"
    assert "free radius is not scale generation" in radius["verdict"]
    assert "ell_*" in radius["arbitrary_inputs"]
    assert payload["selected"] == "SCALAR_TOPOGRAPHIC_SCALE_VACUUM_WITH_UNRESOLVED_UNIT_ANCHOR"


def test_selected_scale_equation_follows_from_action_and_has_nonzero_solution():
    payload = load_artifact("scale_equation")
    assert payload["status"] == "PHYSICAL_SCALE_EQUATION_DERIVED_CONDITIONALLY"
    assert payload["follows_from_stored_action"] is True
    assert payload["not_defined_by_declaration"] is True
    assert payload["scale_equation"] == "dU_scale/dsigma = beta_scale sigma^3 - alpha_scale sigma = 0"
    assert payload["selected_nonzero_solution"] == "sqrt(alpha_scale/beta_scale)"
    assert "M_BH = M_* sqrt(alpha_scale/beta_scale)" in payload["absolute_scale_formula"]


def test_stability_handles_zero_nonzero_and_runaway_branches():
    payload = load_artifact("stability_analysis")
    assert payload["status"] == "NONZERO_SCALE_BRANCH_STABLE_CONDITIONALLY"
    assert payload["zero_branch"]["status_for_selected_conditions"] == "unstable when alpha_scale>0"
    assert payload["nonzero_branch"]["hessian"] == "2 alpha_scale"
    assert payload["nonzero_branch"]["stable_if"] == "alpha_scale>0 and beta_scale>0"
    assert payload["runaway_behavior"] == "avoided when beta_scale>0"
    assert payload["continuous_modulus"] is False


def test_units_are_consistent_and_constants_remain_unit_conventions():
    payload = load_artifact("dimension_unit_map")
    assert payload["status"] == "DIMENSION_AND_UNIT_MAP_CONDITIONAL"
    assert payload["geometric_length"] == "R_BH = ell_* / |sigma_0|"
    assert payload["inverse_length"] == "k_BH = |sigma_0| / ell_*"
    assert payload["unit_convention"] == "hbar=c=1 may be used as a unit convention, not a BHSM prediction"
    assert payload["absolute_or_relative"] == "relative internally; absolute only after unresolved M_* or ell_* is supplied by action"
    assert "mode number is not a mass scale" in payload["forbidden_relabeling"]


def test_scale_propagates_consistently_into_bhsm_operators_without_promotions():
    payload = load_artifact("operator_propagation")
    assert payload["scale_symbol"] == "M_BH = M_* sqrt(alpha_scale/beta_scale)"
    assert payload["fermion_operator"] == "D_phys = M_BH D_hat; mass terms require separate fermion mass-operator theorem"
    assert payload["gauge_operator"] == "L_i,phys = M_BH^2 L_i,hat; alpha_i remains action-gated"
    assert payload["hessian_propagator"] == "G_phys = M_BH^-2 H_hat^-1 after domain and zero-mode gates close"
    assert "gauge couplings" in payload["does_not_promote"]
    assert "rare-B Wilson coefficients" in payload["does_not_promote"]


def test_reduced_calculation_is_deterministic_and_stationary():
    payload = load_artifact("reduced_model")
    model = payload["reduced_model"]
    assert payload["status"] == "REDUCED_SCALE_SETTING_MODEL_DETERMINISTIC_STABLE"
    assert payload["solution_satisfies_stationary_equation"] is True
    assert payload["stability_matches_hessian"] is True
    assert payload["unresolved_constants_remain_symbolic"] is True
    assert model["selected_branch"] == pytest.approx(0.5)
    assert model["selected_gradient"] == pytest.approx(0.0)
    assert model["selected_hessian"] == pytest.approx(4.0)
    assert model["zero_branch_unstable"] is True
    assert model["runaway_avoided"] is True
    assert model["generated_scale_in_symbolic_units"] == pytest.approx(0.5)
    assert model["physical_fit"] is False


def test_report_classifies_result_as_conditional_and_preserves_open_blockers():
    payload = load_artifact("construction_report")
    assert payload["status"] == "BHSM_PHYSICAL_SCALE_GENERATED_CONDITIONALLY"
    assert payload["scale_solution"]["nonzero"] is True
    assert payload["scale_solution"]["stable"] is True
    assert payload["scale_solution"]["absolute_or_relative"] == "conditional absolute in terms of M_*; internally generated relative scale"
    assert "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR" in payload["still_requiring_new_mathematics"]
    assert "OPEN_MISSING_G2_BH_ACTION_SOURCE" in payload["still_requiring_new_mathematics"]
    assert payload["recommended_next_construction_sprint"] == "BHSM scalar/topographic vacuum derivation"


def test_cli_status_json_and_markdown_are_available():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "physical-scale-generation-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_result"] == "BHSM_PHYSICAL_SCALE_GENERATED_CONDITIONALLY"
    assert payload["scale_solution"]["nonzero"] is True
    assert payload["frozen_predictions_changed"] is False

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "physical-scale-generation-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.5 Physical-Scale Generation" in markdown.stdout


def test_public_ledgers_include_v5_5_claim_boundary_and_open_gates():
    text = focused_text()
    assert "BHSM_PHYSICAL_SCALE_GENERATED_CONDITIONALLY" in text
    assert "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR" in text
    assert "OPEN_MISSING_SCALE_POTENTIAL_ACTION_SOURCE" in text
    assert "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT" in text
    assert "python -m bhsm.interface physical-scale-generation-status --format markdown" in text


def test_forbidden_promotions_are_absent_from_public_v5_5_package():
    text = public_text()
    forbidden = (
        "numeric eV/GeV scale is derived",
        "particle masses are derived",
        "alpha_i is derived",
        "g2_BH is derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "Wilson coefficients are derived",
        "rare-B anomalies are explained",
        "full BHSM completion is achieved",
        "W calibration fixes the scale",
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
