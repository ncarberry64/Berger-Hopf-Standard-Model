"""Signed common-normal reduction, moving port and frozen local adapter."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.joint_boundary_port_reduction import reduce_seven_port,moving_port_jet
import derive_n12_gate7_joint_port_reduction as s

OUT=s.BASE/'gate7_joint_port_20260927'


def col(v):return arb_mat([[v]]*7)
def zero(a):return all(v.contains(0) for v in a.entries())
def packet():
    ctx.prec=512
    return json.loads((OUT/'report.json').read_bytes()),s.load(OUT/'arrays.npz')


def test_shared_solve_preserves_signed_sector_cancellation():
    K=arb_mat([[2]]);F=arb_mat([[3]])
    result=reduce_seven_port(K,F,{'a':dict(p=col(100),n=col(40)),
                                'b':dict(p=col(-99),n=col(-39))})
    assert result['direct']==col(1) and result['internal']==col(1)
    assert result['reduced']==col(-0.5)
    assert zero(result['adjoint_replay'])


def test_stationarity_does_not_cancel_reaction_mixed_derivative():
    # Gamma(n,p)=n^2+3np+(5/2)p^2, Gamma_n=0 -> n=-3p/2.
    # Reaction g=Gamma_p=3n+5p; reduced dg/dp=1/2, not 5.
    result=reduce_seven_port(arb_mat([[2]]),arb_mat([[3]]),
                            {'reaction':dict(p=col(5),n=col(3))})
    assert result['reduced']==col(0.5)


def test_orientation_and_moving_port_terms_remain_explicit():
    I=arb_mat(np.eye(7,dtype=int).tolist());S=arb_mat(np.diag([-1]*5+[1]*2).tolist())
    reaction=col(3);jet=col(2)
    assert moving_port_jet(I,reaction,jet,[I])==col(5)
    assert moving_port_jet(S,reaction,jet,[S])==S*col(5)
    K=arb_mat([[2]]);F=arb_mat([[3]])
    a=reduce_seven_port(K,F,{'x':dict(p=jet,n=reaction)})
    b=reduce_seven_port(K,F,{'x':dict(p=S*jet,n=S*reaction)})
    assert b['reduced']==S*a['reduced']
    with pytest.raises(ValueError):moving_port_jet(I,reaction,jet,[])
    with pytest.raises(ValueError):reduce_seven_port(K,F,{'x':dict(p=jet)})


def test_historical_witness_is_not_promoted_to_physical_force():
    d,_=packet();h=d['historical_replay']
    assert h['validation_passed']
    assert h['stored']['role']=='DETERMINISTIC_LINEAR_ALGEBRA_CROSSCHECK_NOT_A_PHYSICAL_FORCE'
    assert h['stored']['natural_orthonormal_pullback_relative_residual']<5e-16
    assert h['replay']['natural_orthonormal_pullback_relative_residual']<1e-12
    records=d['historical_binding']
    core=records['BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE']
    assert all(x['status']=='MATCH' for x in core['inputs'])
    assert records['BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER']['exact_split']['fixed_C2_tangent']=='K_fixedC2={0}_C2_DIRECT_SUM_ker(J_E1)'


def test_local125_cancellation_and_adjoint_forward_agreement():
    d,a=packet()
    assert d['local_port_rank']==7
    assert d['local_port_rank_inverse_defect']['approximate_upper']<1
    assert zero(s.mat(a['local125_adjoint_forward_replay']))
    assert d['local125_adjoint_forward_replay']['approximate_upper']<8.915423761304125e-7
    assert all(v==0 for v in s.mat(a['local125_correction']).entries())
    assert d['local125_correction_uncertainty']['approximate_upper']==0
    assert not d['action_or_history_producers_run']
    assert not d['native_derivative_7x73_recomputed']


def test_rowwise_unknown_joint_corrections_are_not_zero_filled():
    d,_=packet()
    assert len(d['row_accounting'])==7
    for row in d['row_accounting']:
        assert row['local_native']=='ALREADY INCLUDED'
        assert row['descriptor_constraint_local_border']=='INTERNAL-CANCELLED'
        assert row['history_contact_correction_norm'] is None and row['complete_row'] is None
    assert d['complete_joint_7x73_rank'] is None
    assert not d['promoted_to_N12_FIXED_ENVIRONMENT_MATERIAL_RESPONSE_7x73']
    assert not d['Gate7_closed'] and not d['FULL_BHSM_COMPLETE']


def test_hashes_and_repeat():
    d,_=packet()
    assert s.digest(OUT/'arrays.npz')==d['arrays_SHA256']
    for p,h in d['source_SHA256'].items():assert s.digest(ROOT/p)==h
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    for name,item in receipt['files'].items():
        assert item['byte_identical'] and s.digest(OUT/name)==item['SHA256']
