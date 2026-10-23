"""Independent analytic trace-family controls; no physical boundary chosen."""
import numpy as np
import pytest
from bhsm.interface.muon_outgoing_trace_energy_jet import (
    outgoing_energy_pairing,boundary_row_energy_change,
)


def data():
    V=np.array([[1.,0.],[0.,1.],[.2,.3],[-.1,.4]],complex)
    VE=np.array([[0.,0.],[0.,0.],[.7,.1j],[.2,-.6]],complex)
    C=np.c_[-V[2:],np.eye(2)]
    R=np.eye(2,dtype=complex);L=np.array([[1,.2j],[.3,1]],complex)
    T=V.copy();TE=np.array([[0.,.1],[.2,0.],[.3,-.4j],[.5,.6]],complex)
    return dict(annihilator=C,allowed_trace=V,allowed_trace_energy=VE,
                joined_trace=T,joined_trace_energy=TE,right_mode=R,
                left_mode=L,allowed_coordinates=np.eye(2))


def test_subspace_pairing_matches_fresh_original_boundary_derivative():
    a=data();answer=outgoing_energy_pairing(**a)
    h=1e-5
    def f(e):
        v=a['allowed_trace']+e*a['allowed_trace_energy']
        c=np.c_[-v[2:],np.eye(2)]
        return a['left_mode']@c@(a['joined_trace']+e*a['joined_trace_energy'])@a['right_mode']
    fresh=(f(h)-f(-h))/(2*h)
    assert np.max(abs(fresh-answer['energy_pairing']))<4e-12
    assert np.linalg.norm(answer['outgoing_subspace_contribution'])>1


def test_energy_dependent_allowed_frame_change_cancels_without_zeroing_jet():
    a=data();base=outgoing_energy_pairing(**a)
    S=np.array([[1,.2j],[.3,1.1]],complex)
    SE=np.array([[.1,.4],[.2j,-.3]],complex)
    b=dict(a,allowed_trace=a['allowed_trace']@S,
           allowed_trace_energy=a['allowed_trace_energy']@S+a['allowed_trace']@SE,
           allowed_coordinates=np.linalg.solve(S,a['allowed_coordinates']))
    changed=outgoing_energy_pairing(**b)
    assert np.max(abs(base['energy_pairing']-changed['energy_pairing']))<4e-16
    assert np.max(abs(changed['reached_trace_coordinate_rows']))<2e-16


def test_boundary_row_chain_rule_keeps_off_pole_full_spin_contact():
    G=np.diag([0.,0.,2.]).astype(complex)
    GE=np.array([[1,.1j,0],[.2,1.2,0],[0,0,.7]],complex)
    R=np.eye(3,dtype=complex)[:,:2];L=R.T.copy()
    S=np.array([[1,.1j,.2],[0,1.1,.1],[.1,0,.9]],complex)
    SE=np.array([[.3,.2,0],[.1j,.4,.1],[0,.2,.1]],complex)
    base=boundary_row_energy_change(gamma=G,gamma_energy=GE,right_mode=R,
        left_mode=L,row_change=S,row_change_energy=SE)
    assert np.max(abs(base['changed_pairing']-base['original_pairing']))<3e-16
    bad=G+np.diag([1e-4,-1e-4,0])
    answer=boundary_row_energy_change(gamma=bad,gamma_energy=GE,right_mode=R,
        left_mode=L,row_change=S,row_change_energy=SE)
    assert abs(np.trace(bad[:2,:2]))==0
    assert np.linalg.norm(answer['off_pole_row_contact'])>1e-5
    assert np.max(abs(answer['exact_chain_rule_rows']))<4e-16


def test_missing_subspace_energy_jet_is_not_a_zero_default():
    a=data();a['allowed_trace_energy']=None
    with pytest.raises(ValueError):outgoing_energy_pairing(**a)
