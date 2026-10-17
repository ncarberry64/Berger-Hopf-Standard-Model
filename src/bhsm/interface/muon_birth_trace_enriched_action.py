"""Exact reached affine gauge-trace image in a fixed numerical basis.

The added radial function is the actual incoming-minus-child mechanical
lambda profile after removing the existing interior and wall span.  Its
analytic radial derivative is retained.  Reference endpoint q values fix
the numerical basis; no physical field profile or gauge state is chosen.
The literal cap, Maxwell and intrinsic Higgs owners supply every action
derivative on the enlarged same coefficient vector.
"""
from __future__ import annotations
import numpy as np

from .muon_parent_gauge_geometry_correction import correction_representation
from .muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import FIELD_ORDER,background_subtracted_maxwell_action_jet,full_maxwell_weak_geometric_jets,full_maxwell_gauge_hessian_matrix
from .muon_moving_geometric_action import moving_cap_action_jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
from .muon_parent_mean_causal_action import VOLUME,MAXWELL_TO_CAP


def _profile_difference(states,rho):
    applications=[geometric_connection_coefficient_jets(12,x[:37],x[37:74],x[74:98],rho) for x in states]
    d=np.array([p['connection_lambda'].value-c['connection_lambda'].value for p,c in zip(applications[0]['rows'],applications[1]['rows'])])
    dr=np.array([p['lambda_rho'].value-c['lambda_rho'].value for p,c in zip(applications[0]['rows'],applications[1]['rows'])])
    fixed_jet_max=max(float(np.max(abs(r['connection_lambda'].gradient[37:98]))) for a in applications for r in a['rows'])
    return d,dr,fixed_jet_max


def trace_enriched_radial_basis(representation,rho):
    B,D=regular_radial_basis(rho,2)
    d,dr,_=_profile_difference(representation['affine_profile_reference_states'],np.asarray(rho,float))
    projection=representation['affine_interior_projection'];wall=representation['affine_wall_coefficient'];norm=representation['affine_complement_norm']
    f=(d-B[:,:2]@projection-wall*B[:,-1])/norm
    fr=(dr-D[:,:2]@projection-wall*D[:,-1])/norm
    return np.c_[B[:,:2],f,B[:,-1]],np.c_[D[:,:2],fr,D[:,-1]]


def trace_enriched_representation(raw_pair,*,radial_points=48,cap_points=48):
    """Enrich only the actual nonrepresented source image, including its wall."""
    raw=np.asarray(raw_pair,float)
    if raw.shape!=(2,228) or not np.isfinite(raw).all():raise ValueError('actual two original raw228 endpoint vectors required')
    if np.any(raw[:,98:100]):raise ValueError('this frozen-basis initializer owns its recorded normal/rate zero')
    rep=correction_representation(radial_points=radial_points,radial_order=2,cap_points=cap_points,include_wall_lift=True,include_scalar_mean=True)
    states=raw[:,:98].copy();rho=rep['rho'];quad=rep['radial_quadrature'];B,D=regular_radial_basis(rho,2)
    d,dr,fixed=_profile_difference(states,rho);dw,_,_=_profile_difference(states,np.array([WALL]));wall=float(dw[0])
    unrestricted=np.linalg.lstsq(np.sqrt(quad)[:,None]*B,np.sqrt(quad)*d,rcond=None)[0]
    former_complement=float(np.sqrt(quad@((d-B@unrestricted)**2)))
    interior=d-wall*B[:,-1]
    projection=np.linalg.solve(B[:,:2].T@(quad[:,None]*B[:,:2]),B[:,:2].T@(quad*interior))
    complement=interior-B[:,:2]@projection;norm=float(np.sqrt(quad@(complement*complement)))
    if not np.isfinite(norm) or norm<1e-12:raise ValueError('no nontrivial source image requires this enrichment')
    rep.update(affine_profile_reference_states=states,affine_interior_projection=projection,
        affine_wall_coefficient=wall,affine_complement_norm=norm,affine_profile_difference=d,
        former_radial_space_L2_complement=former_complement,
        affine_profile_derivative=dr,affine_velocity_multiplier_jet_max=fixed,
        affine_difference_coefficients=np.r_[projection,norm,wall],
        frozen_profile_scope='basis selected from initial q37 pair; held fixed computational frame; v/m derivatives of lambda value verifiedzero')
    value,derivative=trace_enriched_radial_basis(rep,rho);wall_value,wall_derivative=trace_enriched_radial_basis(rep,np.array([WALL]))
    labels=[];gb=np.zeros((len(rho),80,1,5,4));gr=gb.copy();wallmap=np.zeros((5,4,80));walldr=wallmap.copy()
    k=0
    for radial in range(4):
        for field in range(5):
            for internal in range(4):
                labels.append(dict(radial=radial,field=FIELD_ORDER[field],internal=internal,wall_lift=radial==3,
                    affine_source_enrichment=radial==2))
                gb[:,k,0,field,internal]=value[:,radial];gr[:,k,0,field,internal]=derivative[:,radial]
                wallmap[field,internal,k]=wall_value[0,radial];walldr[field,internal,k]=wall_derivative[0,radial];k+=1
    rep.update(gauge_labels=labels,gauge_count=80,gauge_basis=gb,gauge_radial_basis=gr,
        radial_value_map=value,radial_derivative_map=derivative,wall_trace_map=wallmap,wall_radial_derivative_map=walldr,
        radial_function_count=4,representation_scope='two interior polynomials, exact affine source complement, independent wall lift',
        affine_trace_reconstruction_max=float(np.max(abs(value@rep['affine_difference_coefficients']-d))),
        affine_trace_derivative_reconstruction_max=float(np.max(abs(derivative@rep['affine_difference_coefficients']-dr))))
    return rep


