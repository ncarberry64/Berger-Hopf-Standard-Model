"""Apply actual moving trial traces and full local strong Jacobi response."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_complex_normal_trace_motion import proper_normal_trace_motion,moving_frequency_trial,strong_jacobi_normal_response
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def zjson(x):
    if isinstance(x,dict):return{k:zjson(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[zjson(v)for v in x]
    if isinstance(x,(complex,np.complexfloating)):return[float(x.real),float(x.imag)]
    if isinstance(x,np.ndarray):return zjson(x.tolist())
    if isinstance(x,np.generic):return x.item()
    return x


def materialize(source_folder,output):
    source=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve moving trace/action applications')
    rb=(source/'result.json').read_bytes();md=json.loads(rb);refs=dict(md['input_hashes']);refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    def load(name):
        p=source/name;b=p.read_bytes()
        if sha256(b).hexdigest()!=md['archives'][name]['sha256']:raise ValueError('same normal application archive changed')
        refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    inputs=load('same_action_inputs.npz');frequency=load('frequency_application.npz');clock=load('clock_and_joint_tangent.npz')
    rawrate=(inputs['master_lift']@clock['canonical_full_master_coordinate_rate']).reshape(2,268)
    raw=inputs['raw_pair'];P=inputs['one_lift'];motion=[proper_normal_trace_motion(x,P,r)for x,r in zip(raw,rawrate)]
    Tdot=np.zeros_like(frequency['normal_and_constraint_rows']);Tdot[0,:106]=motion[0]['trace_coordinate_time_first'][-1]
    Tdot[1:4,:106]=motion[0]['trace_coordinate_time_first'];Tdot[1:4,106:212]=-motion[1]['trace_coordinate_time_first']
    order=inputs['ordered_indices'];Ht=clock['Hessian_coordinate_time_first'][np.ix_(order,order)]
    frequency['lapse']=motion[1]['lapse']
    contact=moving_frequency_trial(frequency,Ht,Tdot,motion[1]['lapse_coordinate_time_first'])
    strong=strong_jacobi_normal_response(frequency['action_polynomial']+clock['Jacobi_coefficient_contact'],frequency['normal_and_constraint_rows'],lapse=motion[1]['lapse'])
    control=strong_jacobi_normal_response(frequency['action_polynomial']+clock['Jacobi_coefficient_contact_control'],frequency['normal_and_constraint_rows'],lapse=motion[1]['lapse'])
    out.mkdir(parents=True);archives={}
    def save(name,obj):
        p=out/name;_compressed_npz(p,{k:v for k,v in obj.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete moving trace outputs')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('moving_proper_trace_application.npz',dict(raw_pair=raw,raw_coordinate_rate=rawrate,
        parent_trace=motion[0]['trace'],child_trace=motion[1]['trace'],parent_trace_time_first=motion[0]['trace_coordinate_time_first'],
        child_trace_time_first=motion[1]['trace_coordinate_time_first'],**contact))
    save('reeliminated_local_strong_Jacobi.npz',strong)
    save('reeliminated_local_strong_Jacobi_control.npz',control)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_complex_normal_trace_motion.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('same moving normal action source changed')
    result=dict(classification='EVALUATED_COMPLEX_LOCAL_NORMAL_TRACE_MOTION_AND_FULL_FIRST_GERM_JACOBI_RESPONSE',input_hashes=refs,archives=archives,
        parent_lapse=motion[0]['lapse'],child_lapse=motion[1]['lapse'],
        parent_lapse_time_first=motion[0]['lapse_coordinate_time_first'],child_lapse_time_first=motion[1]['lapse_coordinate_time_first'],
        parent_proper_trace_time_first_norm=float(np.linalg.norm(motion[0]['trace_coordinate_time_first'])),
        child_proper_trace_time_first_norm=float(np.linalg.norm(motion[1]['trace_coordinate_time_first'])),
        moving_frequency_restoring_time_first=contact['proper_restoring_time_first'],
        moving_frequency_inertia_time_first=contact['proper_frequency_inertia_time_first'],
        moving_trial_right_original_rows_max=float(np.max(abs(contact['original_time_first_rows']))),
        moving_trial_transpose_original_rows_max=float(np.max(abs(contact['transpose_time_first_rows']))),
        full_first_germ_normal_response=strong['local_normal_reaction_taylor'],
        full_first_germ_same_clock_response=strong['same_clock_readout_taylor'],
        full_first_germ_right_rows_max=float(np.max(abs(strong['right_original_rows']))),
        full_first_germ_transpose_rows_max=float(np.max(abs(strong['left_original_rows']))),
        strong_polynomial_reelimination_condition=strong['balanced_condition'],
        full_first_germ_contact_step_response_difference=strong['local_normal_reaction_taylor']-control['local_normal_reaction_taylor'],
        frozen_normal_response=frequency['response_taylor'],
        full_minus_frozen_response=strong['local_normal_reaction_taylor']-frequency['response_taylor'],
        frozen_first_insertion=clock['projected_Jacobi_contact_taylor'],
        full_change_minus_first_insertion=strong['local_normal_reaction_taylor']-frequency['response_taylor']-clock['projected_Jacobi_contact_taylor'],
        local_trial_gluing_and_lapse_first_jets_executed=True,
        all80_Gauss_and212_geometry_field_rows_retained=True,
        all8_named_static_radial_frames_retained=True,
        coefficient_time_jet_reeliminated_before_unit_trace_readout=True,
        physical_full_reset_trace_domain_selected=False,global_variable_operator_reeliminated=False,
        local_response_does_not_select_event_eigenline_or_gamma_c=True,
        canonical_reference_clock_included_once=True,original226_reset_guard_passed=False,
        area_gamma_source_is_held_state_partial_not_coupled_parameter_solution=True,
        error_scope='binary exact stored coefficient/trace linear actions plus prior finite Hessian time jet; no original action/canonical tangent/domain error enclosure or physical formation normalization')
    p=out/'result.json';p.write_text(json.dumps(zjson(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='moving_trace_and_reeliminated_local_Jacobi_complete',
        response=zjson(strong['local_normal_reaction_taylor']),right_rows_max=result['full_first_germ_right_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,
        default=Path('artifacts/muon_complex_paired_normal_action_20261012/run_1'));p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.source_folder,a.output)
