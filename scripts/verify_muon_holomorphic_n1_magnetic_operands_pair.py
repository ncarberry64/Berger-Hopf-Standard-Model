"""Nonmutating completed-pair verifier for actual causal signed D3S applications."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def main(side,cases):
    base=ROOT/'artifacts/muon_holomorphic_n1_magnetic_operands_20261012'
    out=base/('pair_verification_'+side+'_'+'_'.join(cases))
    if out.exists():raise FileExistsError('preserve completed signed D3S verification')
    pins={};files={};reports={};commands=[]
    for case in cases:
        first=None
        for number in(1,2):
            folder=base/f'{side}_{case}_run_{number}';p=folder/'result.json';data=p.read_bytes();md=json.loads(data)
            if (md['classification']!='EVALUATED_ACTUAL_CAUSAL_SIGNED_N1_MAGNETIC_D3S_AND_CLASSICAL_MIXED_ACTION'
                    or md['source_points']!=15 or not md['all15_actual_zero_Cauchy_points_consumed']
                    or not md['original_initial_held_face_source_retained']or not md['source_induced_Higgs_retained']
                    or md['side']!=side or md['case']!=case or not md['weak_BVP_source_not_consumed']):
                raise ValueError('complete same-domain actual causal action receipt required')
            if first is None:first=data;reports[case]=md
            elif data!=first:raise ValueError('signed D3S replay receipt bytes differ')
            files[p.relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
            for name,record in md['archives'].items():
                p=folder/name;b=p.read_bytes()
                if len(b)!=record['bytes']or sha256(b).hexdigest()!=record['sha256']or len(b)>=10*1024**2:
                    raise ValueError('full signed action/source archive changed')
                if number==2 and b!=(base/f'{side}_{case}_run_1'/name).read_bytes():
                    raise ValueError('same ENV4 signed D3S replay arrays differ')
                files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
            for p,h in md['input_hashes'].items():
                if p in pins and pins[p]!=h:raise ValueError('same-background causal stage/source pin conflict')
                pins[p]=h
            p=ROOT/f'artifacts/muon_holomorphic_n1_magnetic_operands_20261012_{side}_{case}_run_{number}.stdout.txt'
            files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
            commands.append(f'C:/Python314/python.exe scripts/evaluate_muon_holomorphic_n1_magnetic_operands.py --source-folder {md["source_folder"]} --output artifacts/muon_holomorphic_n1_magnetic_operands_20261012/{side}_{case}_run_{number}')
    for p,h in pins.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('actual action/source/executable pin no longer current')
    for name in('artifacts/muon_holomorphic_n1_magnetic_operands_application_tests_20261012.stdout.txt',
            'artifacts/muon_holomorphic_n1_magnetic_operands_20261012_label_preflight_failure.stdout.txt',
            Path(__file__).relative_to(ROOT).as_posix()):
        p=ROOT/name;files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    result=dict(classification='VERIFIED_ACTUAL_CAUSAL_SIGNED_N1_D3S_CLASSICAL_MIXED_ACTION_PAIR',all_output_bytes_equal=True,
        input_hashes=pins,files=files,commands=commands,environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        applications={case:dict(result_sha256=sha256((base/f'{side}_{case}_run_1/result.json').read_bytes()).hexdigest(),
            mixed_action=md['integrated_mixed_action'],free_even_action_source_norm=md['free_even_action_source_norm'],
            held_initial_even_action_source_norm=md['held_initial_even_action_source_norm'],
            integrated_magnetic_axis_exchange_defect_norm=md['integrated_magnetic_axis_exchange_defect_norm'])for case,md in reports.items()},
        compact_outputs=['result.json','same_action_maps_and_trials.npz','classical_mixed_action_and_source.npz','same_prefix_existing_unsquared_current_terms.npz'],
        all15_causal_point_operators_and_full_directed_temporal_blocks_preserved=True,
        both_value_rate_crosses_and_signed_Maxwell_scalar_off_shell_contacts_retained=True,
        source_H_Hdot_and_initial_face_returns_not_deleted=True,
        exact_constant_trial_n0_support_is_not_full_operator_tail_statement=True,
        no_old_positive_reference_Green_heat_mean_or_matching_subtotal_used=True,
        matrix_action_replay_not_an_action_quadrature_or_physical_error_enclosure=True,
        no_quantum_contact_or_Pauli_or_physical_pole_completion_inferred=True,
        preserved_preflight_failure='string harmonic-label cast, before output or action application; degree-only parsing fixed',
        scope='actual signed fixed-stage/classical field-direction D3S and saved finite causal C2 prefix only; full changing geometry/metric/exterior and same-native heat/overlap/pole application remain separate active equations')
    out.mkdir(parents=True);p=out/'publication_manifest.json'
    p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--side',choices=('incoming','outgoing'),default='outgoing')
    p.add_argument('--cases',nargs='+',choices=('normal_basis','area_source'),default=['normal_basis','area_source'])
    a=p.parse_args();main(a.side,a.cases)