def generic_coordinate_lift(labels):
    N=len(labels);dynamic=np.array([i for i,l in enumerate(labels) if l['field']!=FIELD_ORDER[0]])
    At=np.array([i for i,l in enumerate(labels) if l['field']==FIELD_ORDER[0]])
    nx=42+len(dynamic);ny=24+len(At);P=np.zeros((108+2*N,2*nx+ny));hs=100+2*N
    P[:37,:37]=np.eye(37);P[37:74,nx:nx+37]=np.eye(37);P[74:98,2*nx:2*nx+24]=np.eye(24)
    P[98,37]=1;P[99,nx+37]=1
    for k,i in enumerate(dynamic):P[100+i,38+k]=1;P[100+N+i,nx+38+k]=1
    for k,i in enumerate(At):P[100+i,2*nx+24+k]=1
    P[hs:hs+4,nx-4:nx]=np.eye(4);P[hs+4:hs+8,2*nx-4:2*nx]=np.eye(4)
    return dict(lift=P,x_count=nx,v_count=nx,y_count=ny,dynamic_gauge_indices=dynamic,At_indices=At,raw_gauge_labels=labels)


def pointwise_trace_enriched_action(raw_coefficients,representation,*,nu_squared_action,surface_gamma=None):
    """Literal raw(100+2*N+8) action; all first/second and mixed rows."""
    rep=representation;N=len(rep['gauge_labels']);raw=np.asarray(raw_coefficients,float);nr=108+2*N;hs=100+2*N
    if raw.shape!=(nr,) or not np.isfinite(raw).all():raise ValueError('finite enlarged same coefficient vector required')
    if not np.isfinite(nu_squared_action) or nu_squared_action<0:raise ValueError('explicit nonnegative scalar action parameter required')
    q,v,m=raw[:37],raw[37:74],raw[74:98];s,sr=raw[98:100];a,at=raw[100:100+N],raw[100+N:100+2*N];H,Ht=raw[hs:hs+4],raw[hs+4:]
    cap=moving_cap_action_jet(12,q,v,m,points=rep['cap_points'],source_value=s,source_rate=sr)
    geo=geometric_connection_coefficient_jets(12,q,v,m,rep['rho'],source_value=s,source_rate=sr)
    gb,gr=rep['gauge_basis'],rep['gauge_radial_basis'];count=len(gb)
    tv=np.zeros((count,2*N,1,5,4));tt=tv.copy();tr=tv.copy();ta=np.zeros((count,2*N,1,3,5,4))
    tv[:,:N]=gb;tr[:,:N]=gr;tt[:,N:]=gb
    fields=dict(gauge=np.einsum('rj...,j->r...',gb,a),gauge_tau=np.einsum('rj...,j->r...',gb,at),
        gauge_rho=np.einsum('rj...,j->r...',gr,a),gauge_angular=np.zeros((count,1,3,5,4)))
    tests=dict(tests=tv,tests_tau=tt,tests_rho=tr,tests_angular=ta)
    delta=background_subtracted_maxwell_action_jet(geo,rep['radial_quadrature'],np.ones(1),**fields)
    weak=full_maxwell_weak_geometric_jets(geo,rep['radial_quadrature'],np.ones(1),**fields,**tests)
    gauge=full_maxwell_gauge_hessian_matrix(geo,rep['radial_quadrature'],np.ones(1),**fields,**tests)
    G=np.zeros(nr);K=np.zeros((nr,nr));value=cap['total'].value+MAXWELL_TO_CAP*delta['value']
    G[:100]=cap['total'].gradient+MAXWELL_TO_CAP*delta['gradient'];K[:100,:100]=cap['total'].hessian+MAXWELL_TO_CAP*delta['hessian']
    G[100:hs]=MAXWELL_TO_CAP*weak['weak']['values'];K[100:hs,100:hs]=MAXWELL_TO_CAP*gauge['matrix']
    cross=MAXWELL_TO_CAP*weak['weak']['geometric_jacobian'];K[100:hs,:100]=cross;K[:100,100:hs]=cross.T
    weights=intrinsic_m4_weight_jet(12,q,v,m,source_value=s,source_rate=sr)
    sv=np.zeros((1,4,8));sd=np.zeros((1,4,4,8));sv[0,:,:4]=np.eye(4);sd[0,0,:,4:]=np.eye(4)
    scalar=material_intrinsic_higgs_gauge_action_jet(weights,scalar_coefficients=np.r_[H,Ht],scalar_value_map=sv,scalar_derivative_map=sd,
        gauge_coefficients=a,gauge_trace_map=rep['wall_trace_map'][None],angular_quadrature=np.ones(1),
        lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=nu_squared_action)['action']
    S=np.zeros((108+N,nr));S[:100,:100]=np.eye(100);S[100:108,hs:hs+8]=np.eye(8);S[108:,100:100+N]=np.eye(N)
    value+=scalar.value/VOLUME**2;G+=S.T@scalar.gradient/VOLUME**2;K+=S.T@scalar.hessian@S/VOLUME**2
    if surface_gamma is not None:
        if not np.isfinite(surface_gamma) or surface_gamma<=0:raise ValueError('assigned area coefficient must be positive')
        value+=surface_gamma*cap['surface_per_gamma'].value;G[:100]+=surface_gamma*cap['surface_per_gamma'].gradient;K[:100,:100]+=surface_gamma*cap['surface_per_gamma'].hessian
    coordinates=generic_coordinate_lift(rep['gauge_labels']);P=coordinates['lift'];g=P.T@G;k=P.T@K@P;nx=coordinates['x_count']
    return dict(value=float(value),raw_gradient=G,raw_hessian=K,gradient=g,hessian=k,coordinates=coordinates,
        Lxx=k[:nx,:nx],Lxv=k[:nx,nx:2*nx],Lxy=k[:nx,2*nx:],Lvx=k[nx:2*nx,:nx],Lvv=k[nx:2*nx,nx:2*nx],Lvy=k[nx:2*nx,2*nx:],
        Lyx=k[2*nx:,:nx],Lyv=k[2*nx:,nx:2*nx],Lyy=k[2*nx:,2*nx:],
        surface_value_per_gamma=cap['surface_per_gamma'].value,surface_gradient_per_gamma=cap['surface_per_gamma'].gradient,
        surface_hessian_per_gamma=cap['surface_per_gamma'].hessian,full_stationary_birth_or_native_Pauli_established=False)


