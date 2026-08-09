from pathlib import Path
import json
import numpy as np
import pytest

from bhsm.interface.completion.l2_landau_goldstone_triplet_v14_74 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    invariants, landau_potential, random_rotation, transform,
    reflection_cubic_firewall_payload, quartic_boundedness_condition,
    isotropic_amplitude_squared, isotropic_stationarity_residual,
    projector_trace, projector_antisymmetric, projector_sym_traceless,
    hessian_sector_eigenvalues, even_branch_hessian_after_stationarity,
    local_stability_mod_goldstone, so3_generators, goldstone_tangents,
    goldstone_gram, goldstone_commutator_residual, vacuum_orbit_payload,
    hessian_goldstone_payload, potential_invariance_payload,
    direct_directional_second_derivative, hessian_finite_difference_payload,
    boundedness_and_stability_payload, hopf_curvature_role_payload,
    goldstone_rotor_payload, calderon_handoff_payload,
    neutrino_kill_screen_payload, status_payload, completion_gate_payload,
    artifact_payloads, materialize,
)

def test_version():
    assert VERSION=="v14.74"
    assert "GOLDSTONE" in PRIMARY_VERDICT
    assert "SECOND_AND_FOURTH_SHAPE_VARIATIONS" in EXACT_NEXT_OBJECT

def test_invariants_identity():
    p=invariants(np.eye(3))
    assert p=={"I2":3.0,"I4":3.0,"det":1.0}

def test_group_invariance_direct():
    Q=np.array([[0.7,-0.2,0.4],[0.1,0.9,-0.3],[-0.5,0.2,0.6]])
    L=random_rotation(1); R=random_rotation(2)
    a=invariants(Q); b=invariants(transform(Q,L,R))
    assert abs(a["I2"]-b["I2"])<1e-12
    assert abs(a["I4"]-b["I4"])<1e-12
    assert abs(a["det"]-b["det"])<1e-12

def test_reflection_cubic_odd():
    p=reflection_cubic_firewall_payload()
    assert p["odd_residual"]<1e-12
    assert p["reflection_symmetric_branch_forbids_det_term"] is True

@pytest.mark.parametrize(
    "u,v,expected",
    [(1,1,True),(-0.2,1,True),(-0.5,1,False),(1,-0.2,True),(-0.9,-0.2,False)]
)
def test_boundedness(u,v,expected):
    assert quartic_boundedness_condition(u,v) is expected

def test_isotropic_amplitude():
    assert abs(isotropic_amplitude_squared(-1,1,1)-0.25)<1e-14

def test_isotropic_stationarity():
    s=np.sqrt(isotropic_amplitude_squared(-1,1,1))
    assert abs(isotropic_stationarity_residual(s,-1,1,1))<1e-14

def test_invalid_isotropic_branch():
    with pytest.raises(ValueError):
        isotropic_amplitude_squared(1,1,1)
    with pytest.raises(ValueError):
        isotropic_amplitude_squared(-1,-1,1)

def test_projector_decomposition():
    Q=np.array([[1.2,-0.5,0.3],[0.7,-0.2,0.1],[-0.4,0.8,0.6]])
    p1=projector_trace(Q); p3=projector_antisymmetric(Q); p5=projector_sym_traceless(Q)
    assert np.linalg.norm(p1+p3+p5-Q)<1e-14
    assert abs(np.sum(p1*p3))<1e-14
    assert abs(np.sum(p1*p5))<1e-14
    assert abs(np.sum(p3*p5))<1e-14

def test_general_hessian_formulas_even_stationary():
    r,u,v=-1,1,1
    s=np.sqrt(isotropic_amplitude_squared(r,u,v))
    general=hessian_sector_eigenvalues(s,r,u,v,b=0)
    reduced=even_branch_hessian_after_stationarity(r,u,v)
    for k in ("rank1","rank3","rank5"):
        assert abs(general[k]-reduced[k])<1e-14

def test_stable_goldstone_cone():
    assert local_stability_mod_goldstone(-1,1,1) is True
    assert local_stability_mod_goldstone(1,1,1) is False
    assert local_stability_mod_goldstone(-1,1,-0.1) is False

