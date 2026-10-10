"""Intrinsic metric identities and retained-value applications.

Synthetic metric/profile examples are CONTROL_ONLY.  The retained tests
apply existing geometry; none selects an intrinsic Higgs or formation mode.
"""
from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
import sys

import numpy as np
import pytest
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_intrinsic_m4_normal_pullback import (
    homogeneous_kinetic_density, intrinsic_m4_weight_jet,
    metric_normal_two_jet, retained_intrinsic_m4_application,
)
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0


@pytest.fixture(scope='module')
def retained():
    return retained_intrinsic_m4_application(ROOT)


@pytest.mark.parametrize('side',['outgoing_C2','incoming_C1_E1'])
def test_retained_intrinsic_measure_and_first_metric_variation(side):
    result=retained_intrinsic_m4_application(ROOT,side)
    g=result['geometry']; data=result['weights']; ns,nr=data['source_indices']
    r,N,C=(g[key] for key in ('R4','N','C'))
    a=g['chi_first_log']['R4']/C
    expected={'wT':(r**3/N,3*a),'wS':(N*r,a),'wV':(N*r**3,3*a)}
    for name,(value,ratio) in expected.items():
        jet=data[name]
        assert jet.value==pytest.approx(value,rel=2e-15)
        assert jet.gradient[ns]/jet.value==pytest.approx(ratio,abs=4e-15)
        assert jet.gradient[nr]==pytest.approx(0.,abs=2e-15)
    assert data['potential_weight'].value!=pytest.approx(N*g['A']**3*g['B']**3)
    assert data['induced_lapse'].value==pytest.approx(N,rel=2e-15)
    metric=result['normal_metric']
    assert metric['metric_first'][0,0]==0.
    np.testing.assert_allclose(metric['metric_first'][1:,1:],-2*r*r*a*np.eye(3),rtol=3e-15)
    assert result['full_stationary_base'] is False
    assert result['intrinsic_H_selected'] is False
    assert metric['intrinsic_H_normal_derivative'] is None


def test_actual_outgoing_weights_are_applied_not_symbolic_only(retained):
    data=retained['weights']; ns,nr=data['source_indices']
    actual={
        'wT':(1.4055828045268468,.02911012209585093,29.50367837437703),
        'wS':(.6970926057096961,.004812345645039621,-18.661512408616424),
        'wV':(.6900235796917099,.01429063488052732,-20.46638894956415),
    }
    for name,(value,first,second) in actual.items():
        jet=data[name]
        assert jet.value==pytest.approx(value,rel=3e-15)
        assert jet.gradient[ns]==pytest.approx(first,abs=5e-15)
        assert jet.hessian[ns,ns]==pytest.approx(second,rel=3e-15)
    assert (ns,nr)==(98,99)
    assert data['coordinate_order']==('q','qdot','lapse_shift','s','sdot')


def test_second_weights_keep_shift_graph_speed_and_profile_contacts(retained):
    g=retained['geometry']; data=retained['weights']; ns,nr=data['source_indices']
    C,N,Hc=(g[key] for key in ('C','N','Hc'))
    a=g['chi_first_log']['R4']/C
    r2=g['chi_second_log']['R4']/C**2
    n2=g['chi_second_log']['N']/C**2
    # Direct differentiation of l=N sqrt(1-U^2), U_s=-Hc, U_sdot=1/N.
    expected={
        'wT':(3*r2-n2+9*a*a+Hc*Hc,-Hc/N,1/N**2),
        'wS':(n2+r2+a*a-Hc*Hc,Hc/N,-1/N**2),
        'wV':(n2+3*r2+9*a*a-Hc*Hc,Hc/N,-1/N**2),
    }
    for name,(ss,srate,raterate) in expected.items():
        jet=data[name]
        assert jet.hessian[ns,ns]/jet.value==pytest.approx(ss,rel=3e-15)
        assert jet.hessian[ns,nr]/jet.value==pytest.approx(srate,rel=3e-15)
        assert jet.hessian[nr,nr]/jet.value==pytest.approx(raterate,rel=3e-15)
    assert Hc!=(g['coordinate_time_log_rates']['C']/N)
    dense=retained['normal_metric']; tensor=homogeneous_kinetic_density(data)
    for i in range(4):
        assert tensor[i,i].value==pytest.approx(dense['kinetic_density'][i,i],rel=2e-15)
        assert tensor[i,i].gradient[ns]==pytest.approx(dense['kinetic_density_first'][i,i],abs=5e-15)
        assert tensor[i,i].hessian[ns,ns]==pytest.approx(dense['kinetic_density_second'][i,i],rel=3e-15)
    assert data['wV'].hessian[ns,ns]==pytest.approx(dense['volume_density_second'],rel=3e-15)


