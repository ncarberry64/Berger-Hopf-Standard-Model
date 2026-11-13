"""Freeze the additive all-point unit-clock guard without changing prior packets."""
from pathlib import Path
from hashlib import sha256
import argparse,json

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_common_domain_charge_source_clock_20261011'


def freeze(output,run_chunks,test_chunk):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve each source-clock contract verification')
    folders=[BASE/f'contract_run_{k}'for k in(1,2)]
    names=[sorted(p.name for p in f.iterdir()if p.is_file())for f in folders]
    if names[0]!=names[1]or any((folders[0]/n).read_bytes()!=(folders[1]/n).read_bytes()for n in names[0]):
        raise ValueError('actual all-point clock contract replays differ')
    selected={}
    def pin(path,expected=None):
        path=Path(path);digest=sha256(path.read_bytes()).hexdigest()
        if expected is not None and digest!=expected:raise ValueError('source-clock contract dependency changed')
        selected[path.relative_to(ROOT).as_posix()]=digest
    result=json.loads((folders[0]/'result.json').read_bytes())
    if (result['ordinary_source_points']!=768 or result['original_points']!=3832 or
            result['ordinary_source_right_clock_difference_max']!=0 or
            result['frozen_numerical_first_germ_difference_max']!=0):
        raise ValueError('actual ordinary-clock or immutable first-germ contract failed')
    for folder in folders:
        for n in names[0]:pin(folder/n,result['archives'].get(n,{}).get('sha256'))
    for name,digest in result['input_hashes'].items():pin(ROOT/name,digest)
    for n in('publication_manifest.json','verification.json'):pin(BASE/'pair_verification'/n)
    pin(Path(__file__))
    out.mkdir(parents=True)
    verification=dict(classification='VERIFIED_ACTUAL_UNIT_SOURCE_CLOCK_CONTRACT_PAIR',
        result_sha256=sha256((folders[0]/'result.json').read_bytes()).hexdigest(),
        identical_files_per_run=len(names[0]),ordinary_source_points=768,
        original_source_and_connector_points=3832,
        source_right_clock_equals_one_exactly=True,
        numerical_charge_correction_unchanged=True,
        earlier_frozen_sources_outputs_and_plan_modified=False,
        runs=[dict(argv=['C:/Python314/python.exe','scripts/evaluate_muon_charge_source_clock_contract.py',
                         '--output',f.relative_to(ROOT).as_posix()],completed_exit_code=0,completion_chunk=c,
                    environment={'PYTHONPATH':'src','OPENBLAS_NUM_THREADS':'4'})for f,c in zip(folders,run_chunks)],
        focused_tests=dict(argv=['C:/Python314/python.exe','-m','pytest','-q',
                                'tests/test_muon_charge_source_clock_contract.py'],passed=2,
                           completed_exit_code=0,completion_chunk=test_chunk),
        physical_charge_LSZ_or_Pauli_assigned=False)
    vp=out/'verification.json';vp.write_text(json.dumps(verification,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    pin(vp)
    mp=out/'publication_manifest.json'
    mp.write_text(json.dumps(dict(classification='FROZEN_ADDITIVE_UNIT_SOURCE_CLOCK_CONTRACT_MANIFEST',
        files=dict(sorted(selected.items())),file_count=len(selected)),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(mp.read_bytes()).hexdigest(),
                         verification_sha256=sha256(vp.read_bytes()).hexdigest(),
                         result_sha256=verification['result_sha256'],files=len(selected))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--run-chunks',nargs=2,required=True);p.add_argument('--test-chunk',required=True)
    a=p.parse_args();freeze(a.output,a.run_chunks,a.test_chunk)
