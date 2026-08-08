from pathlib import Path
import json
import numpy as np
import pytest

from bhsm.interface.completion.berger_rank3_polarization_gate_v14_72 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    fixed_volume_lengths, berger_scalar_eigenvalue, ell2_spectrum,
    dimensionless_fixed_volume_spectrum, analytic_round_derivatives,
    finite_difference_round_derivatives, spin1_generators,
    berger_rank3_projector_m_basis, berger_rank6_projector_m_basis,
    berger_ell2_operator, max_commutator_norm, symmetry_breaking_payload,
    diagonal_su2_triplet_projector, berger_axis_projector_cartesian,
    projector_intersection_dimension, aligned_triplet_comparison_payload,
    orientation_average_payload, fixed_volume_splitting_payload,
    action_selection_contract_payload, selector_provenance_payload,
    transverse_channel_firewall_payload, calderon_handoff_payload,
    neutrino_kill_screen_payload, status_payload, completion_gate_payload,
    artifact_payloads, materialize,
)

def test_version():
    assert VERSION == "v14.72"
    assert "RANK_THREE" in PRIMARY_VERDICT
    assert "BETA_STAR" in EXACT_NEXT_OBJECT

def test_fixed_volume_lengths():
    L2,L1=fixed_volume_lengths(2.3,0.7)
    assert abs(L2*L2*L1-2.3**3)<1e-12
    assert abs(L1/L2-0.7)<1e-12

@pytest.mark.parametrize("bad", [0.0,-1.0])
def test_fixed_volume_invalid(bad):
    with pytest.raises(ValueError):
        fixed_volume_lengths(1.0,bad)

def test_round_berger_eigenvalue_J1():
    assert abs(berger_scalar_eigenvalue(1,0,1.0,1.0)-2.0)<1e-14
    assert abs(berger_scalar_eigenvalue(1,1,1.0,1.0)-2.0)<1e-14
    assert abs(berger_scalar_eigenvalue(1,-1,1.0,1.0)-2.0)<1e-14

def test_ell2_dimension_and_multiplicity():
    p=ell2_spectrum(1.0,0.8)
    assert p["dimension_total"]==9
    assert p["m0_multiplicity"]==3
    assert p["combined_abs_m1_multiplicity"]==6

def test_round_gap_zero():
    assert abs(ell2_spectrum(1.0,1.0)["gap_abs_m1_minus_m0"])<1e-14
    assert abs(dimensionless_fixed_volume_spectrum(1.0)["rho2_gap"])<1e-14

def test_nonround_gap_nonzero():
    assert abs(ell2_spectrum(1.0,0.8)["gap_abs_m1_minus_m0"])>1e-3
    assert abs(ell2_spectrum(1.0,1.2)["gap_abs_m1_minus_m0"])>1e-3

def test_gap_sign():
    assert ell2_spectrum(1.0,0.8)["gap_abs_m1_minus_m0"]>0
    assert ell2_spectrum(1.0,1.2)["gap_abs_m1_minus_m0"]<0

def test_dimensionless_formula_matches_direct():
    for beta in (0.6,0.8,1.2,1.7):
        p=ell2_spectrum(2.4,beta)
        q=dimensionless_fixed_volume_spectrum(beta)
        assert abs(p["m0_eigenvalue"]*2.4**2-q["rho2_lambda_m0"])<1e-12
        assert abs(p["mplus_eigenvalue"]*2.4**2-q["rho2_lambda_abs_m1"])<1e-12

def test_round_derivatives_finite_difference():
    a=analytic_round_derivatives(1.7)
    f=finite_difference_round_derivatives(1.7,1e-6)
    for key in f:
        assert abs(f[key]-a[key])<2e-9

def test_first_order_trace_derivative_zero():
    assert abs(analytic_round_derivatives()["multiplicity_weighted_trace_derivative"])<1e-14

def test_spin1_commutators():
    jx,jy,jz=spin1_generators()
    assert np.linalg.norm(jx@jy-jy@jx-1j*jz)<1e-12
    assert np.linalg.norm(jy@jz-jz@jy-1j*jx)<1e-12
    assert np.linalg.norm(jz@jx-jx@jz-1j*jy)<1e-12

