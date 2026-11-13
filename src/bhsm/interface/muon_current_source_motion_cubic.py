"""Actual current-normalization contacts in the sourced cubic weak action.

The field-space third variation and the motion of the b-to-beta chart
are distinct terms of one chain rule.  This module evaluates both on
explicit common fields; it does not reuse an old solved first response.
"""
from __future__ import annotations
import numpy as np

from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_moving_geometric_action import _sqrt
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_weak import M
from .muon_parent_maxwell_corrected_retarded import constant_angular_curvatures
from .muon_parent_maxwell_source_mean_forcing import (
    _first, _second_mean, _paired, _mean_paired, _dot, _mdot,
    maxwell_mean_cotangents, higgs_mean_cotangents,
)
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_parent_mean_causal_action import VOLUME, MAXWELL_TO_CAP
from .muon_parent_retarded_hypercharge import WALL


def _real(value, name, shape=None):
    if value is None or not np.isrealobj(value):
        raise ValueError('explicit real '+name+' required')
    a=np.asarray(value,float)
    if not np.isfinite(a).all() or (shape is not None and a.shape!=shape):
        raise ValueError('finite complete '+name+' required')
    return a


def current_face_source_jets(raw_geometry):
    """Owned Tb and coordinate-time Tbdot, including every geometry100 jet."""
    r=_real(raw_geometry,'geometry100',(100,))
    w=intrinsic_m4_weight_jet(12,r[:37],r[37:74],r[74:98],
                            source_value=r[98],source_rate=r[99])
    Tb=1/(np.sqrt(VOLUME)*_sqrt(w['R4']))
    f=w['fields'];lam=w['mechanical_connection_lambda'];rate=w['wall_rate']
    logRdot=(1-lam)*(f['la']+rate*f['ap'])+lam*(f['lb']+rate*f['bp'])
    return dict(T_b=Tb,T_b_dot=-Tb*logRdot/2,log_R4_dot=logRdot,
                intrinsic_weights=w,normalization='2pi² R4 Tb²=1; same material geometry and clock')


def maxwell_cross_hessian(A,At,Ar,u,ut,ur,v,vt,vr,E,densities):
    """Literal D²S[u_A,v_B], including the background-curvature contact."""
    A,At,Ar=(_real(x,'background connection',(5,4)) for x in (A,At,Ar))
    u,ut,ur=(_real(x,'left connection variation') for x in (u,ut,ur))
    v,vt,vr=(_real(x,'right connection variation') for x in (v,vt,vr))
    if u.ndim!=4 or v.ndim!=4 or u.shape[1:3]!=(5,4) or v.shape[1:]!=u.shape[1:] or ut.shape!=u.shape or ur.shape!=u.shape or vt.shape!=v.shape or vr.shape!=v.shape:
        raise ValueError('complete source/field jets in the same angular basis required')
    E=_real(E,'right angular derivatives',(3,u.shape[-1],u.shape[-1]))
    d=_real(densities,'metric densities',(5,))
    if np.any(d[:4]<=0):raise ValueError('positive metric densities required')
    Fu=_first(A,u,ut,ur,E);Fv=_first(A,v,vt,vr,E)
    base=constant_angular_curvatures(A,At,Ar)
    F0=tuple(base[k] for k in ('Ftr','Ft','Fr','B'))
    return _paired(Fu,Fv,d)+_mean_paired(F0,_second_mean(u,v),d)


def higgs_cross_hessian(H,Ht,A,h,ht,a,k,kt,b,E,weights,*,lambda_H,nu_squared_action):
    """Literal real-2Re scalar D²S including mixed gauge/matter contacts."""
    H,Ht=(_real(x,'background scalar',(4,)) for x in (H,Ht))
    A=_real(A,'background wall connection',(5,4))
    h,ht,a,k,kt,b=(_real(x,'scalar/gauge variation') for x in (h,ht,a,k,kt,b))
    if h.ndim!=3 or k.ndim!=3 or h.shape[1]!=4 or k.shape[1:]!=h.shape[1:] or ht.shape!=h.shape or kt.shape!=k.shape or a.shape!=(len(h),5,4,h.shape[-1]) or b.shape!=(len(k),5,4,k.shape[-1]):
        raise ValueError('complete same-basis scalar and wall connection variations required')
    E=_real(E,'right angular derivatives',(3,h.shape[-1],h.shape[-1]))
    weights=_real(weights,'intrinsic weights',(3,))
    if np.any(weights<=0) or lambda_H is None or nu_squared_action is None or not np.isfinite([lambda_H,nu_squared_action]).all() or lambda_H<=0 or nu_squared_action<0:
        raise ValueError('positive weights/lambda_H and explicit nonnegative nu_squared_action required')
    G=higgs_u2_real_representation()['real_generators'];fields=[0,2,3,4]
    O=np.einsum('fc,cij->fij',A[fields],G)
    Ua=np.einsum('afcn,cij->afijn',a[:,fields],G)
    Ub=np.einsum('bfcn,cij->bfijn',b[:,fields],G)
    D0=np.einsum('fij,j->fi',O,H);D0[0]+=Ht
    def first(s,st,U):
        D=np.einsum('fij,ajn->afin',O,s)+np.einsum('afijn,j->afin',U,H)
        D[:,0]+=st;D[:,1:]+=np.einsum('fhk,aik->afih',E,s)
        return D
    Dh=first(h,ht,Ua);Dk=first(k,kt,Ub)
    mixed=np.einsum('afijn,bjn->abfi',Ua,k)+np.einsum('bfijn,ajn->abfi',Ub,h)
    terms=np.array([2*(_dot(Dh[:,f],Dk[:,f])+_mdot(D0[f],mixed[:,:,f])) for f in range(4)])
    hu=np.einsum('i,ain->an',H,h);kv=np.einsum('i,bin->bn',H,k)
    potential=-lambda_H*(8*hu@kv.T+4*(H@H-nu_squared_action)*_dot(h,k))
    return VOLUME*(weights[0]*terms[0]-weights[1]*terms[1:].sum(axis=0)+weights[2]*potential)