def test_all_same_geometry_columns_and_one_lapse_are_retained(retained):
    data=retained['weights']; g=retained['geometry']; nq=data['qdim']; nm=data['mdim']
    assert (nq,nm,len(data['wT'].gradient))==(37,24,100)
    rgrad=np.zeros(37); rgrad[0]=1
    rgrad[1:13]=(-1.)**np.arange(1,13)
    rgrad[25:37]=(1-2*g['lambda_geom'])*(-1.)**np.arange(12)
    ngrad=np.zeros(24); ngrad[:12]=(-1.)**np.arange(1,13)
    for name,qfactor,nfactor in [('wT',3,-1),('wS',1,1),('wV',3,1)]:
        jet=data[name]
        np.testing.assert_allclose(jet.gradient[:nq]/jet.value,qfactor*rgrad,atol=2e-15,rtol=2e-15)
        np.testing.assert_allclose(jet.gradient[nq:2*nq],0.,atol=2e-15)
        np.testing.assert_allclose(jet.gradient[2*nq:2*nq+nm]/jet.value,nfactor*ngrad,atol=2e-15,rtol=2e-15)
        assert jet.hessian.shape==(100,100)
        np.testing.assert_allclose(jet.hessian,jet.hessian.T,atol=2e-13,rtol=0.)


def _independent_scalar_weights(order, vector, trial):
    """CONTROL_ONLY direct scalar metric, without production Jet/field helpers."""
    nq=1+3*order
    q=vector[:nq]; vel=vector[nq:2*nq]; m=vector[2*nq:2*nq+2*order]
    s,rate=vector[-2:]; k=np.arange(1,order+1); j=np.arange(order)
    sk=(-1.)**k; sj=(-1.)**j
    radius=RADIUS0*math.exp(q[0])
    Cstar=radius*math.exp(q[1:1+order]@sk+q[1+order:1+2*order]@sj)
    lc=vel[0]+vel[1:1+order]@sk+vel[1+order:1+2*order]@sj
    chi=math.pi/4+trial*s/Cstar
    window=math.sin(2*chi)**2
    u=q[1:1+order]@np.cos(4*k*chi)
    w=window*(q[1+order:1+2*order]@np.cos(4*j*chi))
    b=window*(q[1+2*order:1+3*order]@np.cos(4*j*chi))
    C=radius*math.exp(u+w)
    A=radius*math.exp(u+b)*math.cos(chi)
    B=radius*math.exp(u-b)*math.sin(chi)
    N=math.exp(m[:order]@np.cos(4*k*chi))
    beta=math.sin(4*chi)*(m[order:]@np.cos(4*j*chi))
    wallrate=trial/Cstar*(rate-lc*s)
    U=C*(wallrate+beta)/N
    lapse=N*math.sqrt(1-U*U)
    r=A*B/math.sqrt(A*A+B*B)
    return np.array([r**3/lapse,lapse*r,lapse*r**3])


def test_full_off_base_jet_direction_against_independent_induced_metric():
    # CONTROL_ONLY finite chart checks all q/qdot/m/source/rate cross terms.
    order=2; nq=7
    q=np.array([.03,.01,-.02,.02,.01,-.01,.005])
    vel=np.array([.04,.02,-.03,.01,.02,.01,-.01])
    m=np.array([.01,-.015,.03,-.02])
    trial=.7; s=.03; rate=.04
    data=intrinsic_m4_weight_jet(order,q,vel,m,source_value=s,source_rate=rate,trial_normal=trial)
    vector=np.concatenate((q,vel,m,[s,rate]))
    direction=np.random.default_rng(819).normal(size=len(vector))*.2
    eps=1e-3
    lo2=_independent_scalar_weights(order,vector-2*eps*direction,trial)
    lo=_independent_scalar_weights(order,vector-eps*direction,trial)
    mid=_independent_scalar_weights(order,vector,trial)
    hi=_independent_scalar_weights(order,vector+eps*direction,trial)
    hi2=_independent_scalar_weights(order,vector+2*eps*direction,trial)
    for index,name in enumerate(('wT','wS','wV')):
        jet=data[name]
        assert jet.value==pytest.approx(mid[index],rel=2e-15)
        first=(-hi2[index]+8*hi[index]-8*lo[index]+lo2[index])/(12*eps)
        second=(-hi2[index]+16*hi[index]-30*mid[index]+16*lo[index]-lo2[index])/(12*eps**2)
        assert direction@jet.gradient==pytest.approx(first,abs=2e-9)
        assert direction@jet.hessian@direction==pytest.approx(second,abs=2e-7)
        assert np.linalg.norm(jet.gradient[nq:2*nq])>0.


