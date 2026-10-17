"""Higgs-stiffness response of the same moving226 birth action.

The source is the literal derivative -wV*(|H|^2-nu^2)^2/V of the
retained action, including metric/velocity contacts and the constrained
face cotangent.  A parameter continuation does not select the physical
scalar pole, energy unit, formation branch, or exterior domain.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_mean_causal_action import VOLUME
from .muon_parent_gauge_geometry_correction import ROOT,STATE_SOURCE
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_finite_geometric_trace_endpoint import pair_master_chart,moving_endpoint_rows,solve_moving_endpoint
from .muon_birth_area_endpoint_response import projected_parameter_cotangent
from .muon_corrected_birth_mean import moving_birth_ward_relations
from .muon_magnetic_birth_ward_mean import named_ward_mean_application
from .aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_symmetric_power
from .muon_birth_phase_continuation import _compressed_npz
from .muon_birth_attached_phase import enriched_representation_from_values
from .muon_birth_trace_enriched_action import generic_coordinate_lift


def higgs_lambda_action_jet(raw,*,nu_squared_action):
    """Full raw268 derivative of the original signed scalar potential."""
    x=np.asarray(raw)
    if (not np.isrealobj(x)or x.shape!=(268,)or not np.isfinite(x).all()
            or not np.isfinite(nu_squared_action)or nu_squared_action<0):
        raise ValueError('actual real raw268 and retained nonnegative potential center required')
    x=x.astype(float);w=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:98],source_value=x[98],source_rate=x[99])['wV']
    wg=np.zeros(268);wg[:100]=w.gradient;wh=np.zeros((268,268));wh[:100,:100]=w.hessian
    measure=Jet(w.value,wg,wh);eye=np.eye(268)
    h=[Jet.affine(x[j],eye[j])for j in range(260,264)]
    norm2=sum((z*z for z in h),Jet.constant(0.,268))
    return -measure*(norm2-float(nu_squared_action))**2/VOLUME


def lambda_birth_parameter_application(base_directory,*,repository=ROOT,certify=True):
    """Apply the action's lambda source through every original birth row."""
    root=Path(repository);loaded=load_finite_normal_endpoint(base_directory,side='incoming',repository=root)
    rep=deepcopy(loaded['representation']);md=loaded['receipt'];rep['endpoint_action_parameters']=dict(md['action_parameters'])
    with np.load(loaded['source']/'application.npz',allow_pickle=False)as f:base={k:f[k].copy()for k in f.files}
    raw=base['updated_raw_pair'];chart=pair_master_chart(rep);R=chart['lift'];P=chart['one_lift'];n=chart['dynamic_count'];nm=chart['master_count'];vi=chart['v_indices'];yi=chart['y_indices']
    jets=[higgs_lambda_action_jet(x,nu_squared_action=md['action_parameters']['nu_squared_action'])for x in raw]
    ag=np.r_[jets[0].gradient,jets[1].gradient];ah=np.zeros((536,536));ah[:268,:268]=jets[0].hessian;ah[268:,268:]=jets[1].hessian
    g=R.T@ag;H=R.T@ah@R;pg=P.T@jets[0].gradient
    face=-g[vi];face[:n]+=2*pg[n:2*n]
    C=H[np.ix_(yi,vi)];G=np.vstack((np.zeros((6,2*n)),C))
    dK=np.block([[H[np.ix_(vi,vi)],G.T],[G,np.zeros((len(G),len(G)))]])
    common=np.zeros((6,3));common[[0,2],0]=1;common[[1,3],1]=1;common[[4,5],2]=1
    projected=projected_parameter_cotangent(base['saddle'],base['saddle_solution'],base['temporal_face_cotangent'],face,dK,2*n,common)
    with np.load(root/STATE_SOURCE,allow_pickle=False)as f:weights=f['state_weights'].copy()
    with np.load(root/NORMALIZATION_SOURCE,allow_pickle=False)as f:normal=f['normalization_coordinates'].copy()
    groups=md['groups'];source=np.zeros(md['row_count']);put=lambda k,v:source.__setitem__(groups[k]['indices'],np.atleast_1d(v))
    for arm,name in enumerate(('incoming','child')):
        idx=yi[arm*chart['algebraic_count']:(arm+1)*chart['algebraic_count']]
        put(name+'_constraints',g[idx]*np.r_[1/weights[74:98],np.ones(chart['algebraic_count']-24)])
    eta=R.T@raw.ravel();pv=np.zeros(nm);pv[n:2*n]=eta[n:2*n]
    Ep=float(pv@pg-jets[0].value);put('incoming_energy',Ep)
    put('child_energy',float(eta[vi]@g[vi]-sum(a.value for a in jets)-Ep))
    put('gauge_temporal_dual',face[38:n-4]+face[n+38:2*n-4])
    put('Higgs_temporal_dual',face[n-4:n]+face[2*n-4:2*n])
    B=_attachment_jacobian_at_order(12,normal);norm=_symmetric_power(B@B.T,.5)
    put('common_attachment_temporal_dual',norm@projected[:2]);put('common_normal_temporal_dual',projected[2])
    ward=moving_birth_ward_relations(raw,base,rep,chart,groups)
    solved=named_ward_mean_application(base['updated_jacobian'],source[:,None,None],base['row_scale'],base['coordinate_weights'],ward['row_relations'],certify=certify)
    delta=(R@solved['correction'][:,0,0]).reshape(2,268)
    refs=dict(loaded['input_hashes'])
    for p in(STATE_SOURCE,NORMALIZATION_SOURCE):refs[p]=sha256((root/p).read_bytes()).hexdigest()
    return dict(raw_pair=raw,reference_pair=base['reference_raw_pair'],lambda_parameter_source=source,
        lambda_raw_gradient=ag,lambda_raw_hessian=ah,lambda_face_parameter=face,lambda_saddle_parameter=dK,
        lambda_projected_cotangent_parameter=projected,raw_parameter_response=delta,
        named_Ward_relations=ward['row_relations'],response=solved,base=base,representation=rep,
        state_weights=weights,normalization_coordinates=normal,lambda_H_base=rep['scalar_matching']['lambda_H'],input_hashes=refs,base_receipt=md)


