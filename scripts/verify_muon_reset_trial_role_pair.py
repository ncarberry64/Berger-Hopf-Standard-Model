"""Freeze the explicit compact role/source application replay closure."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_reset_trial_role_application_20261012'


def digest(path):return sha256(path.read_bytes()).hexdigest()


def main():
    verification=BASE/'independent_pair_verification.json';manifest=BASE/'publication_manifest.json'
    if verification.exists()or manifest.exists():raise FileExistsError('preserve immutable replay evidence')
    first=BASE/'run_3';second=BASE/'run_4';md=json.loads((first/'result.json').read_text())
    names=['result.json',*md['archives']];files={};pairs={}
    for name in names:
        a=first/name;b=second/name
        if a.read_bytes()!=b.read_bytes():raise ValueError('independent replay bytes differ '+name)
        for p in(a,b):files[p.relative_to(ROOT).as_posix()]=digest(p)
        pairs[name]=dict(sha256=digest(a),bytes=a.stat().st_size,identical=True)
    for path,h in md['input_hashes'].items():
        if digest(ROOT/path)!=h:raise ValueError('consumed role/source input changed '+path)
    owned=['src/bhsm/interface/muon_reset_trial_role_application.py',
        'scripts/evaluate_muon_reset_trial_role_application.py',
        'tests/test_muon_reset_trial_role_application.py',Path(__file__).relative_to(ROOT).as_posix()]
    for rel in owned:files[rel]=digest(ROOT/rel)
    for run in(3,4):
        p=BASE/f'run_{run}.stdout.txt';files[p.relative_to(ROOT).as_posix()]=digest(p)
    data=dict(classification='INDEPENDENT_REPLAY_RESET_TRIAL_ROLE_AND_SOURCE_AUDIT',
        canonical_runs=['run_3','run_4'],pairs=pairs,all_consumed_pins_current=True,
        materialization_commands=[f'C:/Python314/python.exe scripts/evaluate_muon_reset_trial_role_application.py --output artifacts/muon_reset_trial_role_application_20261012/run_{r}'for r in(3,4)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        focused_control=dict(command='C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_reset_trial_role_application.py',
            observed_tool_exit_code=0,observed_tool_result='1 passed in 0.80s',
            source_sha256=digest(ROOT/'tests/test_muon_reset_trial_role_application.py')),
        earlier_runs_scope='run_1/run_2 numerical arrays identical; receipts predate complete imported-source and reference/parameter guard. They remain local and excluded from this canonical publication closure.',
        natural_traction_role='actual force/energy readout, not forbidden variation or forced zero; internal natural matching follows the later action-derived choice of free boundary variations',
        physical_formation_or_Pauli_selected=False)
    verification.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    files[verification.relative_to(ROOT).as_posix()]=digest(verification)
    packet=dict(classification=data['classification'],files=files,
        dependencies=[p for p in md['input_hashes']if p.endswith('result.json')],
        physical_Pauli_completed=False)
    manifest.write_text(json.dumps(packet,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(all_output_files_byte_identical=len(pairs),consumed_pin_count=len(md['input_hashes']),
        verification_sha256=digest(verification),manifest_sha256=digest(manifest)),sort_keys=True))


if __name__=='__main__':main()
