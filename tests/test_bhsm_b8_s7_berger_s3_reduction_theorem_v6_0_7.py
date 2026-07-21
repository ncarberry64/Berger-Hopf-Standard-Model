import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from berger_spectrum import ledger_modes
from bhsm.interface import b8_s7_berger_s3_reduction_theorem as rt


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DOC = ROOT / "docs" / "bhsm_b8_s7_to_berger_s3_reduction_theorem_v6_0_7.md"
EXPECTED_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py": "8fc5a59ac4fcaFE4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b".lower(),
}


def load(key):
    return json.loads((ARTIFACTS / rt.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def public_text():
    paths = [DOC, ROOT / "STATUS.md", ROOT / "CLAIMS.md", ROOT / "ARTIFACT_INDEX.md", ROOT / "CLI_REFERENCE.md"]
    paths.extend(ARTIFACTS / name for name in rt.ARTIFACT_FILES.values())
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_package_has_twenty_mission_essential_artifacts_and_guards():
    assert len(rt.ARTIFACT_FILES) == 20
    for key in rt.ARTIFACT_FILES:
        payload = load(key)
        assert payload["primary_result"] == "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_OBSTRUCTED", key
        assert payload["sp1_to_u1_result"] == "BHSM_SP1_TO_U1_REDUCTION_TOPOLOGICALLY_OBSTRUCTED", key
        assert payload["mode_globalization_result"] == "BHSM_BERGER_MODE_ASSOCIATED_BUNDLE_MAP_DERIVED", key
        assert payload["consistent_truncation_result"] == "BHSM_BERGER_CONSISTENT_TRUNCATION_FAILED", key
        assert payload["program_architecture_result"] == "BHSM_TWISTOR_MEDIATED_BERGER_ROUTE_SELECTED", key
        assert payload["required_formulation_result"] == "BHSM_BERGER_ASSOCIATED_BUNDLE_FORMULATION_REQUIRED", key
        assert payload["direct_route_result"] == "BHSM_DIRECT_FIXED_AXIS_REDUCTION_EXCLUDED", key
        assert payload["v6_0_6_firewall_preserved"] is True
        assert payload["measured_mass_coupling_or_scale_used"] is False
        assert payload["v5_values_used_as_parent_inputs"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_is_deterministic():
    built = rt.build_artifact_payloads(ROOT)
    for key, filename in rt.ARTIFACT_FILES.items():
        assert (ARTIFACTS / filename).read_text(encoding="utf-8") == rt.deterministic_json(built[key])


def test_nested_dimensions_are_four_plus_two_plus_one_without_double_counting():
    assert rt.nested_dimensions() == (4, 2, 1)
    assert sum(rt.nested_dimensions()) == 7
    payload = load("bundle")
    assert payload["vertical_double_counting"] is False
    assert "rank 3" in payload["distributions"]["V"]


def test_connection_components_obey_transition_law_and_eta3_is_not_silently_global():
    payload = load("bundle")
    assert "Ad(g^-1)" in payload["connection"]
    assert "g_ab^-1 A_a g_ab+g_ab^-1 d g_ab" in payload["components"]
    metric = load("metric")
    assert "rotates under general Sp(1) transition" in metric["local_gauge_dependence"]
    assert "not Ad(Sp(1))-invariant" in metric["principal_bundle_statement"]


def test_sp1_to_u1_reduction_is_obstructed_by_nonzero_c2_on_s4():
    assert rt.sp1_to_u1_reduction_possible(1, 0) is False
    assert rt.sp1_to_u1_reduction_possible(-1, 0) is False
    assert rt.sp1_to_u1_reduction_possible(0, 0) is True
    with pytest.raises(ValueError):
        rt.sp1_to_u1_reduction_possible(1, -1)
    with pytest.raises(ValueError):
        rt.sp1_to_u1_reduction_possible(1, 1)
    payload = load("u1")
    assert payload["instanton_number"] == 1
    assert payload["global_section_exists"] is False
    assert "c2(E)=0" in payload["contradiction"]
    assert payload["status"] == "BHSM_SP1_TO_U1_REDUCTION_TOPOLOGICALLY_OBSTRUCTED"


def test_twistor_quotient_is_associated_s2_bundle_not_reduction_section():
    payload = load("u1")
    assert "CP3=P/U(1)" in payload["twistor_relation"]
    assert "supplies no section" in payload["twistor_relation"]
    assert "not a reduction subbundle" in payload["fixed_subgroup_choice"]


def test_global_total_space_metric_is_not_confused_with_bundle_natural_metric():
    payload = load("metric")
    assert payload["status"] == "GLOBAL_TOTAL_SPACE_METRIC_WITH_EXTRA_U1_CHOICE_NOT_SP1_NATURAL"
    assert payload["dimensions"] == [4, 2, 1]
    assert "total space" in payload["global_total_space_statement"]
    assert "not Ad(Sp(1))-invariant" in payload["principal_bundle_statement"]
    assert payload["round_case"] == "L1=L2 restores Ad(Sp(1)) invariance"


def test_vertical_restriction_matches_repository_berger_coefficient_form_only():
    payload = load("fiber")
    assert payload["restriction"] == "g_F=L2^2(eta_1^2+eta_2^2)+L1^2 eta_3^2"
    assert payload["repository_map"] == {"r_base": "L2", "r_fiber": "L1", "status": "EXACT_COEFFICIENT_FORM_IN_STORED_SIGMA_CONVENTION"}
    assert "normalization" in payload["normalization_blocker"]


def test_berger_volume_ricci_scalar_and_round_limit_are_exact_in_declared_convention():
    assert rt.fiber_volume(1.0, 1.0) == pytest.approx(16 * math.pi**2)
    assert rt.berger_ricci_eigenvalues(1.0, 1.0) == pytest.approx((0.5, 0.5, 0.5))
    assert rt.berger_scalar_curvature(1.0, 1.0) == pytest.approx(1.5)
    radius = 3.0
    scale = radius / 2
    assert rt.berger_ricci_eigenvalues(scale, scale) == pytest.approx((2 / radius**2,) * 3)
    assert rt.berger_scalar_curvature(scale, scale) == pytest.approx(6 / radius**2)


@pytest.mark.parametrize("function,args", [
    (rt.fiber_volume, (0, 1)),
    (rt.berger_ricci_eigenvalues, (1, 0)),
    (rt.berger_scalar_curvature, (-1, 1)),
])
def test_degenerate_berger_scales_are_rejected(function, args):
    with pytest.raises(ValueError):
        function(*args)


def test_only_round_fiber_is_canonical_without_extra_structure():
    payload = load("global")
    assert payload["status"] == "ASSOCIATED_FAMILY_NOT_GLOBAL_FIXED_BERGER_AXIS"
    assert "Only the round" in payload["canonical_case"]
    assert payload["one_chart_sufficient"] is False
    assert "independent homogeneous effective model" in payload["existing_engine_role"]


def test_physical_normalized_restricted_and_pushforward_measures_are_distinct():
    payload = load("measure")
    assert payload["restriction_equals_pushforward"] is False
    assert payload["normalized_equals_physical"] is False
    assert "dmu_F/Vol(F)" in payload["normalized_fiber_measure"]
    assert "16 pi^2" in payload["fiber_physical_volume_repository_convention"]
    assert payload["repository_match"].startswith("blocked")


def test_hodge_star_scale_and_orientation_factors():
    unit = rt.hodge_scale(0, (), 2.0, 3.0, 5.0)
    assert unit == {"sign": 1, "scale": pytest.approx(2**4 * 3**2 * 5), "vertical_complement": [1, 2, 3]}
    eta1 = rt.hodge_scale(0, (1,), 2.0, 3.0, 5.0)
    assert eta1["sign"] == 1
    assert eta1["scale"] == pytest.approx(2**4 * 5)
    eta3 = rt.hodge_scale(0, (3,), 2.0, 3.0, 5.0)
    assert eta3["scale"] == pytest.approx(2**4 * 3**2 / 5)
    mixed = rt.hodge_scale(3, (1,), 2.0, 3.0, 5.0)
    assert mixed["sign"] == -1
    top = rt.hodge_scale(4, (1, 2, 3), 2.0, 3.0, 5.0)
    assert top["scale"] == pytest.approx(1 / (2**4 * 3**2 * 5))
    assert top["vertical_complement"] == []


def test_invalid_hodge_inputs_are_rejected():
    with pytest.raises(ValueError):
        rt.hodge_scale(5, (), 1, 1, 1)
    with pytest.raises(ValueError):
        rt.hodge_scale(0, (1, 1), 1, 1, 1)
    with pytest.raises(ValueError):
        rt.hodge_scale(0, (4,), 1, 1, 1)
    with pytest.raises(ValueError):
        rt.hodge_scale(0, (), 0, 1, 1)


def test_pointwise_hodge_recovery_does_not_claim_full_operator_reduction():
    hodge = load("hodge")
    assert hodge["status"] == "PRODUCT_COFRAME_HODGE_FORMULA_DERIVED_V5_NORMALIZATION_OPEN"
    assert "exterior derivatives still mix" in hodge["connection_caveat"]
    assert "physical normalization" in hodge["v5_vertical_recovery"]


def test_delta_s7_is_not_naively_split_without_connection_terms():
    payload = load("operators")
    assert payload["naive_delta_sum_valid"] is False
    assert "O'Neill/connection-curvature" in payload["scalar_laplacian"]
    assert payload["existing_berger_operator_status"].startswith("exact intrinsic fiber operator locally")


def test_nontrivial_fiber_coefficients_transform_as_associated_bundle_sections():
    transformed = rt.associated_transition((1 + 0j, 2 + 0j), ((0, 1), (-1, 0)))
    assert transformed == (2 + 0j, -1 + 0j)
    with pytest.raises(ValueError):
        rt.associated_transition((1, 2), ((1, 0, 0), (0, 1, 0)))
    payload = load("modes")
    assert payload["trivial_representation"].startswith("R=1")
    assert "section of E_R" in payload["nontrivial_representation"]
    assert payload["nontrivial_fiber_mode_automatically_scalar"] is False


def test_consistent_truncation_checks_every_discarded_source_and_fails_exact_engine():
    payload = load("truncation")
    assert payload["status"] == "BHSM_BERGER_CONSISTENT_TRUNCATION_FAILED"
    assert payload["exact_scalar_only_truncation"] is False
    assert payload["nonlinear_closure"] is False
    assert payload["gauge_covariance"] is False
    assert len(payload["discarded_mode_sources"]) == 5
    assert [row["id"] for row in payload["kill_tests"]] == list(range(1, 13))
    assert payload["kill_tests"][-1]["result"] == "PASS_FIREWALL"


def test_low_level_branching_checks_dimensions_and_does_not_fabricate_general_map():
    rows = rt.low_level_branching()
    assert [(row["ell"], row["so8_dimension"], row["dimension_sum"]) for row in rows] == [(0, 1, 1), (1, 8, 8), (2, 35, 35)]
    payload = load("branching")
    assert payload["status"] == "LOW_LEVEL_BRANCHING_DERIVED_GENERAL_LEDGER_MAP_OPEN"
    assert payload["general_branching_formula"] is None
    assert payload["normalized_intertwiner"] is None
    assert payload["eigenvalue_coincidence_sufficient"] is False


def test_existing_mode_ledgers_are_frozen_and_not_parent_promoted():
    ledgers = ledger_modes()
    assert {(mode.k, mode.j) for mode in ledgers["charged_leptons"].values()} == {(0, 0), (5, 2), (9, 3)}
    assert {(mode.k, mode.j) for mode in ledgers["up_quarks"].values()} == {(0, 0), (6, 0), (10, 1)}
    assert {(mode.k, mode.j) for mode in ledgers["down_quarks"].values()} == {(0, 0), (6, 3), (8, 2)}
    payload = load("ledgers")
    assert payload["ledger_values_changed"] is False
    assert payload["operator_map_proved"] is False
    assert payload["representation_map_proved"] is False
    assert payload["particle_interpretation_promoted"] is False


def test_scalar_action_reduction_does_not_reverse_engineer_v5_vacuum():
    payload = load("scalar")
    assert payload["status"] == "SCALAR_ASSOCIATED_BUNDLE_REDUCTION_FORM_DERIVED_V5_COEFFICIENT_RECOVERY_BLOCKED"
    assert payload["v5_recovery"] == "STRUCTURALLY_COMPATIBLE_BUT_BLOCKED"
    assert payload["A_ST_minus_2_derived"] is False
    assert payload["G_ST_8_derived"] is False
    assert payload["sigma_half_derived"] is False


def test_gauge_readiness_is_not_gauge_coupling_or_alpha_derivation():
    payload = load("gauge")
    assert payload["status"] == "NESTED_CONNECTION_GAUGE_ARCHITECTURE_IDENTIFIED_NORMALIZATION_BLOCKED"
    assert payload["gauge_coupling_derived"] is False
    assert payload["alpha_calculated"] is False
    assert payload["geometric_aperture_ready"] is False


def test_dirac_readiness_is_not_fermion_spectrum_mass_or_generation_derivation():
    payload = load("dirac")
    assert payload["spin_structures"] == {"S7": "spin, unique", "S4": "spin, unique", "S3": "spin, unique", "associated_bundles": "require chosen Sp(1)/U1 representation and twisting"}
    assert payload["fermion_spectrum_derived"] is False
    assert payload["fermion_masses_derived"] is False
    assert "structurally compatible" in payload["v5_dirac_pairing"]


def test_internal_fiber_boundary_and_spacetime_normals_are_not_conflated():
    payload = load("boundary")
    assert payload["status"] == "INTERNAL_FIBER_PHYSICAL_BOUNDARY_CONFLATION_REJECTED"
    assert "rank four" in payload["fiber_normal"]
    assert len(payload["objects_distinct"]) == 4
    assert payload["surface_action_recovered"] is False
    assert payload["physical_boundary_role"] == "OPEN"


def test_p1_p2_p3_structures_are_audited_without_selection_by_v5_matching():
    payload = load("lovelock")
    assert [row["family"] for row in payload["rows"]] == ["P1", "P2", "P3"]
    assert payload["parent_family_selected"] is None
    assert payload["selected_by_v5_matching"] is False
    assert payload["v5_action_exactly_recovered"] is False
    assert "not normalized averaging" in payload["reduction_measure"]


def test_every_v5_coefficient_stays_in_symbolic_parent_map():
    payload = load("coefficients")
    required = {"kappa_geom", "kappa_g_i=1/lambda_i", "zeta_psi", "kappa_phi", "A_ST", "G_ST", "g_ch", "g_neu", "kappa_scale"}
    assert {row["v5_coefficient"] for row in payload["rows"]} == required
    assert all(row["parent_formula"] and row["missing"] for row in payload["rows"])
    assert payload["coefficients_omitted"] is False
    assert payload["numerical_v5_values_on_parent_side"] is False
    assert payload["reverse_engineering_used"] is False


def test_ratio_architecture_is_not_absolute_scale_generation():
    payload = load("scale")
    assert "b=L1/L2" in payload["dimensionless"]
    assert "overall common scale L" in payload["not_fixed"]
    assert payload["common_rescaling"].startswith("(L4,L2,L1)->lambda")
    assert payload["unit_radius_physical"] is False
    assert payload["absolute_unit_generated"] is False


def test_v606_correspondence_firewall_remains_present_and_unchanged_in_role():
    payload = json.loads((ARTIFACTS / "BHSM_correspondence_novelty_firewall_report_v6_0_6.json").read_text(encoding="utf-8"))
    assert payload["primary_result"] == "BHSM_CORRESPONDENCE_NOVELTY_FIREWALL_DERIVED"
    assert payload["reduction_status"] == "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_BLOCKED"
    assert load("report")["v6_0_6_firewall_preserved"] is True


def test_report_scopes_obstruction_and_selects_twistor_associated_bundle_route():
    payload = load("report")
    assert payload["status"] == "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_OBSTRUCTED"
    assert "c2(E)=1" in payload["central_answer"]
    assert "direct global fixed-axis scalar reduction" in payload["central_answer"]
    assert "does not remove Berger geometry" in payload["central_answer"]
    assert payload["completion_gate_status"] == "V6_0_7_DIRECT_FIXED_AXIS_ROUTE_STOPS_ASSOCIATED_BUNDLE_ROUTE_CONTINUES"
    assert payload["recommended_next_branch"] == "bhsm-twistor-mediated-berger-associated-bundle-v6-0-8"


def test_fixed_axis_obstruction_is_not_generalized_to_nested_program_failure():
    payload = load("report")
    normalized_public = " ".join(public_text().split()).lower()
    assert payload["program_architecture_result"] == "BHSM_TWISTOR_MEDIATED_BERGER_ROUTE_SELECTED"
    assert payload["architecture_selected"][0] == "S1->S7->CP3 followed by S2->CP3->S4"
    assert "full nested reduction program failed" not in normalized_public
    assert "twistor-mediated program is not obstructed" in normalized_public


def test_cli_json_and_markdown():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    command = [sys.executable, "-m", "bhsm.interface", "b8-s7-berger-s3-reduction-status"]
    result = subprocess.run(command + ["--format", "json"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["primary_result"] == "BHSM_B8_S7_TO_BERGER_S3_REDUCTION_OBSTRUCTED"
    markdown = subprocess.run(command + ["--format", "markdown"], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
    assert "BHSM v6.0.7 B8/S7-to-Berger-S3" in markdown.stdout


def test_public_ledgers_preserve_claim_boundaries():
    text = public_text()
    for required in ["BHSM_B8_S7_TO_BERGER_S3_REDUCTION_OBSTRUCTED", "BHSM_SP1_TO_U1_REDUCTION_TOPOLOGICALLY_OBSTRUCTED", "BHSM_BERGER_MODE_ASSOCIATED_BUNDLE_MAP_DERIVED", "BHSM_TWISTOR_MEDIATED_BERGER_ROUTE_SELECTED", "BHSM_BERGER_ASSOCIATED_BUNDLE_FORMULATION_REQUIRED", "FULL_BHSM_NOT_COMPLETE", "b8-s7-berger-s3-reduction-status"]:
        assert required in text
    forbidden = ["Standard Model gauge fields are derived", "particle generations are derived", "absolute scale is generated", "full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_are_unchanged():
    for relative, digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
