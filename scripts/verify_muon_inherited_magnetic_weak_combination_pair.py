"""Verify byte-identical source-on combined weak-action applications."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def main(run_numbers=(1,2), output='pair_verification'):
    base=ROOT/'artifacts/muon_inherited_magnetic_weak_combination_20261012';out=base/output
    if out.exists():raise FileExistsError('preserve weak-combination replay evidence')
    files={};pins={};original=None;reports=[];commands=[]
    def add(p):
        b=p.read_bytes();files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest();return b
    for ordinal,run in enumerate(run_numbers):
        folder=base/f'run_{run}';p=folder/'result.json';b=add(p);r=json.loads(b)
        if original is None:original=b
        elif b!=original:raise ValueError('same signed bulk/source/return receipt differs')
        if r['classification']!='EVALUATED_INHERITED_SIGNED_MAGNETIC_ACTION_SOURCE_AND_TEMPORAL_RETURNS':
            raise ValueError('completed action consumer required')
        for name,meta in r['archives'].items():
            a=add(folder/name)
            if len(a)!=meta['bytes']or sha256(a).hexdigest()!=meta['sha256']:raise ValueError('action array hash differs')
            if ordinal==1 and a!=(base/f'run_{run_numbers[0]}'/name).read_bytes():raise ValueError('same source/action/return replay differs')
        for name,h in r['input_hashes'].items():
            if name in pins and pins[name]!=h:raise ValueError('action/source input pin conflict')
            pins[name]=h
        for ext in('stdout','stderr'):add(ROOT/f'artifacts/muon_inherited_magnetic_weak_combination_20261012_run_{run}.{ext}.txt')
        commands.append(['C:/Python314/python.exe','scripts/evaluate_muon_inherited_magnetic_weak_combination.py',
            '--source-folder',r['source_folder'],'--faces-folder',r['faces_folder'],'--output',folder.relative_to(ROOT).as_posix()])
        reports.append(r['applications'])
    for name,h in pins.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('executed action/source pin changed')
    add(Path(__file__));add(ROOT/'artifacts/muon_inherited_magnetic_weak_combination_tests_20261012.tool_result.json')
    record=dict(classification='VERIFIED_INHERITED_SIGNED_MAGNETIC_WEAK_COMBINATION_PAIR',
        files=files,input_hashes=pins,all_output_bytes_equal=True,commands=commands,
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        applications=reports[0],source_and_bulk_first_slots_initial_corner_outer_returns_consumed=True,
        weak_closure_defects_retained_not_assigned_zero=True,physical_Pauli_or_error_enclosure_completed=False,
        error_scope='deterministic same-stored action/source replay and input pins; finite weak-closure diagnostics retain their original temporal/domain and normalization scope')
    out.mkdir(parents=True);p=out/'publication_manifest.json'
    p.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest())))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=int,nargs=2,default=(1,2));p.add_argument('--output',default='pair_verification')
    a=p.parse_args();main(tuple(a.runs),a.output)
