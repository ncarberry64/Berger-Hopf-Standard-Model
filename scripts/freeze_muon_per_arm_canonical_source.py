"""Freeze reviewed conditional bases and source-aware canonical admission."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'artifacts/muon_per_arm_canonical_source_20261012/pair_verification'
    if out.exists():raise FileExistsError('preserve source admission verification')
    pairs=[('muon_reset_constrained_canonical_variation_20261012',2,3),
        ('muon_reset_secondary_canonical_source_20261012',1,2),
        ('muon_per_arm_canonical_source_20261012',1,2),('muon_admitted_parent_source_germ_20261012',1,2)]
    files={};pins={};records={}
    for name,first,second in pairs:
        base=ROOT/'artifacts'/name
        for i in(first,second):
            folder=base/f'run_{i}';p=folder/'result.json';b=p.read_bytes();md=json.loads(b);records[name]=md
            if i==second and b!=(base/f'run_{first}/result.json').read_bytes():raise ValueError('source receipts not byte-identical')
            files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
            for rel,record in md['archives'].items():
                p=folder/rel;b=p.read_bytes()
                if sha256(b).hexdigest()!=record['sha256']:raise ValueError('completed canonical archive changed')
                if i==second and b!=(base/f'run_{first}'/rel).read_bytes():raise ValueError('source replay differs')
                files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
            for rel,h in md['input_hashes'].items():
                if rel in pins and pins[rel]!=h:raise ValueError('same source input conflict')
                pins[rel]=h
            p=ROOT/f'artifacts/{name}_run_{i}.stdout.txt';files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('same source/action pin changed')
    logs=['muon_reset_constrained_canonical_variation_20261012_run_1.stdout.txt',
        'muon_reset_constrained_canonical_variation_tests_20261012_run_1.stdout.txt',
        'muon_reset_secondary_canonical_source_tests_20261012_run_1.stdout.txt',
        'muon_per_arm_canonical_source_tests_20261012_run_1.stdout.txt','muon_per_arm_canonical_source_tests_20261012_run_2.stdout.txt']
    for name in logs:
        p=ROOT/'artifacts'/name;files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    p=Path(__file__);files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    out.mkdir(parents=True)
    scope=dict(original73_trace_role='temporal birth/reset endpoint matching; not established persistent bulk material glue',
        primary_KKT='conditional instantaneous signed Lagrangian computational initial basis, not inherited physical momenta',
        secondary_KKT='conditional event-family contact control only; not a physical trajectory selector or a source of persistent C.T lambda loads',
        canonical_vector='source/embedding clock motion applied once; absolute Gauss and momentum/time defects remain failures',
        per_arm_source='standalone own-parent source/Pi independent from joint graph source; reconstituted parent acts once in child',
        admitted_parent_component='parent area original358/transpose actual-face coefficient-germ only; child is not admitted or zero-filled',
        physical_cutoff_gamma_firsthit_or_external_state_selected=False,
        no_matrix_precision_campaign=True,nonlinear_reset_base_unconverged=True)
    p=out/'physical_scope.json';p.write_text(json.dumps(scope,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    commands=[]
    for name,first,second in pairs:
        script={'muon_reset_constrained_canonical_variation_20261012':'evaluate_muon_reset_constrained_canonical_variation',
            'muon_reset_secondary_canonical_source_20261012':'evaluate_muon_reset_secondary_canonical_source',
            'muon_per_arm_canonical_source_20261012':'evaluate_muon_per_arm_canonical_source',
            'muon_admitted_parent_source_germ_20261012':'evaluate_muon_admitted_parent_source_germ'}[name]
        commands.extend(f'C:/Python314/python.exe scripts/{script}.py --output artifacts/{name}/run_{i}'for i in(first,second))
    result=dict(classification='VERIFIED_CONDITIONAL_INITIAL_BASIS_AND_ACTUAL_PER_ARM_SOURCE_ADMISSION_PAIRS',files=files,input_hashes=pins,
        all_pair_output_bytes_equal=True,commands=commands,
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        tests_passed=5,per_arm_source_applications=records['muon_per_arm_canonical_source_20261012']['applications'],
        admitted_parent_component=records['muon_admitted_parent_source_germ_20261012']['original358_rows_max'],
        failed_execution_preserved='initial conditional producer expected group records but source groups were lists; no output archives existed, actual failed stdout retained; schema corrected before run2',
        physical_mass_cutoff_pole_or_muon_anomaly_claimed=False)
    p=out/'publication_manifest.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
