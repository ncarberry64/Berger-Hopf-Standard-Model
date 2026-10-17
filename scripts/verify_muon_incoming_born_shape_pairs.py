"""Nonmutating deterministic verification of OWN/born transmitted sources.

Checks component equations and records all226/nonphysical failure scope.
It never upgrades a source-completed partial solve to full birth admission.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every source pair verification')
    hashes={};files=[];components=[]
    specs=(('muon_incoming_own_normal_shape_20261013','evaluate_muon_incoming_own_normal_shape.py'),
        ('muon_incoming_shape_induced_response_20261013','evaluate_muon_incoming_shape_induced_response.py'),
        ('muon_normal_shape_birth_transmission_20261013','evaluate_muon_normal_shape_birth_transmission.py'))
    for base,driver in specs:
        folder=ROOT/'artifacts'/base;pa,pb=folder/'run_1'/'result.json',folder/'run_2'/'result.json'
        if not pa.is_file()or not pb.is_file():raise FileNotFoundError('both completed receipts required before verification')
        ba,bb=pa.read_bytes(),pb.read_bytes()
        if ba!=bb:raise ValueError('deterministic result bytes differ '+base)
        a=json.loads(ba);b=json.loads(bb)
        if a['archives']!=b['archives']:raise ValueError('archive schema differs '+base)
        entries=[]
        for name,data in a['archives'].items():
            lhs,rhs=folder/'run_1'/name,folder/'run_2'/name;lo,ro=lhs.read_bytes(),rhs.read_bytes()
            if lo!=ro or sha256(lo).hexdigest()!=data['sha256']or len(lo)!=data['bytes']:
                raise ValueError('exact pair/archive receipt failed '+base+'/'+name)
            entries.extend([dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(lo).hexdigest(),bytes=len(lo))for p in(lhs,rhs)])
        entries.extend([dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(ba).hexdigest(),bytes=len(ba))for p in(pa,pb)])
        for path,h in a['input_hashes'].items():
            if path in hashes and hashes[path]!=h:raise ValueError('conflicting current source pin '+path)
            hashes[path]=h
            if sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('current source/action pin changed '+path)
        component=dict(root=folder.relative_to(ROOT).as_posix(),result_sha256=sha256(ba).hexdigest(),equal_scientific_files_per_run=len(a['archives'])+1,
            classification=a['classification'])
        if base=='muon_normal_shape_birth_transmission_20261013':
            if a['physical_environment_formation_energy_gamma_c_retarded_pole_or_LSZ_matching_admitted']:
                raise ValueError('conditional transmission must not assert full physical matching')
            for record in a['records']:
                if not record['conditional_field_trace_transmission_passed']:raise ValueError('conditional field/source transmission failed')
                for stage in record['propagation']:
                    key='original358_upper'if 'original358_upper'in stage else'original146_upper'
                    if stage[key]>2e-10:raise ValueError('original linked response equations failed')
            component['original_BASE226_groups']=a['original_BASE226_groups']
            component['source_records']=a['records']
            component['full_natural_source_projection_not_claimed']=a['complete_natural_source_projection_not_claimed']
        logs=[]
        for index in(1,2):
            name=base+f'_run_{index}.stdout.txt'
            if base=='muon_normal_shape_birth_transmission_20261013'and index==1:name=base+'_run_1_retry_1.stdout.txt'
            log=ROOT/'artifacts'/name
            if not log.is_file():raise FileNotFoundError('actual completed stdout required '+name)
            logs.append(dict(path=log.relative_to(ROOT).as_posix(),sha256=sha256(log.read_bytes()).hexdigest(),bytes=log.stat().st_size))
        component['executions']=[dict(argv=['C:/Python314/python.exe','scripts/'+driver,'--output','artifacts/'+base+f'/run_{i}'],
            environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),stdout=logs[i-1])for i in(1,2)]
        components.append(component);files.extend(entries)
    for p in(Path(__file__),ROOT/'tests/test_muon_normal_shape_birth_transmission.py',ROOT/'artifacts/muon_normal_shape_birth_transmission_focused_20261013.stdout.txt'):
        hashes[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    out.mkdir(parents=True)
    scope=dict(matrix_solution_accuracy_not_action_or_physical_enclosure=True,
        current_component_source_guards_checked=True,all226_BASE_and_state_plus_known_source_failures_retained=True,
        no_energy_geometric_natural_deltaD_or_fullrate_boundary_functional_assumed_zero=True,
        held71_coordinates_are_conditional_not_physical_exterior=True,physical_matching_admitted=False,
        producer_six_port_requirement_is_overcomplete='For three common outputs only the three chronological common lifts U=X_phase*C_common plus one analytic adjoint are required; all six independent phase port histories are unnecessary.',
        remaining_action='Same chronological weak mixed shape Hessian and full boundary functional on common3 ports+analytic adjoint, then incoming/environment and outgoing natural/energy/formation/gamma(c)/pole matching; no frozen phase ports as physical history.')
    verification=dict(classification='IMMUTABLE_INCOMING_OWN_AND_SOURCE_COMPLETED_BORN_TRANSMISSION_PAIRS',components=components,
        input_hashes=hashes,scientific_files=files,scientific_file_count=len(files),current_pin_count=len(hashes),scope=scope)
    vp=out/'verification.json';vp.write_text(json.dumps(verification,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    manifest=dict(classification='REVIEWED_CONDITIONAL_SOURCE_ACTION_PAIRS',verification_path=vp.relative_to(ROOT).as_posix(),
        verification_sha256=sha256(vp.read_bytes()).hexdigest(),files=files,input_hashes=hashes,scope=scope)
    mp=out/'publication_manifest.json';mp.write_text(json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(scientific_files=len(files),pins=len(hashes),verification_sha256=sha256(vp.read_bytes()).hexdigest(),
        manifest_sha256=sha256(mp.read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('artifacts/muon_incoming_born_shape_pairs_20261013'))
    verify(p.parse_args().output)
