"""Nonmutating verification of reached complex geometry/shape applications."""
from pathlib import Path
from hashlib import sha256
import argparse,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SPECS=(
 ('muon_reached_geometry_canonical_return_20261012','evaluate_muon_reached_geometry_canonical_return.py','test_muon_reached_geometry_canonical_return.py'),
 ('muon_reached_geometry_green_source_20261012','evaluate_muon_reached_geometry_green_source.py','test_muon_reached_geometry_green_source.py'),
 ('muon_actual_normal_shape_source_20261012','evaluate_muon_actual_normal_shape_source.py','test_muon_actual_normal_shape_source.py'),
 ('muon_normal_shape_weak_consumption_20261012','evaluate_muon_normal_shape_weak_consumption.py','test_muon_normal_shape_weak_consumption.py'),
 ('muon_normal_shape_rate_attribution_20261012','evaluate_muon_normal_shape_rate_attribution.py','test_muon_normal_shape_rate_attribution.py'))


def run(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior pair verifications')
    selected={};pins={};records=[];scientific_count=0
    for stem,driver,test in SPECS:
        folders=[ROOT/'artifacts'/stem/f'run_{i}'for i in(1,2)]
        paths=[f/'result.json'for f in folders]
        if any(not p.is_file()for p in paths):raise FileNotFoundError('completed result pair required: '+stem)
        if paths[0].read_bytes()!=paths[1].read_bytes():raise ValueError('result bytes differ: '+stem)
        md=json.loads(paths[0].read_bytes())
        for p,h in md['input_hashes'].items():
            if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('input pin changed: '+p)
            if p in pins and pins[p]!=h:raise ValueError('cross-package source conflict: '+p)
            pins[p]=h
        if 'tests/'+test not in md['input_hashes']:raise ValueError('focused test pin missing')
        pairs=[]
        for name,a in md['archives'].items():
            ps=[f/name for f in folders]
            if any(sha256(p.read_bytes()).hexdigest()!=a['sha256']for p in ps)or ps[0].read_bytes()!=ps[1].read_bytes():
                raise ValueError('archive pair failed: '+stem+'/'+name)
            for p in ps:selected[p.relative_to(ROOT).as_posix()]=a['sha256']
            pairs.append(name);scientific_count+=2
        for p in paths:selected[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest();scientific_count+=1
        executions=[]
        for i in(1,2):
            log=ROOT/'artifacts'/f'{stem}_run_{i}.stdout.txt'
            if not log.is_file():raise FileNotFoundError('actual executed stdout required: '+str(log))
            executions.append(dict(argv=['C:/Python314/python.exe','scripts/'+driver,'--output',f'artifacts/{stem}/run_{i}'],
                env={'PYTHONPATH':'src;scripts','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},cwd=ROOT.as_posix(),
                stdout_path=log.relative_to(ROOT).as_posix(),stdout_sha256=sha256(log.read_bytes()).hexdigest(),
                status='executed commands recorded by the actual tool calls; no recipe-only execution claim'))
        records.append(dict(component=stem,result_sha256=sha256(paths[0].read_bytes()).hexdigest(),byte_identical_archives=pairs,executions=executions))
    # Actual admission remains separate from matrix identities and source fits.
    rate=json.loads((ROOT/'artifacts/muon_normal_shape_rate_attribution_20261012/run_1/result.json').read_bytes())
    if any(r['recovered_original_residual_difference']!=0 for r in rate['records']):raise ValueError('original rate recovery failed')
    if any(r['literal_two_term_original146_upper']>2e-10 for r in rate['records']):raise ValueError('literal original rate gate failed')
    weak=json.loads((ROOT/'artifacts/muon_normal_shape_weak_consumption_20261012/run_1/result.json').read_bytes())
    if weak['physical_outgoing_environment_formation_or_selected_mode_admitted']:raise ValueError('unproved domain promoted')
    # Quantify solve correction independently of changed export arithmetic.
    p=ROOT/'artifacts/muon_normal_shape_rate_attribution_20261012/run_1/bounded_rate_effect_on_all67_weak_shape.npz'
    with np.load(p)as a:
        effects={s:dict(fixed_rhs_minus_exact_contraction_of_original_rate_max=float(np.max(abs(a['fixed_stored_rhs_'+s+'_complete']-a['original_binary_'+s+'_complete']))),
            literal_low_rhs_minus_fixed_rhs_max=float(np.max(abs(a['literal_two_term_rhs_'+s+'_complete']-a['fixed_stored_rhs_'+s+'_complete']))))for s in('base','area')}
    out.mkdir(parents=True)
    result=dict(classification='VERIFIED_REACHED_COMPLEX_GEOMETRY_SHAPE_SOURCE_AND_BOUNDED_RATE_PAIRS',pairs=records,
        input_pins_current=len(pins),selected_scientific_file_count=scientific_count,
        all_original_rate_targets_recovered_bitwise=True,literal_two_term_original_rate_guard=2e-10,
        solve_only_projected_effects=effects,original_birth226_max=weak['original_birth226_max'],
        original_all67_mechanical_work=weak['original_all67_clock_scaled_mechanical_work'],
        physical_birth_formation_exterior_or_pole_admitted=False,
        matrix_and_weak_source_work_not_physical_observable_bound=True)
    v=out/'verification.json';v.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    verifier='scripts/'+Path(__file__).name;pins[verifier]=sha256(Path(__file__).read_bytes()).hexdigest()
    manifest=dict(classification='REVIEWED_COMPLETED_REACHED_ACTION_SOURCE_PAIRS_ONLY',files=selected,input_hashes=pins,
        verification=dict(path=v.relative_to(ROOT).as_posix(),sha256=sha256(v.read_bytes()).hexdigest()),
        physical_a_mu=None,physical_g_mu=None)
    m=out/'publication_manifest.json';m.write_text(json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(verification_sha256=sha256(v.read_bytes()).hexdigest(),manifest_sha256=sha256(m.read_bytes()).hexdigest(),scientific_files=scientific_count,pins=len(pins),solve_only_projected_effects=effects),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('artifacts/muon_actual_shape_source_final_pairs_20261012'));a=p.parse_args();run(a.output)
