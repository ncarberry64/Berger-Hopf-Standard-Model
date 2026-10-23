"""Freeze same-action normal trials and quantify the actual local controls."""
from pathlib import Path
from hashlib import sha256
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'artifacts/muon_complex_normal_action_applications_20261012/pair_verification'
    if out.exists():raise FileExistsError('preserve original normal application verification')
    files={};pins={};records={}
    roots=('muon_complex_paired_normal_action_20261012','muon_complex_normal_trace_motion_20261012')
    for name in roots:
        base=ROOT/'artifacts'/name
        for number in(1,2):
            folder=base/f'run_{number}';report=json.loads((folder/'result.json').read_text());records[name]=report
            for rel,record in report['archives'].items():
                p=folder/rel;b=p.read_bytes()
                if sha256(b).hexdigest()!=record['sha256']:raise ValueError('normal application archive changed')
                if number==2 and b!=(base/'run_1'/rel).read_bytes():raise ValueError('normal application replay differs')
                files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
            p=folder/'result.json';b=p.read_bytes()
            if number==2 and b!=(base/'run_1/result.json').read_bytes():raise ValueError('normal receipts differ')
            files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
            for rel,digest in report['input_hashes'].items():
                if rel in pins and pins[rel]!=digest:raise ValueError('same action input conflict')
                pins[rel]=digest
            p=ROOT/f'artifacts/{name}_run_{number}.stdout.txt';files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('same normal source pin changed')
    base=ROOT/'artifacts/muon_complex_normal_trace_motion_20261012/run_1'
    with np.load(base/'reeliminated_local_strong_Jacobi.npz',allow_pickle=False)as z:a={k:z[k].copy()for k in z.files}
    with np.load(base/'reeliminated_local_strong_Jacobi_control.npz',allow_pickle=False)as z:b={k:z[k].copy()for k in z.files}
    K=a['bordered_strong_polynomial'];rhs=a['original_rhs'];quality=[]
    for k in range(3):
        r=a['right_taylor'];l=a['left_taylor']
        rhsabs=abs(rhs)if k==0 else np.zeros_like(abs(rhs))
        scale=np.max(rhsabs+sum(abs(K[j])@abs(r[:,k-j])for j in range(k+1)))
        dualscale=np.max(rhsabs+sum(abs(K[j].T)@abs(l[:,k-j])for j in range(k+1)))
        absolute=float(np.max(abs(a['right_original_rows'][:,k])));dual=float(np.max(abs(a['left_original_rows'][:,k])))
        response=a['local_normal_reaction_taylor'][k];difference=response-b['local_normal_reaction_taylor'][k]
        quality.append(dict(order=k,right_absolute_rows_max=absolute,left_absolute_rows_max=dual,
            right_normwise_stored_residual=absolute/max(scale,np.finfo(float).tiny),
            left_normwise_stored_residual=dual/max(dualscale,np.finfo(float).tiny),
            response=[float(response.real),float(response.imag)],two_Hessian_time_step_difference=[float(difference.real),float(difference.imag)],
            two_Hessian_time_step_relative_difference=float(abs(difference)/max(abs(response),np.finfo(float).tiny))))
    logs=('muon_complex_paired_normal_action_tests_20261012_run_1.stdout.txt',
        'muon_complex_paired_normal_action_tests_20261012_run_2.stdout.txt',
        'muon_holomorphic_joint_reference_clock_tests_20261012_run_1.stdout.txt',
        'muon_complex_normal_trace_motion_tests_20261012_run_1.stdout.txt',
        'muon_complex_normal_trace_motion_tests_20261012_run_2.stdout.txt')
    for name in logs:
        p=ROOT/'artifacts'/name;files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    p=Path(__file__);files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    interpretation=dict(strong_Jacobi_quality_by_order=quality,
        frozen_insertion_is_not_full_reelimination=True,
        moving_trace_frequency_jet_is_not_global_variable_operator=True,
        normwise_residual_is_not_error_enclosure=True,
        original226_candidate_residual=records[roots[0]]['original226_reset_rows_max'],
        conditional_normal_trial_not_in_original_reset_domain=True,
        physical_gamma_c_or_first_hit_selected=False,
        next_action_relation='compose original226 reset tangent/source/field trace rows with original joint canonical variational evolution and moving proper-normal/lapse/coframe jets; current local normal trace constraints alone do not provide that domain',
        gamma_law_preserved='gamma=alpha_FSC*c^(-m/2), no alpha_EM substitute or assigned gamma',
        error_scope='exact stored binary polynomial residuals and two prior directional time-Hessian steps, with no action/background/domain enclosure')
    out.mkdir(parents=True)
    p=out/'projected_control_scope.json';p.write_text(json.dumps(interpretation,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    record=dict(classification='VERIFIED_CURRENT_COMPLEX_NORMAL_ACTION_CLOCK_TRACE_JACOBI_PAIRS',files=files,input_hashes=pins,
        all_application_output_bytes_equal=True,pin_count=len(pins),tests_passed=7,
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        commands=[f'C:/Python314/python.exe scripts/evaluate_muon_complex_paired_normal_action.py --output artifacts/{roots[0]}/run_{i}'for i in(1,2)]+
            [f'C:/Python314/python.exe scripts/evaluate_muon_complex_normal_trace_motion.py --output artifacts/{roots[1]}/run_{i}'for i in(1,2)],
        failed_test_preserved='First dagger counterexample fixture had its only complex normal coefficient on a constrained-zero coordinate; corrected fixture only, failed actual stdout retained',
        physical_formation_cutoff_or_selected_event_or_pole_claimed=False)
    p=out/'publication_manifest.json';p.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest(),strong_quality=quality)),flush=True)


if __name__=='__main__':main()
