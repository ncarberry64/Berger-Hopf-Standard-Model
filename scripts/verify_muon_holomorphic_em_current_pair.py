"""Freeze compact independent actual changing unit EM current replays."""
from pathlib import Path
from hashlib import sha256
import argparse,json
from verify_muon_holomorphic_current_source_pair import verify as verify_core
ROOT=Path(__file__).resolve().parents[1]


def verify(first,second,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve EM replay verification')
    verify_core(first,second,output/'core_pair_verification')
    core=json.loads((out/'core_pair_verification/publication_manifest.json').read_bytes())
    files=core['files']
    for name in ('src/bhsm/interface/muon_holomorphic_em_current.py','scripts/evaluate_muon_holomorphic_em_current.py',
        'tests/test_muon_holomorphic_em_current.py','scripts/verify_muon_holomorphic_em_current_pair.py',
        'artifacts/muon_holomorphic_current_source_20261012/em_test_run_1/verification.json',
        'artifacts/muon_holomorphic_current_source_20261012/em_test_run_1/stdout.txt',
        'artifacts/muon_holomorphic_current_source_20261012/em_test_run_1/stderr.txt',
        (output/'core_pair_verification/publication_manifest.json').as_posix()):
        p=ROOT/name;b=p.read_bytes();files[name]=dict(bytes=len(b),sha256=sha256(b).hexdigest())
    p=out/'publication_manifest.json'
    p.write_text(json.dumps(dict(classification='COMPACT_FROZEN_ACTUAL_CHANGING_UNIT_EM_CURRENT_PAIR',files=files,
        physical_charge_LSZ_pole_or_native_Pauli_completed=False,negative_incoming_component_is_backward_control=True),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(p.read_bytes()).hexdigest(),files=len(files))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--first',type=Path,required=True);p.add_argument('--second',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();verify(a.first,a.second,a.output)