def test_rank_projectors():
    p3=berger_rank3_projector_m_basis()
    p6=berger_rank6_projector_m_basis()
    assert np.linalg.matrix_rank(p3)==3
    assert np.linalg.matrix_rank(p6)==6
    assert np.linalg.norm(p3@p3-p3)<1e-14
    assert np.linalg.norm(p6@p6-p6)<1e-14
    assert np.linalg.norm(p3@p6)<1e-14

def test_operator_projector_spectrum():
    beta=0.8
    op=berger_ell2_operator(1.0,beta)
    vals=np.linalg.eigvalsh(op)
    spec=ell2_spectrum(1.0,beta)
    assert np.sum(np.isclose(vals,spec["m0_eigenvalue"]))==3
    assert np.sum(np.isclose(vals,spec["mplus_eigenvalue"]))==6

def test_symmetry_breaking():
    p=symmetry_breaking_payload(0.8)
    assert p["commutator_with_left_SU2"]<1e-12
    assert p["commutator_with_right_U1_Jz"]<1e-12
    assert p["commutator_with_right_Jx_Jy"]>1e-3
    assert p["residual_symmetry"]=="SU(2)_L x U(1)_R"

def test_diagonal_triplet_projector_rank():
    p=diagonal_su2_triplet_projector()
    assert np.linalg.matrix_rank(p)==3
    assert np.linalg.norm(p@p-p)<1e-14
    assert np.linalg.norm(p-p.T)<1e-14

def test_cartesian_berger_projector_rank():
    p=berger_axis_projector_cartesian((2,0,0))
    assert np.linalg.matrix_rank(p)==3
    assert np.linalg.norm(p@p-p)<1e-14

def test_projector_intersection_zero_aligned():
    pb=berger_axis_projector_cartesian((0,0,1))
    pd=diagonal_su2_triplet_projector()
    assert projector_intersection_dimension(pb,pd)==0

def test_triplet_comparison():
    p=aligned_triplet_comparison_payload()
    assert p["intersection_dimension"]==0
    assert abs(p["trace_projector_overlap"]-1.0)<1e-14
    assert abs(p["frobenius_projector_distance"]-2.0)<1e-14
    assert p["same_subspace"] is False
    assert np.allclose(p["principal_angles_degrees"],[45.0,45.0,90.0],atol=1e-10)

def test_orientation_average_exact():
    p=orientation_average_payload()
    assert p["six_axis_2_design_residual"]<1e-14
    assert np.allclose(p["average_eigenvalues"],np.ones(9)/3.0,atol=1e-14)

def test_splitting_payload():
    p=fixed_volume_splitting_payload()
    assert p["max_derivative_residual"]<1e-8
    assert p["first_order_trace_shift_zero"] is True
    assert p["rank3_isolated_for_every_beta_not_equal_one"] is True
    assert p["absolute_scale_required_for_rank_split"] is False

def test_action_contract():
    p=action_selection_contract_payload()
    assert p["triplet_condition"]=="beta_star != 1"
    assert p["measured_particle_or_flavor_data_allowed_in_selection"] is False
    assert p["current_contract_executed_physically"] is False

def test_provenance_fail_closed():
    p=selector_provenance_payload()
    assert p["rank3_carrier_already_available_mathematically"] is True
    assert p["action_selected_rank3_carrier_available"] is False
    assert p["no_candidate_promoted_by_v14_72"] is True

def test_transverse_firewall():
    p=transverse_channel_firewall_payload()
    assert p["rank3_carrier_dimension"]==3
    assert p["internal_triplet_split"] is False
    assert p["three_noncommuting_generators_derived"] is False
    assert p["CKM_or_PMNS_generated"] is False

def test_calderon_handoff_blocked():
    p=calderon_handoff_payload()
    assert p["eligible_now"] is False
    assert len(p["current_blockers"])==4

def test_neutrino_gate():
    p=neutrino_kill_screen_payload()
    assert p["current_result"]=="PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_execution_allowed"] is False

def test_status_fail_closed():
    p=status_payload()
    assert len(p["validated"])>=9
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["USB_touched"] is False

def test_completion_gate_passes_its_own_validation():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["rank3_carrier_mechanism"]=="KINEMATICALLY_DERIVED"
    assert p["global_physical_selector"]=="OPEN"
    assert p["stationary_beta_star"] is None
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    p=artifact_payloads()
    assert len(p)==11
    assert "BHSM_completion_gate_v14_72.json" in p

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
