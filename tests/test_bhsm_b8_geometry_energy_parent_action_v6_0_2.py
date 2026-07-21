import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import b8_geometry_energy_parent_action as pa


ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=ROOT/"artifacts"
DOC=ROOT/"docs"/"bhsm_b8_geometry_energy_parent_action_v6_0_2.md"
EXPECTED_HASHES={
    "docs/frozen_predictions.md":"9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json":"f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py":"8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS/pa.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text():
    paths=[DOC,ROOT/"STATUS.md",ROOT/"CLAIMS.md",ROOT/"ARTIFACT_INDEX.md",ROOT/"CLI_REFERENCE.md"]
    paths += [ARTIFACTS/name for name in pa.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_artifact_package_is_complete_and_claim_guarded():
    assert len(pa.ARTIFACT_FILES)==16
    for key in pa.ARTIFACT_FILES:
        payload=load(key)
        assert payload["version"]=="v6.0.2",key
        assert payload["primary_result"]=="BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED"
        assert payload["physicality_result"]=="BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED"
        assert payload["preserved_results"]==["BHSM_S7_ARCHITECTURE_AMBIGUOUS","BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING"]
        assert payload["empirical_inputs_used"] is False
        assert payload["signature_emergence_claimed"] is False
        assert payload["absolute_unit_generated"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_round_trip_is_deterministic():
    built=pa.build_artifact_payloads(ROOT)
    for key,name in pa.ARTIFACT_FILES.items():
        assert (ARTIFACTS/name).read_text(encoding="utf-8")==pa.deterministic_json(built[key])


@pytest.mark.parametrize("dimension,maximum",[(2,1),(4,2),(7,3),(8,4),(9,4)])
def test_lovelock_maximum_order_matches_dimension(dimension,maximum):
    assert pa.lovelock_max_order(dimension)==maximum


def test_lovelock_order_classification_in_eight_dimensions():
    assert [pa.lovelock_classification(8,k) for k in range(6)]==[
        "DYNAMICAL_OR_VOLUME","DYNAMICAL_OR_VOLUME","DYNAMICAL_OR_VOLUME","DYNAMICAL_OR_VOLUME","EULER_TOPOLOGICAL_IN_BULK","IDENTICALLY_ZERO"
    ]


def test_lovelock_invalid_inputs_are_rejected():
    with pytest.raises(ValueError): pa.lovelock_max_order(0)
    with pytest.raises(ValueError): pa.lovelock_classification(8,-1)


@pytest.mark.parametrize("k,power,weight",[(0,-8,8),(1,-6,6),(2,-4,4),(3,-2,2),(4,0,0)])
def test_action_dimensions_and_scale_weights_close(k,power,weight):
    assert pa.coefficient_length_power(8,k)==power
    assert pa.scale_weight(8,k)==weight
    assert pa.action_dimension_closes(8,k,power)


def test_constant_curvature_lovelock_density_matches_known_low_orders():
    q=0.2
    assert pa.constant_curvature_lovelock_density(8,0,q)==1
    assert pa.constant_curvature_lovelock_density(8,1,q)==pytest.approx(8*7*q)
    assert pa.constant_curvature_lovelock_density(8,2,q)==pytest.approx(8*7*6*5*q*q)
    with pytest.raises(ValueError): pa.constant_curvature_lovelock_density(8,5,q)


def test_parent_action_matrix_is_finite_and_p1_is_minimal():
    payload=load("parent_matrix")
    rows={row["id"]:row for row in payload["families"]}
    assert set(rows)=={"P0","P1","P2","P3","P4","PX"}
    assert rows["P1"]["differential_order"]==2
    assert rows["P4"]["status"]=="TOPOLOGICAL_NOT_GEOMETRIC_DYNAMICS"
    assert rows["PX"]["status"].startswith("REJECTED_FROM_MINIMAL_SET")
    assert payload["minimal_retained_family"].startswith("P1")
    assert payload["selected_physical_family"] is None


def test_every_p1_parent_term_exposes_domain_measure_dimension_variation_and_source():
    rows=load("parent_matrix")["P1_term_ledger"]
    assert len(rows)==8
    for row in rows:
        assert row["term"] and row["formula"] and row["domain"]
        assert "measure" in row and "signature" in row
        assert "coefficient_dimension" in row and row["fields"]
        assert row["variation"] and "boundary_term" in row and row["source_status"]
    by_name={row["term"]:row for row in rows}
    assert by_name["S_boundary,completion"]["source_status"].endswith("NOT_PHYSICAL_TENSION")
    assert by_name["S_matter,candidate"]["source_status"]=="MISSING_NOT_FILLED_BY_V5_DOMAIN_REASSIGNMENT"


def test_every_retained_geometry_term_is_a_scalar_density_with_closed_dimensions():
    rows=load("geometry_minimality")["terms"]
    assert [row["coefficient"] for row in rows]==["kappa_0","kappa_1","kappa_2","kappa_3","kappa_4"]
    for k,row in enumerate(rows):
        expected=f"[A]L^{2*k-8}" if 2*k-8!=0 else "[A]"
        assert row["dimension"]==expected
        assert pa.action_dimension_closes(8,k,2*k-8)


def test_generic_higher_derivative_terms_are_not_retained_without_risk_classification():
    payload=load("geometry_minimality")
    assert payload["assumptions"][-1]=="no more than second-order metric equations"
    assert "ghostlike" in payload["lovelock_mode_warning"]
    hidden=load("hidden_minimality")
    assert "independent generic R2,Ric2,Riem2 coefficients" in hidden["removed"]


def test_euler8_is_topological_not_dynamical_and_not_quantized():
    payload=load("lovelock")
    row={row["order"]:row for row in payload["rows"]}[4]
    assert row["classification"]=="EULER_TOPOLOGICAL_IN_BULK"
    assert row["bulk_equations"].startswith("zero")
    assert payload["Euler_bulk_variation"]==0
    assert payload["coefficient_quantized"] is False
    assert payload["nested_Hopf_selects_combination"] is False


def test_boundary_completion_coefficients_are_locked_to_bulk_coefficients():
    rows=load("boundary")["rows"]
    assert rows[0]["coefficient_relation"]=="fixed by kappa_1"
    assert all("completion" in row["classification"] or "topological" in row["classification"] for row in rows)
    assert load("boundary")["surface_tension"] is None
    assert load("boundary")["free_K_K2_terms"].startswith("not added")


def test_bulk_variation_and_bianchi_conservation_are_explicit():
    payload=load("bulk_equations")
    assert payload["geometry_equation"].startswith("sum_k kappa_k H_AB^(k)=T_AB")
    assert payload["stress_definition"].startswith("T_AB=-2/sqrt|G|")
    assert payload["bianchi"]=="nabla^A H_AB^(k)=0 identically for every Lovelock order"
    assert payload["conservation"].startswith("nabla^A T_AB=0 follows on shell")
    assert payload["not_called_Einstein_equation"].startswith("only the P1")


def test_physicality_potential_and_threshold_follow_from_sigma_hessian():
    A=3.0; G=5.0
    assert pa.sigma_potential(0.0,A,G)==0
    branches=pa.sigma_stationary_branches(A,G)
    assert branches["zero_hessian"]==A
    assert branches["zero_stability"]=="STABLE"
    assert branches["nonzero_branches"]==[]
    threshold=pa.sigma_stationary_branches(0.0,G)
    assert threshold["zero_stability"]=="THRESHOLD"


def test_formed_quartic_branch_and_hessian_are_correct():
    branches=pa.sigma_stationary_branches(-2.0,8.0)
    assert branches["zero_stability"]=="UNSTABLE"
    assert branches["nonzero_branches"]==pytest.approx([-0.5,0.5])
    assert branches["nonzero_hessian"]==pytest.approx(4.0)
    with pytest.raises(ValueError): pa.sigma_stationary_branches(-1,0)


def test_v57_coefficients_are_target_reduction_not_parent_inputs():
    payload=load("physicality_action")
    assert payload["A_ST_minus_2_imported"] is False
    assert payload["G_ST_8_imported"] is False
    assert "only after a normalized mode projection" in payload["v5_target_reduction"]
    assert payload["negative_quadratic_source"] is None


def test_confinement_candidates_are_covariant_audited_but_unselected():
    payload=load("confinement")
    assert len(payload["candidates"])==8
    assert payload["selected_C_EG"] is None
    assert all(row["domain"] and row["covariance"] and row["dimension"] and row["obstruction"] for row in payload["candidates"])
    assert payload["analogy_prescription_used"] is False


def test_energy_envelopment_requires_stress_interface_and_stability():
    text=load("confinement")["minimum_mathematical_meaning_of_envelopment"]
    for required in ("sourced","conserved","interface","junction","stable"):
        assert required in text


def test_signature_and_time_are_explicit_and_not_selected():
    payload=load("signature")
    rows={row["branch"]:row for row in payload["branches"]}
    assert rows["A"]["time"] is None
    assert rows["A"]["equation_character"].startswith("elliptic")
    assert rows["B_s/B_t"]["equation_character"].startswith("hyperbolic")
    assert rows["D"]["accepted_by_action"] is False
    assert all(row["selected"] is False for row in rows.values())
    assert payload["time_orientation_selected"] is False


def test_no_unspecified_wick_rotation_or_signature_change_is_used():
    payload=load("signature")
    assert payload["signature_change"]["considered"] is False
    assert payload["signature_change"]["degeneracy_surface"] is None
    assert payload["causal_evolution_derived"] is False


def test_collar_is_one_gaussian_rewrite_not_a_duplicate_action():
    payload=load("collar")
    assert payload["independent_collar_term"] is None
    assert payload["scale"]["ell_c"] is None
    assert payload["double_counting"]=={"bulk_rewrite_plus_duplicate_integral":False,"standalone_log_J":False,"v5_collar_promoted":False}
    assert payload["matching"].startswith("continuity/jump conditions follow from the single")


def test_nested_metric_uses_4_plus_2_plus_1_without_double_counting():
    payload=load("nested_hopf")
    assert "4+2+1" in payload["metric"]
    assert "avoid double-counting" in payload["metric"]
    assert payload["selected_fibration"] is None
    assert payload["complex_selected_for_U1"] is False
    assert payload["quaternionic_selected_for_SU2"] is False


def test_reduced_scale_weights_and_derivative_are_exact():
    L=1.7; coefficient=2.3
    for k in range(5):
        weight=pa.scale_weight(8,k)
        eps=1e-6
        numeric=(pa.reduced_scale_term(L+eps,coefficient,weight)-pa.reduced_scale_term(L-eps,coefficient,weight))/(2*eps)
        assert numeric==pytest.approx(pa.reduced_scale_first_derivative(L,coefficient,weight),rel=1e-8,abs=1e-8)
    with pytest.raises(ValueError): pa.reduced_scale_term(0,1,2)


def test_ratio_stabilization_is_not_absolute_scale_generation():
    payload=load("stationarity")
    assert payload["ratio_fixing"].startswith("possible")
    assert payload["absolute_scale"].startswith("requires competing weights")
    assert "unsourced primitives" in payload["absolute_scale"]
    assert payload["stationary_solution"] is None


def test_single_homogeneous_weight_leaves_no_isolated_scale_selection():
    payload=load("stationarity")
    assert payload["flat_direction"].startswith("if only one homogeneous weight")
    L=2.0
    assert pa.reduced_scale_first_derivative(L,3.0,0)==0.0


def test_coupled_hessian_is_defined_but_not_evaluated_or_called_physical():
    payload=load("hessian")
    assert payload["order"]==["ln L","r2","r1","sigma","ell_c/L"]
    assert payload["sigma_zero_entry"]=="H_sigma_sigma=A(C_EG)"
    assert payload["zero_modes"] is None
    assert payload["negative_modes"] is None
    assert payload["physical_branch"] is None
    assert payload["unprojected_physical_modes_checked"] is False


def test_three_thresholds_are_distinct_and_one_eigenvalue_not_reused():
    payload=load("thresholds")
    assert [row["name"] for row in payload["thresholds"]]==["physicality_formation","primordial_surface_release","black_hole_de_enveloping"]
    assert len({row["background"] for row in payload["thresholds"]})==3
    assert payload["one_eigenvalue_reused"] is False


def test_shared_core_remains_only_compatible_not_selected():
    payload=load("thresholds")["shared_core_compatibility"]
    assert payload["one_connected_bulk"]=="topologically permitted"
    assert payload["multiple_throat_embeddings"]=="permitted but not selected"
    assert payload["regular_matching"]=="not proved"
    assert load("thresholds")["singularity_or_information_claim"] is False


def test_lower_dimensional_v5_terms_are_not_relabelled_as_parent_terms():
    payload=load("reduction")
    rows={row["target"]:row for row in payload["rows"]}
    assert rows["v5 boundary action"]["classification"].startswith("NOT_RECOVERED")
    assert rows["v5 scalar/topographic"]["classification"].startswith("RECOVERED_ONLY_AS_TARGET")
    assert payload["historical_artifacts_altered"] is False
    assert payload["scalar_pushforward_localization_ready"] is False


def test_minimality_audit_exposes_every_adjustable_primitive():
    payload=load("hidden_minimality")
    assert payload["hidden_inputs_derived"] is False
    assert all("role" in row and "independently_adjustable" in row and "source" in row for row in payload["retained"])
    assert "C_EG choice" in payload["hidden_inputs"]
    assert "selecting the conserved confinement invariant" in payload["exact_missing_first_principle"]


def test_v60_and_v601_artifacts_remain_byte_unchanged():
    paths=list(ARTIFACTS.glob("BHSM_s7_*_v6_0.json"))+list(ARTIFACTS.glob("*v6_0_1.json"))
    before={path:hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    pa.build_artifact_payloads(ROOT)
    after={path:hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    assert before==after


def test_report_stops_before_scalar_localization_and_routes_narrowly():
    report=load("report")
    assert report["status"]=="BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED"
    assert report["selected_domain"] is None
    assert report["selected_action"] is None
    assert report["selected_C_EG"] is None
    assert report["full_closure_sequence"]=="paused before scalar localization"
    assert report["recommended_next_branch"]=="bhsm-energy-geometry-confinement-invariant-v6-0-3"


def test_cli_json_and_markdown():
    env={**os.environ,"PYTHONPATH":str(ROOT/"src")}
    command=[sys.executable,"-m","bhsm.interface","b8-parent-action-status"]
    result=subprocess.run(command+["--format","json"],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    assert json.loads(result.stdout)["primary_result"]=="BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED"
    markdown=subprocess.run(command+["--format","markdown"],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    assert "BHSM v6.0.2 B8 Geometry-Energy" in markdown.stdout


def test_public_ledgers_preserve_claim_boundary_and_command():
    text=focused_text()
    assert "BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED" in text
    assert "BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED" in text
    assert "b8-parent-action-status" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    forbidden=["v6.0.2 derives physical spacetime","Lorentzian signature emerged","surface tension is derived","black holes share one core","full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    for relative,digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