def trace_enriched_wall_conormal(raw,representation):
    N=len(representation['gauge_labels']);a,at=raw[100:100+N],raw[100+N:100+2*N]
    value=representation['wall_trace_map'][None,None];radial=representation['wall_radial_derivative_map'][None,None]
    fields=dict(gauge=np.einsum('rpfkj,j->rpfk',value,a),gauge_tau=np.einsum('rpfkj,j->rpfk',value,at),
        gauge_rho=np.einsum('rpfkj,j->rpfk',radial,a),gauge_angular=np.zeros((1,1,3,5,4)))
    tests=np.moveaxis(value,-1,1);tr=np.moveaxis(radial,-1,1)
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],np.array([WALL]),source_value=raw[98],source_rate=raw[99])
    app=full_maxwell_weak_geometric_jets(geo,np.ones(1),np.ones(1),**fields,
        tests=tests,tests_tau=np.zeros_like(tests),tests_rho=tr,tests_angular=np.zeros((1,N,1,3,5,4)))
    return dict(radial_action_covector=MAXWELL_TO_CAP*app['radial_momentum_test']['values'],
        geometry_derivative=MAXWELL_TO_CAP*app['radial_momentum_test']['geometric_jacobian'],
        orientation='increasing reference rho lateral wall; distinct from temporal E1 Cauchy normal')
