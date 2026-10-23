"""Literal cubic mean load on the corrected inherited moving-wall action.

The first-response coefficients are held in their existing radial frame.
Background, metric and analytic magnetic trace motion are differentiated
once. Parent/reference coordinates are explicit arguments and are held
in the per-arm partial derivative; their common-birth variation is separate.
"""
from __future__ import annotations
import numpy as np
from .muon_exact_material_response import exact_geometric_connection_coefficient_jets
from .muon_birth_finite_normal_trace_graph import affine_connection_profile_two_jet
from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_parent_positive_coupled_field import corrected_positive_parent_reference
from .muon_corrected_profile_magnetic_response import corrected_wall_reference
from .muon_parent_maxwell_source_mean_forcing import maxwell_mean_cotangents,higgs_mean_cotangents
from .muon_current_source_motion_cubic import maxwell_cross_hessian,higgs_cross_hessian
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_retarded_hypercharge import regular_radial_basis,WALL
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP,VOLUME
from .muon_parent_maxwell_full_weak import M


def corrected_background_geometry_jets(raw,representation,*,coordinate_time,initial_pair=None,reference_pair=None):
    """Apply the exact child partial and keep inherited-parent jets explicitly."""
    x=np.asarray(raw,float);rho=np.asarray(representation['rho']);t=float(coordinate_time)
    ref=corrected_positive_parent_reference(x,representation,coordinate_time=t,
        initial_pair=initial_pair,reference_pair=reference_pair)
    geo=exact_geometric_connection_coefficient_jets(12,x[:37],x[37:74],x[74:98],rho,
        source_value=x[98],source_rate=x[99])
    conn=np.array([[r[k].gradient for k in ('connection_lambda','lambda_tau','lambda_rho')]for r in geo['rows']])
    parent=np.zeros_like(conn)
    if initial_pair is not None:
        p=affine_geometry_germ(np.asarray(initial_pair)[0],t)
        profile=affine_connection_profile_two_jet(np.array([p,x]),rho)
        conn+=profile['first'][:,:,100:];parent=profile['first'][:,:,:100]
    return dict(reference=ref,geometry=geo,connection_raw_geometry_first_jet=conn,
        inherited_parent_geometry_first_jet=parent,
        derivative_scope='child raw100 partial at fixed explicit parent/reference and coordinate time')


