"""Literal warped-worldtube curvature on the retained finite normal chart.

The outward spacelike vector is orthogonal to the actual timelike wall.
Its Ricci and second-fundamental contractions include lapse, shift and
temporal warp derivatives.  The returned curvature coefficient is one
geometric part of J; it is not a raw area Hessian, bulk impedance, local
restoring coefficient or selected normal mode.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_moving_geometric_action import _fields,_sqrt
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_gauge_geometry_correction import ROOT
from .muon_profile_preserving_phase_sample import load_profile_preserving_phase
from .muon_birth_phase_continuation import _compressed_npz


def warped_worldtube_curvature(metric,metric_first,metric_second,warps,*,wall_rate,wall_acceleration):
    """Contract a +− base metric with positive angular warp factors.

    Base indices are (t,chi). Each warp is (value, first2, second2x2,
    positive dimension). Angular curvature does not enter Ric(n,n),
    because the worldtube normal has only base components. The same
    convention R_ab=partial_c Gamma^c_ab-... is used throughout.
    """
    g=np.asarray(metric,float);dg=np.asarray(metric_first,float);ddg=np.asarray(metric_second,float)
    if g.shape!=(2,2)or dg.shape!=(2,2,2)or ddg.shape!=(2,2,2,2):raise ValueError('complete two-dimensional metric twojet required')
    if not np.isfinite(np.concatenate([g.ravel(),dg.ravel(),ddg.ravel(),[wall_rate,wall_acceleration]])).all():raise ValueError('finite metric and embedding twojet required')
    if not np.allclose(g,g.T,rtol=0,atol=0)or np.linalg.det(g)>=0:raise ValueError('Lorentzian +− base metric required')
    inverse=np.linalg.inv(g);dinverse=np.empty_like(dg)
    for i in range(2):dinverse[:,:,i]=-inverse@dg[:,:,i]@inverse
    connection=np.zeros((2,2,2));dconnection=np.zeros((2,2,2,2))
    for a,b,c in np.ndindex((2,2,2)):
        for d in range(2):
            term=dg[d,c,b]+dg[d,b,c]-dg[b,c,d]
            connection[a,b,c]+=.5*inverse[a,d]*term
            for i in range(2):
                dconnection[a,b,c,i]+=.5*(dinverse[a,d,i]*term+inverse[a,d]*(ddg[d,c,b,i]+ddg[d,b,c,i]-ddg[b,c,d,i]))
    ricci=np.zeros((2,2))
    for a,b in np.ndindex((2,2)):
        for c in range(2):
            ricci[a,b]+=dconnection[c,a,b,c]-dconnection[c,a,c,b]
            for d in range(2):ricci[a,b]+=connection[c,a,b]*connection[d,c,d]-connection[d,a,c]*connection[c,b,d]
    tangent=np.array([1.,float(wall_rate)]);lapse_squared=float(tangent@g@tangent)
    if lapse_squared<=0:raise ValueError('timelike wall required')
    lapse=np.sqrt(lapse_squared);unit_tangent=tangent/lapse
    normal=inverse@np.array([wall_rate,-1.]);normal/=np.sqrt(-float(normal@g@normal))
    dg_along=dg[:,:,0]+wall_rate*dg[:,:,1];tangent_rate=np.array([0.,float(wall_acceleration)])
    lapse_rate=(tangent@dg_along@tangent+2*tangent@g@tangent_rate)/(2*lapse)
    acceleration=(tangent_rate/lapse-tangent*lapse_rate/lapse**2)/lapse+np.einsum('abc,b,c->a',connection,unit_tangent,unit_tangent)
    temporal_curvature=-float(normal@g@acceleration);principal=[temporal_curvature];dimensions=[1]
    for value,first,second,dimension in warps:
        first=np.asarray(first,float);second=np.asarray(second,float)
        if value<=0 or first.shape!=(2,)or second.shape!=(2,2)or type(dimension)is not int or dimension<1:
            raise ValueError('positive angular warp and its complete twojet/dimension required')
        covariant_hessian=second-np.einsum('cab,c->ab',connection,first)
        ricci-=dimension*covariant_hessian/value
        principal.append(float(normal@first/value));dimensions.append(dimension)
    second_fundamental_squared=float(np.dot(dimensions,np.array(principal)**2))
    ricci_nn=float(normal@ricci@normal)
    return dict(outward_unit_normal=normal,future_unit_tangent=unit_tangent,induced_lapse=float(lapse),
        principal_curvatures=np.array(principal),principal_dimensions=np.array(dimensions),
        mean_curvature=float(np.dot(dimensions,principal)),second_fundamental_squared=second_fundamental_squared,
        ambient_Ric_normal_normal=ricci_nn,constant_normal_curvature_coefficient=-(second_fundamental_squared+ricci_nn),
        ambient_base_Ricci_with_warps=ricci,normal_norm=float(normal@g@normal),normal_tangent_pairing=float(normal@g@unit_tangent),
        embedding_acceleration=float(wall_acceleration),ambient_signature='+---',
        curvature_coefficient_not_raw_area_Hessian=True,physical_restoring_density_or_mode_selected=False)


def finite_normal_worldvolume_jacobi(raw_fields,*,stratum='M8'):
    """Evaluate geometry on the SAME inside-cell affine coefficient germ.

    q(t) and normal amplitude are affine; m and their represented rates
    are fixed inside the numerical midpoint cell. The coordinate wall
    acceleration is the exact derivative of s(t)/Cstar(q(t)); no physical
    qdd or multiplier evolution is assigned by this application.
    """
    raw=np.asarray(raw_fields)
    if not np.isrealobj(raw)or raw.ndim!=1 or len(raw)<100 or not np.isfinite(raw).all():raise ValueError('complete real finite geometric germ required')
    if stratum not in ('M8','M5'):raise ValueError('explicit M8 or M5 stratum required')
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    time=Jet.affine(0.,np.array([1.,0.]));chi=Jet.affine(w['wall'].value,np.array([0.,1.]))
    q=[Jet.constant(x,2)+time*v for x,v in zip(raw[:37],raw[37:74])]
    v=[Jet.constant(x,2)for x in raw[37:74]];m=[Jet.constant(x,2)for x in raw[74:98]]
    f=_fields(12,q,v,m,chi);N,C,beta=f['N'],f['C'],f['beta']
    metric=((N*N-C*C*beta*beta,-C*C*beta),(-C*C*beta,-C*C))
    g=np.array([[j.value for j in row]for row in metric]);dg=np.array([[j.gradient for j in row]for row in metric]);ddg=np.array([[j.hessian for j in row]for row in metric])
    if stratum=='M8':warp_jets=[(f['A'],3),(f['B'],3)]
    else:warp_jets=[(f['A']*f['B']/_sqrt(f['A']*f['A']+f['B']*f['B']),3)]
    log_Cstar_rate=float(w['Cstar'].gradient[:37]@raw[37:74]/w['Cstar'].value)
    wall_acceleration=(log_Cstar_rate**2*raw[98]-2*log_Cstar_rate*raw[99])/w['Cstar'].value
    a=warped_worldtube_curvature(g,dg,ddg,[(j.value,j.gradient,j.hessian,d)for j,d in warp_jets],
        wall_rate=w['wall_rate'].value,wall_acceleration=wall_acceleration)
    a.update(stratum=stratum,wall_coordinate=w['wall'].value,C=f['C'].value,N=f['N'].value,
        spatial_normal_vector_at_fixed_t=np.array([0.,1/f['C'].value]),
        action_normal_is_outward_spacelike_vector=True,temporal_Cauchy_normal_not_used=True,
        complete_J_principal_operator_or_bulk_impedance_or_formation_selected=False,
        kinematic_scope='exact geometry of the represented inside-cell affine q/s and fixed m/v/y germ; not asserted physical acceleration/history')
    return a


def materialize_worldvolume_jacobi(incoming_phase,outgoing_phase,output,*,repository=ROOT):
    """Execute both owned curvature strata at the saved first midpoints."""
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve previous curvature applications')
    phases=[load_profile_preserving_phase(p,repository=root)for p in (incoming_phase,outgoing_phase)]
    if [p['receipt']['side']for p in phases]!=['incoming','outgoing']:raise ValueError('actual incoming/child order required')
    arrays={};rows=[];refs={}
    for side,phase in zip(('incoming','outgoing'),phases):
        raw=phase['arrays'][phase['stage_key']][0];arrays[side+'_raw_midpoint']=raw
        refs.update(phase['input_hashes'])
        for stratum in ('M8','M5'):
            a=finite_normal_worldvolume_jacobi(raw,stratum=stratum)
            rows.append(dict(side=side,**{k:v for k,v in a.items()if not isinstance(v,np.ndarray)}))
            arrays.update({side+'_'+stratum+'_'+k:v for k,v in a.items()if isinstance(v,np.ndarray)})
    for name in ('muon_finite_normal_worldvolume_jacobi','muon_profile_preserving_phase_sample',
        'muon_moving_geometric_action','muon_intrinsic_m4_normal_pullback','aether_exact_radial_schur_lift_v15_83'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    if refs!={p:sha256((root/p).read_bytes()).hexdigest()for p in refs}:raise RuntimeError('consumed geometry changed')
    md=dict(classification='EVALUATED_FINITE_MOVING_WALL_WARPED_WORLDVOLUME_CURVATURE',rows=rows,
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        definition='constant geometric term -(|II|^2+Ric(n,n)), from the literal ambient warped metric and outward spacelike worldtube normal',
        same_germ_scope='First solved midpoint of each consumed phase: q/s affine and m/v/y held in the represented cell; no physical qdd or history assigned.',
        principal_operator_or_raw_area_Hessian_or_restoring_density_identified=False,
        physical_formation_or_mode_or_cutoff_or_Pauli_selected=False,
        error_scope='Analytic metric twojets in binary64 on the represented germ; no action rounding, physical-acceleration or domain uncertainty enclosed')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('incoming-phase','outgoing-phase','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_worldvolume_jacobi(a.incoming_phase,a.outgoing_phase,a.output),sort_keys=True))