def test_hessian_witness():
    p=even_branch_hessian_after_stationarity(-1,1,1)
    assert p["s_squared"]==0.25
    assert p["rank1"]==2.0
    assert p["rank3"]==0.0
    assert p["rank5"]==0.5

def test_so3_commutators():
    assert goldstone_commutator_residual()<1e-14

def test_goldstone_gram():
    s=0.7
    assert np.linalg.norm(goldstone_gram(s)-2*s*s*np.eye(3))<1e-14

def test_goldstone_tangents_antisymmetric():
    for t in goldstone_tangents(0.4):
        assert np.linalg.norm(t+t.T)<1e-14

def test_vacuum_orbit():
    p=vacuum_orbit_payload()
    assert p["dimension"]==3
    assert p["sample_potential_spread"]<1e-12
    assert p["stabilizer_residual"]<1e-12
    assert p["requires_global_U1_reduction"] is False

def test_goldstone_payload():
    p=hessian_goldstone_payload()
    assert p["exact_goldstone_count"]==3
    assert p["positive_nonGoldstone"] is True
    assert p["gram_residual"]<1e-12
    assert p["so3_commutator_residual"]<1e-12
    assert p["physical_channel_identification"] is False

def test_potential_invariance_payload():
    p=potential_invariance_payload()
    assert p["max_SO3L_times_SO3R_invariance_residual"]<1e-12

def test_directional_fd_matches():
    p=hessian_finite_difference_payload()
    assert p["max_residual"]<2e-5

def test_boundedness_stability_payload():
    p=boundedness_and_stability_payload()
    assert p["under_these_conditions_quartic_is_bounded"] is True
    assert p["physical_coefficients_derived"] is False
    assert p["rows"][0]["stable_isotropic_locking_branch"] is True

def test_hopf_curvature_role_fail_closed():
    p=hopf_curvature_role_payload()
    assert p["canonical_Hopf_connection_exists"] is True
    assert p["global_U1_axis_required"] is False
    assert p["round_homogeneous_curvature_by_itself_selects_Q_orientation"] is False
    assert p["full_preimage_mixed_variation_projected_to_r_u_v"] is None

def test_goldstone_rotor():
    p=goldstone_rotor_payload()
    assert p["I_eff"]==0.5
    assert p["classical_symmetric_Goldstone_gaps"]==[0.0,0.0,0.0]
    assert p["physical_neutrino_interpretation"] is False

def test_calderon_handoff():
    p=calderon_handoff_payload()
    assert p["eligible_now"] is False
    assert p["structural_three_channel_basis"]=="DERIVED_AS_GOLDSTONE_TANGENT_SPACE"
    assert p["physical_three_channel_basis"]=="OPEN"

def test_neutrino_blocked():
    p=neutrino_kill_screen_payload()
    assert p["current_result"]=="PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_execution_allowed"] is False

def test_status():
    p=status_payload()
    assert len(p["validated"])>=10
    assert p["FULL_BHSM_COMPLETE"] is False
    assert p["MARK_III"]=="NOT_REACHED"
    assert p["USB_touched"] is False

def test_completion_gate():
    p=completion_gate_payload()
    assert p["validation_passed"] is True
    assert p["global_U1_axis_required"] is False
    assert p["ell2_diagonal_locking_mechanism"]=="STRUCTURALLY_DERIVED"
    assert p["three_Goldstone_channels"]=="STRUCTURALLY_DERIVED"
    assert p["action_projected_r_u_v"] is None
    assert p["physical_execution_allowed"] is False

def test_artifact_count():
    p=artifact_payloads()
    assert len(p)==12
    assert "BHSM_completion_gate_v14_74.json" in p

def test_materialization_deterministic(tmp_path:Path):
    a=tmp_path/"a"; b=tmp_path/"b"
    pa=materialize(a); pb=materialize(b)
    assert [x.name for x in pa]==[x.name for x in pb]
    for x,y in zip(pa,pb):
        assert x.read_bytes()==y.read_bytes()
        json.loads(x.read_text())
