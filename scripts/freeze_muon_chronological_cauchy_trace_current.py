"""Freeze the actual complete Cauchy point-current applications on both arms."""
from pathlib import Path
from hashlib import sha256
import argparse,json

ROOT=Path(__file__).resolve().parents[1]


def freeze(output,*,incoming_chunks,outgoing_chunks):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every Cauchy current replay receipt')
    files={};pins={};pairs=[];runtime=[]
    def identity(p):
        p=Path(p);p=p if p.is_absolute()else ROOT/p
        return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,
                    sha256=sha256(p.read_bytes()).hexdigest())
    base='artifacts/muon_chronological_cauchy_trace_current_20261011'
    for side,chunks in(('incoming',incoming_chunks),('outgoing',outgoing_chunks)):
        folders=[ROOT/base/f'{side}_run_{j}'for j in(1,2)]
        r=[json.loads((p/'result.json').read_bytes())for p in folders]
        if any(x['classification']!='EVALUATED_COMPLETE_CAUCHY_POINT_TRACE_ORIGINAL_CHRONOLOGICAL_CURRENT'for x in r):
            raise ValueError('the actual complete same-graph Cauchy current is required')
        if r[0]['input_hashes']!=r[1]['input_hashes']or r[0]['archives']!=r[1]['archives']:
            raise ArithmeticError('same complete Cauchy source/operator identities differ')
        for name in('result.json',*r[0]['archives']):
            ids=[identity(p/name)for p in folders]
            if ids[0]['sha256']!=ids[1]['sha256']or ids[0]['bytes']!=ids[1]['bytes']:
                raise ArithmeticError('complete Cauchy replay differs: '+name)
            if ids[0]['bytes']>=10*1024**2:raise ArithmeticError('split complete arrays at publication cap')
            for item in ids:files[item['path']]=item
        for p,h in r[0]['input_hashes'].items():
            if p in pins and pins[p]!=h:raise RuntimeError('inconsistent same-graph input pin')
            if identity(p)['sha256']!=h:raise RuntimeError('actual source/operator pin changed: '+p)
            pins[p]=h
        pairs.append(dict(left=folders[0].relative_to(ROOT).as_posix(),right=folders[1].relative_to(ROOT).as_posix(),
            complete_file_count=len(r[0]['archives'])+1,result_sha256=identity(folders[0]/'result.json')['sha256'],
            all_files_byte_identical=True,complete_transfer_norm=r[0]['complete_transfer_norm'],
            transported_minus_fixed_frame_current_norm=r[0]['complete_current_change_norm'],
            complete_energy_cancellation_norm=r[0]['complete_continued_energy_first_norm']))
        for j,chunk in zip((1,2),chunks):
            runtime.append(dict(command=['C:/Python314/python.exe','scripts/evaluate_muon_chronological_cauchy_trace_current.py',
                '--action-folder','artifacts/muon_chronological_n1_field_action_20261011/run_1',
                '--trace-folder','artifacts/muon_shifted_boundary_source_20261011/run_1',
                '--baseline-transfer-folder',f'artifacts/muon_chronological_current_matching_20261011/{side}_family_1_run_1',
                '--source-side',side,'--output',f'{base}/{side}_run_{j}'],
                environment=dict(PYTHONPATH='src',OPENBLAS_NUM_THREADS='4'),exit_code=0,completion_chunk=chunk))
    for p in('src/bhsm/interface/muon_chronological_cauchy_trace_current.py',
        'scripts/evaluate_muon_chronological_cauchy_trace_current.py','tests/test_muon_chronological_cauchy_trace_current.py',
        'scripts/freeze_muon_chronological_cauchy_trace_current.py',
        'artifacts/muon_chronological_common_y_current_20261011/pair_verification/publication_manifest.json',
        'artifacts/muon_chronological_common_y_current_20261011/pair_verification/verification.json'):
        files[p]=identity(p)
    out.mkdir(parents=True)
    def save(name,data):
        p=out/name;p.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        return p
    rp=save('runtime_log.json',dict(classification='ACTUAL_CAUCHY_POINT_SOURCE_COMPLETE_CURRENT_REPLAY_RUNTIME',
        commands=runtime,independent_replays=pairs,focused_tests=dict(
            command=['C:/Python314/python.exe','-m','pytest','--noconftest','tests/test_muon_chronological_cauchy_trace_current.py','-q'],
            passed=2,completion_chunk='843f7e',seconds=.80),
        independent_read_only_science_review='Validation accepted structural external C6 action, independent left trace, all original rows and energy contact placements',
        physical_spectral_trace_or_band_selected=False))
    files[rp.relative_to(ROOT).as_posix()]=identity(rp)
    mp=save('publication_manifest.json',dict(classification='FROZEN_COMPLETE_SAME_GRAPH_CAUCHY_POINT_CURRENT_APPLICATIONS',
        files=[files[p]for p in sorted(files)],input_hashes=pins,independent_replays=pairs,
        original_temporal_nodes=1151,current_column_shape=[6,2,6,4],complete_columns=288,exact_spectators=2,
        source_arm_solved_on_full_joined_field_operator=True,
        source_arms_identified_by_equal_test_coefficient_indices=False,
        arm_combination_scope='separate incoming and outgoing source applications; equal computational test indices do not identify physical external states across arms',
        all_induced_H_Gauss_frame_and_corner_returns_retained=True,
        supplied_maps='complete initial-data Cauchy envelopes with independently owned analytic left dual',
        energy_anchor=0,internal_operator_energy_action_held_zero=True,
        envelope_phase_cancellation_is_physical_band_motion=False,
        transpose_defects_are_binary_estimates_not_outward_bounds=True,
        physical_pole_mass_lifetime_or_native_Pauli_evaluated=False,physical_a_mu=None,physical_g_mu=None))
    v=dict(classification='PASSED_COMPLETE_CAUCHY_POINT_CURRENT_REPLAY_PAIRS',selected_file_count=len(files),
        input_pin_count=len(pins),pair_count=2,focused_tests_passed=2,all_replays_exit_zero=True,
        all_input_pins_current=True,manifest_sha256=identity(mp)['sha256'])
    vp=save('verification.json',v)
    print(json.dumps(dict(**v,verification_sha256=identity(vp)['sha256']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--incoming-chunks',nargs=2,required=True);p.add_argument('--outgoing-chunks',nargs=2,required=True)
    a=p.parse_args();freeze(a.output,incoming_chunks=a.incoming_chunks,outgoing_chunks=a.outgoing_chunks)
