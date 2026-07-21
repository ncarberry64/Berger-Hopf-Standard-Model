import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface import primordial_boundary_tension_action_source_closure as bt


ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=ROOT/"artifacts"
DOC=ROOT/"docs"/"bhsm_primordial_boundary_tension_action_source_closure_v5_12.md"
EXPECTED_HASHES={
    "docs/frozen_predictions.md":"9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json":"f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    "src/bhsm_model.py":"8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
}


def load(key):
    return json.loads((ARTIFACTS/bt.ARTIFACT_FILES[key]).read_text(encoding="utf-8"))


def focused_text():
    paths=[DOC,ROOT/"STATUS.md",ROOT/"CLAIMS.md",ROOT/"ARTIFACT_INDEX.md",ROOT/"CLI_REFERENCE.md"]
    paths += [ARTIFACTS/name for name in bt.ARTIFACT_FILES.values()]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_artifacts_parse_with_source_not_closed_and_all_guards():
    assert len(bt.ARTIFACT_FILES)==14
    for key,name in bt.ARTIFACT_FILES.items():
        payload=load(key)
        assert payload["version"]=="v5.12",key
        assert payload["primary_result"]=="BHSM_PRIMORDIAL_BOUNDARY_SOURCE_NOT_CLOSED"
        assert payload["empirical_inputs_used"] is False
        assert payload["minus_one_eighth_promoted_to_physical_tension"] is False
        assert payload["absolute_unit_claimed"] is False
        assert payload["frozen_predictions_changed"] is False
        assert payload["official_prediction_logic_changed"] is False


def test_materialization_round_trip_is_deterministic():
    built=bt.build_artifact_payloads(ROOT)
    for key,name in bt.ARTIFACT_FILES.items():
        assert (ARTIFACTS/name).read_text(encoding="utf-8")==bt.deterministic_json(built[key])


def test_boundary_coordinate_dimension_is_explicit_without_inventing_physical_domain():
    dims=load("dimension_localization")["domain_dimension"]
    assert dims["v5_4_coordinate_boundary_dimension"]==3
    assert dims["d_collar_coordinate"]==4
    assert dims["d_Sigma_physical"]=="symbolic"
    assert dims["d_bulk"] is None
    assert dims["time_included"] is None
    assert dims["signature"] is None


def test_all_coefficient_dimensions_close_symbolically_and_at_candidate_d3():
    payload=load("dimension_localization")
    rules=payload["dimension_rules"]
    assert rules["U_boundary"]=="[A] L^(-d_Sigma)"
    assert rules["c_K"]=="[A] L^(1-d_Sigma)"
    assert rules["c_K2"]==rules["c_S"]=="[A] L^(2-d_Sigma)"
    assert rules["B_collar_physical_rho"]=="[A] L^(-(d_Sigma+1))"
    d3=payload["candidate_d_Sigma_3_specialization"]
    assert d3=={"U_boundary":"[A] L^-3","c_K":"[A] L^-2","c_K2":"[A] L^-1","c_S":"[A] L^-1","B_collar_if_physical_rho":"[A] L^-4"}


def test_natural_units_do_not_hide_ell_bh_source():
    payload=load("dimension_localization")["v5_4_dimension_table"]
    assert payload["physical_ell_BH_derived"] is False
    assert payload["natural_units_used_to_close_source"] is False


def test_minus_one_eighth_is_mixed_mode_value_not_local_density():
    loc=load("dimension_localization")["reduced_localization"]
    assert loc["V_red_at_half"]==pytest.approx(-0.125)
    assert loc["classification"]=="coordinate-normalized mode-space functional value"
    assert loc["map_to_U_boundary"] is None
    assert loc["map_to_B_collar"] is None
    assert loc["localization_closed"] is False
    assert loc["component_contributions"]["explicit_boundary"]==0.0
    assert loc["component_contributions"]["quartic_boundary_collar_kernel"]==8.0


