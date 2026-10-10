"""New owner/perturbation checks; old muon production/checks are frozen."""
from pathlib import Path
import json
import sys
import numpy as np
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_native_impedance_energy_response import generalized_simple_mode_jets,moving_rayleigh_first
from control_muon_impedance_eigenbranch import control_data
OUT=ROOT/'artifacts/muon_native_impedance_energy_response_20261006/run_1'


def read(name):return json.loads((OUT/name).read_text())


def test_actual_owner_supersession_has_no_cutoff_scalar_identification():
    r=read('owner_reconciliation.json');c=read('owner_chronology.json')
    assert r['actual_formation_definition'].endswith('<psi,(gamma_s J_Sigma+H_impedance)psi>')
    assert 'one-mode common-charge reduction' in r['actual_historical_relation']
    assert r['scalar_holding_hypothesis_superseded_by_RHO_B2']
    assert not r['AE4_inverse_energy_amended_by_mechanics']
    assert not r['selected_event_equivalence_supplied']
    assert not r['common_charge_energy_pairing_supplied']
    assert any('synthetic' in x for x in r['interface_scalar_exclusion'])
    assert c['AE4_owner'].startswith('999be702') and c['mechanics'].startswith('c4eeb2d5')


def test_one_mode_total_resistance_threshold_and_bulk_residual():
    r=read('exact_reduction_identities.json')
    assert r['total_resistance_threshold_identity']=='0'
    assert r['bulk_only_threshold_residual']=='-S/M'
    Z,S,D,M=sp.symbols('Z S D M',nonzero=True)
    # Same normalization cancels in the quotient, but not in the dimensional
    # resistance scale. Neither M nor S may be chosen away by convenience.
    assert sp.simplify((D/M)/((Z+S)/M)-D/(Z+S))==0
    assert sp.simplify(Z/M-(Z+S)/M)==-S/M


def test_formation_line_motion_is_not_bare_energy_hellmann_feynman():
    r=read('exact_reduction_identities.json')['formation_vs_energy']
    assert r['formation_equation'] and r['line_normalized']
    assert r['energy_eigenline_residual_squared_at_zero']==1
    assert r['bare_R_x']==0 and r['E_x']==-2 and r['E_xy']==2
    R=np.array([[2.,1.],[1.,3.]]);M=np.eye(2);psi=np.array([1.,0.]);px=np.array([0.,-1.])
    E,Ex,bare,motion=moving_rayleigh_first(R,M,psi,px,np.zeros((2,2)),np.zeros((2,2)))
    assert E==2 and Ex==-2 and bare==0 and motion==-2


def test_generalized_energy_jets_against_actual_control_perturbations():
    r=read('arithmetic_eigenbranch_control.json')
    assert r['classification']=='ARITHMETIC_CONTROL_ONLY__NO_PHYSICAL_ENERGY'
    assert not r['explicit_inverse_formed'] and not r['selected_physical_mode']
    assert max(r['checks'].values())<2e-15
    assert all(p['x_error']<1e-9 and p['y_error']<1e-9 and p['mixed_error']<1e-8 for p in r['finite_differences'])
    assert all(p['min_branch_overlap']>.9999 for p in r['finite_differences'])
    assert all(p['max_M_normalization_residual']<2e-15 for p in r['finite_differences'])
    assert r['M_x_norm']>0 and r['M_y_norm']>0 and r['M_xy_norm']>0
    assert r['moving_M_changes_mixed']>.002


def test_independent_second_variation_and_mixed_normalization():
    H,M,p,E,Hx,Hy,Hxy,Mx,My,Mxy=control_data()
    with np.load(OUT/'control_reduced_actions.npz') as z:
        px=z['psi_x'];py=z['psi_y'];Ex=z['E_x'];Ey=z['E_y'];Exy=z['E_xy']
    A=H-E*M;Tx=Hx-E*Mx;Ty=Hy-E*My;Bxy=Hxy-E*Mxy-Ex*My-Ey*Mx
    rhs=-(Tx-Ex*M)@py-(Ty-Ey*M)@px-Bxy@p
    remainder=(np.vdot(px,M@py)+np.vdot(py,M@px)+
        np.vdot(px,My@p)+np.vdot(p,My@px)+
        np.vdot(py,Mx@p)+np.vdot(p,Mx@py)+np.vdot(p,Mxy@p))
    border=np.block([[A,(M@p)[:,None]],[(p@M)[None,:],np.zeros((1,1))]])
    solved=np.linalg.solve(border,np.r_[rhs,-remainder/2])
    pxy=solved[:3];independent=-solved[3]
    assert abs(independent-Exy)<1e-16
    assert abs(2*np.vdot(p,M@pxy)+remainder)<1e-16
    assert np.linalg.norm(A@pxy-Exy*M@p+(Tx-Ex*M)@py+(Ty-Ey*M)@px+Bxy@p)<1e-16


def test_fixed_M_familiar_reduced_resolvent_formula():
    _,_,_,_,Hx,Hy,Hxy,_,_,_=control_data()
    H=np.diag([2.,5.,9.]);M=np.eye(3);p=np.array([1.,0,0]);zero=np.zeros((3,3))
    r=generalized_simple_mode_jets(H,M,p,2,Hx,Hy,Hxy,zero,zero,zero)
    # Exact explicit diagonal reduced action in this CONTROL, not an inverse
    # or model of any retained BHSM operator.
    red=np.diag([0.,1/3,1/7])
    expected=np.vdot(p,Hxy@p)-np.vdot(Hx@p,red@Hy@p)-np.vdot(Hy@p,red@Hx@p)
    assert abs(expected-r['E_xy'])<1e-16


def test_crossing_motion_chain_rule_counts_mixed_surface_once():
    x,y,t=sp.symbols('x y t');e,a,b,c,d,f,g,h=sp.symbols('e a b c d f g h')
    F=t-(x+y)**2;tx=-sp.diff(F,x)/sp.diff(F,t);ty=-sp.diff(F,y)/sp.diff(F,t)
    tx0=tx.subs({x:0,y:0,t:0});ty0=ty.subs({x:0,y:0,t:0})
    txy=-(sp.diff(F,x,y)+sp.diff(F,t,x)*ty0+sp.diff(F,t,y)*tx0+sp.diff(F,t,t)*tx0*ty0)/sp.diff(F,t)
    assert txy==2
    energy=e+a*t+b*x+c*y+d*x*y+f*t*x+g*t*y+h*t*t/2
    total=sp.diff(energy.subs(t,(x+y)**2),x,y).subs({x:0,y:0})
    assert sp.simplify(total-d-a*txy)==0


def test_no_physical_scalar_or_cutoff_installed_and_frozen_work_not_replayed():
    r=read('result.json')
    assert all(value is None for value in r['physical'].values())
    assert not r['synthetic_rho_hold_inserted'] and not r['new_scalar_constitutive_law_inserted']
    assert not r['native_heat_default_length_used'] and not r['physical_eigenvalue_or_frequency_chosen']
    assert r['execution']['old_producers_replayed']==0 and r['execution']['old_targeted_checks_rerun']==0
    assert r['execution']['physical_eigenbranches_evaluated']==0
    assert not r['Gate7_invoked'] and not r['inherited_domains_changed']
