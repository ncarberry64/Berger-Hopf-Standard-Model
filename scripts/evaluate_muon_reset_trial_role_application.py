"""Partition actual original reset trial rows and known source/moving contacts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_reset_trial_role_application import (
    reset_trial_role_application,reset_algebraic_duplicate_application,reset_role_indices)
from bhsm.interface.muon_holomorphic_two_arm_reset import holomorphic_moving_trace
from bhsm.interface.aether_full_reset_action_jacobian import (
    _attachment_jacobian_at_order,_trace_jacobian_at_order,_symmetric_power)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every original fixed-source trial interpretation')
    refs={}
    def receipt(folder):
        p=ROOT/folder/'result.json';b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest();return json.loads(b)
    def archive(folder,md,name):
        p=ROOT/folder/name;b=p.read_bytes();h=sha256(b).hexdigest()
        if h!=md['archives'][name]['sha256']:raise ValueError('same original source pin changed '+name)
        refs[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    tf=Path('artifacts/muon_reset_normal_trial_domain_20261012/run_1')
    rf=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1')
    nf=Path('artifacts/muon_complex_paired_normal_action_20261012/run_1')
    mf=Path('artifacts/muon_complex_normal_trace_motion_20261012/run_1')
    tm,rm,nm,mm=(receipt(x)for x in (tf,rf,nf,mf))
    trial=archive(tf,tm,'application.npz');reset=archive(rf,rm,'application.npz')
    base=archive(nf,nm,'same_action_inputs.npz');clock=archive(nf,nm,'clock_and_joint_tangent.npz')
    freq=archive(nf,nm,'frequency_application.npz');moving=archive(mf,mm,'moving_proper_trace_application.npz')
    if (not np.array_equal(trial['raw_pair'],reset['raw_pair'])or not np.array_equal(base['raw_pair'],reset['raw_pair'])
            or not np.array_equal(moving['raw_pair'],reset['raw_pair'])
            or not np.array_equal(base['reference_pair'],reset['reference_pair'])
            or nm['action_parameters']!=rm['action_parameters']):
        raise ValueError('exact same candidate required for role/source interpretation')
    wp=next(Path(x)for x in rm['input_hashes']if x.endswith('true_phase_projection_inputs.npz'))
    b=(ROOT/wp).read_bytes();h=sha256(b).hexdigest()
    if h!=rm['input_hashes'][wp.as_posix()]:raise ValueError('declared geometry scaling pin changed')
    refs[wp.as_posix()]=h
    with np.load(ROOT/wp,allow_pickle=False)as z:weights=z['state_weights'];normalization=z['normalization_coordinates']
    scales=np.tile(np.r_[1/weights[74:98],np.ones(16)],2)
    H=reset['full_master_Hessian'];J=reset['original226_Jacobian'];roles=reset_role_indices(rm['groups'])
    arrays=dict(raw_pair=reset['raw_pair'],reference_pair=reset['reference_pair'],
        candidate_original226_rows=reset['original226_rows'],named_original_Ward_rows=reset['Ward_rows'],
        declared_algebraic_scales=scales,area_parameter_source_original226=reset['area_parameter_source'],
        explicit_reference_clock_gradient504=clock['gradient_clock_first'])
    for role,ids in roles.items():arrays['role_'+role+'_indices']=ids
    summaries={};duplicate=None
    for name in tm['applications']:
        D=trial[name+'_master_lifts'];a=reset_trial_role_application(J,D,rm['groups'])
        duplicate=reset_algebraic_duplicate_application(J,H,rm['groups'],scales,D,
            gradient_source=clock['gradient_clock_first'])
        arrays[name+'_original226_fixed_source_rows']=a['original226_fixed_source_rows']
        arrays[name+'_bulk_algebraic_rows_with_reference_clock_source']=duplicate['original_bulk_algebraic_trial_rows']
        arrays[name+'_reset_algebraic_rows_with_reference_clock_source']=duplicate['scaled_reset_algebraic_trial_rows']
        summaries[name]=a['roles']
    arrays['reset_Ly_duplicate_Jacobian_defect']=duplicate['duplicate_Jacobian_defect']
    arrays['explicit_reference_clock_original80_reset_source']=duplicate['explicit_reset_algebraic_source_rows']
    # Actual time derivative of geometric trace coefficients along the
    # saved joint canonical/reference tangent. This is Cdot*xi, not a
    # selected event/source perturbation or an extra stationarity row.
    R=base['master_lift'];raw=reset['raw_pair'];rate=moving['raw_coordinate_rate']
    B=_attachment_jacobian_at_order(12,normalization);T0=np.vstack((_trace_jacobian_at_order(12),B[1]))
    norm=_symmetric_power(T0@np.diag(1/weights[:37]**2)@T0.T,-.5)
    C=np.zeros((4,504),complex);Ct=np.zeros_like(C)
    for arm,sign in ((0,-1),(1,1)):
        tr=holomorphic_moving_trace(raw[arm]);P=R[arm*268+np.arange(100)]
        C+=sign*tr['first']@P
        Ct+=sign*np.einsum('aij,j,ik->ak',tr['second'],rate[arm,:100],P,optimize=True)
    C=norm@C;Ct=norm@Ct
    arrays['moving_geometric_trace_coordinate_time_first']=Ct
    arrays['moving_geometric_trace_same_Jacobian_defect']=C-J[rm['groups']['moving_geometric_trace']]
    for name,key in (('frequency_right','right_taylor'),('frequency_left_analytic_trial','left_taylor')):
        D=trial[name+'_master_lifts'];arrays[name+'_original_geometric_Cdot_xi']=Ct@D
        z=freq[key][:292];dz=moving[key+'_time_first'][:292]
        t=freq['normal_and_constraint_rows'];dt=moving['normal_and_constraint_time_first']
        arrays[name+'_local_moving_constraint_source']=dt@z
        arrays[name+'_local_moving_constraint_response']=t@dz
        arrays[name+'_local_moving_constraint_total_rows']=t@dz+dt@z
    for rel in ('src/bhsm/interface/muon_reset_trial_role_application.py',
                'tests/test_muon_reset_trial_role_application.py',Path(__file__).relative_to(ROOT).as_posix(),
                'src/bhsm/interface/muon_holomorphic_two_arm_reset.py',
                'src/bhsm/interface/aether_full_reset_action_jacobian.py',
                'src/bhsm/interface/muon_birth_phase_continuation.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('role/source inputs changed')
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,arrays)
    if p.stat().st_size>10*1024**2:raise ValueError('split complete source/row images')
    maximum=lambda x:float(np.max(abs(x)))
    result=dict(classification='EVALUATED_ROLE_AND_SOURCE_AUDIT_OF_SUPPLIED_RESET_NORMAL_TRIALS',
        archives={'application.npz':dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        input_hashes=refs,roles={k:dict(indices=v.tolist(),count=len(v))for k,v in roles.items()},
        fixed_source_trials=summaries,bulk_Ly_duplicate_max=maximum(arrays['reset_Ly_duplicate_Jacobian_defect']),
        bulk_Ly_duplicate_relative=float(np.linalg.norm(arrays['reset_Ly_duplicate_Jacobian_defect'])/np.linalg.norm(J[roles['bulk_algebraic_compatibility']])),
        geometric_trace_C_same_J_max=maximum(arrays['moving_geometric_trace_same_Jacobian_defect']),
        explicit_reference_clock_original80_source_max=maximum(arrays['explicit_reference_clock_original80_reset_source']),
        gamma_source_role_max={k:maximum(reset['area_parameter_source'][v])for k,v in roles.items()},
        moving_contacts={name:dict(original_geometric_Cdot_xi_max_by_coefficient=np.max(abs(arrays[name+'_original_geometric_Cdot_xi']),axis=0).tolist(),
            local_constraint_source_max_by_coefficient=np.max(abs(arrays[name+'_local_moving_constraint_source']),axis=0).tolist(),
            local_constraint_total_max_by_coefficient=np.max(abs(arrays[name+'_local_moving_constraint_total_rows']),axis=0).tolist())
            for name in ('frequency_right','frequency_left_analytic_trial')},
        candidate_original226_rows_max=maximum(reset['original226_rows']),
        interpretation='73 kinematic trace rows,80 bulk algebraic/Gauss rows,73 natural energy/temporal-traction response rows; category counts are not an independence/rank assertion',
        natural_traction_not_forbidden_or_zero_by_definition=True,
        old_trial_receipt_domain_wording_qualified_by_this_additive_role_audit=True,
        source_scope='actual held-state area gamma source; reference-only affine-clock source for80 Ly rows; actual moving coefficient trace contacts along saved joint tangent. No selected physical normal/source trajectory is inferred.',
        full_reference_clock_natural_readout_source_not_claimed=True,
        governing_reduction='fullD292 canonical constitutive solve with independent delta x/delta p and g_v,s/g_y,s,4 named phase frames; canonical Jacobi evolution and prescribed kinematic R_z delta_z+R_s, then natural force/energy readout and later formation selection',
        prescribed_normal_source_must_be_supplied_to_governing_lift=True,
        signed_action_not_replaced_by_least_norm_metric=True,
        physical_mode_i_over_r_firsthit_gamma_or_Pauli_selected=False)
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),
        duplicate_relative=result['bulk_Ly_duplicate_relative'],roles={k:v['count']for k,v in result['roles'].items()},
        reference_clock_source=result['explicit_reference_clock_original80_source_max'],
        moving_contacts=result['moving_contacts']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    materialize(p.parse_args().output)