def current_source_cubic_application(raw_fields,representation,angular,b_coefficients,
        profile,profile_rate,*,first_gauge,first_gauge_rate,first_gauge_radial,
        first_wall_gauge,first_H,first_H_rate,nu_squared_action):
    """Full fixed-field cubic plus moving-chart terms for explicit first jets.

    The first variation arrays must contain the total variation, including
    its moving prescribed source.  Geometry/source differentiation keeps
    the represented interior first coefficients fixed.  The resulting
    load enters a joint second-response solve; it is not that solve.
    """
    rep=representation;N=len(rep['gauge_labels']);nr=108+2*N;hs=100+2*N
    raw=_real(raw_fields,'common raw fields',(nr,))
    b=_real(b_coefficients,'inherited full400 source columns')
    if b.ndim!=2 or b.shape[0]!=400 or b.shape[1]<1 or np.any(b[:160]):
        raise ValueError('spatial inherited400 source columns required')
    p,pt=_real([profile,profile_rate],'explicit source profile',(2,))
    count=len(b.T);n=20;R=len(rep['rho']);shape=(R,count,5,4,n)
    u=_real(first_gauge,'total first gauge value',shape)
    ut=_real(first_gauge_rate,'total first gauge rate',shape)
    ur=_real(first_gauge_radial,'total first gauge radial derivative',shape)
    aw=_real(first_wall_gauge,'total first wall gauge',(count,5,4,n))
    h=_real(first_H,'total first H',(count,4,n));ht=_real(first_H_rate,'total first H rate',h.shape)
    E=_real(angular['derivative_matrices'],'inherited angular derivative',(3,n,n))
    source=b.T.reshape(count,5,4,n)
    chart=current_face_source_jets(raw[:100]);T,Td=chart['T_b'],chart['T_b_dot'];w=chart['intrinsic_weights']
    if 'radial_value_map' in rep:
        lift=rep['radial_value_map'][:,-1];lift_r=rep['radial_derivative_map'][:,-1]
        wallmap=rep['wall_trace_map']
    else:
        from .muon_parent_retarded_hypercharge import regular_radial_basis
        bv,br=regular_radial_basis(rep['rho'],rep['radial_order']);lift,lift_r=bv[:,-1],br[:,-1]
        wb,_=regular_radial_basis(np.array([WALL]),rep['radial_order']);wallmap=np.zeros((5,4,N))
        from .muon_parent_maxwell_full_weak import FIELD_ORDER
        for j,label in enumerate(rep['gauge_labels']):wallmap[FIELD_ORDER.index(label['field']),label['internal'],j]=wb[0,label['radial']]
    gb,gr=rep['gauge_basis'],rep['gauge_radial_basis']
    A=np.einsum('rj...,j->r...',gb,raw[100:100+N])[:,0]
    At=np.einsum('rj...,j->r...',gb,raw[100+N:hs])[:,0]
    Ar=np.einsum('rj...,j->r...',gr,raw[100:100+N])[:,0]
    geo=geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],rep['rho'],source_value=raw[98],source_rate=raw[99])
    fixed=np.zeros((100,count,count));motion_T=np.zeros((count,count));motion_Td=motion_T.copy()
    names=('electric','radial','angular','electric_radial','shift')
    for j,row in enumerate(geo['rows']):
        A[j,2:]+=M*(row['connection_lambda'].value-1);At[j,2:]+=M*row['lambda_tau'].value;Ar[j,2:]+=M*row['lambda_rho'].value
        d=np.array([row[k].value for k in names]);q=rep['radial_quadrature'][j]
        result=maxwell_mean_cotangents(A[j],At[j],Ar[j],u[j],ut[j],ur[j],E,d)
        fixed+=q*(np.einsum('kc,kab->cab',np.array([row[k].gradient for k in names]),result['metric_density_cotangent'])+np.einsum('kc,kab->cab',np.array([row[k].gradient for k in ('connection_lambda','lambda_tau','lambda_rho')]),result['mechanical_lambda_cotangents']))
        v=p*lift[j]*source;vt=pt*lift[j]*source;vr=p*lift_r[j]*source
        cross=maxwell_cross_hessian(A[j],At[j],Ar[j],u[j],ut[j],ur[j],v,vt,vr,E,d)
        motion_T+=q*(cross+cross.T)
        z=np.zeros_like(v)
        cross=maxwell_cross_hessian(A[j],At[j],Ar[j],u[j],ut[j],ur[j],z,p*lift[j]*source,z,E,d)
        motion_Td+=q*(cross+cross.T)
    max_motion=T.gradient[:,None,None]*motion_T+Td.gradient[:,None,None]*motion_Td
    wall=np.einsum('fcj,j->fc',wallmap,raw[100:100+N]);wall[2:]+=M*(w['mechanical_connection_lambda'].value-1)
    H,Ht=raw[hs:hs+4],raw[hs+4:];weights=np.array([w[k].value for k in ('wT','wS','wV')])
    lam=rep['scalar_matching']['lambda_H']
    scalar=higgs_mean_cotangents(H,Ht,wall,h,ht,aw,E,weights,lambda_H=lam,nu_squared_action=nu_squared_action)
    scalar_fixed=np.einsum('kc,kab->cab',np.array([w[k].gradient for k in ('wT','wS','wV')]),scalar['metric_weight_cotangent'])+w['mechanical_connection_lambda'].gradient[:,None,None]*scalar['mechanical_lambda_cotangent']
    z=np.zeros_like(h)
    cross=higgs_cross_hessian(H,Ht,wall,h,ht,aw,z,z,p*source,E,weights,lambda_H=lam,nu_squared_action=nu_squared_action)
    scalar_motion=T.gradient[:,None,None]*(cross+cross.T)
    fixed=MAXWELL_TO_CAP*fixed+scalar_fixed/VOLUME**2
    motion=MAXWELL_TO_CAP*max_motion+scalar_motion/VOLUME**2
    return dict(fixed_field_geometry_cubic=fixed,moving_source_geometry_cubic=motion,
        complete_geometry_cubic_at_fixed_interior_first_coefficients=fixed+motion,
        Maxwell_moving_source_geometry_cubic=MAXWELL_TO_CAP*max_motion,
        scalar_moving_source_geometry_cubic=scalar_motion/VOLUME**2,
        T_b=T.value,T_b_dot=Td.value,T_b_gradient=T.gradient,T_b_dot_gradient=Td.gradient,
        T_b_hessian=T.hessian,T_b_dot_hessian=Td.hessian,
        scalar_source_rate_motion_exact_zero_reason='material intrinsic action contains At_ref and Ai, but no independent gauge-rate coordinate',
        source_motion_count=1,source_pair_derivative_divided_by_two=False,
        equation='D_z S_AB=D3S[z,u_A,u_B]+D2S[D_z u_A,u_B]+D2S[u_A,D_z u_B]',
        geometry_order='q37,qdot37,m24,normal,normal_rate',
        background_field_and_source_chart_bound=True,mean_second_response_solved=False,
        physical_native_heat_or_Pauli_evaluated=False)