def _control_geometry():
    """CONTROL_ONLY radial profiles and inherited time/shift coefficients."""
    return dict(C=5.,N=2.,R4=3.,
                chi_first_log=dict(N=.2,R4=-.3),
                chi_second_log=dict(N=.4,R4=.7),
                shift=dict(beta=0.,beta_chi=.8),
                coordinate_time_log_rates=dict(C=.6))


def test_dense_graph_density_two_jet_by_exact_symbolic_inverse_and_measure():
    # CONTROL_ONLY: nonzero speed, gradient, lapse derivative and z_ss contact.
    g=_control_geometry()
    result=metric_normal_two_jet(g,normal_value=2.,normal_coordinate_time_derivative=1.,
                                 normal_unit_s3_gradient=(3.,0.,0.),embedding_coordinate_second=.1)
    s=sp.Symbol('s',real=True)
    z1=sp.Rational(2,5); z2=sp.Rational(1,10)
    nr1=sp.Rational(1,5)*z1
    nr2=sp.Rational(2,5)*z1**2+sp.Rational(1,5)*z2
    rr1=-sp.Rational(3,10)*z1
    rr2=sp.Rational(7,10)*z1**2-sp.Rational(3,10)*z2
    # Polynomial N(s), r(s) have the same prescribed log two-jets.
    N=2*(1+nr1*s+(nr2+nr1**2)*s**2/2)
    r=3*(1+rr1*s+(rr2+rr1**2)*s**2/2)
    u=sp.Rational(7,25)*s; p=sp.Rational(3,5)*s
    h=sp.diag(N*N,-r*r,-r*r,-r*r)
    cov=sp.Matrix([u,p,0,0]); h=h-25*cov*cov.T
    volume=sp.sqrt(-h.det()); density=volume*h.inv()
    for derivative,key in [(0,'metric'),(1,'metric_first'),(2,'metric_second')]:
        expected=np.array(h.diff(s,derivative).subs(s,0),dtype=float)
        np.testing.assert_allclose(result[key],expected,atol=1e-14,rtol=1e-14)
    for derivative,key in [(0,'volume_density'),(1,'volume_density_first'),(2,'volume_density_second')]:
        assert result[key]==pytest.approx(float(sp.diff(volume,s,derivative).subs(s,0)),rel=2e-14)
    for derivative,key in [(0,'kinetic_density'),(1,'kinetic_density_first'),(2,'kinetic_density_second')]:
        expected=np.array(density.diff(s,derivative).subs(s,0),dtype=float)
        np.testing.assert_allclose(result[key],expected,atol=2e-13,rtol=2e-14)
    assert result['kinetic_density_second'][0,1]!=0.


def test_angular_graph_contacts_include_rank_one_and_time_angular_terms(retained):
    g=retained['geometry']; r=g['R4']; N=g['N']; gradient=np.array([.3,-.2,.4]); rate=.7
    d=metric_normal_two_jet(g,normal_value=0.,normal_coordinate_time_derivative=rate,
                           normal_unit_s3_gradient=gradient)
    np.testing.assert_allclose(d['metric_first'],0.,atol=0.)
    np.testing.assert_allclose(d['metric_second'][0,1:],-2*rate*gradient,atol=2e-16)
    np.testing.assert_allclose(d['metric_second'][1:,1:],-2*np.outer(gradient,gradient),atol=2e-16)
    assert d['volume_density_second']==pytest.approx(N*r**3*(gradient@gradient/r**2-rate**2/N**2),rel=3e-15)
    np.testing.assert_allclose(d['kinetic_density_second'][0,1:],-2*r/N*rate*gradient,rtol=3e-15)
    expected=-N*r*(gradient@gradient/r**2-rate**2/N**2)*np.eye(3)+2*N/r*np.outer(gradient,gradient)
    np.testing.assert_allclose(d['kinetic_density_second'][1:,1:],expected,rtol=3e-15,atol=1e-16)


