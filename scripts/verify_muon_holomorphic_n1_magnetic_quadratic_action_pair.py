"""Freeze completed full supplied-direction quadratic action replay evidence."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def main():
    base=ROOT/'artifacts/muon_holomorphic_n1_magnetic_quadratic_action_20261012';out=base/'pair_verification'
    if out.exists():raise FileExistsError('preserve actual quadratic action verification')
    files={};pins={};reports={};commands=[]
    for case in('normal_basis','area_source'):
        original=None
        for number in(1,2):
            folder=base/f'outgoing_{case}_run_{number}';p=folder/'result.json';b=p.read_bytes();md=json.loads(b)
            if (md['classification']!='EVALUATED_FULL_SUPPLIED_DIRECTION_SIGNED_MAGNETIC_QUADRATIC_ACTION_DERIVATIVE'
                    or md['source_points']!=15 or not md['full_stage_coefficient_derivative_M_BF_BR_K_applied']
                    or not md['both_independent_causal_field_response_slots_applied']
                    or not md['source_wall_and_induced_Higgs_response_retained']
                    or md['case']!=case or md['side']!='outgoing'):
                raise ValueError('completed complete supplied-direction action receipt required')
            if original is None:original=b;reports[case]=md
            elif b!=original:raise ValueError('same full action replay receipt differs')
            files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
            for name,record in md['archives'].items():
                p=folder/name;b=p.read_bytes()
                if len(b)!=record['bytes']or sha256(b).hexdigest()!=record['sha256']:
                    raise ValueError('complete source/action contraction changed')
                if number==2 and b!=(base/f'outgoing_{case}_run_1'/name).read_bytes():
                    raise ValueError('same coefficient/source response replay array differs')
                files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
            for p,h in md['input_hashes'].items():
                if p in pins and pins[p]!=h:raise ValueError('same-background source/action pin conflict')
                pins[p]=h
            p=ROOT/f'artifacts/muon_holomorphic_n1_magnetic_quadratic_action_20261012_outgoing_{case}_run_{number}.stdout.txt'
            files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
            commands.append(f'C:/Python314/python.exe scripts/evaluate_muon_holomorphic_n1_magnetic_quadratic_action.py --d3-folder {md["d3_folder"]} --output artifacts/muon_holomorphic_n1_magnetic_quadratic_action_20261012/outgoing_{case}_run_{number}')
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('consumed signed action/source pin changed')
    for name in('artifacts/muon_holomorphic_n1_magnetic_quadratic_action_tests_20261012.stdout.txt',
            'artifacts/muon_holomorphic_n1_magnetic_quadratic_action_20261012_failed_serialization_1.stdout.txt',
            Path(__file__).relative_to(ROOT).as_posix()):
        p=ROOT/name;files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    result=dict(classification='VERIFIED_FULL_SUPPLIED_DIRECTION_SIGNED_MAGNETIC_QUADRATIC_ACTION_PAIR',
        all_output_bytes_equal=True,input_hashes=pins,files=files,commands=commands,
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        applications={case:dict(result_sha256=sha256((base/f'outgoing_{case}_run_1/result.json').read_bytes()).hexdigest(),
            integrated=md['integrated'])for case,md in reports.items()},
        compact_outputs=['result.json','quadratic_action_and_complete_supplied_direction.npz'],
        all_four_directed_value_rate_placements_and_source_high_low_preserved=True,
        full_coefficient_motion_geometry_profile_coframe_and_induced_H_applied=True,
        both_left_and_right_response_slots_retained_without_conjugation=True,
        initial_face_causal_source_domain_not_replaced_by_old_weak_BVP=True,
        physical_time_event_endpoint_native_heat_pole_normalization_not_inferred=True,
        preserved_failed_execution='first serializer attempted abs(list) after computing all points; failed directory/stdout retained, fixed with np.abs before final paired executions',
        scope='complete supplied source derivative of the saved signed quadratic action on this finite fixed numerical-time prefix; replay only, no action/physical outward enclosure')
    out.mkdir(parents=True);p=out/'publication_manifest.json'
    p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
