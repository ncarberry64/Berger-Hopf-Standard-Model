from pathlib import Path
import json
import numpy as np
import pytest

from bhsm.interface.completion.hopf_u1_obstruction_diagonal_locking_v14_73 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    u1_reduction_obstruction_payload, normalizer_axis_obstruction_payload,
    descent_firewall_payload, fixed_volume_lengths, berger_scalar_curvature,
    fixed_volume_dimensionless_scalar_curvature,
    fixed_volume_scalar_curvature_derivative,
    fixed_volume_scalar_curvature_second_at_round,
    intrinsic_berger_eh_payload, ricci_invariants_fixed_volume,
    anisotropy_invariant_payload, spin1_generators, diagonal_locking_operator,
    diagonal_generators, product_generators, max_commutator_norm,
    diagonal_spectral_projectors, projector_quality, diagonal_locking_payload,
    diagonal_hessian_eigenvalues, triplet_softest_condition,
    triplet_selection_cone_payload, nonabelian_replacement_gate_payload,
    calderon_handoff_payload, neutrino_kill_screen_payload, status_payload,
    completion_gate_payload, artifact_payloads, materialize,
)

def test_version():
    assert VERSION=="v14.73"
    assert "C2_EQUALS_ONE" in PRIMARY_VERDICT
    assert "NONABELIAN_HOPF_CURVATURE" in EXACT_NEXT_OBJECT

def test_u1_reduction_obstruction():
    p=u1_reduction_obstruction_payload()
    assert p["retained_second_Chern_class"]==1
    assert p["therefore_c1_L"]==0
    assert p["reduced_c2_value"]==0
    assert p["global_smooth_U1_reduction_exists"] is False

def test_normalizer_axis_obstruction():
    p=normalizer_axis_obstruction_payload()
    assert p["quotient"]=="N(U1)/U1 = Z2"
    assert p["global_unoriented_axis_reduction_exists"] is False
    assert p["global_rank3_fixed_axis_projector_descends_to_S4"] is False

def test_descent_firewall():
    p=descent_firewall_payload()
    assert p["global_total_space_Berger_metric_possible"] is True
    assert p["principal_Sp1_equivariant_basic_axis_over_S4"] is False
    assert p["fixed_right_weight_m_is_globally_preserved_by_general_Sp1_transition_functions"] is False

@pytest.mark.parametrize("rho,beta",[(1.0,1.0),(2.3,0.6),(0.8,1.7)])
def test_fixed_volume_lengths(rho,beta):
    L2,L1=fixed_volume_lengths(rho,beta)
    assert abs(L2*L2*L1-rho**3)<1e-12
    assert abs(L1/L2-beta)<1e-12

def test_berger_round_scalar_curvature():
    assert abs(berger_scalar_curvature(1.0,1.0)-1.5)<1e-14

def test_fixed_volume_formula_matches_direct():
    for beta in (0.5,0.8,1.0,1.3,2.0):
        rho=1.7
        L2,L1=fixed_volume_lengths(rho,beta)
        direct=berger_scalar_curvature(L2,L1)*rho*rho
        closed=fixed_volume_dimensionless_scalar_curvature(beta)
        assert abs(direct-closed)<1e-12

def test_scalar_derivative_zero_only_round_witnesses():
    assert fixed_volume_scalar_curvature_derivative(0.7)>0
    assert abs(fixed_volume_scalar_curvature_derivative(1.0))<1e-14
    assert fixed_volume_scalar_curvature_derivative(1.4)<0

def test_scalar_derivative_finite_difference():
    eps=1e-6
    for beta in (0.6,0.9,1.2,1.8):
        fd=(fixed_volume_dimensionless_scalar_curvature(beta+eps)-fixed_volume_dimensionless_scalar_curvature(beta-eps))/(2*eps)
        assert abs(fd-fixed_volume_scalar_curvature_derivative(beta,1.0))<5e-9

def test_round_second_derivative():
    assert abs(fixed_volume_scalar_curvature_second_at_round()+8/3)<1e-14

def test_intrinsic_eh_payload():
    p=intrinsic_berger_eh_payload()
    assert p["positive_stationary_points"]==[1.0]
    assert p["bare_intrinsic_EH_selects_nonround_beta"] is False
    assert p["full_M8_action_reduced_to_this_term_only"] is False

def test_ricci_closed_form():
    for beta in (0.4,0.7,1.0,1.4,2.2):
        p=ricci_invariants_fixed_volume(beta)
        assert p["closed_form_residual"]<1e-12
        assert p["rho4_twice_traceless_Ricci2"]>=-1e-12

