from pathlib import Path
import json
import sys
import mpmath as mp
import pytest
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.heat_zeta_mixed_boundary_launch import (
    heat_divided_difference,heat_pair_7x73,element_mixed,zeta_element_mixed,
    reduce_mixed_reactions,implicit_objective_adjoint,reduce_implicit_mixed,OBJECT)


def agrees(ball, number):
    return ball.overlaps(arb(mp.nstr(number,95))+arb(0,arb('1e-94')))


def test_heat_divided_difference_handles_repeated_and_crossing_spectrum():
    ctx.prec=512
    x=arb(2)
    expected=-(-x).exp()*(1+x)/(2*x*x)
    assert (heat_divided_difference(x,x)-expected).contains(0)
    interval=arb(2)+arb(0,arb('0.01'))
    assert heat_divided_difference(interval,interval).contains(expected)
    assert heat_divided_difference(interval,interval)<0


def test_noncommuting_heat_pair_matches_actual_scalar_action_derivative():
    ctx.prec=512
    B=[arb_mat(2,2) for _ in range(7)];P=[arb_mat(2,2) for _ in range(73)]
    B[0]=arb_mat([[1,2],[2,-1]]);P[0]=arb_mat([[2,-1],[-1,3]])
    pair=heat_pair_7x73([arb(2),arb(3)],B,P)
    with mp.workdps(110):
        def action(b,p):
            a=2+b+2*p;d=3-b+3*p;off=2*b-p
            mid=(a+d)/2;gap=mp.sqrt((a-d)**2/4+off**2)
            return -(mp.e1(mid-gap)+mp.e1(mid+gap))/2
        truth=mp.diff(lambda b:mp.diff(lambda p:action(b,p),0),0)
        assert agrees(pair[0,0],truth)
    assert all(pair[a,j].is_zero() for a in range(7) for j in range(73) if (a,j)!=(0,0))


def test_internal_stationarity_does_not_remove_genuine_mixed_operator_term():
    ctx.prec=512
    # Algebraic counterexample, not a BHSM seed: P=2+b+p+c*b*p,
    # Gamma=f(P)+n^2/2, F=Gamma_n=n. All first jets agree for c=0,1.
    B=[arb_mat([[int(i==0)]]) for i in range(7)]
    P=[arb_mat([[int(j==0)]]) for j in range(73)]
    pair=heat_pair_7x73([arb(2)],B,P)
    q=(-arb(2)).exp()/4;contact=arb_mat(7,73);contact[0,0]=q
    common=dict(pair=pair,zeta_mixed=arb_mat(7,73),Gamma_bn=arb_mat(7,1),
                F_n=arb_mat([[1]]),F_p=arb_mat(1,73),moving_seed=arb_mat(7,73))
    first=reduce_mixed_reactions(mixed_operator_trace=arb_mat(7,73),**common)
    second=reduce_mixed_reactions(mixed_operator_trace=contact,**common)
    assert (second['reduced'][0,0]-first['reduced'][0,0]-q).contains(0)
    assert second['reduced'][0,0]-first['reduced'][0,0]>0
    with pytest.raises(ValueError,match=OBJECT):reduce_mixed_reactions(mixed_operator_trace=None,**common)


@pytest.mark.parametrize('channel,value,chi',[('scalar','3',1),('product_Dirac','1.5',1),('product_Dirac','1.5',-1)])
def test_owned_element_mixed_includes_duration_and_coefficient_cross_terms(channel,value,chi):
    ctx.prec=512
    inputs=dict(x='0.1',h='0.4',xb='0.2',xp='-0.3',xbp='0.07',hb='0.04',hp='-0.06',hbp='0.02')
    result=element_mixed(**inputs,channel=channel,value=value,chirality=chi)
    with mp.workdps(110):
        d={k:mp.mpf(v) for k,v in inputs.items()};val=mp.mpf(value)
        for i in range(2):
            for j in range(2):
                def element(b,p):
                    x=d['x']+d['xb']*b+d['xp']*p+d['xbp']*b*p
                    h=d['h']+d['hb']*b+d['hp']*p+d['hbp']*b*p
                    W=chi*val*mp.exp(-x) if channel=='product_Dirac' else 0
                    V=W*W if channel=='product_Dirac' else val*mp.exp(-2*x)
                    S=1 if i==j else -1;A=2 if i==j else 1
                    C=(-1 if i==0 else 1) if i==j else 0
                    return S/h+V*h*A/6+W*C
                truth=mp.diff(lambda b:mp.diff(lambda p:element(b,p),0),0)
                assert agrees(result['K_bp'][i,j],truth)
                assert result['M_bp'][i,j].contains(arb('0.02')*(2 if i==j else 1)/6)