def test_action_ledger_preserves_exact_formulas_and_coefficient_statuses():
    rows={row["term"]:row for row in load("action_source")["terms"]}
    assert rows["U_boundary"]["stored_formula"]=="U_boundary(T,Phi)"
    assert rows["K"]["coefficient_status"]=="SYMBOLIC_UNSOURCED"
    assert rows["K_squared"]["dimension"]=="[action] L^(2-d_Sigma)"
    assert "J(Y,rho)" in rows["collar"]["stored_formula"]
    assert rows["v5.4_geometry"]["localization"].startswith("already quadratic")


def test_metric_independent_density_reproduces_declared_pure_tension_stress():
    inverse=[[2.0,0.25],[0.25,1.0]]
    assert bt.pure_tension_stress(3.0,inverse)==[[6.0,0.75],[0.75,3.0]]
    stress=load("stress_tensor")
    row={item["source"]:item for item in stress["rows"]}["U_boundary"]
    assert "equals U h^AB" in row["tangential_stress"]
    with pytest.raises(ValueError):
        bt.pure_tension_stress(1.0,[[1.0,0.0],[1.0]])


def test_normal_displacement_identities_follow_one_declared_convention():
    payload=load("normal_variation")
    identities=payload["identities"]
    assert identities["delta_h_AB"]=="2 xi_perp K_AB"
    assert identities["delta_dmu_h"]=="K xi_perp dmu_h"
    assert "-Delta_Sigma" in identities["delta_K"]
    assert "delta log J" in identities["delta_collar_measure"]
    assert payload["actual_BHSM_orientation_fixed"] is False


def test_collar_log_jacobian_variation_matches_finite_difference():
    rho=0.2; shape=[0.3,-0.1,0.2]; variation=[0.4,0.2,-0.3]; eps=1e-6
    analytic=bt.collar_log_jacobian_variation(rho,shape,variation)
    def log_j(values):
        return sum(math.log(1.0+rho*value) for value in values)
    plus=[value+eps*delta for value,delta in zip(shape,variation)]
    minus=[value-eps*delta for value,delta in zip(shape,variation)]
    numeric=(log_j(plus)-log_j(minus))/(2*eps)
    assert analytic==pytest.approx(numeric,rel=1e-8)


def test_collar_jacobian_remains_active_while_cj_prevents_duplication():
    payload=load("collar_stress")
    assert payload["c_J_zero_meaning"]=="prevents a duplicate standalone log J term"
    assert payload["J_removed_from_measure"] is False
    assert payload["rho_star"]["value_in_v5_7"]==1.0
    assert payload["rho_star"]["unit_anchor"] is False


def test_v57_geometric_zeros_are_not_vanishing_theorems():
    payload=load("curvature_coefficients")
    for row in payload["rows"]:
        assert row["v5_7_zero"]=="fixed-geometry scalar-reduction choice, not a geometric theorem"
        assert row["derived_from_unified_action"] is False
    assert payload["GHY_audit"]["standard_gravitational_coefficient_imported"] is False
    assert payload["kappa_geom_relation"].startswith("no stored theorem")


def test_pressure_jump_keeps_outside_and_plasma_states_open():
    payload=load("pressure")
    assert payload["definition"].startswith("Delta p=p_inside-p_outside")
    assert payload["external_pressure_assumed_zero"] is False
    assert payload["post_release_plasma_pressure"]=="not derived"
    assert payload["hot_plasma_equation_of_state_used"] is False


def test_every_shape_equation_term_is_sourced_or_explicitly_open():
    payload=load("shape_equation")
    assert payload["all_named_terms_have_source_or_open_status"] is True
    assert payload["background_on_shell"] is False
    assert payload["background_residual"] is None
    for row in payload["terms"]:
        assert row["source"] and row["status"] and row["dimension"]
    quantum={row["name"]:row for row in payload["terms"]}["quantum"]
    assert quantum["status"]=="OPEN_NOT_RETAINED_AS_DERIVED_LOCAL_TERM"


