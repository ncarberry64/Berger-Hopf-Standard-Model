"""Freeze the exact profile source and qualified coefficient-test replay."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_moving_reference_trace_source_20261012'


def digest(p):return sha256(p.read_bytes()).hexdigest()


def main():
    verification=BASE/'independent_pair_verification.json';manifest=BASE/'publication_manifest.json'
    if verification.exists()or manifest.exists():raise FileExistsError('preserve immutable full source image evidence')
    md=json.loads((BASE/'run_1/result.json').read_text());pairs={};files={}
    for name in('result.json',*md['archives']):
        a=BASE/'run_1'/name;b=BASE/'run_2'/name
        if a.read_bytes()!=b.read_bytes():raise ValueError('reference source replay differs '+name)
        pairs[name]=dict(bytes=a.stat().st_size,sha256=digest(a),identical=True)
        for p in(a,b):files[p.relative_to(ROOT).as_posix()]=digest(p)
    for p,h in md['input_hashes'].items():
        if digest(ROOT/p)!=h:raise ValueError('same profile source pin changed '+p)
    for rel in('src/bhsm/interface/muon_moving_reference_trace_source.py',
        'scripts/evaluate_muon_moving_reference_trace_source.py','tests/test_muon_moving_reference_trace_source.py',
        Path(__file__).relative_to(ROOT).as_posix()):files[rel]=digest(ROOT/rel)
    for r in(1,2):
        p=ROOT/f'artifacts/muon_moving_reference_trace_source_20261012_run_{r}.stdout.txt'
        files[p.relative_to(ROOT).as_posix()]=digest(p)
    record=dict(classification='INDEPENDENT_REPLAY_FULL_MOVING_REFERENCE_PROFILE_SOURCE_AND_FINITE_FIELD_TESTS',
        pairs=pairs,all_consumed_pins_current=True,
        exact_commands=[f'C:/Python314/python.exe scripts/evaluate_muon_moving_reference_trace_source.py --output artifacts/muon_moving_reference_trace_source_20261012/run_{r}'for r in(1,2)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        focused_control=dict(command='C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_moving_reference_trace_source.py',
            observed_tool_exit_code=0,observed_tool_result='2 passed in 1.85s',
            source_sha256=digest(ROOT/'tests/test_muon_moving_reference_trace_source.py')),
        actual_source_reproduction=dict(radial=md['radial_source_reproduction_max'],wall=md['wall_source_reproduction_max']),
        coefficient_test_convention='column0 is the original64 gauge VALUE-trace test source. Columns1/2 are independent VALUE-basis tests of the time/radial output FUNCTIONS; column2 is not the physical radial derivative of column0 coefficients.',
        complete_source_germ='exact full value/time/radial profile and exact wall are primary; derivative consistency belongs to the analytic profile, not auxiliary projected columns',
        source_image_complement_and_wall_mismatch_preserved=True,
        frozen_coefficient_offset_zero_not_substituted_for_full_source=True,
        original_trace_rows_temporal_endpoint_not_continuous_bulk_glue=True,
        physical_event_clock_or_mode_or_exterior_selected=False,
        physical_Pauli_completed=False)
    verification.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    files[verification.relative_to(ROOT).as_posix()]=digest(verification)
    packet=dict(classification=record['classification'],files=files,
        dependencies=[p for p in md['input_hashes']if p.endswith('result.json')],physical_Pauli_completed=False)
    manifest.write_text(json.dumps(packet,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(all_outputs_byte_identical=len(pairs),input_pins_current=len(md['input_hashes']),
        verification_sha256=digest(verification),manifest_sha256=digest(manifest)),sort_keys=True))


if __name__=='__main__':main()
