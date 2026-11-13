"""Tests of analytic native continuation and its noncommuting two-jet."""
import numpy as np
from pathlib import Path

from bhsm.interface.muon_stationary_native_reference_load import (
    factor_twojet,native_pencil,heat_trace_twojet,original_operator_checks,
    lorentz_load,
)


def theta():
    # Test coefficients, not a physical incoming reference or state.
    return np.r_[1.3,1.2,[.002,-.003,.001,.004],
                 np.arange(12)*.001-.006,[.1,.2,.03,-.02]]


def test_native_continuation_preserves_sharp_and_frequency_reality():
    t=theta();checks=original_operator_checks(t,cutoff=.8)
    for key,value in checks.items():
        if key!='wrong_redaggered_Hcan_square_difference':assert value<2e-10,(key,value)
    assert checks['wrong_redaggered_Hcan_square_difference']>1e-3
    f=factor_twojet(t);p,_,_=native_pencil(f,.17)
    assert np.linalg.norm(p-p.conj().T)>1e-4


def test_noncommuting_field_and_cutoff_twojet_directional_derivative():
    t=theta();c=.8;omega=.17
    v=np.arange(23,dtype=float)/23-.4;v[:2]*=.1
    value,g,h=heat_trace_twojet(factor_twojet(t),omega,c)
    step=1e-5
    vp,gp,_=heat_trace_twojet(factor_twojet(t+step*v[:22]),omega,c+step*v[22])
    vm,gm,_=heat_trace_twojet(factor_twojet(t-step*v[:22]),omega,c-step*v[22])
    assert abs((vp-vm)/(2*step)-g@v)<2e-8
    assert np.max(abs((gp-gm)/(2*step)-h@v))<3e-7
    assert np.max(abs(h-h.T))<2e-10


def test_both_native_second_contacts_are_present():
    t=theta();f=factor_twojet(t);p,g,h=native_pencil(f,.2)
    direction=np.sin(np.arange(22))*.03;step=1e-5
    _,gp,_=native_pencil(factor_twojet(t+step*direction),.2)
    _,gm,_=native_pencil(factor_twojet(t-step*direction),.2)
    assert np.max(abs((gp-gm)/(2*step)-np.einsum('ijab,j->iab',h,direction)))<2e-8


def test_material_geometry_lapse_and_wall_pullback_on_saved_iterate():
    root=Path(__file__).resolve().parents[1]
    with np.load(root/'artifacts/muon_coupled_reference_replacement_20261019/run_2/coupled_replacement.npz') as z:
        x=z['provisional_iterate151'].copy();active=z['original_active52_indices84'].astype(int)
    v=np.cos(np.arange(151))*.003;v[150]=0.;step=2e-5
    a=lorentz_load(x,cutoff=1.,points_per_panel=8)
    p=lorentz_load(x+step*v,cutoff=1.,points_per_panel=8)
    m=lorentz_load(x-step*v,cutoff=1.,points_per_panel=8)
    assert abs((p['value']-m['value'])/(2*step)-a['gradient']@v)<2e-8
    assert np.max(abs((p['gradient']-m['gradient'])/(2*step)-a['hessian']@v))<3e-6
    assert np.max(abs(a['gradient'][62+active]))==0.
    assert np.max(abs(a['hessian'][62+active]))==0.
    assert a['ambient_lapse']!=a['induced_lapse']
    assert a['gradient'][150]==0.  # independent physical c/unit matching remains required.
