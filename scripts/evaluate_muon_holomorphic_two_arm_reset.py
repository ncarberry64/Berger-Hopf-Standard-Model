"""Apply full complex two-arm action/reset to the supplied held snapshots."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import _affine_geometry
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_two_arm_reset import holomorphic_two_arm_reset
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_parent_gauge_geometry_correction import STATE_SOURCE
from bhsm.interface.muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(endpoint_folder,output):
    source=ROOT/endpoint_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every actual held-pair reset application')
    refs={}
    def read(path):
        p=ROOT/path;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(endpoint_folder/'result.json');refs.update(md['input_hashes']);data=read(endpoint_folder/'application.npz')
    if refs[(endpoint_folder/'application.npz').as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('actual compatible child endpoint changed')
    if not md['compatible_endpoint']:raise ValueError('reached child constitutive solution required')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];time=data['coordinate_time'].item();params=md['action_parameters']
    parent=_affine_geometry(phase['arrays']['initial_pair'][0],time)
    reference=np.array([_affine_geometry(x,time)for x in phase['arrays']['reference_pair']])
    raw=np.stack((parent,data['raw_fields']));state=read(Path(STATE_SOURCE));norm=read(Path(NORMALIZATION_SOURCE))
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split all full536/reset arrays')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    print(json.dumps(dict(stage='actual_held_parent_complex_two_arm_action',coordinate_time=[time.real,time.imag])),flush=True)
    a=holomorphic_two_arm_action(raw,reference,rep,**params)
    vi=a['velocity_indices'];yi=a['algebraic_indices'];w_indices=np.r_[vi,yi];D=a['hessian'][np.ix_(w_indices,w_indices)]
    frames=[canonical_central_frame(x,rep)for x in raw]
    F=np.zeros((4,292),complex);Z=np.zeros((292,4),complex)
    for arm,frame in enumerate(frames):
        ids=np.r_[arm*106+np.arange(106),212+arm*40+np.arange(40)]
        F[np.ix_(arm*2+np.arange(2),ids)]=frame['named_frame_covectors']
        Z[np.ix_(ids,arm*2+np.arange(2))]=frame['literal_generators']
    save('full_original_two_arm_action.npz',dict(raw_pair=raw,reference_pair=reference,coordinate_time=np.array(time),
        master_lift=a['master_lift'],one_lift=a['one_lift'],gradient=a['gradient'],Hessian=a['hessian'],
        raw_gradient=a['raw_gradient'],raw_Hessian=a['raw_hessian'],action_value=np.array(a['value']),
        parent_gradient=a['parent']['gradient'],parent_Hessian=a['parent']['hessian'],parent_value=np.array(a['parent']['value']),
        temporal_cotangent=a['temporal_cotangent'],temporal_cotangent_first=a['temporal_cotangent_first'],
        velocity_indices=vi,algebraic_indices=yi,phase_indices=w_indices,full_Legendre_block=D,named_frames=F,literal_generators=Z,
        full_Legendre_generator_image=D@Z,full_Legendre_generator_source_pairing=Z.T@a['gradient'][w_indices],
        area_gradient_per_gamma=a['area_gradient_per_gamma'],area_Hessian_per_gamma=a['area_Hessian_per_gamma'],
        area_temporal_cotangent_per_gamma=a['area_temporal_cotangent_per_gamma'],area_value_per_gamma=np.array(a['area_value_per_gamma']),
        reference_clock_work=np.array(a['reference_clock_work']),child_actual_canonical_momentum_target=data['canonical_momentum_target'],
        child_original_constitutive_rows=a['gradient'][252+106:]-np.r_[data['canonical_momentum_target'],np.zeros(40,complex)]))
    print(json.dumps(dict(stage='full_original536_held_action_saved',parent_algebraic_max=float(np.max(abs(a['gradient'][yi[:40]]))),
        child_algebraic_max=float(np.max(abs(a['gradient'][yi[40:]]))),reference_clock_work=[a['reference_clock_work'].real,a['reference_clock_work'].imag])),flush=True)
    r=holomorphic_two_arm_reset(raw,reference,rep,state['state_weights'],norm['normalization_coordinates'],
        compute_projected_derivative=False,**params)
    save('historical_held_reset.npz',dict(residual=r['residual'],analytic_first_rows=r['jacobian'],area_parameter_source=r['area_parameter_source'],
        projected_saddle=r['projected_saddle'],projected_solution=r['projected_solution'],projected_adjoint=r['projected_adjoint'],
        projected_saddle_residual=r['projected_saddle_residual'],projected_adjoint_residual=r['projected_adjoint_residual'],
        projected_cotangent=r['projected_cotangent'],projected_area_cotangent=r['projected_area_cotangent'],
        trace_B=r['trace_B'],trace_DB=r['trace_DB'],trace_values=r['trace_values'],reference_clock_work_first=r['reference_clock_work_first']))
    # This port map is provided to the additive TRUE v/y projection, rather
    # than treating the old fixed-y lift as full temporal stationarity.
    save('true_phase_projection_inputs.npz',dict(full_Legendre_block=D,trace_map=np.c_[r['trace_B'],np.zeros((6,80))],
        named_frames=F,temporal_dual=np.r_[a['temporal_cotangent'],np.zeros(80)],
        area_D_parameter=a['area_Hessian_per_gamma'][np.ix_(w_indices,w_indices)],
        area_temporal_dual_parameter=np.r_[a['area_temporal_cotangent_per_gamma'],np.zeros(80)],
        literal_generators=Z,raw_pair=raw,reference_pair=reference,coordinate_time=np.array(time),
        state_weights=state['state_weights'],normalization_coordinates=norm['normalization_coordinates']))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_holomorphic_two_arm_action.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same complex two-arm source changed')
    groups={name:dict(indices=ids,max_residual=float(np.max(abs(r['residual'][ids]))))for name,ids in r['groups'].items()}
    record=dict(classification='EVALUATED_COMPLEX_FULL536_HELD_TWO_ARM_ACTION_AND_DECLARED_RESET_RESIDUAL',
        input_hashes=refs,archives=archives,groups=groups,reset_row_count=len(r['residual']),held_reset_residual_max=float(np.max(abs(r['residual']))),
        parent_algebraic_max=float(np.max(abs(a['gradient'][yi[:40]]))),child_algebraic_max=float(np.max(abs(a['gradient'][yi[40:]]))),
        full_Legendre_generator_image_max=float(np.max(abs(D@Z))),
        historical_fixed_y_saddle_residual_max=float(np.max(abs(r['projected_saddle_residual']))),
        historical_fixed_y_adjoint_residual_max=float(np.max(abs(r['projected_adjoint_residual']))),
        supplied_parent='recorded incoming affine geometry/profile germ evaluated at the actual child complex endpoint coordinate time',
        supplied_child='actually reconstructed compatible original full canonical endpoint x/Pi/v/y',
        supplied_reference='both recorded affine reference geometry/profile germs at the same actual coordinate time',
        parent_or_pair_stationarity_claimed=False,old_real_parameter_response_grafted=False,action_parameters=params,
        historical_projection_scope=r['projection_scope'],full_historical_reset_Jacobian_evaluated=False,
        true_full_phase_projection_inputs_exported=True,physical_reset_first_hit_or_gamma_assigned=False,
        required_coupled_application='true full292 v/y trace projection and its state/source derivatives, then coupled reset equations on the same actual canonical parent/child continuation and selected descriptor; held affine parent is not that solved parent',
        gamma_law='gamma=alpha_FSC*c^(-m/2) with first/second c chain jets; no alpha_EM substitution',
        error_scope='binary analytic full536 signed action and independent transpose fixed-y trial; held pair/full226 residual diagnostic, not physical reset, firsthit or Pauli enclosure')
    p=out/'result.json';p.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='actual_held_two_arm_reset_complete',reset_rows=len(r['residual']),
        reset_residual_max=record['held_reset_residual_max'],result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--endpoint-folder',type=Path,
        default=Path('artifacts/muon_complex_canonical_endpoint_20261012/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.endpoint_folder,a.output)
