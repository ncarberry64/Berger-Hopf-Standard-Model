"""Original full child x106/v106/y40 action at a complex terminal germ.

The inherited profile cancels the child's mechanical lambda in the TOTAL
connection, not in the subtracted mechanical Maxwell energy or cap action.
All child metric/cap/baseline/normal derivatives and analytic field contacts
therefore remain. This is an analytic action, not a Hilbert complex square.
"""
from __future__ import annotations
import numpy as np
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_holomorphic_normal_geometry import holomorphic_geometry_rows,holomorphic_cap_and_weights
from .muon_nonlinear_n0_field_action import analytic_constant_maxwell_jet,analytic_intrinsic_n0_jet
from .muon_nonlinear_chronological_n0_action import analytic_constant_maxwell_batch
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP


def _affine_geometry(raw,time):
    x=np.asarray(raw,complex).copy();x[:37]+=time*x[37:74];x[98]+=time*x[99];return x


def _parameters(raw,rho):
    a=holomorphic_geometry_rows(raw[:100],rho,differentiate=False,connection_only=True)
    return np.array([[row[k].value for k in('connection_lambda','lambda_tau','lambda_rho')]for row in a['rows']])


def holomorphic_inherited_child_action(raw_child,coordinate_time,initial_pair,reference_pair,representation,
                                       *,nu_squared_action,surface_gamma=None):
    """Full original raw268 two-jet, with its explicit inherited clock.

    Parent/reference are the SAME recorded affine germs evaluated at the
    actual complex coordinate time. No real-phase momentum or terminal
    load is inserted. Pi=L_v is returned from THIS full action.
    """
    raw=np.asarray(raw_child,complex);rep=representation;ng=rep['gauge_count'];hs=100+2*ng;nr=hs+8
    initial,reference=np.asarray(initial_pair,complex),np.asarray(reference_pair,complex);time=complex(coordinate_time)
    if raw.shape!=(nr,)or initial.shape!=(2,nr)or reference.shape!=initial.shape or not np.isfinite(raw).all():
        raise ValueError('same complete complexified REAL raw268 and both inherited germs required')
    if ng!=80 or nu_squared_action<0:raise ValueError('original80 gauge coordinates and assigned scalar parameter required')
    cap=holomorphic_cap_and_weights(raw[:100],points=rep['cap_points'])
    geo=holomorphic_geometry_rows(raw[:100],rep['rho'])
    p=_affine_geometry(initial[0],time);rp,rc=(_affine_geometry(x,time)for x in reference)
    eff=_parameters(p,rep['rho'])-_parameters(rp,rep['rho'])+_parameters(rc,rep['rho'])
    effwall=(_parameters(p,np.array([WALL]))-_parameters(rp,np.array([WALL]))+_parameters(rc,np.array([WALL])))[0]
    gb=np.asarray(rep['gauge_basis'])[:,:,0].reshape(len(eff),ng,20)
    gr=np.asarray(rep['gauge_radial_basis'])[:,:,0].reshape(len(eff),ng,20)
    A=np.einsum('rjc,j->rc',gb,raw[100:100+ng]).reshape(-1,5,4)
    At=np.einsum('rjc,j->rc',gb,raw[100+ng:hs]).reshape(-1,5,4)
    Ar=np.einsum('rjc,j->rc',gr,raw[100:100+ng]).reshape(-1,5,4)
    A[:,2:]+=M[None]*(eff[:,0]-1)[:,None,None]
    At[:,2:]+=M[None]*eff[:,1,None,None];Ar[:,2:]+=M[None]*eff[:,2,None,None]
    densities=np.array([[row[k].value for k in('electric','radial','angular','electric_radial','shift')]for row in geo['rows']])
    local=analytic_constant_maxwell_batch(A,At,Ar,densities)
    maps=np.zeros((len(eff),60,2*ng));maps[:,:20,:ng]=gb.transpose(0,2,1)
    maps[:,20:40,ng:]=gb.transpose(0,2,1);maps[:,40:,:ng]=gr.transpose(0,2,1)
    g=np.zeros(nr,complex);K=np.zeros((nr,nr),complex);total=cap['total']
    if surface_gamma is not None:
        if surface_gamma<=0:raise ValueError('assigned area coefficient must be positive')
        total+=surface_gamma*cap['surface_per_gamma']
    # Density/shift polynomial polarizations are EXACT derivatives: linear
    # in each density and degree2 in beta; step1 has no truncation error.
    dgdc=np.empty((len(eff),60,5),complex)
    for k in range(4):
        c=np.zeros_like(densities);c[:,k]=1;c[:,4]=densities[:,4]
        dgdc[:,:,k]=analytic_constant_maxwell_batch(A,At,Ar,c)['gradient']
    cp=densities.copy();cm=densities.copy();cp[:,4]+=1;cm[:,4]-=1
    dgdc[:,:,4]=(analytic_constant_maxwell_batch(A,At,Ar,cp)['gradient']-analytic_constant_maxwell_batch(A,At,Ar,cm)['gradient'])/2
    for j,(row,weight)in enumerate(zip(geo['rows'],rep['radial_quadrature'])):
        e,r,d,k,beta=(row[name]for name in('electric','radial','angular','electric_radial','shift'))
        cur=analytic_constant_maxwell_jet(A[j],At[j],Ar[j],densities[j])['curvatures']
        X,T,R,B=(cur[name]for name in('Ftr','Ft','Fr','B'))
        constant=lambda x:Jet.constant(x,100)
        Y2=constant(np.sum(T*T))-2*beta*np.sum(T*R)+beta*beta*np.sum(R*R)
        full=.5*(k*(X@X)+e*Y2-r*np.sum(R*R)-d*np.sum(B*B))
        lam,lt,lr=(row[name]for name in('connection_lambda','lambda_tau','lambda_rho'))
        baseline=.5*np.sum(M*M)*(e*(lt-beta*lr)**2-r*lr**2-d*(2*(lam-1)*lam)**2)
        factor=MAXWELL_TO_CAP*weight;total+=factor*(full-baseline)
        J=maps[j];g[100:hs]+=factor*J.T@local['gradient'][j]
        K[100:hs,100:hs]+=factor*J.T@local['hessian'][j]@J
        density_first=np.array([row[name].gradient for name in('electric','radial','angular','electric_radial','shift')])
        cross=factor*J.T@dgdc[j]@density_first
        K[100:hs,:100]+=cross;K[:100,100:hs]+=cross.T
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:100+ng]);wall[2:]+=M*(effwall[0]-1)
    H,Hdot=raw[hs:hs+4],raw[hs+4:];weights=[cap[k]for k in('wT','wS','wV')]
    wv=np.array([a.value for a in weights]);lam=rep['scalar_matching']['lambda_H']
    scalar=analytic_intrinsic_n0_jet(wall,H,Hdot,wv,lambda_H=lam,nu_squared_action=nu_squared_action)
    S=np.zeros((28,nr-100));S[:4,2*ng:2*ng+4]=np.eye(4)
    S[4:24,:ng]=rep['wall_trace_map'].reshape(20,ng);S[24:,2*ng+4:]=np.eye(4)
    g[100:]+=S.T@scalar['gradient'];K[100:,100:]+=S.T@scalar['hessian']@S
    for j,weight in enumerate(weights):
        unit=np.eye(3)[j];part=analytic_intrinsic_n0_jet(wall,H,Hdot,unit,lambda_H=lam,nu_squared_action=nu_squared_action)
        total+=weight*part['value'];cross=np.outer(S.T@part['gradient'],weight.gradient)
        K[100:,:100]+=cross;K[:100,100:]+=cross.T
    g[:100]=total.gradient;K[:100,:100]=total.hessian
    c=generic_coordinate_lift(rep['gauge_labels']);P=c['lift'];G=P.T@g;HH=P.T@K@P;n=c['x_count']
    out=dict(value=total.value,raw_gradient=g,raw_hessian=K,gradient=G,hessian=HH,coordinates=c,
        effective_connection_parameters=eff,effective_wall_connection_parameters=effwall,total_wall_connection=wall,
        child_metric_connection_baseline=np.array([[r[k].value for k in('connection_lambda','lambda_tau','lambda_rho')]for r in geo['rows']]),
        full_child_mechanical_baseline_subtraction_retained=True,child_total_lambda_derivative_cancels_only_in_total_connection=True,
        scalar_orbit_normalization='analytic_intrinsic_n0_jet already supplies raw S4/V^2=local polynomial/V',
        raw_coefficient_or_action_dual_conjugated=False,material_At_advection_count=1,
        R4=cap['R4'].value,induced_lapse=cap['N'].value,response_chart=cap['chart'],
        FR_denominator=cap['FR_denominator'].value,coordinate_time=time)
    for a,sl in(('x',slice(0,n)),('v',slice(n,2*n)),('y',slice(2*n,None))):
        for b,sr in(('x',slice(0,n)),('v',slice(n,2*n)),('y',slice(2*n,None))):out['L'+a+b]=HH[sl,sr]
    out.update(canonical_momentum=G[n:2*n],algebraic_Gauss_multiplier_rows=G[2*n:])
    return out
