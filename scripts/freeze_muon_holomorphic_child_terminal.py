"""Freeze completed analytic terminal controls and action-defect replays."""
from pathlib import Path
from hashlib import sha256
import json,sys
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'artifacts/muon_holomorphic_child_terminal_20261011/pair_verification'
    if out.exists():raise FileExistsError('preserve the immutable completed action verification')
    pairs=[('muon_holomorphic_child_terminal_20261011','run_2','run_3','evaluate_muon_holomorphic_child_terminal.py'),
           ('muon_complex_terminal_defect_attribution_20261011','run_1','run_2','evaluate_muon_complex_terminal_defect_attribution.py'),
           ('muon_complex_terminal_action_sectors_20261011','run_1','run_2','evaluate_muon_complex_terminal_action_sectors.py')]
    selected=set();pins={};records=[];commands=[]
    for family,left,right,script in pairs:
        a=ROOT/'artifacts'/family/left;b=ROOT/'artifacts'/family/right
        ma=json.loads((a/'result.json').read_bytes());mb=json.loads((b/'result.json').read_bytes())
        if ma!=mb:raise ArithmeticError('completed action replay receipts differ')
        names=sorted(set(ma['archives'])|{'result.json'})
        for name in names:
            pa,pb=a/name,b/name;ba,bb=pa.read_bytes(),pb.read_bytes()
            if ba!=bb:raise ArithmeticError('completed action replay arrays differ: '+name)
            if name!='result.json'and sha256(ba).hexdigest()!=ma['archives'][name]['sha256']:
                raise ArithmeticError('archive receipt mismatch')
            selected.update((pa.relative_to(ROOT).as_posix(),pb.relative_to(ROOT).as_posix()))
            records.append(dict(group=family,relative_name=name,sha256=sha256(ba).hexdigest(),bytes=len(ba)))
        for run in(left,right):
            log=Path('artifacts')/(family+'_'+run+'_stdout.txt');selected.add(log.as_posix())
            commands.append(dict(argv=['C:/Python314/python.exe','scripts/'+script,'--output','artifacts/'+family+'/'+run],
                exit_code=0,stdout_log=log.as_posix(),environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4')))
        for path,h in ma['input_hashes'].items():
            if path in pins and pins[path]!=h:raise ArithmeticError('action applications consumed different source bytes')
            pins[path]=h
    sources=['src/bhsm/interface/muon_holomorphic_normal_geometry.py','src/bhsm/interface/muon_holomorphic_child_action.py',
        'src/bhsm/interface/muon_complex_canonical_compatibility.py',
        'scripts/evaluate_muon_holomorphic_child_terminal.py','scripts/evaluate_muon_complex_canonical_compatibility.py',
        'scripts/evaluate_muon_complex_terminal_defect_attribution.py','scripts/evaluate_muon_complex_terminal_action_sectors.py',
        'tests/test_muon_holomorphic_child_action.py','tests/test_muon_holomorphic_child_action_review.py',
        'tests/test_muon_complex_canonical_compatibility.py',Path(__file__).relative_to(ROOT).as_posix()]
    selected.update(sources)
    review=ROOT/'artifacts/muon_holomorphic_child_independent_review_20261011/run_1'
    selected.update(p.relative_to(ROOT).as_posix()for p in review.iterdir()if p.is_file())
    # The earlier three-step application is deliberately retained as an
    # unsuccessful Newton control, never as constraint stationarity.
    old=ROOT/'artifacts/muon_complex_canonical_compatibility_20261011/run_1'
    selected.update(p.relative_to(ROOT).as_posix()for p in old.iterdir()if p.is_file())
    selected.add('artifacts/muon_complex_canonical_compatibility_20261011_run_1_stdout.txt')
    oldmd=json.loads((old/'result.json').read_bytes())
    if oldmd['status']=='FRAMED_CONSTITUTIVE_TOLERANCE':raise ArithmeticError('unsuccessful control classification changed')
    for path,h in oldmd['input_hashes'].items():
        if path in pins and pins[path]!=h:raise ArithmeticError('old constitutive diagnostic source differs')
        pins[path]=h
    for path,h in pins.items():
        if sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ArithmeticError('consumed input changed: '+path)
    out.mkdir(parents=True)
    verification=dict(classification='VERIFIED_REPLAY_OF_ORIGINAL_COMPLEX_CHILD252_ACTION_AND_CONSTRAINT_ATTRIBUTION',
        completed_action_pairs_byte_identical=True,pairs=records,commands=commands,input_hashes=pins,
        independent_review='artifacts/muon_holomorphic_child_independent_review_20261011/run_1/verification.json',
        named_Ward_control='artifacts/muon_holomorphic_child_independent_review_20261011/run_1/canonical_ward_control.json',
        original_three_step_Newton_status=oldmd['status'],original_constraint_stationarity_established=False,
        physical_exterior_first_hit_Pauli_or_error_bound=False,
        scope='Original analytic raw268/full252 action at actual complex node1150; completed differential/replay controls and lapse/shift stress attribution. Node1150 remains finite exhaustion and original constraint correction remains active.')
    p=out/'verification.json';p.write_text(json.dumps(verification,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    selected.add(p.relative_to(ROOT).as_posix())
    files={path:dict(bytes=(ROOT/path).stat().st_size,sha256=sha256((ROOT/path).read_bytes()).hexdigest())for path in sorted(selected)}
    p=out/'publication_manifest.json';p.write_text(json.dumps(dict(classification='IMMUTABLE_COMPLETED_COMPLEX_CHILD_ACTION_PUBLICATION_FILES',
        files=files,input_hashes=pins),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='complex_child_action_publication_frozen',files=len(files),input_pins=len(pins),
        manifest=p.relative_to(ROOT).as_posix(),manifest_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
