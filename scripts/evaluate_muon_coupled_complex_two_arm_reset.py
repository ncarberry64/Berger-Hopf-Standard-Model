"""Apply full v/y reset projection and an original226 Newton source probe."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_two_arm_reset import holomorphic_two_arm_reset
from bhsm.interface.muon_coupled_phase_trace_projection import coupled_phase_trace_projection,coupled_phase_trace_parameter
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,output,difference_step,newton_probe):
    source=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve full coupled292 reset/source applications')
    refs={}
    def read(name):
        p=source/name;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read('result.json');refs.update(md['input_hashes']);a=read('full_original_two_arm_action.npz');r=read('historical_held_reset.npz');p=read('true_phase_projection_inputs.npz')
    for name in ('full_original_two_arm_action.npz','historical_held_reset.npz','true_phase_projection_inputs.npz'):
        if refs[(source/name).relative_to(ROOT).as_posix()]!=md['archives'][name]['sha256']:raise ValueError('same held-pair projection input changed')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];params=md['action_parameters']
    common=np.zeros((6,3));common[[0,2],0]=1;common[[1,3],1]=1;common[[4,5],2]=1
    projection=coupled_phase_trace_projection(p['full_Legendre_block'],p['trace_map'],p['named_frames'],p['temporal_dual'],common)
    parameter=coupled_phase_trace_parameter(projection,p['area_D_parameter'],p['area_temporal_dual_parameter'])
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        file=out/name;_compressed_npz(file,arrays)
        if file.stat().st_size>10*1024**2:raise RuntimeError('split full coupled reset/source rows')
        archives[name]=dict(bytes=file.stat().st_size,sha256=sha256(file.read_bytes()).hexdigest())
    save('full_coupled_phase_projection.npz',{k:v for k,v in projection.items()if isinstance(v,np.ndarray)})
    save('full_coupled_area_parameter.npz',{k:v for k,v in parameter.items()if isinstance(v,np.ndarray)})
    physical=r['residual'].copy();source_gamma=r['area_parameter_source'].copy();groups=md['groups']
    baseB=np.asarray(projection['common_trace_map']);port=projection['common_trace_cotangent'];portgamma=parameter['common_trace_cotangent_parameter']
    # Recover the inherited attachment normalization from the original
    # component map; use its owned real normalization, never a new fit.
    from bhsm.interface.aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_symmetric_power
    attachment=_attachment_jacobian_at_order(12,p['normalization_coordinates']);attachment_norm=_symmetric_power(attachment@attachment.T,.5)
    ai=groups['common_attachment_temporal_dual']['indices'];ni=groups['common_normal_temporal_dual']['indices']
    physical[ai]=attachment_norm@port[:2];physical[ni]=port[2]
    source_gamma[ai]=attachment_norm@portgamma[:2];source_gamma[ni]=portgamma[2]
    print(json.dumps(dict(stage='full_coupled292_held_reset_projection',phase_rows_max=float(np.max(abs(projection['original_phase_rows']))),
        coupled_reset_rows_max=float(np.max(abs(physical))),coupled_minus_fixed_y_cotangent_norm=float(np.linalg.norm(port-r['projected_cotangent'])))),flush=True)
    # One full-Hessian directional contraction retains all v/y placements.
    R=a['master_lift'];ids=a['phase_indices'];eta=R.T@a['raw_pair'].reshape(-1)
    av=np.zeros(504,complex);av[ids]=projection['adjoint'][:292]
    b=np.zeros((504,6),complex);b[ids]=projection['phase_lift']
    mw=abs(R.T)@np.tile(np.r_[p['state_weights'],np.ones(170)],2);magnitude=float(np.max(abs(mw*av)));unit=av/magnitude
    print(json.dumps(dict(stage='full_coupled_projection_third_action',step=difference_step,magnitude=magnitude)),flush=True)
    plus=holomorphic_two_arm_action((R@(eta+difference_step*unit)).reshape(2,268),a['reference_pair'],rep,**params)['hessian']
    minus=holomorphic_two_arm_action((R@(eta-difference_step*unit)).reshape(2,268),a['reference_pair'],rep,**params)['hessian']
    derivative=magnitude*(plus-minus)/(2*difference_step);third=derivative@b
    theta_first=np.zeros((292,504),complex);theta_first[:212]=a['temporal_cotangent_first']
    contact=np.empty((504,6),complex)
    for j,db in enumerate(r['trace_DB']):
        de=np.c_[db,np.zeros((6,80))]
        contact[j]=projection['adjoint'][:292]@de.T@projection['port_reactions']+projection['adjoint'][292:298]@de@projection['phase_lift']
    port_first=common.T@(theta_first.T@projection['phase_lift']-third-contact).T
    J=r['analytic_first_rows'].copy();J[ai]=attachment_norm@port_first[:2];J[ni]=port_first[2]
    save('full_coupled_original_reset.npz',dict(raw_pair=a['raw_pair'],reference_pair=a['reference_pair'],master_lift=R,
        original226_reset_rows=physical,original226_Jacobian=J,area_parameter_source=source_gamma,
        coupled_trace_cotangent=port,coupled_trace_cotangent_first=port_first,
        full_Hessian_direction=unit,full_Hessian_direction_magnitude=np.array(magnitude),
        plus_Hessian=plus,minus_Hessian=minus,third_action_contraction=third,trace_second_contact=contact,
        named_frame_map=p['named_frames'],original_canonical_child_target=a['child_actual_canonical_momentum_target']))
    probe=dict(performed=False)
    if newton_probe:
        # A represented Newton application keeps every original source
        # row. Its least-norm coordinate choice is computational; rank and
        # unresolved original rows are exported, never a physical quotient.
        row_scale=1/np.maximum(np.max(abs(J/mw[None,:]),axis=1),1.)
        scaled=row_scale[:,None]*J/mw[None,:]
        correction,residuals,rank,singular=np.linalg.lstsq(scaled,-row_scale*physical,rcond=None)
        correction=correction/mw;linear=J@correction+physical
        save('original226_Newton_source_probe.npz',dict(master_correction=correction,original_linearized_rows=linear,
            row_scale=row_scale,coordinate_weights=mw,singular_values=singular,all_original226_source_rows=physical))
        probe=dict(performed=True,rank=int(rank),master_correction_norm=float(np.linalg.norm(correction)),
            original_linearized_rows_max=float(np.max(abs(linear))),trials=[])
        old_merit=float(np.linalg.norm(row_scale*physical));accepted=False
        for damping in (1.,.25,.0625,.015625):
            try:
                trialraw=(R@(eta+damping*correction)).reshape(2,268)
                trial=holomorphic_two_arm_reset(trialraw,a['reference_pair'],rep,p['state_weights'],p['normalization_coordinates'],**params)
                tp=trial['action'];tid=np.r_[tp['velocity_indices'],tp['algebraic_indices']]
                from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
                frames=[canonical_central_frame(x,rep)for x in trialraw];F=np.zeros((4,292),complex)
                for arm,fr in enumerate(frames):
                    localids=np.r_[arm*106+np.arange(106),212+arm*40+np.arange(40)]
                    F[np.ix_(arm*2+np.arange(2),localids)]=fr['named_frame_covectors']
                pp=coupled_phase_trace_projection(tp['hessian'][np.ix_(tid,tid)],np.c_[trial['trace_B'],np.zeros((6,80))],F,
                    np.r_[tp['temporal_cotangent'],np.zeros(80)],common)
                rr=trial['residual'].copy();rr[ai]=attachment_norm@pp['common_trace_cotangent'][:2];rr[ni]=pp['common_trace_cotangent'][2]
                merit=float(np.linalg.norm(row_scale*rr));good=merit<old_merit
                probe['trials'].append(dict(damping=damping,merit=merit,all_original_rows_max=float(np.max(abs(rr))),accepted=good))
                save(f'original226_probe_damping_{str(damping).replace(".","p")}.npz',dict(raw_pair=trialraw,original226_rows=rr,
                    full_gradient=tp['gradient'],full_Hessian=tp['hessian']))
                if good:accepted=True;break
            except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError)as error:
                probe['trials'].append(dict(damping=damping,accepted=False,error=str(error)))
        probe['accepted_decrease_only_not_compatible']=accepted
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for file in(Path(__file__),'tests/test_muon_coupled_phase_trace_projection.py','tests/test_muon_holomorphic_two_arm_action.py'):
        file=Path(file);file=file if file.is_absolute()else ROOT/file;refs[file.relative_to(ROOT).as_posix()]=sha256(file.read_bytes()).hexdigest()
    if any(sha256((ROOT/path).read_bytes()).hexdigest()!=h for path,h in refs.items()):raise RuntimeError('same full coupled action source changed')
    record=dict(classification='EVALUATED_TRUE_FULL292_COMPLEX_TWO_ARM_RESET_PROJECTION_AND_ORIGINAL_SOURCE_APPLICATION',
        input_hashes=refs,archives=archives,groups={k:dict(v,full_coupled_residual_max=float(np.max(abs(physical[v['indices']]))))for k,v in groups.items()},
        full_coupled_reset_rows_max=float(np.max(abs(physical))),coupled_minus_historical_cotangent_norm=float(np.linalg.norm(port-r['projected_cotangent'])),
        all292_original_phase_rows_max=float(np.max(abs(projection['original_phase_rows']))),
        full302_saddle_rows_max=float(np.max(abs(projection['saddle_rows']))),
        full302_transpose_adjoint_rows_max=float(np.max(abs(projection['analytic_adjoint_rows']))),
        area_cotangent_dual_identity_max=float(np.max(abs(parameter['cotangent_dual_identity_rows']))),
        area_parameter_original_saddle_rows_max=float(np.max(abs(parameter['parameter_saddle_rows']))),
        full_Lyy_and_Lyy_parameter_retained=True,original_frame_reactions_retained=True,original226_Newton_probe=probe,
        full_Jacobian_third_action_scope='one centered holomorphic full-Hessian directional contraction, allphase placements, exact traceDB contacts; binary finite-difference derivative not enclosure',
        difference_step=difference_step,parent_or_pair_stationarity_claimed=False,physical_reference_first_hit_or_Pauli_selected=False,
        gamma_assigned=False,gamma_law=md['gamma_law'],action_parameters=params,
        error_scope='actual complex full536 signed action, full292/302 Legendre/trace/frame application and explicit original226 reset source probe; no physical firsthit/exterior matching or anomaly enclosure')
    path=out/'result.json';path.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='full_coupled_complex_reset_complete',original_rows_max=record['full_coupled_reset_rows_max'],
        probe=probe,result_sha256=sha256(path.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-folder',type=Path,
        default=Path('artifacts/muon_holomorphic_two_arm_reset_20261012/run_1'))
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--difference-step',type=float,default=2e-5)
    parser.add_argument('--newton-probe',action='store_true');args=parser.parse_args()
    materialize(args.source_folder,args.output,args.difference_step,args.newton_probe)
