"""Apply actual moving-normal shape/embedding source at the complex action face."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_per_arm_canonical_source import clean
from bhsm.interface.muon_actual_normal_shape_source import proper_normal_shape_coefficient,mixed_normal_shape_weak_source
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_child_action import _affine_geometry
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,anchored_holomorphic_chart,_response
from bhsm.interface.muon_holomorphic_two_arm_reset import holomorphic_moving_trace
from bhsm.interface.muon_complex_paired_normal_action import complex_proper_normal_trace
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(history,geometry_return,output,difference_step):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve actual shape action applications')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    md=read(history,'result.json');gm=read(geometry_return,'result.json')
    if not md['all_steps_and_endpoints_passed']:raise ValueError('actual complex action source required')
    key=next(p for p in md['input_hashes']if p.endswith('candidate.npz'));base=read(Path(key).parent,Path(key).name)
    last=read(history,'actual_complex_endpoint_comparison.npz')
    endpoint=read(history,f"step_{md['steps']-1:04d}_endpoint.npz")
    returned=read(geometry_return,'actual_endpoint_geometry_and_all67_natural_return.npz')
    if not np.array_equal(returned['endpoint_raw'],endpoint['endpoint_raw']):raise ValueError('same actual complex face required')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    t=endpoint['coordinate_time'].item();child=endpoint['endpoint_raw'];parent=_affine_geometry(base['raw_pair'][0],t)
    ref=np.array([_affine_geometry(r,t)for r in base['reference_pair']]);pair=np.array([parent,child])
    print(json.dumps(dict(stage='actual_full_two_arm_shape_face',coordinate_time=clean(t)),sort_keys=True),flush=True)
    action=holomorphic_two_arm_action(pair,ref,rep,**md['action_parameters']);eta=(P.T@pair.T).T.reshape(-1)
    child_rate=P.T@last['actual_raw_time'];parent_raw_rate=np.zeros(268,complex)
    parent_raw_rate[:37]=base['raw_pair'][0,37:74];parent_raw_rate[98]=base['raw_pair'][0,99]
    rate=np.r_[P.T@parent_raw_rate,child_rate]
    def shape(raw,G,H,r):
        a=proper_normal_shape_coefficient(raw,P);da=np.r_[np.zeros(252,complex),a['gradient']]
        dd=np.zeros((504,504),complex);dd[252:,252:]=a['hessian']
        return mixed_normal_shape_weak_source(G,H,r,a['value'],da,dd,normal_position=252+37,
            normal_velocity=252+143,amplitude=1,amplitude_coordinate_first=0),a
    S,a=shape(child,action['gradient'],action['hessian'],rate)
    Sa,_=shape(child,action['area_gradient_per_gamma'],action['area_Hessian_per_gamma'],rate)
    b=S['shape_direction'];normal=complex_proper_normal_trace(child,P)
    tr=holomorphic_moving_trace(child);q,v,m,delta,dr,wall,Cstar=_geometry_variables(child[:100])
    chart=anchored_holomorphic_chart(delta.value);response=_response(wall,delta,dr,chart)
    raw_shape=P@b[252:];material_rows=np.array([response[k].gradient@raw_shape[:100]for k in ('f','sigma')])
    response_base=np.array([response['f'].value-np.pi/4,response['sigma'].value])
    proper_pair=normal['proper_normal']@b[252:358]
    temporal=-S['ordinary_action_shape_source'][action['velocity_indices']]
    weak_temporal=-S['full_weak_state_source'][action['velocity_indices']]
    weak_rate_temporal=-S['full_weak_phase_rate_source'][action['velocity_indices']]
    # Independently check the literal mixed derivative of G(eta).b(eta,eta_t).
    # This is a supplied derivative control, not an admitted response mode.
    d=np.zeros(504,complex);actual=returned['full_phase_direction_high']+returned['full_phase_direction_low']
    k=int(np.argmax(np.max(abs(actual),axis=0)));d[252:]=actual[:,k]/np.max(abs(actual[:,k]))
    d[0]=.1+.03j;d[37]=.02-.01j;d[106]=.04+.02j;d[212]=.03-.01j
    rd=rate/max(np.max(abs(rate)),1.)*(1+.1j)
    literal=S['literal_shape_action_state_gradient']@d+S['full_weak_phase_rate_source']@rd
    comparisons=[]
    for h in (difference_step,difference_step/2):
        values=[]
        for sign in (-1,1):
            shifted=eta+sign*h*d;raw=(np.kron(np.eye(2),P)@shifted).reshape(2,268)
            aa=holomorphic_two_arm_action(raw,ref,rep,**md['action_parameters'])
            ss,_=shape(raw[1],aa['gradient'],aa['hessian'],rate+sign*h*rd)
            values.append(ss['shape_action_first'].item())
        fd=(values[1]-values[0])/(2*h)
        rec=dict(step=h,literal_derivative=clean(literal),finite_derivative=clean(fd),
            absolute_difference=float(abs(fd-literal)),relative_difference=float(abs(fd-literal)/max(abs(literal),np.finfo(float).tiny)))
        comparisons.append(rec);print(json.dumps(dict(stage='actual_shape_mixed_control',**rec),sort_keys=True),flush=True)
    out.mkdir(parents=True)
    def save(name,values):
        p=out/name;_compressed_npz(p,{k:v for k,v in values.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split shape action result')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('actual_shape_source_and_embedding.npz',dict(**S,raw_pair=pair,reference_pair=ref,
        original_full_gradient=action['gradient'],original_full_Hessian=action['hessian'],
        area_gradient_per_gamma=action['area_gradient_per_gamma'],area_Hessian_per_gamma=action['area_Hessian_per_gamma'],
        actual_master_coordinate_rate=rate,child_original_raw_time=last['actual_raw_time'],
        proper_normal_shape_gradient=a['gradient'],proper_normal_shape_Hessian=a['hessian'],
        actual_geometric_trace_shape=tr['first']@raw_shape[:100],
        actual_attachment_trace_shape=tr['attachment_first']@raw_shape[:100],
        proper_normal_pairing=np.array(proper_pair),material_response_base= response_base,
        material_response_shape_rows=material_rows,
        ordinary_signed_temporal_face_shape=temporal,weak_state_temporal_covector=weak_temporal,
        weak_phase_rate_temporal_covector=weak_rate_temporal,
        derivative_control_state=d,derivative_control_phase_rate=rd,
        coordinate_time=np.array(t)))
    save('common_stratum_area_shape_coefficient.npz',Sa)
    x=np.r_[np.arange(106),252+np.arange(106)];vv=action['velocity_indices'];yy=action['algebraic_indices']
    def norms(z):return dict(full=float(np.linalg.norm(z)),x=float(np.linalg.norm(z[x])),v=float(np.linalg.norm(z[vv])),y=float(np.linalg.norm(z[yy])),
        parent=float(np.linalg.norm(z[:252])),child=float(np.linalg.norm(z[252:])))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):
            p=Path(path);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in (Path(__file__),ROOT/'tests/test_muon_actual_normal_shape_source.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual material/action source changed')
    result=dict(classification='EXECUTED_ACTUAL_COMPLEX_PROPER_NORMAL_MIXED_ACTION_SOURCE_WITH_EMBEDDING_AND_RATE_CONTACT',
        input_hashes=pins,archives=archives,action_parameters=md['action_parameters'],
        original_birth226_max=gm['original_birth226_max'],actual_coordinate_time=clean(t),
        actual_child_original146_max=float(np.max(abs(np.r_[action['gradient'][358:464]-endpoint['endpoint_Pi'],action['gradient'][464:]]))),
        actual_joint_Ly_max=float(np.max(abs(action['gradient'][yy]))),
        full_shape_action_first=clean(S['shape_action_first'].item()),
        ordinary_H_shape_source_norms=norms(S['ordinary_action_shape_source']),
        moving_embedding_source_norms=norms(S['moving_embedding_action_source']),
        full_weak_state_source_norms=norms(S['full_weak_state_source']),
        full_weak_phase_rate_source_norms=norms(S['full_weak_phase_rate_source']),
        held_common_area_state_source_norms=norms(Sa['full_weak_state_source']),
        held_common_area_rate_source_norms=norms(Sa['full_weak_phase_rate_source']),
        proper_normal_pairing=clean(proper_pair),material_f_sigma_response_base=clean(response_base),
        material_f_sigma_shape_rows_max=float(np.max(abs(material_rows))),
        shape_operator_minus_literal_action_gradient_max=float(np.max(abs(S['stored_mixed_source_minus_literal_gradient']))),
        derivative_controls=comparisons,original_actual_rate_rows_max=md['actual_endpoint_comparison']['original_tangent_rows_max'],
        source_law='b_s=a psi, b_v=(D_eta a eta_t)psi+a psi_t; a=1/N37; D_eta(G.b)=H.T b+Db.T G, while stored mixed operator H b is exported separately; D_eta_t(G.b)=Db_rate.T G',
        normal_trial='unit proper-normal graph amplitude psi=1, coordinate psi_t=0 at the actual face; computational source, not selected physical mode',
        material_coefficient_fixed_during_shape_and_embedding_not_added_again=True,
        parent_affine_source_feedback_kept_in_full504_action=True,
        parent_affine_snapshot_not_declared_solved_canonical_parent=True,
        common_M8_area_per_gamma_kept_on_both_arms=True,
        gamma_law='gamma=alpha_FSC*c^(-7/2), alpha and c unselected; held-state affine source coefficient does not solve parameter stationarity',
        full_weak_rate_contact_not_set_zero_or_already_integrated=True,
        next_chronological_action='Apply the exported state and rate covectors to actual canonical/source variations, retain the rate-contact temporal boundary and coefficient-corner terms, then apply the full exterior Noether/source return and all226/natural/energy/common gamma(c) formation equations.',
        physical_base_response_mode_outgoing_domain_or_pole_admitted=False,
        error_scope='Literal full signed action and analytic geometry twojet at actual complex point; two weighted directional/halved finite-difference controls only. Original rate residual, action/quadrature, temporal/domain and physical observable errors are not enclosed.')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='actual_shape_source_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        state_norm=result['full_weak_state_source_norms']['full'],rate_norm=result['full_weak_phase_rate_source_norms']['full'],
        embedding_norm=result['moving_embedding_source_norms']['full'],material_response_rows=result['material_f_sigma_shape_rows_max']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history',type=Path,default=Path('artifacts/muon_reached_complex_normal_history_20261012/trial_0000_run_1'))
    p.add_argument('--geometry-return',type=Path,default=Path('artifacts/muon_reached_geometry_canonical_return_20261012/run_1'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--difference-step',type=float,default=2e-5)
    a=p.parse_args();run(a.history,a.geometry_return,a.output,a.difference_step)
