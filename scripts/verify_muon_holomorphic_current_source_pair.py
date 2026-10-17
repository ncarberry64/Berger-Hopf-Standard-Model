"""Freeze two independent same-input full18 changing current applications."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(first,second,output):
    a,b,out=(ROOT/p for p in (first,second,output))
    if out.exists():raise FileExistsError('preserve independent pair verification')
    md=[json.loads((p/'result.json').read_bytes())for p in (a,b)]
    names=set(md[0]['archives'])|{'result.json'}
    if names!=set(md[1]['archives'])|{'result.json'}:raise ValueError('complete replay membership differs')
    selected={};pairs=[]
    def identity(p):
        if not p.is_relative_to(ROOT):raise ValueError('keep provenance inside intended checkout')
        raw=p.read_bytes()
        if len(raw)>=10*1024**2:raise ValueError('individual completed operand exceeds cap')
        rel=p.relative_to(ROOT).as_posix();value=dict(bytes=len(raw),sha256=sha256(raw).hexdigest())
        selected[rel]=value;return value
    for name in sorted(names):
        aa,bb=identity(a/name),identity(b/name)
        if aa!=bb:raise ValueError('independent complete replay differs: '+name)
        if name!='result.json':
            for m in md:
                if m['archives'][name]!=aa:raise ValueError('archive receipt differs')
        pairs.append(dict(name=name,**aa,byte_identical=True))
    pins=md[0]['input_hashes']
    if pins!=md[1]['input_hashes']:raise ValueError('both applications must use the same executed source inputs')
    for name,digest in pins.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('input/source pin changed: '+name)
    for name in ('src/bhsm/interface/muon_holomorphic_current_source.py','scripts/evaluate_muon_holomorphic_current_source.py',
            'tests/test_muon_holomorphic_current_source.py','scripts/verify_muon_holomorphic_current_source_pair.py',
            'artifacts/muon_holomorphic_current_source_20261012/test_run_1/verification.json',
            'artifacts/muon_holomorphic_current_source_20261012/test_run_1/stdout.txt',
            'artifacts/muon_holomorphic_current_source_20261012/test_run_1/stderr.txt'):
        identity(ROOT/name)
    out.mkdir(parents=True)
    record=dict(classification='IMMUTABLE_REPLAYED_CHANGING_CANONICAL_FULL18_CURRENT_SOURCE_PAIR',
        first=first.as_posix(),second=second.as_posix(),pairs=pairs,checked_input_pin_count=len(pins),
        inherited_source_high_low_applied_separately=True,all_inputs_current=True,
        complete_clean_ancestor_regeneration_proved=False,physical_event_exterior_pole_or_Pauli_completed=False)
    p=out/'verification.json';p.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');identity(p)
    manifest=dict(classification='COMPACT_FROZEN_FULL18_CURRENT_SOURCE_PUBLICATION_MANIFEST',files=selected,
        original_scientific_arrays_and_prior_failed_applications_preserved=True,
        physical_initial_or_terminal_exterior_maps_not_selected=True)
    p=out/'publication_manifest.json';p.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=sha256(p.read_bytes()).hexdigest(),files=len(selected),pair_outputs=len(pairs),pins=len(pins))))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--first',type=Path,required=True);p.add_argument('--second',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();verify(a.first,a.second,a.output)
