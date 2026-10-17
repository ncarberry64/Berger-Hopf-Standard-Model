"""Freeze the conditional actual descriptor-frame source pair only."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def verify():
    base=ROOT/'artifacts/muon_canonical_descriptor_frame_application_20261012'
    out=base/'independent_pair_verification.json'
    if out.exists():raise FileExistsError('preserve every descriptor control verification')
    a,b=base/'run_1',base/'run_2'
    af={p.name:p for p in a.iterdir()if p.is_file()};bf={p.name:p for p in b.iterdir()if p.is_file()}
    if af.keys()!=bf.keys():raise ValueError('every output must be replayed')
    hashes={}
    for n in sorted(af):
        h=sha256(af[n].read_bytes()).hexdigest()
        if h!=sha256(bf[n].read_bytes()).hexdigest():raise ValueError('byte mismatch '+n)
        hashes[n]=h
    md=json.loads((a/'result.json').read_bytes())
    for p,h in md['input_hashes'].items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed pin changed '+p)
    logs={}
    for i in(1,2):
        data=(Path('C:/Users/carbe/Downloads')/f'BHSM_canonical_descriptor_frame_run_{i}.stdout.txt').read_bytes()
        p=base/f'run_{i}.stdout.txt';p.write_bytes(data)
        logs[p.name]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
    data=Path('C:/Users/carbe/Downloads/BHSM_canonical_descriptor_frame_tests_final.stdout.txt').read_bytes()
    p=base/'tests_final.stdout.txt';p.write_bytes(data)
    result=dict(classification='INDEPENDENT_REPLAY_CONTROL_ONLY_ACTUAL_FRAME_REFERENCE_SOURCE_APPLICATION',
        all_output_bytes_identical=True,all_output_count=len(hashes),all_output_sha256=hashes,input_pins_current=True,
        executions=[dict(argv=['C:/Python314/python.exe','scripts/evaluate_muon_canonical_descriptor_frame_application.py',
            '--output',f'artifacts/muon_canonical_descriptor_frame_application_20261012/run_{i}'],exit_code=0)for i in(1,2)],
        shared_environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),cwd=str(ROOT),
        exact_default_inputs=dict(endpoint='artifacts/muon_complex_canonical_endpoint_20261012/continued_run_1',
            reference_archive='artifacts/flagship_integration/BHSM_N12_C2_LOHNER_STEP_1222.npz'),
        stdout=logs,capture_provenance='complete actual PowerShell Tee-Object bytes',
        test=dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q','tests/test_muon_canonical_descriptor_frame_application.py'],
            exit_code=0,stdout_path=p.relative_to(ROOT).as_posix(),stdout_sha256=sha256(data).hexdigest()),
        physical_stop_reference_or_pole_selected=False,full_ancestor_rematerialization_executed=False,
        verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    files=['src/bhsm/interface/muon_canonical_descriptor_frame_application.py',
        'scripts/evaluate_muon_canonical_descriptor_frame_application.py',
        'tests/test_muon_canonical_descriptor_frame_application.py',Path(__file__).relative_to(ROOT).as_posix()]
    files+=sorted(p.relative_to(ROOT).as_posix()for p in base.rglob('*')if p.is_file())
    manifest=base/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification=result['classification'],
        files={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in files},physical_first_hit_or_Pauli_completed=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification=out.relative_to(ROOT).as_posix(),verification_sha256=sha256(out.read_bytes()).hexdigest(),
        result_sha256=hashes['result.json'],application_sha256=hashes['application.npz'],
        manifest_sha256=sha256(manifest.read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':verify()
