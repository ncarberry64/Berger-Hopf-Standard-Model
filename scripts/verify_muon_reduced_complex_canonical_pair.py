"""Verify every independently replayed original62 output and consumed pin."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def verify():
    base=ROOT/'artifacts/muon_reduced_complex_canonical_geometry_20261011'
    out=base/'independent_pair_verification.json'
    if out.exists():raise FileExistsError('preserve immutable replay evidence')
    a,b=base/'run_1',base/'replay_run_1'
    def files(p):return{x.relative_to(p).as_posix():x for x in p.rglob('*')if x.is_file()}
    aa,bb=files(a),files(b)
    if aa.keys()!=bb.keys():raise ValueError('all-output membership differs')
    pairs={}
    for n in sorted(aa):
        h=sha256(aa[n].read_bytes()).hexdigest()
        if h!=sha256(bb[n].read_bytes()).hexdigest():raise ValueError('byte mismatch: '+n)
        pairs[n]=h
    md=json.loads((a/'result.json').read_bytes())
    for p,h in md['input_hashes'].items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed pin changed: '+p)
    log=base/'replay_run_1.stdout.txt';data=log.read_bytes()
    result=dict(classification='INDEPENDENT_BYTE_IDENTICAL_EXACT84_FIELD_PLUS2_TO62_CANONICAL_APPLICATION',
        original='artifacts/muon_reduced_complex_canonical_geometry_20261011/run_1',
        replay='artifacts/muon_reduced_complex_canonical_geometry_20261011/replay_run_1',
        all_output_byte_identical=True,all_output_count=len(pairs),all_output_sha256=pairs,
        argv=['C:/Python314/python.exe','scripts/evaluate_muon_reduced_complex_canonical_geometry.py',
            '--output','artifacts/muon_reduced_complex_canonical_geometry_20261011/replay_run_1','--max-evaluations','40'],
        default_input_paths=dict(initial_folder='artifacts/muon_safeguarded_complex_constitutive_20261011/resumed_run_1',
            terminal_folder='artifacts/muon_holomorphic_child_terminal_20261011/run_2'),
        cwd=str(ROOT),environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        exit_code=0,stdout=dict(path=log.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest(),
            provenance='Complete actual PowerShell Tee-Object bytes from independent replay'),
        consumed_input_pins_current=True,consumed_pin_count=len(md['input_hashes']),
        original_rows_max=md['original_rows_max'],status=md['status'],
        full_ancestor_rematerialization_executed=False,physical_stationarity_or_Pauli_claim=False,
        verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=out.relative_to(ROOT).as_posix(),sha256=sha256(out.read_bytes()).hexdigest(),
        all_output_count=len(pairs),result_sha256=pairs['result.json'],application_sha256=pairs['application.npz']),sort_keys=True))


if __name__=='__main__':verify()
