import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface import absolute_unit_anchor_generation as aua


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_absolute_unit_anchor_generation_v5_8.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"
ARTIFACT_INDEX = ROOT / "ARTIFACT_INDEX.md"

EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load_v58(key: str) -> dict:
    return json.loads((ARTIFACT_DIR / aua.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text() -> str:
    paths = [
        DOC,
        STATUS,
        CLAIMS,
        ARTIFACT_INDEX,
        *(ARTIFACT_DIR / filename for filename in aua.ARTIFACT_FILES.values()),
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_v5_8_artifacts_exist_parse_and_preserve_guards():
    for key, filename in aua.ARTIFACT_FILES.items():
        payload = load_v58(key)
        assert (ARTIFACT_DIR / filename).exists(), key
        assert payload["version"] == "v5.8"
        assert payload["sprint"] == "bhsm-absolute-unit-anchor-generation-v5-8"
        assert payload["primary_result"] == "BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED"
        assert payload["empirical_inputs_used"] is False
        assert payload["observed_mass_or_vev_used"] is False
        assert payload["cosmological_parameter_used"] is False
        assert payload["hubble_or_cmb_calibration_used"] is False
        assert payload["planck_length_inserted"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False
        assert payload["numerical_particle_masses_emitted"] is False


def test_materialized_v5_8_artifacts_match_builders():
    built = aua.build_artifact_payloads(ROOT)
    for key, filename in aua.ARTIFACT_FILES.items():
        assert (ARTIFACT_DIR / filename).read_text(encoding="utf-8") == aua.deterministic_json(built[key])


def test_primordial_state_is_defined_without_imported_cosmology():
    payload = load_v58("primordial_state")
    state = payload["primordial_state"]
    assert state["metric"] == "g(L)=L^2 g_hat with dimensionless Berger metric g_hat"
    assert state["scalar_topographic_state"]["sigma_scale"] == pytest.approx(0.5)
    assert state["scalar_topographic_state"]["M_BH_over_M_star"] == pytest.approx(0.5)
    assert state["scalar_topographic_state"]["R_BH_over_ell_star"] == pytest.approx(2.0)
    assert state["white_hole_like_interpretation"].endswith("not an additional equation that fixes L.")
    assert state["late_universe_doctrine"]["early_release_still_occurring"] is False


def test_serious_invariant_candidates_do_not_hide_absolute_length():
    candidates = {row["symbol"]: row for row in load_v58("primordial_state")["candidate_invariants"]}
    assert candidates["R_0=L R_hat"]["can_define_ell_star"] is False
    assert candidates["V_0=L^3 V_hat"]["can_define_ell_star"] is False
    assert candidates["A_0=L^2 A_hat"]["can_define_ell_star"] is False
    assert candidates["rho_star L"]["reason"] == "rho_star=1 is a coordinate convention, not a physical length"
    assert candidates["lambda_n=lambda_hat_n/L^2"]["can_define_ell_star"] is False
    assert candidates["n"]["dimension"] == "dimensionless"
    assert candidates["L_0"]["fixed_by_equation"] is False


def test_action_scaling_terms_are_recorded_and_do_not_select_L():
    terms = {row["term"]: row for row in load_v58("scale_modulus")["scaling_terms"]}
    assert terms["geometric curvature term"]["raw_L_power"] == 2
    assert terms["gauge Yang-Mills term"]["raw_L_power"] == 0
    assert terms["fermion kinetic term"]["raw_L_power"] == 0
    assert terms["scalar/topographic vacuum term"]["raw_L_power"] == 4
    assert terms["boundary term"]["status"] == "BOUNDARY_TENSION_OPEN"
    assert terms["spectral term"]["status"] == "SPECTRAL_ANCHOR_OPEN"
    assert all("derived" not in row["status"].lower() for row in terms.values())


def test_effective_scale_action_is_flat_and_stationarity_does_not_fix_unit():
    action = load_v58("scale_modulus")["effective_scale_action"]
    assert action["metric_decomposition"] == "g = L^2 g_hat"
    assert action["dS_eff_dL"] == pytest.approx(0.0)
    assert action["d2S_eff_dL2"] == pytest.approx(0.0)
    assert action["stationary_points"] == "all positive L are stationary in the normalized reduced model"
    assert action["selected_branch"] is None
    assert action["positive_finite_unique_solution"] is False
    assert action["dimensionful_inputs"] == []
    assert "unfixed" in action["why_no_anchor"] or "unproved" in action["why_no_anchor"]


def test_spectral_topology_and_regularity_do_not_fix_scale():
    assessment = load_v58("construction_report")["spectral_topological_assessment"]
    assert assessment["topology_fixes_scale"] is False
    assert assessment["spectrum_fixes_scale"] is False
    assert assessment["regularity_fixes_scale"] is False
    assert assessment["action_stationarity_fixes_scale"] is False
    assert "lambda_hat_n/L^2" in assessment["spectrum_reason"]


def test_unit_anchor_remains_relative_and_M_BH_requires_M_star():
    anchor = load_v58("construction_report")["unit_anchor"]
    assert anchor["ell_star"] is None
    assert anchor["M_star"] is None
    assert anchor["M_BH"] is None
    assert anchor["R_BH"] is None
    assert anchor["absolute_or_relative"] == "relative only"
    assert anchor["preserved_relative_ratios"] == {"M_BH_over_M_star": 0.5, "R_BH_over_ell_star": 2.0, "sigma_scale": 0.5}
    assert anchor["M_BH_equals_M_star_over_2_only_after_M_star_exists"] is True
    assert "conversion convention" in anchor["hbar_c_status"]


def test_redshift_transports_but_does_not_generate_and_relics_are_physical():
    mapping = load_v58("construction_report")["primordial_to_late_time_map"]
    assert mapping["redshift_generates_unit"] is False
    assert mapping["cmb_and_relic_matter_are_virtual"] is False
    assert "physical on-shell relic" in mapping["redshifted_relics"]
    assert "effective or virtual" in mapping["virtual_or_effective_memory"]
    assert mapping["cosmological_fit_attempted"] is False


def test_physical_operator_propagation_remains_blocked_pending_anchor():
    propagation = load_v58("unit_propagation")["propagation"]
    assert propagation["status"] == "UNIT_PROPAGATION_BLOCKED_PENDING_ABSOLUTE_ANCHOR"
    assert "only after M_BH exists" in propagation["fermion_operator"]
    assert "alpha_i remains action-gated" in propagation["gauge_operator"]
    assert propagation["particle_masses_derived_by_multiplication"] is False


def test_cli_status_json_and_markdown_are_available():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "absolute-unit-anchor-status", "--format", "json"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["primary_result"] == "BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED"
    assert payload["unit_anchor"]["ell_star"] is None

    markdown = subprocess.run(
        [sys.executable, "-m", "bhsm.interface", "absolute-unit-anchor-status", "--format", "markdown"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "BHSM v5.8 Absolute Unit-Anchor Generation" in markdown.stdout


def test_public_ledgers_include_v5_8_claim_boundary():
    text = focused_text()
    assert "BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED" in text
    assert "OPEN_MISSING_GLOBAL_SCALE_MODULUS_ACTION_SOURCE" in text
    assert "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR" in text
    assert "lambda_n=lambda_hat_n/L^2" in text
    assert "python -m bhsm.interface absolute-unit-anchor-status --format markdown" in text


def test_forbidden_unit_anchor_promotions_are_absent():
    text = focused_text()
    forbidden = (
        "ell_star is derived",
        "M_star is derived",
        "Planck length is inserted",
        "Hubble rate fixes",
        "CMB temperature fixes",
        "particle masses are derived",
        "gauge couplings are derived",
        "CKM values are derived",
        "rare-B observables are predicted",
        "CMB and relic matter are virtual",
        "full BHSM completion is achieved",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    report = load_v58("construction_report")
    assert report["frozen_predictions_changed"] is False
    assert report["official_prediction_logic_changed"] is False
    assert report["physics_model_logic_changed"] is False
    for relative, digest in EXPECTED_HASHES.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