def test_surface_hessian_is_derivative_of_reduced_normal_equation():
    L=1.7; coeffs=(-0.4,0.2,1.1); eps=1e-6
    numeric=(bt.reduced_normal_force(eps,L,*coeffs)-bt.reduced_normal_force(-eps,L,*coeffs))/(2*eps)
    assert numeric==pytest.approx(bt.reduced_lambda(L,*coeffs))


def test_surface_domain_boundary_form_is_only_formally_closed_without_edge():
    payload=load("surface_hessian")
    assert payload["formal_closed_surface_boundary_form_zero"] is True
    assert payload["physical_domain_closed"] is False
    assert payload["self_adjoint"] is False
    assert payload["strongly_elliptic"] is False
    assert payload["uniform_mode_only_assumed"] is False


def test_surface_scaling_origins_and_dependencies_are_explicit():
    payload=load("surface_hessian")
    assert "T_boundary q_tau" in payload["scaling_architecture"]
    assert payload["scaling_origins"]["L^-2"].startswith("two derivatives")
    assert payload["Berger_dependence"].startswith("q functions")
    assert "sigma=1/2" in payload["sigma_dependence"]
    assert "rho_star=1" in payload["rho_star_dependence"]


def test_uniform_surface_mode_is_physical_candidate_not_tangential_gauge():
    payload=load("normal_variation")
    assert payload["tangential_gauge_distinct"] is True
    assert payload["xi_perp_physical_candidate"] is True


def test_stable_to_unstable_and_reverse_crossings_are_distinguished():
    roots=bt.positive_roots(-1.0,0.0,1.0)
    assert roots==pytest.approx([1.0])
    assert bt.classify_crossing(roots[0],-1.0,0.0,1.0)=="STABLE_TO_UNSTABLE_FOR_INCREASING_L"
    reverse=bt.positive_roots(1.0,0.0,-1.0)
    assert bt.classify_crossing(reverse[0],1.0,0.0,-1.0)=="UNSTABLE_TO_STABLE_FOR_INCREASING_L"


def test_tangential_and_multiple_roots_are_distinguished():
    tangent=bt.positive_roots(1.0,-2.0,1.0)
    assert tangent==pytest.approx([1.0])
    assert bt.classify_crossing(1.0,1.0,-2.0,1.0)=="TANGENTIAL_TOUCH"
    multiple=bt.positive_roots(1.0,-3.0,2.0)
    assert multiple==pytest.approx([1.0,2.0])
    assert bt.classify_crossing(1.0,1.0,-3.0,2.0)=="STABLE_TO_UNSTABLE_FOR_INCREASING_L"
    assert bt.classify_crossing(2.0,1.0,-3.0,2.0)=="UNSTABLE_TO_STABLE_FOR_INCREASING_L"


def test_one_homogeneous_term_cannot_generate_isolated_finite_root():
    assert bt.positive_roots(1.0,0.0,0.0)==[]
    assert bt.positive_roots(0.0,1.0,0.0)==[]
    theorem=load("release_threshold")["competing_scaling_theorem"]
    assert theorem["statement"].startswith("A single nonzero homogeneous term")
    assert "at least two nonzero contributions" in theorem["necessary_conditions"]


def test_reduced_model_is_scale_covariant_and_examples_are_not_BHSM_values():
    L=1.3; coeffs=(-1.0,0.4,2.0); scale=2.7
    original=bt.reduced_lambda(L,*coeffs)
    transformed=(scale**2*coeffs[0],scale**3*coeffs[1],scale**4*coeffs[2])
    assert bt.reduced_lambda(scale*L,*transformed)==pytest.approx(original)
    roots=bt.positive_roots(-1.0,0.0,1.0)
    scaled=bt.positive_roots(-scale**2,0.0,scale**4)
    assert scaled==pytest.approx([scale*roots[0]])
    payload=load("reduced_model")
    assert payload["illustrative_coefficients_promoted"] is False


