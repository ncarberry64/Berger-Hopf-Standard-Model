import math
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from bhsm.interface import muon_moving_geometric_action as moving
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import exact_full_action_jet_at_state
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def evaluated():
    state=moving.retained_state(ROOT)
    data=moving.moving_cap_action_jet(12,*state,points=96)
    return state,data


def test_unchanged_base_all_derivatives(evaluated):
    state,data=evaluated
    original=exact_full_action_jet_at_state(12,*state,points=96)
    actual=data['total']
    assert actual.value==pytest.approx(original.value,abs=2e-13)
    np.testing.assert_allclose(actual.gradient[:98],original.gradient,rtol=2e-10,atol=7e-12)
    np.testing.assert_allclose(actual.hessian[:98,:98],original.hessian,rtol=2e-10,atol=5e-10)


def test_response_matches_independent_normalization():
    x=.31; k=-.04; eps=1e-4
    def sigma(t):
        W=lambda y: math.sin(y+t*k*(21*math.sin(2*y)+5*math.sin(6*y)))**2*math.cos(y+t*k*(21*math.sin(2*y)+5*math.sin(6*y)))**2
        return quad(W,0,x,epsabs=1e-14)[0]/quad(W,0,math.pi/2,epsabs=1e-14)[0]-.5
    s=Jet.affine(0.,np.array([1.]))
    _,sig=moving.response_two_jet(x,s,k)
    assert (sigma(eps)-sigma(-eps))/(2*eps)==pytest.approx(sig.gradient[0],abs=2e-9)
    assert (sigma(eps)-2*sigma(0)+sigma(-eps))/eps**2==pytest.approx(sig.hessian[0,0],abs=3e-8)


def test_two_material_trace_rows():
    s=Jet.affine(0.,np.array([1.]))
    k=-.071
    wall=math.pi/4-16*k*s
    f,sigma=moving.response_two_jet(wall,s,k)
    assert f.value==pytest.approx(math.pi/4)
    assert sigma.value==pytest.approx(0.,abs=1e-15)
    np.testing.assert_allclose(f.gradient,[0.],atol=1e-14)
    np.testing.assert_allclose(f.hessian,[[0.]],atol=1e-14)
    np.testing.assert_allclose(sigma.gradient,[0.],atol=1e-14)
    np.testing.assert_allclose(sigma.hessian,[[0.]],atol=1e-14)


def test_independent_exact_response_primal_action(evaluated,monkeypatch):
    state,data=evaluated
    original=moving.response_two_jet
    def exact_response(chi,s,k):
        f,_=original(chi,s,k)
        raw=lambda x: math.sin(x+s.value*k.value*(21*math.sin(2*x)+5*math.sin(6*x)))**2*math.cos(x+s.value*k.value*(21*math.sin(2*x)+5*math.sin(6*x)))**2
        sig=quad(raw,0,chi.value,epsabs=2e-13)[0]/quad(raw,0,math.pi/2,epsabs=2e-13)[0]-.5
        return f,Jet.constant(sig,len(s.gradient))
    monkeypatch.setattr(moving,'response_two_jet',exact_response)
    eps=2e-5
    p=moving.moving_cap_action_jet(12,*state,points=96,source_value=eps)['total'].value
    m=moving.moving_cap_action_jet(12,*state,points=96,source_value=-eps)['total'].value
    S=data['total']; index=data['source_indices'][0]
    assert (p-m)/(2*eps)==pytest.approx(S.gradient[index],rel=1e-7)
    assert (p-2*S.value+m)/eps**2==pytest.approx(S.hessian[index,index],abs=1.5e-4)


def test_mixed_source_keeps_unit_normal_metric_motion(evaluated):
    state,data=evaluated
    q,v,m=state; eps=2e-6; qp=q.copy(); qm=q.copy()
    qp[13]+=eps; qm[13]-=eps
    p=moving.moving_cap_action_jet(12,qp,v,m,points=96)['total'].gradient[98]
    minus=moving.moving_cap_action_jet(12,qm,v,m,points=96)['total'].gradient[98]
    assert (p-minus)/(2*eps)==pytest.approx(data['total'].hessian[13,98],rel=2e-7)


