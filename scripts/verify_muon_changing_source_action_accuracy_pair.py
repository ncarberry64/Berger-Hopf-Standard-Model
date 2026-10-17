"""Freeze only completed bounded fresh-action derivative control replays."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def main():
    base=ROOT/'artifacts/muon_changing_source_action_accuracy_20261012';out=base/'pair_verification'
    if out.exists():raise FileExistsError('preserve bounded action accuracy verification')
    files={};pins={};reports=[]
    for number in(1,2):
        folder=base/f'run_{number}';p=folder/'result.json';b=p.read_bytes();md=json.loads(b);reports.append(md)
        if md['classification']!='BOUNDED_TWO_STEP_FRESH_LITERAL_ACTION_DERIVATIVE_ACCURACY_AT_ACTUAL_OUTGOING_SOURCES':
            raise ValueError('completed actual action control receipt required')
        if number==2 and b!=(base/'run_1/result.json').read_bytes():raise ValueError('actual action control replay receipt differs')
        files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        for name,record in md['archives'].items():
            p=folder/name;b=p.read_bytes()
            if len(b)!=record['bytes']or sha256(b).hexdigest()!=record['sha256']:
                raise ValueError('actual full action/control archive changed')
            if number==2 and b!=(base/'run_1'/name).read_bytes():raise ValueError('actual action control replay arrays differ')
            files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        for name,h in md['input_hashes'].items():
            if name in pins and pins[name]!=h:raise ValueError('same actual source/action pin conflict')
            pins[name]=h
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('literal action or supplied source changed')
    for i in(1,2):
        p=ROOT/f'artifacts/muon_changing_source_action_accuracy_20261012_run_{i}.stdout.txt'
        files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    p=Path(__file__);files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    result=dict(classification='VERIFIED_BOUNDED_TWO_STEP_FRESH_ACTION_DIRECTIONAL_CONTROL_PAIR',
        all_output_bytes_equal=True,input_hashes=pins,files=files,
        commands=[f'C:/Python314/python.exe scripts/evaluate_muon_changing_source_action_accuracy.py --output artifacts/muon_changing_source_action_accuracy_20261012/run_{i} --source-folder artifacts/muon_changing_canonical_source_20261012/run_3 --normalized-step 2e-5 --precision-bits 192'for i in(1,2)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        applications=reports[0]['applications'],action_parameters=reports[0]['action_parameters'],
        finite_difference_step_halving_diagnostics_not_an_action_enclosure=True,
        original_gradient_Higgs_geometry_gauge_and_literal_source_duals_retained=True,
        direct_area_source_preserved_separately=True,held_reference_is_declared_source_partial=True,
        no_additional_matrix_refinement_or_old_action_rerun=True,
        physical_mode_pole_domain_or_muon_anomaly_selected=False,
        scope='two consumed actual outgoing normal/area source directions only; finite directional/step-halving diagnostics and their existing readout effects, not outward action or physical error bounds')
    out.mkdir(parents=True);p=out/'publication_manifest.json'
    p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