def prescribed_source_cubic_application(raw_fields,representation,angular,b_coefficients,
        profile,profile_rate,*,nu_squared_action):
    """Evaluate the explicit affine source part, without induced response.

    Zero scalar/interior variations define this action-test restriction;
    they do not fill an unavailable solved scalar or causal response.
    """
    raw=_real(raw_fields,'common raw fields');b=_real(b_coefficients,'full400 source columns')
    chart=current_face_source_jets(raw[:100]);T,Td=chart['T_b'].value,chart['T_b_dot'].value
    rep=representation
    if 'radial_value_map' in rep:lift=rep['radial_value_map'][:,-1];lr=rep['radial_derivative_map'][:,-1]
    else:
        from .muon_parent_retarded_hypercharge import regular_radial_basis
        values,derivatives=regular_radial_basis(rep['rho'],rep['radial_order']);lift,lr=values[:,-1],derivatives[:,-1]
    source=b.T.reshape(b.shape[1],5,4,20)
    u=lift[:,None,None,None,None]*T*profile*source[None]
    ut=lift[:,None,None,None,None]*(Td*profile+T*profile_rate)*source[None]
    ur=lr[:,None,None,None,None]*T*profile*source[None]
    zeros=np.zeros((len(source),4,20))
    result=current_source_cubic_application(raw,rep,angular,b,profile,profile_rate,
        first_gauge=u,first_gauge_rate=ut,first_gauge_radial=ur,
        first_wall_gauge=T*profile*source,first_H=zeros,first_H_rate=zeros,
        nu_squared_action=nu_squared_action)
    result.update(explicit_prescribed_source_part=True,solved_causal_first_response_substituted=False,
                  scalar_first_zero_scope='defined fixed-H action variation; not an active-H or sourced-response assertion')
    return result
