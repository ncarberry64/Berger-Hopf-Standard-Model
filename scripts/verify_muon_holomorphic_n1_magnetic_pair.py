"""Freeze actual signed magnetic weak/causal current replay operands."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(first,second,output):
    a,b,out=(ROOT/p for p in(first,second,output))
    if out.exists():raise FileExistsError('preserve original magnetic pair verification')
    md=[json.loads((p/'result.json').read_bytes())for p in(a,b)]
    names=set(md[0]['archives'])|{'result.json'}
    if names!=set(md[1]['archives'])|{'result.json'}:raise ValueError('complete scientific pair membership differs')
    selected={};pairs=[]
    def identity(p):
        p=Path(p)
        if not p.is_absolute():p=ROOT/p
        raw=p.read_bytes()
        if not p.is_relative_to(ROOT)or len(raw)>=10*1024**2:raise ValueError('keep explicit compact same-checkout paths')
        rec=dict(bytes=len(raw),sha256=sha256(raw).hexdigest());selected[p.relative_to(ROOT).as_posix()]=rec;return rec
    for n in sorted(names):
        aa,bb=identity(a/n),identity(b/n)
        if aa!=bb:raise ValueError('independent actual magnetic replay differs: '+n)
        if n!='result.json'and any(m['archives'][n]!=aa for m in md):raise ValueError('archive receipt differs')
        pairs.append(dict(name=n,**aa,byte_identical=True))
    pins=md[0]['input_hashes']
    if pins!=md[1]['input_hashes']:raise ValueError('both source/program input pins must agree')
    for p,d in pins.items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=d:raise ValueError('source/input changed after execution: '+p)
    science=('src/bhsm/interface/muon_holomorphic_n1_magnetic_action.py',
        'src/bhsm/interface/muon_holomorphic_n1_magnetic_cauchy.py',
        'scripts/evaluate_muon_holomorphic_n1_magnetic_action.py',
        'scripts/run_muon_holomorphic_n1_magnetic_pairs.py',
        'scripts/verify_muon_holomorphic_n1_magnetic_pair.py')
    tests=('tests/test_muon_holomorphic_n1_magnetic_action.py','tests/test_muon_holomorphic_n1_magnetic_cauchy.py',
        'tests/test_muon_holomorphic_n1_magnetic_current_first.py','tests/test_muon_complex_n1_literal_action.py',
        'tests/test_muon_complex_n1_row_polynomial.py','tests/test_muon_n1_magnetic_current_independent.py',
        'tests/test_muon_mixed_magnetic_current_independent.py')
    for p in science+tests:identity(p)
    # This helper belongs only to the independently executed control.
    identity('src/bhsm/interface/muon_holomorphic_magnetic_current_source_jet.py')
    controls=Path('artifacts/muon_holomorphic_n1_magnetic_action_20261012/final_focused_tests_run_1')
    for n in ('stdout.txt','stderr.txt','verification.json'):identity(controls/n)
    controls_md=json.loads((ROOT/controls/'verification.json').read_bytes())
    if controls_md['exit_code']!=0:raise ValueError('focused controls did not pass')
    for p,d in controls_md['test_source_pins'].items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=d:raise ValueError('executed control source changed')
    for folder in (a,b):
        for suffix in ('.stdout.txt','.stderr.txt','.execution.json'):
            identity(folder.parent/(folder.name+suffix))
        execution=json.loads((folder.parent/(folder.name+'.execution.json')).read_bytes())
        if execution['exit_code']!=0:raise ValueError('recorded subprocess did not complete')
    out.mkdir(parents=True)
    rec=dict(classification='IMMUTABLE_REPLAYED_SIGNED_CHANGING_N1_MAGNETIC_ACTION_AND_CURRENT',
        first=first.as_posix(),second=second.as_posix(),scientific_pairs=pairs,checked_input_pin_count=len(pins),
        all_inputs_current=True,high_low_sources_acted_independently=True,
        causal_incoming_stage_order_reversed_and_Qdot_kept=True,
        weak_initial_held_final_natural_not_same_as_zero_Cauchy=True,
        absolute_causal_or_physical_admission_certificate=False,
        original_row_scales_reactions_and_residuals_preserved=True,
        current_projection_is_not_Pauli_or_a_residual_enclosure=True,
        complete_clean_ancestor_regeneration_proved=False,
        physical_exterior_pole_charge_LSZ_native_or_anomaly_completed=False)
    p=out/'verification.json';p.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');identity(p)
    m=dict(classification='COMPACT_FROZEN_SIGNED_N1_MAGNETIC_FIELD_AND_CURRENT_PAIR',files=selected,
        preserved_development_attempts_not_selected=True,source_function_and_independent_control_reference_distinct=True,
        no_physical_total_or_zero_omitted_sector_claim=True)
    p=out/'publication_manifest.json';p.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(p.read_bytes()).hexdigest(),files=len(selected),scientific_pairs=len(pairs),pins=len(pins))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--first',type=Path,required=True);p.add_argument('--second',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.first,a.second,a.output)