def test_anisotropy_zero_round():
    p=ricci_invariants_fixed_volume(1.0)
    assert abs(p["rho4_twice_traceless_Ricci2"])<1e-14

def test_anisotropy_positive_nonround():
    assert ricci_invariants_fixed_volume(0.8)["rho4_twice_traceless_Ricci2"]>0
    assert ricci_invariants_fixed_volume(1.2)["rho4_twice_traceless_Ricci2"]>0

def test_anisotropy_payload():
    p=anisotropy_invariant_payload()
    assert p["nonnegative"] is True
    assert p["zero_only_at_round_for_positive_beta"] is True
    assert p["coefficient_sign_derived_by_current_authoritative_action"] is False

def test_spin1_algebra():
    jx,jy,jz=spin1_generators()
    assert np.linalg.norm(jx@jy-jy@jx-1j*jz)<1e-12
    assert np.linalg.norm(jy@jz-jz@jy-1j*jx)<1e-12
    assert np.linalg.norm(jz@jx-jx@jz-1j*jy)<1e-12

def test_diagonal_locking_spectrum():
    vals=np.linalg.eigvalsh(diagonal_locking_operator())
    assert np.allclose(vals,[-2,-1,-1,-1,1,1,1,1,1],atol=1e-12)

def test_diagonal_locking_commutators():
    K=diagonal_locking_operator()
    assert max_commutator_norm(K,diagonal_generators())<1e-12
    assert max_commutator_norm(K,product_generators())>1e-3

def test_diagonal_projector_ranks():
    ps=diagonal_spectral_projectors()
    assert [np.linalg.matrix_rank(p,tol=1e-10) for p in ps]==[1,3,5]

def test_diagonal_projector_quality():
    q=projector_quality()
    assert q["ranks"]==[1,3,5]
    assert q["sum_identity_residual"]<1e-12
    assert q["idempotence_residual"]<1e-12
    assert q["orthogonality_residual"]<1e-12
    assert q["self_adjoint_residual"]<1e-12

def test_diagonal_locking_payload():
    p=diagonal_locking_payload()
    assert p["distinct_eigenvalues"]==[-2.0,-1.0,1.0]
    assert p["multiplicities"]==[1,3,5]
    assert p["requires_global_U1_axis"] is False
    assert p["physical_soldering_map_derived"] is False

def test_hessian_sector_formulas():
    e=diagonal_hessian_eigenvalues(5.0,2.0,3.0)
    assert e["rank1"]==13.0
    assert e["rank3"]==6.0
    assert e["rank5"]==10.0

def test_triplet_softest_exact_witness():
    assert triplet_softest_condition(1.0,1.0) is True
    e=diagonal_hessian_eigenvalues(0,1,1)
    assert e=={"rank1":2.0,"rank3":0.0,"rank5":2.0}

def test_triplet_softest_inequality_edges():
    assert triplet_softest_condition(0.5,1.0) is True
    assert triplet_softest_condition(3.0,1.0) is False
    assert triplet_softest_condition(-0.2,1.0) is False

def test_linear_K_alone_does_not_make_triplet_softest():
    assert triplet_softest_condition(1.0,0.0) is False
    assert triplet_softest_condition(-1.0,0.0) is False

def test_selection_cone_payload():
    p=triplet_selection_cone_payload()
    assert p["rank3_strictly_softest_condition"]=="c1>0 and c1<3 c2"
    assert p["witness_selects_triplet"] is True
    assert p["physical_coefficients_derived"] is False

def test_nonabelian_replacement_gate():
    p=nonabelian_replacement_gate_payload()
    assert p["global_U1_axis_route"]=="TOPOLOGICALLY_BLOCKED_ON_FULL_S4"
    assert p["current_action_owned_soldering"] is None
    assert p["physical_gate_open"] is False

def test_calderon_handoff():
    p=calderon_handoff_payload()
    assert p["eligible_now"] is False
    assert p["fixed_axis_Berger_handoff_superseded"] is True

def test_neutrino_blocked():
    p=neutrino_kill_screen_payload()
    assert p["current_result"]=="PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_execution_allowed"] is False

def test_status_fail_closed():
    p=status_payload()
    assert len(p["validated"])>=10
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["global_fixed_axis_Berger_route"]=="TOPOLOGICALLY_BLOCKED"
    assert p["local_Berger_rank3_mechanism"]=="VALIDATED_CONDITIONAL"
    assert p["bare_intrinsic_EH_nonround_beta_selection"]=="INVALIDATED"
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    p=artifact_payloads()
    assert len(p)==12
    assert "BHSM_completion_gate_v14_73.json" in p

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