def load_lambda_coupled_birth(folder,*,side,repository=ROOT):
    """Restore the varied stiffness explicitly; the old base loader does not."""
    root=Path(repository);path=Path(folder);path=path if path.is_absolute()else root/path
    if side not in('incoming','outgoing'):raise ValueError('actual chronological arm required')
    b=(path/'result.json').read_bytes();md=json.loads(b)
    if (md['classification']!='EVALUATED_SAME_MOVING226_COUPLED_HIGGS_STIFFNESS_CONTINUATION'
            or md['status']!='REPRESENTED_MOVING_TRACE_TOLERANCE'):
        raise ValueError('consume only a solved same-action coupled stiffness continuation')
    refs=dict(md['input_hashes'])
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('coupled stiffness owner changed: '+p)
    az=(path/'application.npz').read_bytes()
    if sha256(az).hexdigest()!=md['numerical_sha256']:raise ValueError('coupled fields changed')
    with np.load(path/'application.npz',allow_pickle=False)as f:arrays={k:f[k].copy()for k in f.files}
    rep=enriched_representation_from_values(md,arrays);rep['scalar_matching']=deepcopy(md['scalar_matching'])
    rep['endpoint_action_parameters']=dict(md['action_parameters']);coordinates=generic_coordinate_lift(rep['gauge_labels'])
    raw=arrays['updated_raw_pair'][int(side=='outgoing')];master=coordinates['lift'].T@raw
    if not np.array_equal(coordinates['lift']@master,raw):raise ValueError('all changed fields must survive the actual coordinate lift')
    refs[(path/'result.json').relative_to(root).as_posix()]=sha256(b).hexdigest();refs[(path/'application.npz').relative_to(root).as_posix()]=sha256(az).hexdigest()
    return dict(raw=raw,master=master,representation=rep,coordinates=coordinates,arrays=arrays,receipt=md,input_hashes=refs)