def test_release_threshold_is_not_evaluated_or_physical():
    payload=load("release_threshold")
    assert payload["finite_L_c"] is None
    assert payload["number_of_roots"] is None
    assert payload["physical"] is False
    assert payload["action_derived"] is False
    assert payload["energy_threshold"]["E_break"] is None


def test_no_primitive_scale_or_absolute_unit_is_silently_promoted():
    payload=load("absolute_one_scale")
    assert payload["outputs"]=={"ell_star":None,"M_star":None,"M_BH":None,"R_BH":None}
    minimal=payload["minimal_one_scale"]
    assert minimal["all_dimensionless_ratios_derived"] is False
    assert minimal["one_scale_theorem"] is False
    assert minimal["exponent_currently_derived_as_physical_BHSM_law"] is False
    assert payload["hidden_scale"] is None


def test_quantum_mu_rho_and_pilot_wave_boundaries_are_preserved():
    absolute=load("absolute_one_scale")["absolute_test"]
    assert absolute["arbitrary_mu"] is False
    assert absolute["rho_star_as_length"] is False
    model=load("reduced_model")["valid_global_quantum_diagnostic"]
    assert model["stored_separately"] is True
    assert model["added_to_local_A2"] is False
    pilot=load("energy_conversion")["pilot_wave_connection"]
    assert pilot["surface_threshold_in_v5_9_Hamiltonian"] is False
    assert pilot["pilot_wave_generates_threshold"] is False
    assert pilot["double_counting_avoided"] is True


def test_energy_conversion_remains_formal_without_plasma_predictions():
    payload=load("energy_conversion")
    assert payload["time_split_available"] is False
    assert payload["conservation_template"]=="E_initial=E_expansion+E_plasma+E_residual"
    assert all(value is None for value in payload["ledger"].values())
    assert payload["temperature"] is None and payload["reheating"] is None


def test_report_preserves_old_mass_gap_and_recommends_localization_sprint():
    report=load("construction_report")
    assert any("old curvature-threshold mass-gap" in item for item in report["invalidated_or_ruled_out"])
    assert report["recommended_next_construction_sprint"]=="bhsm-scalar-topographic-physical-localization-v5-13"
    assert report["absolute_unit"]=={"ell_star":None,"M_star":None,"M_BH":None,"R_BH":None}


def test_cli_json_and_markdown():
    env={**os.environ,"PYTHONPATH":str(ROOT/"src")}
    command=[sys.executable,"-m","bhsm.interface","primordial-boundary-tension-status"]
    result=subprocess.run(command+["--format","json"],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    assert json.loads(result.stdout)["primary_result"]=="BHSM_PRIMORDIAL_BOUNDARY_SOURCE_NOT_CLOSED"
    markdown=subprocess.run(command+["--format","markdown"],cwd=ROOT,env=env,check=True,capture_output=True,text=True)
    assert "BHSM v5.12 Primordial Boundary-Tension" in markdown.stdout


def test_public_ledgers_preserve_result_open_gates_and_forbidden_promotions():
    text=focused_text()
    assert "BHSM_PRIMORDIAL_BOUNDARY_SOURCE_NOT_CLOSED" in text
    assert "OPEN_MISSING_SCALAR_TOPOGRAPHIC_PHYSICAL_LOCALIZATION_MAP" in text
    assert "FULL_BHSM_NOT_COMPLETE" in text
    assert "primordial-boundary-tension-status" in text
    forbidden=["v5.12 derives an absolute unit","-1/8 is the physical boundary tension","rho_star=1 fixes the collar length","v5.10 is a local Casimir pressure","primordial hot plasma is derived","full BHSM completion is achieved"]
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_and_official_logic_hashes_remain_unchanged():
    for relative,digest in EXPECTED_HASHES.items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