def test_trial_scaling_and_weak_momentum_contact(evaluated):
    state,data=evaluated
    double=moving.moving_cap_action_jet(12,*state,points=96,trial_normal=2.)
    a=moving.weak_action_blocks(data); b=moving.weak_action_blocks(double)
    assert b['normal_first_variation']==pytest.approx(2*a['normal_first_variation'])
    assert b['D_ss']==pytest.approx(4*a['D_ss'])
    np.testing.assert_allclose(b['B_q_momentum_contact'],2*a['B_q_momentum_contact'],rtol=1e-12,atol=1e-11)
    assert np.linalg.norm(a['B_q_momentum_contact'])>90
    assert not a['stationarity_claim'] and not a['physical_formation_mode_selected']
    assert a['eta_FR_kinetic_component']>0


def test_correct_endpoint_modes(evaluated):
    _,data=evaluated
    assert data['Cstar'].value==pytest.approx(1.9180902180140678,abs=1e-14)
    assert 1/data['Cstar'].value==pytest.approx(.5213519106704843,abs=1e-14)


def test_local_chart_guard(evaluated):
    state,data=evaluated
    with pytest.raises(ValueError,match='monotonicity'):
        moving.moving_cap_action_jet(12,*state,points=32,source_value=data['Cstar'].value/3)


def test_retained_constraint_scope(evaluated):
    _,data=evaluated; b=moving.weak_action_blocks(data)
    assert np.max(np.abs(b['multiplier_constraint_residual']))<5e-12
    assert b['H_qq'].shape==(37,37) and b['H_vm'].shape==(37,24)
    np.testing.assert_allclose(b['H_qv'],b['H_vq'].T,rtol=0,atol=0)


def test_surface_internal_and_mixed_blocks_are_not_discarded(evaluated):
    _,data=evaluated; S=data['surface_per_gamma']
    assert abs(S.gradient[98])<1e-12  # actual even ambient area, not M5 or total traction
    assert S.hessian[98,98]>160
    assert S.hessian[99,99]>11
    assert np.max(np.abs(S.hessian[:98,98]))<3e-11  # parity + U_base=0; evaluated rather than omitted
    assert np.linalg.norm(S.hessian[:98,:98])>1
    assert np.linalg.norm(data['moving_GHY_Hayward'].hessian[:98,98])>1


def test_gravitational_boundary_corner_contact(evaluated):
    _,data=evaluated; G=data['moving_GHY_Hayward']
    # Moving EH+GHY cancellation and Hayward integration by parts give
    # -theta Dt rho. At this wall theta_s=-Hc, so first=Hc*Dt rho.
    from bhsm.interface.muon_birth_candidate_geometry_action import wall_geometry_snapshot
    q,v,m=evaluated[0]; g=wall_geometry_snapshot(q,v,m,order=12)
    expected=g['Hc']*(3*g['A']**3*g['B']**3*(g['coordinate_time_log_rates']['A']+g['coordinate_time_log_rates']['B']))
    assert G.gradient[98]==pytest.approx(expected,rel=2e-13)
    assert data['total'].gradient[98]-data['fixed_wall_extension'].gradient[98]==pytest.approx(expected,rel=2e-13)



@pytest.mark.parametrize("operand",["source_value","source_rate","trial_normal"])
def test_nonfinite_normal_chart_rejected(evaluated,operand):
    with pytest.raises(ValueError,match="finite trial"):
        moving.moving_cap_action_jet(12,*evaluated[0],points=8,**{operand:float('nan')})


def test_surface_changes_the_uncompleted_base_constraints(evaluated):
    _,data=evaluated
    # The positive symbolic gamma area sector adds nonzero lapse constraints.
    # Reset constraints alone therefore cannot certify the interacting base.
    mm=data['surface_per_gamma'].gradient[74:86]
    signs=(-1.)**np.arange(1,13)
    np.testing.assert_allclose(mm,-5.437863897715984*signs,rtol=2e-14,atol=2e-13)


@pytest.mark.parametrize('side',['outgoing_C2','incoming_C1_E1'])
def test_both_action_states_bound_to_original_bits(tmp_path,side):
    import json,shutil
    receipt=tmp_path/moving.STATE_RECEIPT; receipt.parent.mkdir(parents=True)
    data=json.loads((ROOT/moving.STATE_RECEIPT).read_text())
    data['geometry_field_blocks'][side]['q']['binary64_hex'][0]=0.0.hex()
    receipt.write_text(json.dumps(data))
    original=tmp_path/moving.STATE_SOURCE; original.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/moving.STATE_SOURCE,original)
    with pytest.raises(ValueError,match='action blocks disagree'):
        moving.retained_state(tmp_path,side)