def test_dense_density_transforms_as_a_tensor_density_under_unit_metric_chart(retained):
    # CONTROL_ONLY chart transformation, not a fitted angular field/frame.
    g=retained['geometry']; grad=np.array([.1,.3,-.2])
    L=np.array([[2.,.25,0.],[0.,1.5,0.],[0.,0.,.5]])
    first=metric_normal_two_jet(g,normal_value=.8,normal_coordinate_time_derivative=.3,normal_unit_s3_gradient=grad)
    second=metric_normal_two_jet(g,normal_value=.8,normal_coordinate_time_derivative=.3,
                               normal_unit_s3_gradient=L.T@grad,unit_s3_metric=L.T@L)
    P=np.eye(4); P[1:,1:]=L; Pinv=np.linalg.inv(P)
    for name in ('metric','metric_first','metric_second'):
        np.testing.assert_allclose(second[name],P.T@first[name]@P,atol=2e-14,rtol=3e-15)
    for name in ('kinetic_density','kinetic_density_first','kinetic_density_second'):
        np.testing.assert_allclose(second[name],np.linalg.det(L)*Pinv@first[name]@Pinv.T,atol=2e-14,rtol=3e-15)


def test_mechanical_connection_pullback_preserves_both_sections_and_no_representation(retained):
    g=retained['geometry']; data=retained['weights']; ns,nr=data['source_indices']
    lam=g['lambda_geom']; C=g['C']; v2=g['chi_second_log']['A']-g['chi_second_log']['B']
    first=-4*lam*(1-lam)/C
    second=(2*lam*(1-lam)*v2+16*lam*(1-lam)*(1-2*lam))/C**2
    jet=data['mechanical_connection_lambda']
    assert jet.value==pytest.approx(lam,rel=2e-15)
    assert jet.gradient[ns]==pytest.approx(first,rel=2e-15)
    assert jet.hessian[ns,ns]==pytest.approx(second,rel=2e-14)
    assert jet.gradient[nr]==0.
    sumjet=jet+data['mechanical_connection_one_minus_lambda']
    assert sumjet.value==1.
    np.testing.assert_array_equal(sumjet.gradient,np.zeros(100))
    np.testing.assert_array_equal(sumjet.hessian,np.zeros((100,100)))
    difference=data['section0_orthonormal_connection_coefficient']-data['section1_orthonormal_connection_coefficient']
    inverse=data['R4'].reciprocal()
    assert difference.value==pytest.approx(inverse.value,rel=2e-15)
    np.testing.assert_allclose(difference.hessian,inverse.hessian,atol=2e-14,rtol=3e-15)
    assert data['associated_bundle_representation'] is None
    assert data['full_gauge_connection_selected'] is False


@pytest.mark.parametrize('metric',[np.diag([1.,1.,-1.]),np.array([[1.,1.,0.],[0.,1.,0.],[0.,0.,1.]]),np.full((3,3),np.nan)])
def test_dense_metric_rejects_invalid_unit_metric(metric):
    with pytest.raises(ValueError,match='positive unit S3 metric'):
        metric_normal_two_jet(_control_geometry(),unit_s3_metric=metric)


def test_dense_metric_rejects_nonfinite_or_incompatible_base():
    g=_control_geometry()
    with pytest.raises(ValueError,match='finite normal'):
        metric_normal_two_jet(g,normal_unit_s3_gradient=(0.,float('nan'),0.))
    bad=deepcopy(g); bad['shift']['beta']=.1
    with pytest.raises(ValueError,match='zero-shift wall'):
        metric_normal_two_jet(bad)
    bad=deepcopy(g); bad['R4']=-1.
    with pytest.raises(ValueError,match='positive finite'):
        metric_normal_two_jet(bad)


@pytest.mark.parametrize('order',[0,True,1.5])
def test_weight_jet_rejects_invalid_order(order):
    with pytest.raises(ValueError,match='positive retained Galerkin order'):
        intrinsic_m4_weight_jet(order,np.zeros(4),np.zeros(4),np.zeros(2))


def test_weight_jet_rejects_nonfinite_spacelike_and_outside_chart_inputs():
    q=np.zeros(4); vel=np.zeros(4); m=np.zeros(2)
    with pytest.raises(ValueError,match='finite source'):
        intrinsic_m4_weight_jet(1,q,vel,m,trial_normal=float('nan'))
    with pytest.raises(ValueError,match='dimensions'):
        intrinsic_m4_weight_jet(1,q[:-1],vel,m)
    with pytest.raises(ValueError,match='timelike'):
        intrinsic_m4_weight_jet(1,q,vel,m,source_rate=2.)
    with pytest.raises(ValueError,match='outside retained local'):
        intrinsic_m4_weight_jet(1,q,vel,m,source_value=RADIUS0/4)
