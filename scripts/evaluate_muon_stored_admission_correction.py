"""One bounded exact-stored per-arm admission residual correction application."""
from pathlib import Path
from hashlib import sha256
import argparse, json, sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.muon_stored_admission_correction import bounded_stored_admission_correction
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder, trace_folder, output, precision, corrections):
    out=ROOT/output
    if out.exists(): raise FileExistsError('preserve bounded stored admission application')
    pins={}
    def receipt(folder):
        p=ROOT/folder/'result.json'; b=p.read_bytes()
        pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        return json.loads(b)
    def archive(folder, md, name):
        p=ROOT/folder/name; b=p.read_bytes(); h=sha256(b).hexdigest()
        if h != md['archives'][name]['sha256']: raise ValueError('unchanged admission input digest required')
        pins[p.relative_to(ROOT).as_posix()]=h
        with np.load(p, allow_pickle=False) as z: return {k:z[k].copy() for k in z.files}
    sm, tm=receipt(source_folder), receipt(trace_folder)
    trace=archive(trace_folder, tm, 'application.npz')
    out.mkdir(parents=True); archives={}; records={}
    for case in ('normal_basis', 'area_source'):
        for arm in ('parent', 'child'):
            name=case+'_'+arm+'_original146.npz'
            saved=archive(source_folder, sm, name)
            H=trace['parent_standalone_Hessian'] if arm=='parent' else trace['full_joint_Hessian'][252:,252:]
            n=106; no=146; K=saved['original_saddle']; rhs=saved['original_rhs']
            if K.shape != (148,148) or rhs.shape != (148,) or not np.array_equal(K[:no,:no], H[n:,n:]):
                raise ValueError('same final-candidate 146 phase block required')
            if not np.array_equal(saved['solution'][no:], saved['frame_reactions']):
                raise ValueError('saved frame reaction schema changed')
            target=np.r_[saved['canonical_momentum_target'], np.zeros(40,complex)]
            a=bounded_stored_admission_correction(K, rhs, saved['solution'], no,
                action_rows=H[n:], fixed_x=saved['delta_x'],
                source_rows=saved['source_gradient'][n:], target_rows=target,
                precision_bits=precision, correction_count=corrections)
            arrays=a.pop('arrays')
            high, low=arrays['correction_solution_high'], arrays['correction_solution_low']
            arrays.update(saved_original_phase_rows=saved['original_phase_rows'],
                unchanged_canonical_momentum_target=saved['canonical_momentum_target'],
                unchanged_source_gradient=saved['source_gradient'],
                corrected_direction_high=np.r_[saved['delta_x'],high[:no]],
                corrected_direction_low=np.r_[np.zeros(n),low[:no]],
                corrected_frame_reaction_high=high[no:], corrected_frame_reaction_low=low[no:])
            direction=arrays['corrected_direction_high']
            rows64=H[n:]@direction+saved['source_gradient'][n:]-target
            arrays['binary_reexecuted_original_phase_rows']=rows64
            initial64=H[n:]@saved['direction']+saved['source_gradient'][n:]-target
            if not np.array_equal(initial64, saved['original_phase_rows']):
                raise ValueError('saved original action rows not reproduced under same environment')
            a.update(binary_original_rows_max=float(np.max(abs(rows64))),
                binary_original_Legendre_rows_max=float(np.max(abs(rows64[:n]))),
                binary_original_Gauss_rows_max=float(np.max(abs(rows64[n:]))),
                rounded_original_Legendre_rows_max=float(np.max(abs(arrays['rounded_original_action_rows'][:n]))),
                rounded_original_Gauss_rows_max=float(np.max(abs(arrays['rounded_original_action_rows'][n:]))),
                reaction_norm=float(np.linalg.norm(high[no:])),
                corrected_state_change_norm=float(np.linalg.norm(high-saved['solution'])),
                original_rows_unchanged_binary_guard_passed=bool(np.max(abs(rows64))<=2e-10),
                initial_saved_original_rows_max=float(np.max(abs(saved['original_phase_rows']))),
                source_target_or_matrix_changed=False,
                no_action_or_changing_background_application_executed=True)
            p=out/(case+'_'+arm+'_stored_correction.npz'); _compressed_npz(p, arrays)
            archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
            records[case+'_'+arm]=a
            print(json.dumps(dict(case=case,arm=arm,
                initial_original_rows=a['initial_saved_original_rows_max'],
                exact_stored_bordered_upper=a['exact_stored']['bordered_residual_upper'],
                rounded_original_upper=a['rounded_state']['original_action_rows_residual_upper'],
                high_low_original_upper=a['high_low_state']['original_action_rows_residual_upper'],
                binary_original_rows=a['binary_original_rows_max'],
                reaction_phase_upper=a['exact_stored']['frame_reaction_phase_rows_upper'],
                rhs_assembly_difference_upper=a['stored_rhs_assembly_difference_upper'],
                rounded_guard=a['rounded_original_rows_guard_passed']),sort_keys=True),flush=True)
    for path in ('src/bhsm/interface/muon_stored_admission_correction.py',
                 'src/bhsm/interface/muon_complex_paired_normal_action.py',
                 'tests/test_muon_stored_admission_correction.py',
                 'scripts/evaluate_muon_stored_admission_correction.py'):
        p=ROOT/path; pins[path]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):
        raise ValueError('fixed stored source changed during bounded application')
    result=dict(classification='BOUNDED_FIXED_STORED148_PER_ARM_RESIDUAL_CORRECTION_WITH_ALL_ORIGINAL146_ROWS',
        archives=archives,input_hashes=pins,applications=records,tolerance=2e-10,
        precision_bits=precision,correction_budget=corrections,
        unchanged_balanced_solver_not_globally_edited=True,
        high_low_state_is_matrix_representation_not_a_new_action_state=True,
        no_action_accuracy_or_physical_admission_enclosure=True,
        no_canonical_step_or_state_or_pole_selection=True,
        error_scope='Acb arithmetic enclosures on exact stored binary K/rhs/H/source/target only; producer, source assembly, action evaluation, changing background and physical domain excluded')
    p=out/'result.json'
    p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='bounded_stored_admission_complete',result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-folder',type=Path,default=Path('artifacts/muon_per_arm_canonical_source_20261012/run_1'))
    p.add_argument('--trace-folder',type=Path,default=Path('artifacts/muon_coupled_reset_canonical_trace_20261012/run_1'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--precision-bits',type=int,default=192)
    p.add_argument('--corrections',type=int,default=3)
    a=p.parse_args(); materialize(a.source_folder,a.trace_folder,a.output,a.precision_bits,a.corrections)
