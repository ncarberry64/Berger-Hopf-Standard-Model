"""Two-step literal action-direction checks on final outgoing source stages.

This compares fresh action gradient differences with supplied Hessian source
predictions. It does not refine a stored matrix solve or enclose action error.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
import numpy as np
from flint import acb, acb_mat, ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_current_source import holomorphic_current_stage
from bhsm.interface.muon_stored_admission_correction import _matrix, _mid, _upper
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def _split(z):
    hi=_mid(z)[:,0]
    return hi,_mid(z-_matrix(hi))[:,0]


def _complex(z):
    return complex(float(z.real.mid()),float(z.imag.mid()))


def materialize(source_folder,output,normalized_step,precision_bits):
    source=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve bounded fresh action accuracy controls')
    if normalized_step<=0 or precision_bits<128:
        raise ValueError('positive declared normalized step and exact-stored arithmetic required')
    pins={};archives={}
    def read(folder,name,md=None):
        p=ROOT/folder/name;b=p.read_bytes();digest=sha256(b).hexdigest()
        pins[p.relative_to(ROOT).as_posix()]=digest
        if md is not None and digest!=md['archives'][name]['sha256']:
            raise ValueError('completed actual source archive changed')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(source_folder,'result.json')
    if md['classification']!='EVALUATED_CHANGING_NONLINEAR_CANONICAL_ARM_SOURCE_APPLICATION':
        raise ValueError('completed actual changing source receipt required')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    trace_folder=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1')
    tm=read(trace_folder,'result.json')
    weight_names=[p for p in tm['input_hashes']if p.endswith('true_phase_projection_inputs.npz')]
    if len(weight_names)!=1:raise ValueError('one declared original state-weight owner required')
    wp=Path(weight_names[0]);wb=(ROOT/wp).read_bytes()
    if sha256(wb).hexdigest()!=tm['input_hashes'][wp.as_posix()]:raise ValueError('original weights changed')
    pins[wp.as_posix()]=sha256(wb).hexdigest()
    with np.load(ROOT/wp,allow_pickle=False)as z:geometry_weights=z['state_weights'].copy()
    if geometry_weights.shape!=(98,)or np.any(geometry_weights<=0):raise ValueError('original98 geometry comparison weights required')
    raw_weights=np.r_[geometry_weights,np.ones(170)]
    records={};out.mkdir(parents=True)
    def save(name,values):
        p=out/name;_compressed_npz(p,values)
        if p.stat().st_size>10*1024**2:raise ValueError('split actual direction controls')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    old=ctx.prec;ctx.prec=precision_bits
    try:
        for case in('normal_basis','area_source'):
            names=sorted(n for n in md['archives']if n.startswith('outgoing_')and n.endswith('_'+case+'_source_response.npz'))
            if not names:raise ValueError('actual outgoing consumed direction missing; do not fill zero')
            name=names[-1];s=read(source_folder,name,md)
            raw=np.stack((s['parent_source_stage_raw'],s['stage_raw']))
            refs=s['reference_stage_pair']
            dh=np.stack((s['parent_source_stage_raw_direction_high'],s['stage_raw_direction_high']))
            dl=np.stack((s['parent_source_stage_raw_direction_low'],s['stage_raw_direction_low']))
            if (raw.shape!=(2,268)or refs.shape!=(2,268)or dh.shape!=raw.shape or dl.shape!=raw.shape
                    or np.any(s['reference_stage_direction_high']!=0)or np.any(s['reference_stage_direction_low']!=0)):
                raise ValueError('same actual stage, two-term parent/child and explicitly held refs required')
            combined=_matrix(dh.reshape(-1))+_matrix(dl.reshape(-1))
            magnitude=max(float((abs(combined[i,0])*float(np.tile(raw_weights,2)[i])).upper())for i in range(536))
            if not np.isfinite(magnitude)or magnitude==0:raise ValueError('nonzero actual weighted source required')
            direction_h=np.r_[P.T@dh[0],P.T@dh[1]]
            direction_l=np.r_[P.T@dl[0],P.T@dl[1]]
            a=holomorphic_two_arm_action(raw,refs,rep,**md['action_parameters'])
            pred=_matrix(a['hessian'][252:])*(_matrix(direction_h)+_matrix(direction_l))
            direct=a['area_gradient_per_gamma'][252:]if case=='area_source'else np.zeros(252,complex)
            prediction_full=pred+_matrix(direct)
            G0=a['gradient'][252:]
            base_current=holomorphic_current_stage(raw[1],np.stack((dh[1],dl[1]),axis=-1),
                raw[0],np.stack((dh[0],dl[0]),axis=-1),refs,np.zeros((2,268,2),complex),rep,side='child')
            temporal_pred=-1j*(_matrix(base_current['temporal_connection_first'][0].reshape(-1))
                +_matrix(base_current['temporal_connection_first'][1].reshape(-1)))
            body_pred=_matrix(base_current['Hcan_first'][0].reshape(-1))+_matrix(base_current['Hcan_first'][1].reshape(-1))
            ph,pl=_split(pred);fh,fl=_split(prediction_full)
            rec=dict(source_archive=name,weighted_direction_magnitude=magnitude,
                stage_coefficient_Hessian_change_max=float(np.max(abs(a['hessian'][252:,252:]-s['stage_Hessian']))),
                reference_directions_held=True,direct_area_source_kept_separate=True,steps={})
            arrays=dict(raw_pair=raw,reference_pair=refs,raw_direction_high=dh,raw_direction_low=dl,
                raw_comparison_weights=raw_weights,child_gradient_at_base=G0,
                predicted_action_derivative_high=ph,predicted_action_derivative_low=pl,
                direct_area_gradient_source=direct,predicted_total_source_high=fh,predicted_total_source_low=fl,
                child_Hessian=a['hessian'][252:,252:],parent_to_child_Hessian=a['hessian'][252:,:252],
                literal_normal_transpose_high=s['literal_transpose_solution_high'],
                literal_normal_transpose_low=s['literal_transpose_solution_low'],
                supplied_stage_normal_covector=s['proper_normal_covector'])
            errors=[]
            for label,h in(('primary',normalized_step),('half_step',normalized_step/2)):
                epsilon=h/magnitude;branches=[];bodies=[];temporals=[]
                for sign in(1,-1):
                    shifted=raw+sign*epsilon*dh+sign*epsilon*dl
                    b=holomorphic_two_arm_action(shifted,refs,rep,**md['action_parameters'])
                    branches.append(b['gradient'][252:])
                    current=holomorphic_current_stage(shifted[1],np.zeros((268,1),complex),
                        shifted[0],np.zeros((268,1),complex),refs,np.zeros((2,268,1),complex),rep,side='child')
                    bodies.append(current['Hcan']);temporals.append(-1j*current['temporal_connection'])
                    save(case+'_'+label+('_plus.npz'if sign==1 else'_minus.npz'),
                        dict(raw_pair=shifted,reference_pair=refs,full_gradient504=b['gradient'],
                            child_gradient252=b['gradient'][252:],action_value=np.array(b['value']),
                            wall_connection=b['branch_fields'][1]['wall'],child_Hcan=current['Hcan'],
                            child_temporal_body=-1j*current['temporal_connection']))
                scale=acb(2*epsilon)
                fd=(_matrix(branches[0])-_matrix(branches[1]))/scale
                err=fd-pred;fdh,fdl=_split(fd);eh,el=_split(err)
                errors.append(eh+el)
                # Error in THIS supplied action gradient propagates through
                # the existing literal normal transpose, with no new state.
                hs=complex(s['coordinate_time_step'].item());hsb=acb(hs.real,hs.imag)
                zero=acb_mat(106,1)
                rhs_error=acb_mat([[v[i,0]]for v in(zero,
                    hsb*acb_mat([[err[i,0]]for i in range(106)]),
                    -acb_mat([[err[i,0]]for i in range(106,212)]),
                    -acb_mat([[err[i,0]]for i in range(212,252)]),acb_mat(2,1))for i in range(v.nrows())])
                left=_matrix(s['literal_transpose_solution_high'])+_matrix(s['literal_transpose_solution_low'])
                projected=left.transpose()*rhs_error
                temporal_fd=(_matrix(temporals[0].reshape(-1))-_matrix(temporals[1].reshape(-1)))/scale
                body_fd=(_matrix(bodies[0].reshape(-1))-_matrix(bodies[1].reshape(-1)))/scale
                temporal_error=_mid(temporal_fd-temporal_pred)[:,0].reshape(18,18)
                body_error=_mid(body_fd-body_pred)[:,0].reshape(18,18)
                pi_error=-(eh+el)[106:212]
                error_norm=float(np.linalg.norm(eh+el));prediction_norm=float(np.linalg.norm(ph+pl))
                pair=_complex(projected[0,0])
                rec['steps'][label]=dict(normalized_step=h,source_parameter_step=epsilon,
                    original_child_gradient_max_error=_upper(err),original_child_gradient_relative_error=error_norm/max(prediction_norm,np.finfo(float).tiny),
                    original_child_gradient_error_norm=error_norm,predicted_derivative_norm=prediction_norm,
                    projected_stage_normal_pairing_defect=[pair.real,pair.imag],
                    projected_stage_normal_pairing_defect_absolute_upper=_upper(projected),
                    child_temporal_dual_error_norm=float(np.linalg.norm(pi_error)),
                    child_temporal_geometry_error_norm=float(np.linalg.norm(pi_error[:38])),
                    child_temporal_gauge_error_norm=float(np.linalg.norm(pi_error[38:102])),
                    child_temporal_Higgs_error_norm=float(np.linalg.norm(pi_error[102:])),
                    full18_body_derivative_error_norm=float(np.linalg.norm(body_error)),
                    full18_temporal_body_derivative_error_norm=float(np.linalg.norm(temporal_error)),
                    full18_temporal_body_derivative_error_max=float(np.max(abs(temporal_error))))
                arrays.update({label+'_gradient_FD_high':fdh,label+'_gradient_FD_low':fdl,
                    label+'_gradient_derivative_defect_high':eh,label+'_gradient_derivative_defect_low':el,
                    label+'_total_source_FD_high':_split(fd+_matrix(direct))[0],
                    label+'_total_source_FD_low':_split(fd+_matrix(direct))[1],
                    label+'_temporal_face_dual_derivative_defect':pi_error,
                    label+'_full18_body_derivative_defect':body_error,
                    label+'_full18_temporal_body_derivative_defect':temporal_error,
                    label+'_literal_normal_readout_source_defect':np.array(pair)})
                print(json.dumps(dict(stage='fresh_action_accuracy',case=case,step=label,**rec['steps'][label]),sort_keys=True),flush=True)
            rec['two_step_derivative_defect_difference_norm']=float(np.linalg.norm(errors[0]-errors[1]))
            rec['normal_readout_scope']='existing literal transpose midpoint-normal test on final displacement; no physical mode or endpoint pole'
            rec['temporal_dual_scope']='outgoing action face derivative -deltaPi with geometry38/gauge64/Higgs4 retained; no physical current normalization'
            records[case]=rec;save(case+'_action_derivative_controls.npz',arrays)
    finally:ctx.prec=old
    for name,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p:
            try:rel=Path(p).relative_to(ROOT).as_posix()
            except ValueError:continue
            pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual source or helper changed')
    result=dict(classification='BOUNDED_TWO_STEP_FRESH_LITERAL_ACTION_DERIVATIVE_ACCURACY_AT_ACTUAL_OUTGOING_SOURCES',
        archives=archives,input_hashes=pins,action_parameters=md['action_parameters'],applications=records,
        source_folder=source_folder.as_posix(),comparison_normalized_step=normalized_step,precision_bits=precision_bits,
        source_functions_and_wall_enter_full_literal_graph_before_coefficient_restriction=True,
        independent_raw_direction_not_conjugated=True,full_Higgs_source_retained=True,
        reference_seed_held_no_event_or_clock_selected=True,known_direct_area_source_separate=True,
        stored_matrix_refinement_not_repeated=True,physical_a_mu_or_pole_or_mode_selected=False,
        error_scope='two finite directional action evaluations per sign/step on each supplied normal/area source; Acb only evaluates arithmetic of stored gradient differences and predictions. No action/discretization/physical outward enclosure or anomaly bound.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='fresh_action_accuracy_complete',result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-folder',type=Path,default=Path('artifacts/muon_changing_canonical_source_20261012/run_3'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--normalized-step',type=float,default=2e-5)
    p.add_argument('--precision-bits',type=int,default=192)
    a=p.parse_args();materialize(a.source_folder,a.output,a.normalized_step,a.precision_bits)
