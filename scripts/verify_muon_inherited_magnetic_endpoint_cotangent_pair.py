"""Freeze compact repeated actual joined endpoint action/source consumption."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(base,output):
    folder=ROOT/base;out=ROOT/output
    if out.exists():raise FileExistsError('preserve endpoint-source verification')
    paths=[folder/f'run_{k}'for k in(1,2)];md=[json.loads((p/'result.json').read_bytes())for p in paths];selected={};pairs=[]
    def identity(p):
        p=ROOT/p if not p.is_absolute()else p;raw=p.read_bytes()
        if not p.is_relative_to(ROOT)or len(raw)>=10*1024**2:raise ValueError('only explicit compact same-checkout files')
        rec=dict(bytes=len(raw),sha256=sha256(raw).hexdigest());selected[p.relative_to(ROOT).as_posix()]=rec;return rec
    names=set(md[0]['archives'])|{'result.json'}
    if names!=set(md[1]['archives'])|{'result.json'}:raise ValueError('full scientific pair membership differs')
    for n in sorted(names):
        a,b=[identity(p/n)for p in paths]
        if a!=b:raise ValueError('repeated actual endpoint application differs '+n)
        if n!='result.json'and any(m['archives'][n]!=a for m in md):raise ValueError('frozen archive receipt differs')
        pairs.append(dict(name=n,**a,byte_identical=True))
    pins=md[0]['input_hashes']
    if pins!=md[1]['input_hashes']:raise ValueError('pair input pins differ')
    for p,h in pins.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('actual source/input pin changed '+p)
    for p in('src/bhsm/interface/muon_inherited_magnetic_endpoint_cotangent.py',
        'scripts/evaluate_muon_inherited_magnetic_endpoint_cotangent.py','scripts/run_muon_inherited_magnetic_endpoint_cotangent_pair.py',
        'scripts/verify_muon_inherited_magnetic_endpoint_cotangent_pair.py','tests/test_muon_inherited_magnetic_endpoint_cotangent.py'):
        identity(Path(p))
    for stem in('focused_tests_run_1','run_1','run_2'):
        for suffix in('.stdout.txt','.stderr.txt','.execution.json'):identity(folder/(stem+suffix))
        if json.loads((folder/(stem+'.execution.json')).read_bytes())['exit_code']!=0:raise ValueError('actual execution failed')
    out.mkdir(parents=True)
    v=dict(classification='IMMUTABLE_REPEATED_JOINED_MAGNETIC_ENDPOINT_ACTION_SOURCE_FIRST',scientific_pairs=pairs,
        checked_input_pins=len(pins),all_input_pins_current=True,direct_source_and_both_Pi_response_slots_consumed=True,
        parent_source_package='artifacts/muon_holomorphic_magnetic_inherited_cauchy_20261012/run_1',
        parent_regeneration_and_physical_state_not_selected_by_this_verification=True,
        endpoint_work_is_not_a_required_zero_reaction_or_Pauli_error_bound=True,
        physical_full_formation_exterior_pole_native_and_LSZ_completed=False,complete_clean_ancestor_regeneration_proved=False)
    p=out/'verification.json';p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');identity(p)
    m=dict(classification='COMPACT_REVIEWED_JOINED_MAGNETIC_ENDPOINT_CONSUMER_PAIR',files=selected,
        old_zero_child_D3_or_quadratic_not_relabelled_joined=True,all_raw_arrays_preserved=True,physical_a_mu_or_g_mu_assigned=False)
    p=out/'publication_manifest.json';p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(p.read_bytes()).hexdigest(),files=len(selected),scientific_pairs=len(pairs),pins=len(pins),
        selected_bytes=sum(r['bytes']for r in selected.values()),max_bytes=max(r['bytes']for r in selected.values()))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();verify(a.base,a.output)
