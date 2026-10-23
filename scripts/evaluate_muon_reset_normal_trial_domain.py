"""Evaluate the saved original reset Jacobian on the actual normal trial lifts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_reset_normal_trial_domain import (
    frequency_master_trial_lifts,kinetic_master_trial_lifts,original_reset_trial_application)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(normal_folder,reset_folder,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every original reset/trial domain application')
    refs={}
    def receipt(folder):
        p=ROOT/folder/'result.json';b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest();return json.loads(b)
    def archive(folder,md,name):
        p=ROOT/folder/name;b=p.read_bytes();h=sha256(b).hexdigest()
        if h!=md['archives'][name]['sha256']:raise ValueError('same normal/reset source pin changed '+name)
        refs[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    nm,rm=receipt(normal_folder),receipt(reset_folder)
    base=archive(normal_folder,nm,'same_action_inputs.npz')
    freq=archive(normal_folder,nm,'frequency_application.npz')
    kinetic=archive(normal_folder,nm,'true_Lyy_kinetic_application.npz')
    reset=archive(reset_folder,rm,'application.npz')
    if (not np.array_equal(base['raw_pair'],reset['raw_pair'])
            or not np.array_equal(base['reference_pair'],reset['reference_pair'])
            or nm['action_parameters']!=rm['action_parameters']):
        raise ValueError('same actual candidate/parameters/reference snapshot required')
    J=reset['original226_Jacobian'];order=base['ordered_indices']
    directions=dict(frequency_right=frequency_master_trial_lifts(freq['right_taylor'],order),
        frequency_left_analytic_trial=frequency_master_trial_lifts(freq['left_taylor'],order,left=True),
        true_Lyy_kinetic_right=kinetic_master_trial_lifts(kinetic['phase_lift'],order),
        true_Lyy_kinetic_left_analytic_trial=kinetic_master_trial_lifts(kinetic['left'][:292],order))
    arrays=dict(raw_pair=reset['raw_pair'],reference_pair=reset['reference_pair'],
        original226_candidate_rows=reset['original226_rows'],original226_Jacobian=J,
        original504_ordering=order,named_original_Ward_rows=reset['Ward_rows'],
        candidate_Ward_identity=reset['Ward_identity'])
    summaries={}
    for name,D in directions.items():
        a=original_reset_trial_application(J,D,rm['groups']);summaries[name]={k:v for k,v in a.items()if not isinstance(v,np.ndarray)}
        arrays[name+'_master_lifts']=D;arrays[name+'_original226_rows']=a['all_original226_trial_rows']
        arrays[name+'_max_abs_by_coefficient']=a['max_abs_by_coefficient']
        arrays[name+'_named_Ward_contraction']=reset['Ward_rows']@a['all_original226_trial_rows']
    # The existing trial constraints are also tested without re-solving the
    # normal application. They do not replace the original reset equations.
    for name,key in(('frequency_right','right_taylor'),('frequency_left_analytic_trial','left_taylor')):
        z=freq[key][:292]
        arrays[name+'_local_physical_glue_rows']=base['physical_gluing']@z
        arrays[name+'_local_named_radial_frame_rows']=base['named_static_radial_frames']@z
    out.mkdir(parents=True);p=out/'application.npz';_compressed_npz(p,arrays)
    if p.stat().st_size>10*1024**2:raise ValueError('retain all original rows in split files')
    for rel in('src/bhsm/interface/muon_reset_normal_trial_domain.py','tests/test_muon_reset_normal_trial_domain.py',
        Path(__file__).relative_to(ROOT).as_posix(),'src/bhsm/interface/muon_birth_phase_continuation.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/path).read_bytes()).hexdigest()!=h for path,h in refs.items()):raise RuntimeError('same trial/reset input changed')
    result=dict(classification='EVALUATED_ORIGINAL226_RESET_DOMAIN_OF_ACTUAL_PAIRED_NORMAL_TRIAL_LIFTS',
        input_hashes=refs,archives={'application.npz':dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        applications=summaries,action_parameters=rm['action_parameters'],
        candidate_original226_rows_max=float(np.max(abs(reset['original226_rows']))),
        candidate_reset_status=rm['status'],candidate_guard_passed=rm['original226_rows_max']<=rm['tolerance'],
        supplied_normal_scope='same current complex full504 action; frozen frequency and held-position true-Lyy kinetic trials',
        frequency_coefficient_convention='Taylor x/y order0..2; right velocity orderk=i*x_(k−1), left analytic velocity=−i*x_(k−1); order0 velocity0',
        true_kinetic_coefficient_convention='delta x=0, delta(v212,y80)=full trial phase lift',
        independent_analytic_left_is_not_physical_state_selected=True,
        local_three_row_gluing_is_not_all_original_reset_domain=True,
        candidate_nonlinear_residual_distinct_from_trial_linearized_row_image=True,
        original_Jacobian_scope=rm['derivative_scope'],
        omitted_variables_not_filled_as_physical_zero='no moving event-time/domain/source-gamma jet added; directions are exactly the supplied fixed-state/fixed-reference local trials',
        physical_normal_mode_i_over_r_firsthit_gamma_or_Pauli_selected=False,
        error_scope='binary original stored-J action on exact saved numerical trial arrays; original source/third-derivative production and physical domain corrections are not enclosed')
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),
        candidate_rows_max=result['candidate_original226_rows_max'],
        original_trial_rows_max={name:float(np.max(abs(arrays[name+'_original226_rows'])))for name in directions}),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--normal-folder',type=Path,default=Path('artifacts/muon_complex_paired_normal_action_20261012/run_1'))
    p.add_argument('--reset-folder',type=Path,default=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.normal_folder,a.reset_folder,a.output)