def materialize_lambda_coupled_birth(base_directory,output,*,lambda_increment=.001,max_iterations=3,repository=ROOT):
    """Execute a coupled finite parameter step and re-evaluate original rows."""
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier coupled lambda applications')
    a=lambda_birth_parameter_application(base_directory,repository=root)
    step=float(lambda_increment);lam=a['lambda_H_base']+step
    if not np.isfinite(step)or step==0 or lam<=0:raise ValueError('nonzero finite stiffness increment preserving positive lambda required')
    rep=deepcopy(a['representation']);rep['scalar_matching']['lambda_H']=lam
    initial=a['raw_pair']+step*a['raw_parameter_response'];out.mkdir(parents=True)
    refs=dict(a['input_hashes'])
    for name in('muon_lambda_coupled_birth_continuation','muon_birth_area_endpoint_response','muon_corrected_birth_mean','muon_magnetic_birth_ward_mean','muon_birth_finite_geometric_trace_endpoint'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    checks=[]
    for d in(step,step/2):
        varied=deepcopy(a['representation']);varied['scalar_matching']['lambda_H']=a['lambda_H_base']+d
        value=moving_endpoint_rows(a['raw_pair'],a['reference_pair'],varied,a['state_weights'],a['normalization_coordinates'],compute_cotangent_derivative=False)
        estimate=(value['residual']-a['base']['updated_residual'])/d
        checks.append(dict(step=d,source_difference_norm=float(np.linalg.norm(estimate-a['lambda_parameter_source'])),source_norm=float(np.linalg.norm(estimate))))
        print(json.dumps(dict(stage='lambda_parameter_check',**checks[-1]),sort_keys=True),flush=True)
    def checkpoint(k,raw,current,scale,history):
        folder=out/'checkpoints'/f'accepted_{k:04d}';folder.mkdir(parents=True)
        _compressed_npz(folder/'application.npz',dict(raw_pair=raw,residual=current['residual'],jacobian=current['jacobian'],row_scale=scale))
        print(json.dumps(dict(stage='coupled_lambda_newton',iteration=k,scaled_residual=float(np.linalg.norm(scale*current['residual']))),sort_keys=True),flush=True)
    solved=solve_moving_endpoint(initial,a['reference_pair'],rep,a['state_weights'],a['normalization_coordinates'],max_iterations=max_iterations,checkpoint=checkpoint)
    arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
    for key in('affine_profile_reference_states','affine_interior_projection','affine_difference_coefficients','wall_trace_map','wall_radial_derivative_map','rho','radial_quadrature','gauge_basis','gauge_radial_basis','radial_value_map','radial_derivative_map'):
        arrays[key]=rep[key]
    arrays.update({'response_'+k:v for k,v in a['response'].items()if isinstance(v,np.ndarray)})
    arrays.update(initial_raw_pair=initial,updated_raw_pair=solved['raw'],updated_residual=solved['application']['residual'],updated_jacobian=solved['application']['jacobian'],row_scale=solved['row_scale'],coordinate_weights=solved['coordinate_weights'])
    _compressed_npz(out/'application.npz',arrays)
    delta=solved['raw']-a['raw_pair']
    if any(sha256((root/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same birth source owner changed')
    md=dict(classification='EVALUATED_SAME_MOVING226_COUPLED_HIGGS_STIFFNESS_CONTINUATION',status=solved['status'],lambda_H_base=a['lambda_H_base'],lambda_H=lam,lambda_increment=step,
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),history=solved['history'],finite_parameter_checks=checks,
        action_parameters=rep['endpoint_action_parameters'],scalar_matching=rep['scalar_matching'],
        groups={k:dict(indices=list(range(*s)),norm=float(np.linalg.norm(solved['application']['residual'][slice(*s)])))for k,s in solved['application']['groups'].items()},
        changed_coordinate_norms=dict(geometry=float(np.linalg.norm(delta[:,:100])),gauge=float(np.linalg.norm(delta[:,100:260])),Higgs=float(np.linalg.norm(delta[:,260:268]))),
        original_row_residual_norm=float(np.linalg.norm(solved['application']['residual'])),scaled_residual=solved['scaled_residual'],
        parameter_source_norm=float(np.linalg.norm(a['lambda_parameter_source'])),parameter_response_norm=float(np.linalg.norm(a['raw_parameter_response'])),
        arithmetic_certificate=a['response']['stored_action_arithmetic_certificate'],named_Ward_compatibility_max=float(np.max(abs(a['response']['named_source_compatibility']))),
        physical_phase_continuation_recomputed=False,physical_scalar_resonance_or_energy_unit_selected=False,physical_Pauli_value=False,
        error_scope='original moving226 equations re-evaluated on one changed field/geometry vector; fixed numerical reference and minimum weighted continuation, binary64 action/D3/Newton production not rigorously enclosed')
    for key in('affine_profile_enrichment','gauge_labels','gauge_count','radial_points','cap_points'):
        md[key]=a['base_receipt'][key]
    (out/'result.json').write_text(json.dumps(md,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--lambda-increment',type=float,default=.001);p.add_argument('--max-iterations',type=int,default=3)
    b=p.parse_args();print(json.dumps(materialize_lambda_coupled_birth(b.base_directory,b.output,lambda_increment=b.lambda_increment,max_iterations=b.max_iterations),sort_keys=True))