def corrected_profile_mean_load(raw,representation,angular,source_jet,profile,profile_rate,*,
        first_gauge,first_gauge_rate,first_gauge_radial,first_wall_gauge,first_H,first_H_rate,
        coordinate_time,nu_squared_action,initial_pair=None,reference_pair=None):
    """Evaluate every raw268 row of D_z S_AB on the actual full first fields."""
    x=np.asarray(raw,float);rep=representation;E=np.asarray(angular['derivative_matrices'])
    u,ut,ur,aw,h,ht=(np.asarray(a,float)for a in(first_gauge,first_gauge_rate,first_gauge_radial,
        first_wall_gauge,first_H,first_H_rate))
    count=len(h);nr=268;R=len(rep['rho']);p,pt=float(profile),float(profile_rate)
    if (x.shape!=(nr,)or u.shape!=(R,count,5,4,20)or ut.shape!=u.shape or ur.shape!=u.shape or
        aw.shape!=(count,5,4,20)or h.shape!=(count,4,20)or ht.shape!=h.shape or count!=3 or
        any(not np.isfinite(a).all()for a in(x,u,ut,ur,aw,h,ht))):
        raise ValueError('same raw268 and all three solved magnetic first fields required')
    kw=dict(coordinate_time=coordinate_time,initial_pair=initial_pair,reference_pair=reference_pair)
    background=corrected_background_geometry_jets(x,rep,**kw);ref=background['reference'];geo=background['geometry']
    A,At,Ar=(ref[k]for k in('background_values','background_time_derivatives','background_radial_derivatives'))
    fixed=np.zeros((nr,count,count));max_value=np.zeros((80,count,count));max_rate=max_value.copy()
    names=('electric','radial','angular','electric_radial','shift')
    for j,row in enumerate(geo['rows']):
        dens=ref['positive_two_form_densities'][j];quad=rep['radial_quadrature'][j]
        r=maxwell_mean_cotangents(A[j],At[j],Ar[j],u[j],ut[j],ur[j],E,dens)
        fixed[:100]+=MAXWELL_TO_CAP*quad*(
            np.einsum('kc,kab->cab',np.array([row[k].gradient for k in names]),r['metric_density_cotangent'])+
            np.einsum('kc,kab->cab',background['connection_raw_geometry_first_jet'][j],r['mechanical_lambda_cotangents']))
        gb,gr=rep['gauge_basis'][j,:,0],rep['gauge_radial_basis'][j,:,0]
        max_value+=quad*(np.einsum('jfc,fcab->jab',gb,r['value'].reshape(5,4,count,count))+
            np.einsum('jfc,fcab->jab',gr,r['radial'].reshape(5,4,count,count)))
        max_rate+=quad*np.einsum('jfc,fcab->jab',gb,r['time'].reshape(5,4,count,count))
    fixed[100:180]=MAXWELL_TO_CAP*max_value;fixed[180:260]=MAXWELL_TO_CAP*max_rate
    wall=corrected_wall_reference(x,rep,**kw)['background_values'][0]
    wallrep=dict(rep);wallrep['rho']=np.array([WALL]);wallrep['radial_quadrature']=np.ones(1)
    wallrep['gauge_basis']=np.moveaxis(rep['wall_trace_map'],-1,0)[None,:,None]
    wallrep['gauge_radial_basis']=np.moveaxis(rep['wall_radial_derivative_map'],-1,0)[None,:,None]
    walljets=corrected_background_geometry_jets(x,wallrep,**kw)
    w=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:98],source_value=x[98],source_rate=x[99])
    weights=np.array([w[k].value for k in('wT','wS','wV')]);lam=rep['scalar_matching']['lambda_H']
    scalar=higgs_mean_cotangents(x[260:264],x[264:],wall,h,ht,aw,E,weights,
        lambda_H=lam,nu_squared_action=nu_squared_action)
    fixed[:100]+=(np.einsum('kc,kab->cab',np.array([w[k].gradient for k in('wT','wS','wV')]),scalar['metric_weight_cotangent'])+
        walljets['connection_raw_geometry_first_jet'][0,0,:,None,None]*scalar['mechanical_lambda_cotangent'])/VOLUME**2
    fixed[100:180]+=np.einsum('fcj,fcab->jab',rep['wall_trace_map'],scalar['gauge_value'].reshape(5,4,count,count))/VOLUME**2
    fixed[260:264]=scalar['scalar_value']/VOLUME**2;fixed[264:]=scalar['scalar_time']/VOLUME**2
    # Two source-chart contacts use the actual Q(H,geometry), Qdot jets.
    dQ,dQt=(np.asarray(source_jet[k],float)[:,:,:count]for k in('Q_first_jet','Qdot_first_jet'))
    if dQ.shape!=(nr,400,count)or dQt.shape!=dQ.shape:raise ValueError('full same-source analytic raw jets required')
    b,br=regular_radial_basis(rep['rho'],1);lift,lr=b[:,1],br[:,1]
    motion=np.zeros_like(fixed);active=np.flatnonzero(np.any(dQ,axis=(1,2))|np.any(dQt,axis=(1,2)))
    for start in range(0,len(active),16):
        ids=active[start:start+16];n=len(ids);q=dQ[ids].transpose(0,2,1).reshape(n*count,5,4,20)
        qt=dQt[ids].transpose(0,2,1).reshape(q.shape)
        for j in range(R):
            C=maxwell_cross_hessian(A[j],At[j],Ar[j],u[j],ut[j],ur[j],p*lift[j]*q,
                lift[j]*(pt*q+p*qt),p*lr[j]*q,E,ref['positive_two_form_densities'][j])
            C=C.reshape(count,n,count).transpose(1,0,2)
            motion[ids]+=MAXWELL_TO_CAP*rep['radial_quadrature'][j]*(C+C.swapaxes(-1,-2))
        z=np.zeros((n*count,4,20))
        C=higgs_cross_hessian(x[260:264],x[264:],wall,h,ht,aw,z,z,p*q,E,weights,
            lambda_H=lam,nu_squared_action=nu_squared_action).reshape(count,n,count).transpose(1,0,2)
        motion[ids]+=(C+C.swapaxes(-1,-2))/VOLUME**2
    return dict(raw_mean_cotangent=fixed+motion,fixed_field_raw_mean_cotangent=fixed,
        source_motion_cotangent=motion,raw_base=x.copy(),
        background_geometry_connection_first_jet=background['connection_raw_geometry_first_jet'],
        inherited_parent_geometry_first_jet=background['inherited_parent_geometry_first_jet'],
        scalar_wall_connection_first_jet=walljets['connection_raw_geometry_first_jet'][0],
        source_motion_count=1,all268_mean_rows_retained=True,active_magnetic_axes=[0,1,2],
        parent_reference_and_boundary_mean_motion_completed=False,
        equation='D_z S_AB=D3S[z,u_A,u_B]+D2S[D_z u_A,u_B]+D2S[u_A,D_z u_B]',
        derivative_scope=background['derivative_scope'],
        normalization='same Maxwell1/(8 V²), intrinsic scalar1/V²; unit-Haar and real2Re once',
        error_scope='binary64 exact action contractions on the same corrected fields; no temporal/radial complement or native/Pauli enclosure')
