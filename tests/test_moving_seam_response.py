"""Exact algebra controls, explicitly not physical N12 environment fixtures."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from flint import arb_mat,ctx
import pytest
from bhsm.interface.moving_seam_response import (
    pullback_first_jet,cotangent_first_jet,on_shell_reaction_jet,
    stack_seven,solve_seven_balance,compose_weak_feedback)


def eye(n):
    return arb_mat([[int(i==j) for j in range(n)] for i in range(n)])


def zero(a):return all(v.contains(0) for v in a.entries())


def test_fixed_field_has_nonzero_moving_trace():
    # Fixed field f(x)=x^2 sampled at x=2+3p; density J=1+5p.
    value,jet=pullback_first_jet(arb_mat([[4]]),arb_mat([[12]]),arb_mat([[1]]),[arb_mat([[5]])])
    assert value==arb_mat([[4]])
    assert jet==arb_mat([[32]])


def test_momentum_jet_preserves_differentiated_canonical_pairing():
    ctx.prec=256
    L=arb_mat([[2,1],[0,3]]);dL=arb_mat([[1,-2],[3,1]])
    We=arb_mat([[2,0],[0,5]]);Ws=arb_mat([[3,1],[1,2]])
    dWe=arb_mat([[1,2],[2,3]]);dWs=arb_mat([[2,1],[1,4]])
    m=arb_mat([[2],[7]]);dm=arb_mat([[3],[-1]])
    p,dp=cotangent_first_jet(m,dm,L,[dL],We,[dWe],Ws,[dWs])
    # d(L^T Ws p)=d(We m), independent canonical work identity.
    assert zero(dL.transpose()*Ws*p+L.transpose()*dWs*p+L.transpose()*Ws*dp-dWe*m-We*dm)


def test_on_shell_elimination_matches_explicit_stationary_action():
    # S=x^2+x*q+3*x*s+5*q^2/2+7*q*s. x=-(q+3s)/2.
    # Therefore D(S_q)=9dq/2+11ds/2.
    a=lambda x:arb_mat([[x]])
    jet,dx=on_shell_reaction_jet(a(2),a(1),a(3),a(1),a(5),a(7),a(4),a(2))
    assert jet==a(29) and dx==a(-5)


def test_full_boundary_balance_changes_tangent_and_retains_env_q():
    ctx.prec=256;I=eye(7);cp=arb_mat(7,66);ep=arb_mat(7,66);ep[0,0]=6
    Tp=arb_mat(73,66);Tq=arb_mat(73,7)
    for i in range(66):Tp[i,i]=1
    for i in range(7):Tq[66+i,i]=1
    x=solve_seven_balance(cp,I,ep,2*I,I,Tp,Tq)
    assert zero(x['replay']);assert x['reactions'][0,0]==-2
    assert x['tangent'][66,0]==-2 # Freezing the environment would miss this.
    assert not x['tangent'][66,0].contains(0)
    # Independence is retained by the identity intrinsic rows.
    assert zero(x['tangent'].transpose()*x['tangent']-(eye(66)+x['reactions'].transpose()*x['reactions']))


def test_singular_coupled_reaction_is_not_hidden_by_child_inverse():
    I=eye(7)
    with pytest.raises(ZeroDivisionError):
        solve_seven_balance(arb_mat(7,1),I,arb_mat(7,1),-I,I,arb_mat(8,1),arb_mat(8,7))


def test_row_ownership_and_missing_shape_jet_rejected():
    with pytest.raises(ValueError):stack_seven(arb_mat(2,66),arb_mat(3,66),arb_mat(2,66))
    with pytest.raises(ValueError):pullback_first_jet(arb_mat([[1]]),arb_mat([[0]]),eye(1),[])
    assert stack_seven(arb_mat(3,66),arb_mat(2,66),arb_mat(2,66)).nrows()==7


def test_frozen_weak_owner_material_response_is_retained():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
    from certify_n12_gate7_coupled_center_neighborhood import load
    import solve_n12_gate7_fiber_constrained_center as c
    ctx.prec=512
    a=load(c.BASE/'gate7_comoving_interface_20260927/feedback13/arrays.npz')
    v=c.matrix(a['rate_acceleration_affine'])
    # Zero state motion isolates a conormal material jet, not delta e.
    # Basis columns here are algebra checks, not physical N12 seam directions.
    result=compose_weak_feedback(v,arb_mat(61,98),arb_mat(98,2),eye(2))
    expected=arb_mat([[v[i,1],v[i,2]] for i in range(61)])
    assert zero(result-expected)
    assert any(not x.contains(0) for x in result.entries())


def test_compilation_reproduces_without_claiming_a_physical_tangent():
    import json,hashlib
    root=Path(__file__).resolve().parents[1]
    out=root/'artifacts/flagship_integration/gate7_environment_seam_20260927'
    r=json.loads((out/'report.json').read_bytes())
    h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
    assert h(out/'arrays.npz')==r['arrays_SHA256']
    for p,s in r['source_SHA256'].items():assert h(Path(p))==s
    assert r['coupling_rank_certified']==2
    assert r['coupling_Gram_inverse_defect']['approximate_upper']<1
    assert r['response_required_shape']==[7,73]
    assert not r['physical_environment_response_constructed']
    assert not r['physical_tangent_comparison_completed']
    assert not r['Gate7_closed'] and not r['FULL_BHSM_COMPLETE']
    receipt=json.loads((out/'reproduction.json').read_bytes())
    for name,item in receipt['files'].items():
        assert item['byte_identical'] and h(out/name)==item['SHA256']
