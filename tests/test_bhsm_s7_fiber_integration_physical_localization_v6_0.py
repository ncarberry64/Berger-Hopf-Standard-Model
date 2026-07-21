import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import s7_fiber_integration_physical_localization as s7


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_s7_fiber_integration_physical_localization_v6_0.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / s7.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths += [ARTIFACTS / name for name in s7.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_artifacts_parse_with_ambiguous_primary_result_and_guards():
    assert len(s7.ARTIFACT_FILES) == 8
    for key in s7.ARTIFACT_FILES:
        payload = load(key)
        assert payload["version"] == "v6.0", key
        assert payload["primary_result"] == "BHSM_S7_ARCHITECTURE_AMBIGUOUS"
        assert payload["empirical_inputs_used"] is False
        assert payload["probability_measure_substituted_for_action_measure"] is False
        assert payload["absolute_unit_claimed"] is False
        assert payload["full_bhsm_completion_claimed"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_round_trip_is_deterministic():
    built = s7.build_artifact_payloads(ROOT)
    for key, name in s7.ARTIFACT_FILES.items():
        assert (ARTIFACTS / name).read_text(encoding="utf-8") == s7.deterministic_json(built[key])


@pytest.mark.parametrize("dims", [(7, 4, 3), (7, 6, 1), (6, 4, 2)])
def test_all_fibration_dimensions_close(dims):
    assert s7.validate_fibration_dimensions(*dims)


def test_dimension_validation_rejects_negative_and_mismatch():
    assert not s7.validate_fibration_dimensions(7, 5, 1)
    with pytest.raises(ValueError):
        s7.validate_fibration_dimensions(7, -1, 8)


def test_fibration_types_are_not_conflated():
    rows = {row["name"]: row for row in load("fibration_ledger")["fibrations"]}
    assert rows["quaternionic_Hopf"]["structure"] == "principal Sp(1) bundle"
    assert rows["complex_Hopf"]["structure"] == "principal U(1) bundle"
    assert "not a principal S2" in rows["twistor"]["structure"]
    assert load("fibration_ledger")["topology_selects_physical_BHSM_domain"] is False


def test_nested_diagram_commutes_and_keeps_selection_open():
    payload = load("nested_diagram")
    assert payload["commutative_identity"] == "p_H=tau o p_C"
    assert payload["fiber_quotient"] == "Sp(1)/U(1)=S2"
    assert payload["unique_physical_selection"] is False
    assert payload["nested_result"] == "BHSM_S7_NESTED_HOPF_TWISTOR_DIAGRAM_DERIVED"


def test_pushforward_degree_and_rejection():
    assert s7.pushforward_degree(7, 3) == 4
    assert s7.pushforward_degree(7, 1) == 6
    assert s7.pushforward_degree(6, 2) == 4
    with pytest.raises(ValueError):
        s7.pushforward_degree(1, 2)


def test_actual_fiber_integral_is_not_probability_average():
    assert s7.actual_fiber_integral(3.0, 2.5) == pytest.approx(7.5)
    assert s7.actual_fiber_integral(3.0, 2.5) != pytest.approx(3.0)
    with pytest.raises(ValueError):
        s7.actual_fiber_integral(1.0, 0.0)


def test_orientation_reversal_changes_pushforward_sign():
    assert s7.orientation_reversal(2.75) == pytest.approx(-2.75)
    assert s7.orientation_reversal(s7.orientation_reversal(2.75)) == pytest.approx(2.75)


@pytest.mark.parametrize("k,r,sign", [(7, 3, 1), (6, 3, -1), (7, 1, 1), (5, 2, -1)])
def test_boundary_chain_rule_sign_matches_declared_convention(k, r, sign):
    assert s7.boundary_correction_sign(k, r) == sign


def test_standard_hopf_s3_volume_factorization_is_only_a_convention_check():
    circle = s7.round_s1_volume()
    base = s7.round_s2_area(0.5)
    assert circle * base == pytest.approx(s7.berger_s3_volume())
    payload = load("metric_measure")
    assert payload["physical_scale_selected"] is False


def test_berger_anisotropy_changes_s3_volume_linearly():
    assert s7.berger_s3_volume(2.0, 0.4) == pytest.approx(2 * math.pi**2 * 8 * 0.4)
    with pytest.raises(ValueError):
        s7.berger_s3_volume(1.0, 0.0)


def test_source_inventory_does_not_relabel_s3_as_s7():
    payload = load("source_inventory")
    assert payload["repository_has_explicit_CP3_construction"] is False
    assert payload["repository_has_explicit_S7_metric"] is False
    assert payload["repository_has_B8_bulk_action"] is False
    assert payload["legacy_architecture_inconsistent"] is False
    assert all(row["selects_S7"] is False for row in payload["sources"])


def test_metric_ledger_distinguishes_uniform_and_berger_vertical_deformations():
    metrics = load("metric_measure")["metric_families"]
    assert "uniform vertical rescaling" in metrics["canonical_variation"]
    assert "selection of U(1)" in metrics["Berger_inside_S3_fiber"]
    assert load("metric_measure")["existing_Berger_metric_is"].startswith("three-dimensional S3")


def test_pushforward_theorem_exposes_boundary_metric_and_bundle_valued_limits():
    payload = load("pushforward")
    assert payload["map"] == "pi_*:Omega^k(E)->Omega^(k-r)(B)"
    assert payload["closed_fiber_chain_rule"] == "d pi_* omega=pi_* d omega"
    assert "(-1)^(k-r)" in payload["fiber_boundary_chain_rule"]
    assert payload["normalization"] == "actual integral, not a probability average"
    assert "connection/parallel identification" in payload["bundle_valued_limit"]


def test_physical_domain_candidates_keep_time_signature_and_dimension_explicit():
    payload = load("physical_domain")
    assert payload["S4_is_observed_Lorentzian_spacetime"] is False
    assert payload["coordinate_dimension_implies_physical_dimension"] is False
    assert len(payload["candidates"]) == 5
    assert all("dimension" in row and "time" in row and "signature" in row for row in payload["candidates"])


def test_action_localization_does_not_emit_tension_or_absolute_scale():
    payload = load("action_localization")
    assert payload["v5_action_attachment"] is None
    assert payload["physical_boundary_tension_from_pushforward"] is None
    assert payload["absolute_scale_from_pushforward"] is None
    assert "actual physical fiber volume" in payload["fiber_constant_zero_mode"]


def test_report_routes_to_narrower_gate_instead_of_v61():
    report = load("report")
    assert report["status"] == "BHSM_S7_ARCHITECTURE_AMBIGUOUS"
    assert report["absolute_scale"] is None
    assert report["physical_action_domain"] is None
    assert report["recommended_next_construction_sprint"] == "bhsm-b8-s7-physical-domain-action-source-closure-v6-0-1"
    assert "OPEN_MISSING_ACTION_SELECTED_S7_TOTAL_SPACE" in report["remaining_open_blockers"]
    assert "FULL_BHSM_NOT_COMPLETE" in report["remaining_open_blockers"]


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "s7-fiber-integration-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_S7_ARCHITECTURE_AMBIGUOUS"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "BHSM v6.0 S7 Fiber Integration" in markdown.stdout


def test_public_ledgers_preserve_result_open_gates_and_forbidden_promotions():
    text = focused_text()
    assert "BHSM_S7_ARCHITECTURE_AMBIGUOUS" in text
    assert "OPEN_MISSING_B8_BULK_ACTION_AND_SIGNATURE" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    assert "s7-fiber-integration-status" in text
    forbidden = ["v6.0 derives an absolute unit", "S4 is observed Lorentzian spacetime", "unit fiber volume is physical", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