def test_zeta_mixed_matches_integrated_action_with_moving_duration():
    ctx.prec=512
    args=dict(xl='0.1',xr='0.15',h='0.4',xb=['0.2','0.3'],xp=['-0.1','0.1'],
              xbp=['0.07','-0.03'],hb='0.04',hp='-0.06',hbp='0.02')
    result=zeta_element_mixed(**args)
    with mp.workdps(110):
        def action(b,p):
            x=mp.mpf('.1')+mp.mpf('.2')*b-mp.mpf('.1')*p+mp.mpf('.07')*b*p
            y=mp.mpf('.15')+mp.mpf('.3')*b+mp.mpf('.1')*p-mp.mpf('.03')*b*p
            h=mp.mpf('.4')+mp.mpf('.04')*b-mp.mpf('.06')*p+mp.mpf('.02')*b*p
            return -mp.mpf(59)/30*h*mp.exp(-x)*(-mp.expm1(-(y-x)))/(y-x)
        truth=mp.diff(lambda b:mp.diff(lambda p:action(b,p),0),0)
        assert agrees(result,truth)


def test_history_sector_needs_general_objective_adjoint():
    ctx.prec=512
    # F=n-b*p and Gamma_history=n at zero. Gamma_red=b*p. The stationary
    # shortcut applied to this nonstationary sector would incorrectly give 0.
    K=arb_mat([[1]]);eta,replay=implicit_objective_adjoint(K,arb_mat([[1]]))
    assert eta[0,0]==1 and replay[0,0].is_zero()
    Lbp=arb_mat(7,73);Lbp[0,0]=1  # -eta*F_bp
    result=reduce_implicit_mixed(L_bp=Lbp,L_bn=arb_mat(7,1),L_np=arb_mat(1,73),
        L_nn=arb_mat(1,1),F_n=K,F_b=arb_mat(1,7),F_p=arb_mat(1,73))
    assert result['reduced'][0,0]==1


def test_general_adjoint_retains_all_normal_cross_terms():
    ctx.prec=512
    # Gamma=.5*n^2+b*n+3*b*p, F=n-b*p, evaluated at b=p=n=1.
    K=arb_mat([[1]]);Lbp=arb_mat(7,73);Lbp[0,0]=5
    Lbn=arb_mat(7,1);Lbn[0,0]=1;Fb=arb_mat(1,7);Fp=arb_mat(1,73)
    Fb[0,0]=-1;Fp[0,0]=-1
    result=reduce_implicit_mixed(L_bp=Lbp,L_bn=Lbn,L_np=arb_mat(1,73),
        L_nn=arb_mat([[1]]),F_n=K,F_b=Fb,F_p=Fp)
    assert result['reduced'][0,0]==7
    assert all(v.is_zero() for v in result['adjoint_replay'].entries()+result['boundary_replay'].entries())


def test_moving_seed_conventions_are_explicit():
    zeros=arb_mat(7,73);seed=arb_mat(7,73);seed[0,0]=2
    result=reduce_mixed_reactions(pair=zeros,mixed_operator_trace=zeros,zeta_mixed=zeros,
        Gamma_bn=arb_mat(7,1),F_n=arb_mat([[1]]),F_p=arb_mat(1,73),moving_seed=seed)
    assert result['ordinary_reaction_derivative'][0,0]==2
    assert result['requested_minus_seed_convention'][0,0]==-2


def test_current_derivation_packet_preserves_scope_and_frozen_inputs():
    sys.path.insert(0,str(ROOT/'scripts'))
    from checkpoint_n12_gate7_66d_tangent_binding import digest
    out=ROOT/'artifacts/flagship_integration/gate7_mixed_boundary_launch_20260927'
    report=json.loads((out/'report.json').read_bytes())
    assert report['object']==OBJECT and not report['physical_7x73_materialized']
    assert report['R_history_7x73'] is None and report['R_reset_total_7x73'] is None
    assert report['coefficient_partial_is_not_boundary_seed']
    for flag in ('prefix_rebuilt','historical_actions_run','generic_second_operator_jet_computed',
                 'arbitrary_seeds_used_for_physical_data','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert not report[flag]
    for p,h in report['source_SHA256'].items():assert digest(ROOT/p)==h
    receipt=json.loads((out/'reproduction.json').read_bytes())
    for name,entry in receipt['files'].items():
        assert entry['byte_identical'] and digest(out/name)==entry['SHA256']
