"""New total-branch and heat-composition checks, not physical evaluations."""
from pathlib import Path
import sys
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from control_muon_support_loss_quotient import control_expressions
from bhsm.interface.muon_native_support_loss_cutoff import (
    quadratic_form_branch_jets,cutoff_from_total_contractions,lower_limit_coefficients,
)
from bhsm.interface.muon_native_induced_polarization import lower_limit_mixed


def evaluated_jets(expr,x,y):
    zero={x:0,y:0}
    return [np.array(z.subs(zero),float) for z in (expr,sp.diff(expr,x),sp.diff(expr,y),sp.diff(expr,x,y))]


def test_total_form_and_second_embedding_jets_against_independent_differentiation():
    x,y,_,p,R,I=control_expressions()
    pv,px,py,pxy=[z.reshape(-1) for z in evaluated_jets(p,x,y)]
    for K in (R,I):
        K0,Kx,Ky,Kxy=evaluated_jets(K,x,y)
        got=quadratic_form_branch_jets(K0,pv,K_x=Kx,K_y=Ky,K_xy=Kxy,psi_x=px,psi_y=py,psi_xy=pxy)
        exact=evaluated_jets((p.T*K*p)[0],x,y)
        assert max(abs(got[key]-float(value)) for key,value in zip(('value','x','y','xy'),exact))<2e-15
        omitted=quadratic_form_branch_jets(K0,pv,K_x=Kx,K_y=Ky,K_xy=Kxy,psi_x=px,psi_y=py,psi_xy=np.zeros(2))
        assert abs(got['xy']-omitted['xy'])>.3


def test_cutoff_consumes_the_total_branch_without_energy_eigenline_assumption():
    x,y,_,p,R,I=control_expressions()
    pv,px,py,pxy=[z.reshape(-1) for z in evaluated_jets(p,x,y)]
    results=[]
    for K in (R,I):
        K0,Kx,Ky,Kxy=evaluated_jets(K,x,y)
        results.append(quadratic_form_branch_jets(K0,pv,K_x=Kx,K_y=Ky,K_xy=Kxy,psi_x=px,psi_y=py,psi_xy=pxy))
    c=cutoff_from_total_contractions(*results)
    exact=(p.T*I*p)[0]/(p.T*R*p)[0]
    zero={x:0,y:0}
    assert abs(c['c_xy']-float(sp.diff(exact,x,y).subs(zero)))<2e-15
    R0=np.array(R.subs(zero),float);I0=np.array(I.subs(zero),float)
    lam=results[0]['value']/results[1]['value']
    assert np.linalg.norm((R0-lam*I0)@pv)>.1


def test_common_branch_normalization_motion_cancels_only_when_all_jets_retained():
    x,y,_,p,R,I=control_expressions()
    scale=1+x/7-y/11+x*y/13
    zero={x:0,y:0}
    for vector in (p,scale*p):
        pv,px,py,pxy=[z.reshape(-1) for z in evaluated_jets(vector,x,y)]
        jets=[]
        for K in (R,I):
            K0,Kx,Ky,Kxy=evaluated_jets(K,x,y)
            jets.append(quadratic_form_branch_jets(K0,pv,K_x=Kx,K_y=Ky,K_xy=Kxy,psi_x=px,psi_y=py,psi_xy=pxy))
        result=cutoff_from_total_contractions(*jets)
        target=(p.T*I*p)[0]/(p.T*R*p)[0]
        assert abs(result['c_xy']-float(sp.diff(target,x,y).subs(zero)))<2e-15


def test_adopted_quotient_is_consumed_into_existing_complete_length_identity():
    r,i=sp.symbols('r i',positive=True)
    rx,ry,rxy,ix,iy,ixy=sp.symbols('r_x r_y r_xy i_x i_y i_xy')
    T,Hp,Hx,Hy=sp.symbols('T H_P H_x H_y')
    c=i/r;cx=ix/r-i*rx/r**2;cy=iy/r-i*ry/r**2
    cxy=ixy/r-(ix*ry+iy*rx+i*rxy)/r**2+2*i*rx*ry/r**3
    coefficients=lower_limit_coefficients(r=r,i=i,r_x=rx,r_y=ry,r_xy=rxy,i_x=ix,i_y=iy,i_xy=ixy)
    composed=(coefficients['coefficient_T']*T+coefficients['coefficient_H_P']*Hp
              +coefficients['coefficient_H_x']*Hx+coefficients['coefficient_H_y']*Hy)
    assert sp.simplify(composed-lower_limit_mixed(c,cx,cy,cxy,T,Hp,Hx,Hy))==0
    assert sp.simplify(coefficients['coefficient_T']-(ixy/i-ix*iy/i**2-rxy/r+rx*ry/r**2)/2)==0


def test_numerical_branch_control_has_independent_finite_difference_scope():
    # Saved new control only; do not rerun its producer in this check.
    import json
    report=json.loads((ROOT/'artifacts/muon_native_support_loss_cutoff_20261007/run_1/branch_control.json').read_text())
    assert report['max_symbolic_difference']<2e-15
    assert all(row['absolute_error']<1e-7 for row in report['finite_differences'])
    assert report['total_event_motion_included_once'] and report['second_embedding_terms_retained']
    assert report['classification'].endswith('NO_PHYSICAL_SUPPORT_LOSS')


def test_physical_cutoff_and_native_heat_are_not_filled_with_control_values():
    import json
    result=json.loads((ROOT/'artifacts/muon_native_support_loss_cutoff_20261007/run_1/result.json').read_text())
    assert result['owner_definition_adopted']
    assert all(value is None for value in result['physical'].values())
    assert result['execution']['old_production_replays']==0
    assert result['execution']['physical_heat_applications']==0
    assert not result['formation_zero_used_as_support_loss']
    assert not result['canonical_stop_used_as_support_loss']
    assert result['next_operand']['name']=='interface-normal/bulk-field mixed response forcing'
    assert all(item['status']=='UNEVALUATED' for item in result['ownership'].values())
