"""Read-only science-output verification of completed changing-stage run3/4.

Only a new verification directory is written, after every check succeeds.
Scientific run directories, producers and their pins are never modified.
"""
from pathlib import Path
from hashlib import sha256
import argparse, json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]


def verify(first, second, output, evidence=(), check_only=False):
    out=ROOT/output
    if out.exists() and not check_only:
        raise FileExistsError('preserve completed changing-stage verification')
    folders=[ROOT/first,ROOT/second]
    if folders[0].resolve()==folders[1].resolve():
        raise ValueError('independent completed replay folders required')
    # An absent final receipt means an active or failed execution. Do not
    # manufacture a final package from its partial arrays.
    for folder in folders:
        if not (folder/'result.json').is_file():
            raise FileNotFoundError('completed result.json required: '+str(folder))
    files={};pins={};reports=[]
    for number,folder in enumerate(folders):
        p=folder/'result.json';b=p.read_bytes();md=json.loads(b);reports.append(md)
        if md.get('classification')!='EVALUATED_CHANGING_NONLINEAR_CANONICAL_ARM_SOURCE_APPLICATION':
            raise ValueError('completed actual changing action receipt required')
        if md.get('tolerance')!=2e-10:
            raise ValueError('original canonical guard must remain unchanged')
        if md.get('physical_formation_or_first_hit_or_pole_or_native_Pauli_selected') is not False:
            raise ValueError('finite changing-stage application scope changed')
        if number and b!=(folders[0]/'result.json').read_bytes():
            raise ValueError('actual changing-stage receipts are not byte-identical')
        files[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        for name,record in md['archives'].items():
            p=folder/name
            if p.parent!=folder or not p.is_file():
                raise ValueError('all and only completed run archive paths required')
            b=p.read_bytes();h=sha256(b).hexdigest()
            if h!=record['sha256'] or len(b)!=record['bytes']:
                raise ValueError('completed changing-stage archive digest/size differs')
            if number and b!=(folders[0]/name).read_bytes():
                raise ValueError('actual changing-stage archive replay differs: '+name)
            files[p.relative_to(ROOT).as_posix()]=h
        for rel,h in md['input_hashes'].items():
            if rel in pins and pins[rel]!=h:
                raise ValueError('same changing-stage source pin conflict')
            pins[rel]=h
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):
        raise ValueError('actual source/action input pin changed')
    md=reports[0];folder=folders[0];guard=md['tolerance'];cache={}
    def load(name):
        if name not in md['archives']:
            raise ValueError('a declared application lacks its completed archive: '+name)
        if name not in cache:
            with np.load(folder/name,allow_pickle=False) as z:
                cache[name]={k:z[k].copy() for k in z.files}
        return cache[name]
    role_audits=[];endpoint_failures=[];stages=md['stages']
    for case,admission in md['admissions'].items():
        expected=max(admission['fresh_parent_original_upper'],admission['child_reassembled_original_upper'])<=guard
        if bool(admission['admitted'])!=expected:
            raise ValueError('fresh birth original146 gate differs from original guard')
        for arm in ('parent','child'):
            a=load(case+'_consumed_birth_'+arm+'_source.npz')
            if a['direction_high'].shape!=(252,) or a['direction_low'].shape!=(252,):
                raise ValueError('every original fresh birth coordinate must be retained')
    for s in stages:
        side,k=s['side'],int(s['cell']);prefix=f'{side}_{k:04d}'
        base=load(prefix+'_actual_base.npz')
        if base['original358_rows'].shape!=(358,) or base['initial_Pi'].shape!=(106,):
            raise ValueError('all original canonical rows and own Pi must be stored')
        base_max=float(np.max(abs(base['original358_rows'])))
        if s['base_admitted'] and base_max>guard:
            raise ValueError('base admission differs from original358 row guard')
        if not s['base_admitted']:
            if any(t['side']==side and int(t['cell'])>k for t in stages):
                raise ValueError('failed actual base was propagated')
            continue
        endpoint=load(prefix+'_actual_endpoint.npz')
        if (endpoint['endpoint_original146_rows'].shape!=(146,)
                or not np.array_equal(endpoint['endpoint_Pi'],base['Pi_final'])
                or not np.array_equal(endpoint['endpoint_master'][:106],base['x_final'])):
            raise ValueError('endpoint must retain actual final x/Pi without a momentum graft')
        endpoint_ok=float(np.max(abs(endpoint['endpoint_original146_rows'])))<=guard
        declared=s['endpoint_status']=='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE'
        if declared and not endpoint_ok:
            raise ValueError('actual endpoint original146 guard disagrees with solver status')
        if k:
            previous=load(f'{side}_{k-1:04d}_actual_base.npz')
            if (not np.array_equal(base['initial_Pi'],previous['Pi_final'])
                    or not np.array_equal(base['initial_master'][:106],previous['x_final'])):
                raise ValueError('actual base canonical targets changed between steps')
        for case,source in s['sources'].items():
            a=load(prefix+'_'+case+'_source_response.npz')
            if (a['original_rows'].shape!=(358,) or a['stage_solution_high'].shape!=(360,)
                    or a['stage_solution_low'].shape!=(360,)
                    or a['proper_normal_covector'].shape!=(106,)):
                raise ValueError('every source row, named frame and literal normal test must be retained')
            source_ok=source['original_rows_upper']<=guard
            if bool(source['all_original_source_rows_admitted'])!=source_ok:
                raise ValueError('source midpoint must use literal original358 rows')
            next_name=f'{side}_{k+1:04d}_{case}_source_response.npz'
            if not source_ok and next_name in md['archives']:
                raise ValueError('failed original source midpoint was propagated')
            endpoint_source_ok=False
            if declared:
                e=load(prefix+'_'+case+'_endpoint_source_response.npz')
                if (not np.array_equal(e['endpoint_Pi'],base['Pi_final'])
                        or not np.array_equal(e['canonical_momentum_target_high'],a['stage_solution_high'][106:212])
                        or not np.array_equal(e['canonical_momentum_target_low'],a['stage_solution_low'][106:212])):
                    raise ValueError('endpoint source must keep carried canonical variation targets')
                if e['original_rows'].shape!=(146,) or e['endpoint_normal_covector'].shape!=(106,):
                    raise ValueError('actual endpoint source rows/coframe missing')
                endpoint_source_ok=source['actual_endpoint_original_source146_upper']<=guard
                if not endpoint_source_ok:
                    endpoint_failures.append(dict(side=side,cell=k,case=case,
                        original146_upper=source['actual_endpoint_original_source146_upper']))
                    if next_name in md['archives']:
                        raise ValueError('failed endpoint source propagated instead of being quarantined')
            if next_name in md['archives']:
                nxt=load(next_name)
                for label,indices in (('x',slice(0,106)),('Pi',slice(106,212))):
                    for term in ('high','low'):
                        if not np.array_equal(nxt[f'delta_{label}_initial_{term}'],a[f'stage_solution_{term}'][indices]):
                            raise ValueError('source canonical high/low terms not carried unchanged')
            role_audits.append(dict(side=side,cell=k,case=case,
                base_original358_max=base_max,source_original358_upper=source['original_rows_upper'],
                source_assembled_difference_upper=source['original_assembly_difference_upper'],
                actual_endpoint_base146_max=float(np.max(abs(endpoint['endpoint_original146_rows']))),
                actual_endpoint_source146_upper=source.get('actual_endpoint_original_source146_upper'),
                endpoint_source_admitted=endpoint_source_ok,
                midpoint_normal_pairing=source['normal_pairing'],
                endpoint_normal_pairing_high=source.get('actual_endpoint_normal_pairing_high'),
                endpoint_normal_pairing_low=source.get('actual_endpoint_normal_pairing_low')))
    evidence_files={}
    for name in evidence:
        p=ROOT/name
        if not p.is_file():raise FileNotFoundError('actual verification evidence not found: '+str(p))
        evidence_files[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    focused_tests={}
    for name in ('tests/test_muon_changing_canonical_source.py',
                 'tests/test_muon_full_profile_source_weak_application.py'):
        focused_tests[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    files.update(evidence_files);files.update(focused_tests)
    files[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    record=dict(classification='VERIFIED_COMPLETED_CHANGING_CANONICAL_STAGE_AND_SOURCE_PAIR',
        all_output_bytes_equal=True,producer_input_hashes=pins,files=files,
        focused_tests_are_verification_evidence_not_retroactive_producer_pins=focused_tests,
        actual_execution_or_test_evidence_hashes=evidence_files,
        run_folders=[first.as_posix(),second.as_posix()],original_guard=guard,
        numerical_parameters=dict(step=md['step'],requested_steps=md['requested_steps']),
        requested_environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        argv_provenance='actual argv must be read from supplied execution evidence; numerical parameters alone are not an execution transcript',
        action_parameters=md['action_parameters'],fresh_birth_admissions=md['admissions'],
        source_and_endpoint_gate_audits=role_audits,failed_endpoint_source_quarantines=endpoint_failures,
        all_evaluated_endpoint_sources_pass_original_guard=not endpoint_failures,
        endpoint_x_Pi_preserved=True,independent_midpoint_and_endpoint_normal_scopes=True,
        inherited_child_source_scope=md['inherited_child_source'],
        birth_reset_not_continuous_bulk_constraints=True,
        weak_source_complement_retained_and_applied_before_restriction=True,
        physical_mode_first_hit_exterior_pole_or_muon_anomaly_selected=False,
        error_scope='byte identity and original equation-gate audits of completed finite changing-stage applications; no action-coefficient, discretization, continuum or outward physical enclosure')
    if not check_only:
        out.mkdir(parents=True)
        p=out/'publication_manifest.json'
        p.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        print(json.dumps(dict(files=len(files),pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest(),endpoint_source_failures=len(endpoint_failures))),flush=True)
    else:
        print(json.dumps(dict(check_only=True,files=len(files),pins=len(pins),endpoint_source_failures=len(endpoint_failures))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--first',type=Path,default=Path('artifacts/muon_changing_canonical_source_20261012/run_3'))
    p.add_argument('--second',type=Path,default=Path('artifacts/muon_changing_canonical_source_20261012/run_4'))
    p.add_argument('--output',type=Path,default=Path('artifacts/muon_changing_canonical_source_20261012/pair_verification'))
    p.add_argument('--evidence',type=Path,action='append',default=[])
    p.add_argument('--check-only',action='store_true')
    a=p.parse_args();verify(a.first,a.second,a.output,a.evidence,a.check_only)
