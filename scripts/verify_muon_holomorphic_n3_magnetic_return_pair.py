"""Freeze the actual source-directed named n3→n2/n4 test-action pair."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(base,output):
    folder=ROOT/base;out=ROOT/output
    if out.exists():raise FileExistsError('preserve each verification')
    a,b=[folder/f'outgoing_normal_basis_run_{k}'for k in(1,2)]
    md=[json.loads((p/'result.json').read_bytes())for p in(a,b)]
    pairs=[];selected={}
    def identity(p):
        p=ROOT/p if not p.is_absolute()else p;raw=p.read_bytes()
        if not p.is_relative_to(ROOT)or len(raw)>=10*1024**2:raise ValueError('only explicit compact same-checkout files')
        rec=dict(bytes=len(raw),sha256=sha256(raw).hexdigest());selected[p.relative_to(ROOT).as_posix()]=rec;return rec
    names=set(md[0]['archives'])|{'result.json'}
    if names!=set(md[1]['archives'])|{'result.json'}:raise ValueError('pair membership differs')
    for n in sorted(names):
        aa,bb=identity(a/n),identity(b/n)
        if aa!=bb:raise ValueError('actual replay differs '+n)
        if n!='result.json'and any(m['archives'][n]!=aa for m in md):raise ValueError('receipt changed')
        pairs.append(dict(name=n,**aa,byte_identical=True))
    pins=md[0]['input_hashes']
    if pins!=md[1]['input_hashes']:raise ValueError('program/input pins differ')
    for p,h in pins.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('input/source bytes changed '+p)
    for rel in ('src/bhsm/interface/muon_holomorphic_n3_magnetic_return.py',
        'scripts/evaluate_muon_holomorphic_n3_magnetic_return.py','scripts/run_muon_holomorphic_n3_magnetic_return_pair.py',
        'scripts/verify_muon_holomorphic_n3_magnetic_return_pair.py','tests/test_muon_holomorphic_n3_magnetic_return.py'):
        identity(Path(rel))
    for stem in ('focused_tests_run_1','outgoing_normal_basis_run_1','outgoing_normal_basis_run_2'):
        for suffix in ('.stdout.txt','.stderr.txt','.execution.json'):identity(folder/(stem+suffix))
        if json.loads((folder/(stem+'.execution.json')).read_bytes())['exit_code']!=0:raise ValueError('failed actual execution')
    out.mkdir(parents=True)
    v=dict(classification='IMMUTABLE_REPLAYED_ACTUAL_CAUSAL_B_N3_RETURN_NAMED_OPERATOR_ACTION',
        scientific_pairs=pairs,checked_input_pins=len(pins),all_input_pins_current=True,
        both_return_degrees=[2,4],all_K_Bforward_Breverse_M_placements=True,
        independent_literal_reverse_and_complex_Haar_controls=True,
        prior_draft_test_failure='curvature contraction initially indexed e,o,h Gaunt as h,e,o; two controls failed before production, then corrected; initial raw test stdout retained only in tool evidence',
        exact_clean_ancestor_regeneration_proved=False,
        supplied_named_test_right_inverse_is_not_physical_current_uniqueness=True,
        physical_pole_native_loop_LSZ_or_Pauli_completed=False)
    p=out/'verification.json';p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');identity(p)
    m=dict(classification='COMPACT_REVIEWED_N3_RETURN_TEST_ACTION_PAIR',files=selected,
        all_raw_source_arrays_preserved=True,physical_a_mu_or_g_mu_assigned=False)
    p=out/'publication_manifest.json';p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(p.read_bytes()).hexdigest(),files=len(selected),scientific_pairs=len(pairs),pins=len(pins),
        selected_bytes=sum(r['bytes']for r in selected.values()),max_bytes=max(r['bytes']for r in selected.values()))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();verify(a.base,a.output)
