"""Freeze actual pure U_B and all three source-first slots, without pole claims."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(base,output):
    folder=ROOT/base;out=ROOT/output
    if out.exists():raise FileExistsError('preserve each puretrace verification')
    paths=[folder/f'run_{k}'for k in(1,2)];md=[json.loads((p/'result.json').read_bytes())for p in paths];selected={};pairs=[]
    def identity(p):
        p=ROOT/p if not p.is_absolute()else p;raw=p.read_bytes()
        if not p.is_relative_to(ROOT)or len(raw)>=10*1024**2:raise ValueError('explicit compact same-checkout files only')
        rec=dict(bytes=len(raw),sha256=sha256(raw).hexdigest());selected[p.relative_to(ROOT).as_posix()]=rec;return rec
    names=set(md[0]['archives'])|{'result.json'}
    if names!=set(md[1]['archives'])|{'result.json'}:raise ValueError('complete pair membership differs')
    for n in sorted(names):
        a,b=[identity(p/n)for p in paths]
        if a!=b:raise ValueError('actual independent U_B replay differs '+n)
        if n!='result.json'and any(m['archives'][n]!=a for m in md):raise ValueError('archive receipt differs')
        pairs.append(dict(name=n,**a,byte_identical=True))
    pins=md[0]['input_hashes']
    if pins!=md[1]['input_hashes']:raise ValueError('pair input pins differ')
    for p,h in pins.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('actual source/stage bytes changed '+p)
    for p in('src/bhsm/interface/muon_inherited_magnetic_pure_trace.py','scripts/evaluate_muon_inherited_magnetic_pure_trace.py',
        'scripts/run_muon_inherited_magnetic_pure_trace_pair.py','scripts/verify_muon_inherited_magnetic_pure_trace_pair.py',
        'tests/test_muon_inherited_magnetic_pure_trace.py'):
        identity(Path(p))
    for stem in('focused_tests_run_1','run_1','run_2'):
        for suffix in('.stdout.txt','.stderr.txt','.execution.json'):identity(folder/(stem+suffix))
        if json.loads((folder/(stem+'.execution.json')).read_bytes())['exit_code']!=0:raise ValueError('recorded control/production failed')
    out.mkdir(parents=True)
    v=dict(classification='IMMUTABLE_ACTUAL_SOURCE_ON_PURE_U_B_AND_THREE_FIRST_SLOTS',scientific_pairs=pairs,
        checked_input_pins=len(pins),all_inputs_current=True,source_points=20,all18_fibers_preserved=True,
        whole_complex_FD_control=True,earlier_control_attempt='all whole-transfer FD comparisons passed; a 2e-17 transpose tolerance missed a 2.78e-17 product-order rounding difference; tolerance2e-16 adopted without numerical implementation change, raw initial stdout remains in tool evidence',
        test_degrees=[0,1],n1_to_n2_image_full_complement_not_evaluated=True,
        current_J_transpose_inverse_J_not_used_as_pure_transfer=True,
        physical_Bi_Bf_pole_residue_charge_or_Pauli_not_selected=True,
        failed_original_coupled_row223_retained_as_separately_pinned_action_relation=True,
        complete_clean_ancestor_regeneration_proved=False,preserved_development_run_not_selected=True)
    p=out/'verification.json';p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');identity(p)
    m=dict(classification='COMPACT_REVIEWED_ACTUAL_MAGNETIC_PURE_TRACE_OPERAND_PAIR',files=selected,
        all_raw_arrays_preserved=True,physical_a_mu_or_g_mu_assigned=False)
    p=out/'publication_manifest.json';p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(p.read_bytes()).hexdigest(),files=len(selected),scientific_pairs=len(pairs),pins=len(pins),
        selected_bytes=sum(r['bytes']for r in selected.values()),max_bytes=max(r['bytes']for r in selected.values()))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();verify(a.base,a.output)
