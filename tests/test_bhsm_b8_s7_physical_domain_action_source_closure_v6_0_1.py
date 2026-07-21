import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import b8_s7_physical_domain_action_source_closure as b8


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_b8_s7_physical_domain_action_source_closure_v6_0_1.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS / b8.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths += [ARTIFACTS / name for name in b8.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_artifact_package_is_complete_parseable_and_claim_guarded():
    assert len(b8.ARTIFACT_FILES) == 14
    for key in b8.ARTIFACT_FILES:
        payload = load(key)
        assert payload["version"] == "v6.0.1", key
        assert payload["primary_result"] == "BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING"
        assert payload["preserved_v6_0_result"] == "BHSM_S7_ARCHITECTURE_AMBIGUOUS"
        assert payload["empirical_inputs_used"] is False
        assert payload["time_silently_introduced"] is False
        assert payload["absolute_unit_generated"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_round_trip_is_deterministic():
    built = b8.build_artifact_payloads(ROOT)
    for key, name in b8.ARTIFACT_FILES.items():
        assert (ARTIFACTS / name).read_text(encoding="utf-8") == b8.deterministic_json(built[key])


@pytest.mark.parametrize("dims", [(8, 7, 1), (7, 4, 3), (7, 6, 1), (6, 4, 2)])
def test_parent_boundary_and_nested_dimensions_close(dims):
    assert b8.validate_bundle_dimensions(*dims)


def test_dimension_validation_rejects_mismatch_and_negative_values():
    assert not b8.validate_bundle_dimensions(8, 4, 3)
    with pytest.raises(ValueError):
        b8.validate_bundle_dimensions(8, -1, 9)


def test_riemannian_boundary_signature_and_normal_agree():
    assert b8.induced_signature((0, 8), 1) == (0, 7)
    row = {item["branch"]: item for item in load("time_signature")["branches"]}["A"]
    assert row["boundary_signature"] == [0, 7]
    assert row["epsilon_n"] == 1
    assert row["time_location"] is None


def test_lorentzian_spacelike_and_timelike_boundary_signatures_differ():
    assert b8.induced_signature((1, 7), -1) == (0, 7)
    assert b8.induced_signature((1, 7), 1) == (1, 6)
    rows = {item["branch"]: item for item in load("time_signature")["branches"]}
    assert rows["B_s"]["S7_type"] == "spacelike"
    assert rows["B_t"]["S7_type"].startswith("timelike topology")


def test_signature_helper_rejects_impossible_normal():
    with pytest.raises(ValueError):
        b8.induced_signature((0, 8), -1)
    with pytest.raises(ValueError):
        b8.induced_signature((1, 0), 1)


def test_all_required_domain_candidates_remain_separate_and_unselected():
    payload = load("domain_matrix")
    ids = {row["id"] for row in payload["candidates"]}
    assert ids == {"A", "B_s", "B_t", "C", "D", "E"}
    assert payload["selected_branch"] is None
    assert payload["incompatible_notation_combined"] is False


def test_time_is_absent_external_continued_or_factorized_but_never_silent():
    rows = {row["id"]: row for row in load("domain_matrix")["candidates"]}
    assert rows["A"]["time"] is None
    assert rows["C"]["time"] == "introduced only by a specified continuation"
    assert rows["D"]["time"] == "external Hamiltonian coordinate"
    assert rows["E"]["time"] == "one coordinate of M3,1"
    assert load("time_signature")["stored_action_time"] is None


def test_parent_action_source_trace_has_no_b8_or_selected_s7_action():
    payload = load("parent_action")
    assert payload["B8_action_exists"] is False
    assert payload["S7_action_selected"] is False
    assert payload["term_migration_used"] is False
    assert all(row["source"] for row in payload["terms"])
    assert all(row["domain"] and row["measure"] for row in payload["terms"])
    assert payload["attempted_parent_action"]["S_B8_geometry"] is None


def test_energy_geometry_envelopment_is_a_conditional_test_not_a_claim():
    candidate = load("parent_action")["relational_physicality_candidate"]
    assert candidate["status"] == "CONDITIONAL_PRINCIPLE_NOT_DERIVED_FROM_STORED_BHSM_ACTION"
    assert len(candidate["required_equations"]) == 4
    assert "topology" in candidate["not_equivalent_to"]
    gate = load("physical_boundary")["relational_physicality_gate"]
    assert gate["current_result"].startswith("not evaluable")


def test_b8_boundary_geometry_uses_seven_dimensional_shape_operator():
    payload = load("boundary_embedding")
    assert payload["dimension_check"] == {"dim_B8": 8, "dim_boundary": 7, "S_matrix_shape": "7x7"}
    assert payload["definitions"]["induced_metric"] == "h=i^*g_B8"
    assert payload["embedding_selected"] is False
    assert "v5 evaluated 3x3" in payload["v5_formula_reuse"]


def test_round_s7_volume_and_curvature_are_declared_without_physical_selection():
    assert b8.round_s7_volume(2.0) == pytest.approx(math.pi**4 * 2.0**7 / 3.0)
    round_row = {row["name"]: row for row in load("metric")["metrics"]}["round_S7"]
    assert round_row["scalar_curvature"] == "42/L^2"
    assert round_row["isometry"] == "SO(8)"
    assert round_row["action_selected"] is False


def test_metric_ansatz_isometries_and_nested_scale_independence_are_explicit():
    payload = load("metric")
    rows = {row["name"]: row for row in payload["metrics"]}
    assert "Sp(2)xSp(1)" in rows["quaternionic_canonical_variation"]["isometry"]
    assert "U(4)" in rows["complex_U1_variation"]["isometry"]
    assert "Sp(2)xU(1)" in rows["nested_independent_scales"]["isometry"]
    assert payload["single_Berger_parameter_controls_all_fibers"] is False
    assert payload["selected_metric"] is None


def test_all_s7_volume_families_reduce_to_round_at_equal_scale():
    L = 1.7
    expected = b8.round_s7_volume(L)
    assert b8.quaternionic_s7_volume(L, L) == pytest.approx(expected)
    assert b8.complex_s7_volume(L, L) == pytest.approx(expected)
    assert b8.nested_s7_volume(L, L, L) == pytest.approx(expected)


def test_volume_scale_powers_follow_dimensions():
    scale = 2.3
    assert b8.quaternionic_s7_volume(2 * scale, 3 * scale) / b8.quaternionic_s7_volume(2, 3) == pytest.approx(scale**7)
    assert b8.complex_s7_volume(2 * scale, 3 * scale) / b8.complex_s7_volume(2, 3) == pytest.approx(scale**7)
    assert b8.nested_s7_volume(2 * scale, 3 * scale, 4 * scale) / b8.nested_s7_volume(2, 3, 4) == pytest.approx(scale**7)


def test_metric_stationarity_is_unavailable_not_falsely_flat():
    payload = load("stationarity")
    assert payload["reduced_parent_action"] is None
    assert payload["first_variations"] is None
    assert payload["reduced_hessian"] is None
    assert payload["stationary_branch"] is None
    assert payload["flat_directions"].startswith("not classifiable")
    assert "not scale generation" in payload["scale_covariance"]


def test_standard_measure_factorizations_and_dimensions_close():
    payload = load("measure")
    rows = {row["space"]: row for row in payload["rows"]}
    assert rows["S7"]["dimension"] == 7 and rows["S7"]["physical_dimension"] == "L^7"
    assert rows["S3"]["dimension"] == 3 and rows["S3"]["physical_dimension"] == "L^3"
    assert rows["S1"]["dimension"] == 1 and rows["S1"]["physical_dimension"] == "L"
    assert payload["physical_measure"] is None
    assert payload["candidate_measure_types"]["normalized_Haar_probability"] == "not selected by action"


def test_pushforward_degrees_preserve_v60_topology():
    assert b8.pushforward_degree(7, 3) == 4
    assert b8.pushforward_degree(7, 1) == 6
    assert b8.pushforward_degree(6, 2) == 4
    with pytest.raises(ValueError):
        b8.pushforward_degree(1, 2)


def test_bundle_valued_pushforward_requires_parallel_identification():
    assert b8.bundle_pushforward_allowed("scalar")
    assert b8.bundle_pushforward_allowed("differential_form")
    assert not b8.bundle_pushforward_allowed("gauge_connection")
    assert not b8.bundle_pushforward_allowed("spinor")
    assert not b8.bundle_pushforward_allowed("stress_tensor")
    assert b8.bundle_pushforward_allowed("spinor", parallel_identification=True)
    with pytest.raises(ValueError):
        b8.bundle_pushforward_allowed("unknown")


def test_bundle_pushforward_ledger_does_not_average_affine_connections():
    rows = {row["object"]: row for row in load("bundle_pushforward")["rows"]}
    assert rows["gauge connection"]["direct"] is False
    assert "affine space" in rows["gauge connection"]["output"]
    assert rows["spinors"]["direct"] is False
    assert load("bundle_pushforward")["parallel_identification"]["connection"] is None


def test_collar_matching_metric_and_jacobian_agree_in_principal_frame():
    curvatures = [0.2, -0.1, 0.3]
    u = 0.4
    factors = b8.collar_metric_factors(curvatures, u)
    assert math.sqrt(math.prod(factors)) == pytest.approx(b8.collar_jacobian(curvatures, u))


def test_orientation_reversal_preserves_unsigned_collar_geometry_when_both_signs_change():
    curvatures = [0.2, -0.1, 0.3]
    u = 0.4
    assert b8.collar_jacobian(curvatures, u) == pytest.approx(b8.collar_jacobian([-k for k in curvatures], -u))
    assert b8.collar_metric_factors(curvatures, u) == pytest.approx(b8.collar_metric_factors([-k for k in curvatures], -u))


def test_normalized_rho_requires_an_independent_physical_collar_scale():
    assert b8.physical_collar_distance(0.5, 3.0) == pytest.approx(1.5)
    with pytest.raises(ValueError):
        b8.physical_collar_distance(1.0, None)
    collar = load("collar")
    assert collar["rho_star"]["stored"] == 1.0
    assert collar["rho_star"]["physical_thickness"] is None
    assert collar["ell_c"] is None


def test_riemannian_s4_is_not_observed_spacetime_and_no_3plus1_map_is_closed():
    payload = load("physical_boundary")
    row = payload["candidates"][0]
    assert row["map"] == "S7->S4 as spacetime"
    assert row["status"] == "REJECTED_AS_OBSERVED_SPACETIME_WITHOUT_LORENTZIAN_ACTION"
    assert payload["selected_map"] is None
    assert payload["lower_dimensional_action_produced"] is False


def test_berger_s3_is_reclassified_without_discarding_correct_results():
    payload = load("berger_s3")
    assert payload["selected_classification"] is None
    assert payload["metric_pullback_proved"] is False
    assert payload["action_reduction_proved"] is False
    assert payload["retained_results"].startswith("all correct S3")
    assert "not the physical S7 boundary" in payload["invalidated_interpretation"]


def test_scalar_localization_is_blocked_before_v61():
    payload = load("scalar_readiness")
    assert payload["readiness"] == "blocked because the parent action is absent"
    assert payload["unique"] is False
    assert payload["finite_conditional_branches"] is False
    assert payload["v6_1_may_proceed"] is False
    assert payload["inputs"]["parent_domain"] is None


def test_hidden_inputs_are_all_exposed_and_none_action_derived():
    payload = load("hidden_inputs")
    assert len(payload["inputs"]) >= 16
    assert all(row["action_derived"] is False and row["physical_value"] is None for row in payload["inputs"])
    assert payload["hidden_inputs_promoted"] is False


def test_v60_topology_artifacts_remain_byte_unchanged_by_materializer():
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in (ARTIFACTS.glob("BHSM_s7_*_v6_0.json"))}
    b8.build_artifact_payloads(ROOT)
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in before}
    assert before == after
    nested = json.loads((ARTIFACTS / "BHSM_s7_nested_hopf_twistor_diagram_v6_0.json").read_text(encoding="utf-8"))
    assert nested["commutative_identity"] == "p_H=tau o p_C"


def test_report_stops_at_parent_action_gate_and_routes_next_branch():
    report = load("report")
    assert report["status"] == "BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING"
    assert report["selected_branch"] is None
    assert report["scalar_localization_readiness"] == "BLOCKED_PARENT_ACTION_ABSENT"
    assert report["completion_gate_status"] == "V6_0_1_STOP_PARENT_ACTION_SOURCE_MISSING"
    assert report["recommended_next_branch"] == "bhsm-b8-geometric-action-construction-v6-0-2"
    assert "OPEN_MISSING_ENERGY_GEOMETRY_ENVELOPMENT_ACTION" in report["still_requiring_new_mathematics"]


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "b8-s7-physical-domain-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "BHSM v6.0.1 B8/S7" in markdown.stdout


def test_public_ledgers_preserve_claim_boundary_and_command():
    text = focused_text()
    assert "BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING" in text
    assert "OPEN_MISSING_ENERGY_GEOMETRY_ENVELOPMENT_ACTION" in text
    assert "b8-s7-physical-domain-status" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    forbidden = ["v6.0.1 derives an absolute unit", "Riemannian S4 is observed spacetime", "rho_star=1 is physical thickness", "energy enclosure is a derived BHSM equation", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
