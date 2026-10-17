"""Owned area-coefficient source in the active geometric birth equations.

This differentiates the retained common action and its implicit cotangent
projection.  The coefficient is not fitted or set to zero physically.
The response is a represented parameter derivative, not a formation root.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .muon_parent_gauge_geometry_correction import ROOT,STATE_SOURCE
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_exact_material_response import exact_moving_cap_action_jet
from .muon_birth_finite_geometric_trace_endpoint import pair_master_chart,moving_endpoint_rows
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .muon_magnetic_birth_ward_mean import named_ward_mean_application
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_birth_phase_continuation import _compressed_npz


def projected_parameter_cotangent(saddle, solution, face_covector, face_parameter,
                                   saddle_parameter, velocity_count, common_trace_map):
    """Differentiate X^T theta using the SAME saddle and its adjoint."""
    K=np.asarray(saddle,float);X=np.asarray(solution,float);n=int(velocity_count)
    theta=np.asarray(face_covector,float);dt=np.asarray(face_parameter,float);dK=np.asarray(saddle_parameter,float)
    adjoint=np.linalg.solve(K.T,np.r_[theta,np.zeros(len(K)-n)])
    return np.asarray(common_trace_map).T@(X[:n].T@dt-adjoint@dK@X)


def area_endpoint_parameter_application(base_directory,*,repository=ROOT,difference_steps=(1e-4,5e-5)):
    root=Path(repository);loaded=load_finite_normal_endpoint(base_directory,side='incoming',repository=root)
    source=loaded['source'];receipt=loaded['receipt'];rep=loaded['representation'];chart=pair_master_chart(rep)
    with np.load(source/'application.npz',allow_pickle=False) as a:saved={k:a[k].copy() for k in a.files}
    raw=saved['updated_raw_pair'];nr=chart['raw_count'];R=chart['lift'];P=chart['one_lift'];n=chart['dynamic_count'];nm=chart['master_count'];vi=chart['v_indices'];yi=chart['y_indices']
    area=[exact_moving_cap_action_jet(12,x[:37],x[37:74],x[74:98],points=rep['cap_points'],source_value=x[98],source_rate=x[99])['surface_per_gamma'] for x in raw]
    ag=np.zeros(2*nr);ah=np.zeros((2*nr,2*nr))
    for arm,a in enumerate(area):
        gi=arm*nr+np.arange(100);ag[gi]=a.gradient;ah[np.ix_(gi,gi)]=a.hessian
    g=R.T@ag;H=R.T@ah@R;pg=P[:100].T@area[0].gradient
    face=-g[vi];face[:n]+=2*pg[n:2*n]
    C=H[np.ix_(yi,vi)];Bcount=6;G=np.vstack((np.zeros((Bcount,2*n)),C))
    dK=np.block([[H[np.ix_(vi,vi)],G.T],[G,np.zeros((len(G),len(G)))]])
    common=np.zeros((6,3));common[[0,2],0]=1;common[[1,3],1]=1;common[[4,5],2]=1
    projected=projected_parameter_cotangent(saved['saddle'],saved['saddle_solution'],
        saved['temporal_face_cotangent'],face,dK,2*n,common)
    with np.load(root/STATE_SOURCE,allow_pickle=False) as a:w=a['state_weights']
    with np.load(root/NORMALIZATION_SOURCE,allow_pickle=False) as a:normal=a['normalization_coordinates']
    from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_symmetric_power
    norm=_symmetric_power(_attachment_jacobian_at_order(12,normal)@_attachment_jacobian_at_order(12,normal).T,.5)
    f=np.zeros(receipt['row_count']);groups=receipt['groups']
    def put(name,value):f[groups[name]['indices']]=np.atleast_1d(value)
    for arm,name in enumerate(('incoming','child')):
        idx=yi[arm*chart['algebraic_count']:(arm+1)*chart['algebraic_count']]
        put(name+'_constraints',g[idx]*np.r_[1/w[74:98],np.ones(chart['algebraic_count']-24)])
    eta=R.T@raw.reshape(-1);pv=np.zeros(nm);pv[n:2*n]=eta[n:2*n]
    Ep=float(pv@pg-area[0].value);put('incoming_energy',Ep)
    put('child_energy',float(eta[vi]@g[vi]-sum(a.value for a in area)-Ep))
    put('gauge_temporal_dual',face[38:n-4]+face[n+38:2*n-4])
    put('Higgs_temporal_dual',face[n-4:n]+face[2*n-4:2*n])
    put('common_attachment_temporal_dual',norm@projected[:2]);put('common_normal_temporal_dual',projected[2])
    # The central U(1) Ward identities act on the literal trace/dual rows.
    profiles=enriched_central_profiles(rep);theta=profiles['theta_coefficients'];D=profiles['radial_derivative_coefficients'];labels=rep['gauge_labels'];coords=chart['coordinates']
    At=[j for j,i in enumerate(coords['At_indices']) if labels[i]['internal']==3]
    Ar=[j for j,i in enumerate(coords['dynamic_gauge_indices']) if labels[i]['field']=='A_rho' and labels[i]['internal']==3]
    L=np.zeros((2,len(f)));generator=higgs_u2_real_representation()['real_generators'][3]
    for arm,name in enumerate(('incoming','child')):
        indices=np.array(groups[name+'_constraints']['indices']);L[:,indices[24+np.array(At)]]=(1 if arm==0 else -1)*theta.T
    L[:,np.array(groups['gauge_temporal_dual']['indices'])[Ar]]=D.T
    Hparent=raw[0,-8:-4];pchild=saved['temporal_face_cotangent'][2*n-4:2*n]*(-1)
    L[:,groups['Higgs_temporal_dual']['indices']]=-np.tile(generator@Hparent,(2,1))
    L[:,groups['Higgs_trace']['indices']]=np.tile(generator.T@pchild,(2,1))
    response=named_ward_mean_application(saved['updated_jacobian'],f[:,None,None],saved['row_scale'],saved['coordinate_weights'],L)
    master=response['coefficient_correction'][:,0,0] if 'coefficient_correction' in response else response['correction'][:,0,0]
    delta=(R@master).reshape(raw.shape)
    checks=[]
    rep['endpoint_action_parameters']=dict(receipt['action_parameters'])
    for step in difference_steps:
        rep['endpoint_action_parameters']['surface_gamma']=step
        a=moving_endpoint_rows(raw,saved['reference_raw_pair'],rep,w,normal,compute_cotangent_derivative=False)
        checks.append(dict(step=float(step),derivative_norm=float(np.linalg.norm((a['residual']-saved['updated_residual'])/step)),
            source_difference_norm=float(np.linalg.norm((a['residual']-saved['updated_residual'])/step-f))))
    return dict(raw_pair=raw,area_raw_gradient=ag,area_raw_hessian=ah,area_parameter_source=f,
        area_temporal_face_parameter=face,area_projected_cotangent_parameter=projected,
        area_saddle_parameter=dK,named_Ward_relations=L,raw_parameter_response=delta,
        response=response,finite_parameter_checks=checks,input_hashes=loaded['input_hashes'],
        gamma_law='gamma=alpha_FSC*c^(-m/2); apply d_gamma/d_c to this SAME represented base response',
        actual_formation_or_physical_cutoff_selected=False)


def materialize_area_endpoint_parameter(base_directory,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve earlier parameter applications')
    a=area_endpoint_parameter_application(base_directory,repository=root);arrays={k:v for k,v in a.items() if isinstance(v,np.ndarray)}
    arrays.update({'response_'+k:v for k,v in a['response'].items() if isinstance(v,np.ndarray)})
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    refs=dict(a['input_hashes'])
    for name in ('muon_birth_area_endpoint_response','muon_birth_finite_normal_phase','muon_magnetic_birth_ward_mean'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    md=dict(classification='EVALUATED_OWNED_AREA_SOURCE_AND_ACTIVE_GEOMETRIC_ENDPOINT_RESPONSE',
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        source_norm=float(np.linalg.norm(a['area_parameter_source'])),raw_response_norm=float(np.linalg.norm(a['raw_parameter_response'])),
        finite_parameter_checks=a['finite_parameter_checks'],gamma_law=a['gamma_law'],
        arithmetic_certificate=a['response']['stored_action_arithmetic_certificate'],
        original_row_residual_norm=float(np.linalg.norm(a['response']['original_residual'])),
        area_not_independent_missing_packet=True,alpha_EM_substituted=False,
        reference_zero_coefficient_is_formal_sector_derivative_not_physical_gamma_zero=True,
        actual_formation_or_physical_cutoff_selected=False,
        error_scope='Arb encloses exact stored row/source arithmetic only; analytic action producer rounding and finite-parameter derivative diagnostics are not rigorously enclosed')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-directory',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    print(json.dumps(materialize_area_endpoint_parameter(a.base_directory,a.output),sort_keys=True))
