"""Read-only additive selection; no scientific file, old plan or Git index edits."""
from __future__ import annotations
import ast
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
OLD=ROOT/'artifacts/muon_common_domain_publication_plan_20261011'
old_path=OLD/'publication_plan.json';old=json.loads(old_path.read_bytes())
TRACKED=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=ROOT).decode().splitlines())
selected={};expected=defaultdict(lambda:defaultdict(set));owners=defaultdict(set);receipts={}


def identity(name):
    p=ROOT/name;b=p.read_bytes()
    return dict(path=name,bytes=len(b),sha256=sha256(b).hexdigest(),tracked_at_HEAD=name in TRACKED)


def select(name,role):
    if not (ROOT/name).is_file():raise FileNotFoundError(name)
    selected[name]=dict(**identity(name),role=role)


for row in old['selected_files']:
    now=identity(row['path'])
    if now['sha256']!=row['sha256'] or now['bytes']!=row['bytes']:
        raise ValueError('old immutable publication selection changed: '+row['path'])
    selected[row['path']]=dict(**now,role='preserved old264 selection: '+row['role'])

new_roots=[
 'artifacts/muon_common_domain_charge_source_clock_20261011/run_1',
 'artifacts/muon_common_domain_charge_source_clock_20261011/run_2',
 'artifacts/muon_common_domain_charge_source_clock_20261011/contract_run_1',
 'artifacts/muon_common_domain_charge_source_clock_20261011/contract_run_2',
 'artifacts/muon_holomorphic_child_terminal_20261011/run_2',
 'artifacts/muon_holomorphic_child_terminal_20261011/run_3',
 'artifacts/muon_holomorphic_child_clock_application_20261011/run_1',
 'artifacts/muon_holomorphic_child_clock_application_20261011/run_2',
 'artifacts/muon_complex_canonical_compatibility_20261011/run_1',
 'artifacts/muon_complex_terminal_defect_attribution_20261011/run_1',
 'artifacts/muon_complex_terminal_defect_attribution_20261011/run_2',
 'artifacts/muon_complex_terminal_action_sectors_20261011/run_1',
 'artifacts/muon_complex_terminal_action_sectors_20261011/run_2',
]
# Only finalized results are accepted; ongoing accepted-state streams are
# never copied. Add a finalized safeguarded folder through its owner ledger.
safeguarded_ledger=OUT/'finalized_safeguarded_roots.json'
pending=['Owner safeguarded canonical continuation final receipt/verification']
if safeguarded_ledger.is_file():
    new_roots+=json.loads(safeguarded_ledger.read_text())['roots'];pending=[]
additional_ledger=OUT/'finalized_additional_action_roots.json'
additional=json.loads(additional_ledger.read_bytes())if additional_ledger.is_file()else dict(roots=[],commands=[],manual=[],pending=['final geometry/material action and independent trust replay'])
new_roots+=additional['roots'];pending+=additional['pending']

manual=[
 'theory/muon_common_domain_physical_matching_20261012.md',
 'src/bhsm/interface/muon_complex_canonical_midpoint.py',
 'tests/test_muon_complex_canonical_midpoint.py',
 'tests/test_muon_holomorphic_child_action_review.py',
 'scripts/evaluate_muon_holomorphic_child_ward_review.py',
 'scripts/verify_muon_holomorphic_child_clock_application.py',
 'scripts/freeze_muon_holomorphic_child_terminal.py',
 'scripts/record_muon_common_domain_test_scope.py',
 'scripts/prepare_muon_matching_publication.py',
 'src/bhsm/interface/muon_safeguarded_complex_constitutive.py',
 'tests/test_muon_safeguarded_complex_constitutive.py',
 'scripts/evaluate_muon_safeguarded_complex_constitutive.py',
 'scripts/continue_muon_safeguarded_complex_constitutive.py',
 'scripts/freeze_muon_safeguarded_complex_constitutive.py',
 'scripts/evaluate_muon_paired_changing_magnetic_columns.py',
 'artifacts/muon_safeguarded_complex_constitutive_20261011/finite_solver_verification.json',
 'artifacts/muon_safeguarded_complex_constitutive_20261011/resumed_run_1.stdout.txt',
 'scripts/freeze_muon_common_domain_charge_source_clock.py',
 'scripts/freeze_muon_charge_source_clock_contract.py',
 'artifacts/muon_holomorphic_child_clock_application_20261011/verification.json',
 'artifacts/muon_holomorphic_child_independent_review_20261011/run_1/verification.json',
 'artifacts/muon_holomorphic_child_independent_review_20261011/run_1/tests.stdout.txt',
 'artifacts/muon_holomorphic_child_independent_review_20261011/run_2/canonical_ward_control.json',
 'artifacts/muon_holomorphic_child_independent_review_20261011/run_1/independent_clock_test.verification.json',
 'artifacts/muon_holomorphic_child_independent_review_20261011/run_1/independent_clock_test.stdout.txt',
 'artifacts/muon_holomorphic_child_terminal_20261011/pair_verification/publication_manifest.json',
 'artifacts/muon_holomorphic_child_terminal_20261011/pair_verification/verification.json',
 'artifacts/muon_common_domain_test_scope_20261012/verification.json',
 'artifacts/muon_common_domain_publication_selected_tests_20261011.log',
 'artifacts/muon_common_domain_seed_only_tests_0455_20261011.log',
 'artifacts/muon_common_domain_publication_plan_20261011/publication_plan.json',
 'artifacts/muon_common_domain_publication_plan_20261011/selected_test_paths.txt',
 'artifacts/muon_common_domain_publication_plan_20261011/prepare_seed_only_regeneration.py',
]
manual+=additional['manual']
for folder in ('pair_verification','contract_pair_verification'):
    manual += [f'artifacts/muon_common_domain_charge_source_clock_20261011/{folder}/{n}'
               for n in ('publication_manifest.json','verification.json')]
for name in manual:select(name,'additive reviewed code/control/verification or explicit test evidence')
accounting_paths=['artifacts/muon_observable_combination_20261011/contribution_error_table.json',
                  'artifacts/muon_observable_combination_20261011/contribution_error_table.md']
accounting_metadata=json.loads((ROOT/accounting_paths[0]).read_bytes())
for name in accounting_paths:select(name,'ONE existing reviewed accounting snapshot; historical producer closure is excluded')
accounting_scope=dict(classification='REVIEWED_ONE_CONSOLIDATED_ACCOUNTING_SNAPSHOT_ONLY',
    files=[identity(name)for name in accounting_paths],
    historical_input_reference_count=len(accounting_metadata.get('input_hashes',{})),
    complete_observable=accounting_metadata.get('complete_observable'),
    broad_updater_historical_program_and_evidence_are_not_publication_dependencies=True,
    snapshot_is_not_a_second_table_or_a_new_physical_combination=True,
    regeneration_or_full_historical_dependency_closure_proved=False)
for name in json.loads((ROOT/'artifacts/muon_holomorphic_child_terminal_20261011/pair_verification/publication_manifest.json').read_bytes())['files']:
    if name.endswith(('.stdout.txt','_stdout.txt')):
        select(name,'completed-action actual runtime or independent-review stdout')

queue=[p+'/result.json'for p in old['roots']+new_roots]
queue += [p for p in manual if p.endswith('.json') and 'publication_manifest'not in p]
while queue:
    name=queue.pop()
    if name in receipts:continue
    md=json.loads((ROOT/name).read_bytes());receipts[name]=md
    pins=md.get('input_hashes',{})|md.get('assessed_source_hashes',{})|md.get('own_source_hashes',{})
    for path,digest in pins.items():
        expected[path][digest].add(name)
        if path in TRACKED or not path.startswith('artifacts/'):continue
        owner=path if path.endswith('/result.json')else(Path(path).parent/'result.json').as_posix()
        if (ROOT/owner).is_file()and owner!=name:
            owners[name].add(owner);queue.append(owner)
    if name.endswith('/result.json') and name not in TRACKED:
        select(name,'compact computed receipt ancestor; full raw streams regenerate locally')

for folder in new_roots:
    md=receipts[folder+'/result.json']
    for name in md.get('archives',{}):
        if 'charge_source_clock' in folder:
            keep=name.startswith('complete_')or name=='actual_source_clock_contract.npz'
        elif 'complex_canonical_compatibility' in folder:
            keep=name=='application.npz'or name=='iteration_3_full_constitutive_action.npz'
        elif 'safeguarded_complex_constitutive' in folder:
            keep=name=='application.npz'
        elif 'canonical_geometry' in folder:
            keep=name=='application.npz'or 'control'in name
        elif 'canonical_compatibility_20261012' in folder or 'canonical_exterior_step_20261012' in folder or 'canonical_endpoint_20261012' in folder:
            keep=name=='application.npz'or'control'in name or'tangent'in name
        elif 'unsquared_forced_boundary_attachment' in folder:
            keep=name=='complete_n0_n2_actual_source_boundary_currents.npz'or'boundary_current_application'in name
        elif 'coupled_complex_two_arm_reset' in folder:
            keep=not name.startswith(('accepted_','iteration_'))
        elif 'endpoint_second_domain_germ' in folder:
            keep=name=='endpoint_second_domain_contacts.npz'
        else:keep=True
        if keep:select(folder+'/'+name,'compact complete corrected action/control/charge result')

fixture_ledger=OUT/'completed_fixture_ledger.json'
fixture_owner_code_pins=[]
if fixture_ledger.is_file():
    fixture_record=json.loads(fixture_ledger.read_bytes())
    for name in fixture_record['fixture_paths']:
        if not name.endswith('/result.json'):continue
        for path,digest in json.loads((ROOT/name).read_bytes()).get('input_hashes',{}).items():
            if path.endswith('.py'):
                expected[path][digest].add(name)
                fixture_owner_code_pins.append(dict(path=path,sha256=digest,owner=name))

commands=[dict(row)for row in old['producer_commands']]
for row in additional.get('extra_producer_commands',[]):
    row=dict(row);row['depends_on']=sorted(owners.get(row['output']+'/result.json',()))
    commands.append(row)
def command(folder,script,args=(),note=''):
    commands.append(dict(output=folder,command=['python','scripts/'+script,*args,'--output',folder],
                         depends_on=sorted(owners.get(folder+'/result.json',())),note=note))
for folder in new_roots:
    if 'charge_source_clock' in folder:
        script=('evaluate_muon_charge_source_clock_contract.py'if '/contract_run_'in folder
                else'evaluate_muon_common_domain_charge_source_clock.py');args=[]
    elif 'holomorphic_child_terminal' in folder:script='evaluate_muon_holomorphic_child_terminal.py';args=[]
    elif 'holomorphic_child_clock_application' in folder:script='evaluate_muon_holomorphic_child_clock_application.py';args=[]
    elif 'complex_canonical_compatibility' in folder:
        script='evaluate_muon_complex_canonical_compatibility.py';args=['--terminal-folder','artifacts/muon_holomorphic_child_terminal_20261011/run_2','--max-iterations','3']
    elif 'complex_terminal_defect_attribution' in folder:
        script='evaluate_muon_complex_terminal_defect_attribution.py';args=['--terminal-folder','artifacts/muon_holomorphic_child_terminal_20261011/run_2']
    elif 'complex_terminal_action_sectors' in folder:
        script='evaluate_muon_complex_terminal_action_sectors.py';args=['--attribution-folder','artifacts/muon_complex_terminal_defect_attribution_20261011/run_1']
    elif 'safeguarded_complex_constitutive' in folder:
        row=next(r for r in json.loads(safeguarded_ledger.read_text())['commands']if r['output']==folder)
        row['depends_on']=sorted(owners.get(folder+'/result.json',()))
        commands.append(row);continue
    elif folder in additional['roots']:
        row=next(r for r in additional['commands']if r['output']==folder)
        row['depends_on']=sorted(owners.get(folder+'/result.json',()))
        commands.append(row);continue
    else:raise ValueError('unmapped new producer: '+folder)
    command(folder,script,args)
for row in commands:select(row['command'][1],'required existing producer entry point')
# Prefer the already executed command/environment over equivalent inferred
# CLI defaults where the immutable verifier records it.
observed_executions={}
for name in [
    'artifacts/muon_holomorphic_child_terminal_20261011/pair_verification/verification.json',
    'artifacts/muon_complex_canonical_compatibility_20261011/replay_verification.json',
    'artifacts/muon_safeguarded_complex_constitutive_20261011/deterministic_pair_verification.json',
    'artifacts/muon_material_cancellation_audit_20261012/independent_pair_verification.json',
    'artifacts/muon_uniform_clock_action_identity_20261012/independent_pair_verification.json']:
    record=json.loads((ROOT/name).read_bytes())
    for execution in record.get('commands',record.get('executions',[])):
        argv=execution['argv']
        if '--output'in argv:
            observed_executions[argv[argv.index('--output')+1]]=dict(execution,verification=name)
for row in commands:
    if row['output']in observed_executions:
        execution=observed_executions[row['output']]
        row['command']=execution['argv'];row['environment']=execution['environment']
        row['actual_command_verification']=execution['verification']

# Package initializers, tests and local imported helpers are copied too.
code={p for p in expected if p.endswith('.py')}
code|={p for p in selected if p.endswith('.py')}
code|={r['command'][1]for r in commands}
todo=list(code);visited=set()
while todo:
    name=todo.pop()
    if name in visited:continue
    visited.add(name);parent=Path(name).parent
    candidates=[]
    while parent!=Path('.'):
        if (ROOT/parent/'__init__.py').is_file():candidates.append(parent/'__init__.py')
        parent=parent.parent
    tree=ast.parse((ROOT/name).read_text(encoding='utf8'))
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):modules=[a.name for a in node.names]
        elif isinstance(node,ast.ImportFrom):
            module=node.module or ''
            if node.level:
                parent=Path(name).parent
                for _ in range(node.level-1):parent=parent.parent
                local=([parent/Path(module.replace('.','/')).with_suffix('.py')]if module else
                       [parent/Path(a.name.replace('.','/')).with_suffix('.py')for a in node.names])
                candidates+=local;continue
            modules=[module]+[module+'.'+a.name for a in node.names if module and a.name!='*']
        else:continue
        candidates += [Path(base)/Path(mod.replace('.','/')).with_suffix('.py')
                       for mod in modules for base in('src','scripts','tests','')]
    for p in candidates:
        key=p.as_posix()
        if (ROOT/p).is_file()and key not in code:code.add(key);todo.append(key)
approved_tests=set(json.loads((OUT/'approved77_test_inventory.json').read_bytes())['paths'])if(OUT/'approved77_test_inventory.json').is_file()else set(old['selected_test_paths'])
approved_tests|={p for p in manual if p.startswith('tests/')}
approved_tests|={p for p in expected if p.startswith('tests/')}
for name in sorted(code):
    if name not in TRACKED:select(name,'untracked code/test/package import closure')
    if name.startswith('src/bhsm/interface/muon_'):
        test='tests/test_'+Path(name).name
        if (ROOT/test).is_file()and test not in TRACKED and test in approved_tests:select(test,'focused test of selected code')

# Primary and failed seed-only results remain visible. Compact fixture
# caches are selected only after the unchanged scratch regression consumes
# them; no failed physical normalization is promoted by this test closure.
log=ROOT/'artifacts/muon_common_domain_seed_only_tests_0455_20261011.log'
fixture_names=set()
for path in re.findall(r"No such file or directory: '([^']+)'",log.read_text()):
    path=path.replace('\\','/')
    while '//'in path:path=path.replace('//','/')
    if '/artifacts/'in path:fixture_names.add('artifacts/'+path.split('/artifacts/',1)[1])
fixture_audit=dict(classification='PRIMARY_SUITE_AND_UNREGENERATED_SEED_SMOKE_EVIDENCE',
    primary_passed=152,primary_seconds=45.08,primary_selected_test_files=57,
    seed_passed=124,seed_failed=26,seed_errors=2,seed_seconds=24.78,
    fixture_paths_visible_before_first_missing_predecessor=[identity(p)for p in sorted(fixture_names)],
    all_transitive_test_fixtures_enumerated=False,missing_fixtures_numerical_failures=False,
    clean_test_or_producer_regeneration_proved=False,
    chosen_test_policy='retain primary152-passed and original seed124/26/2 evidence; new fixture-complete regression is recorded separately, never as full producer regeneration')
OUT.mkdir(parents=True,exist_ok=True)
fixture_paths=[]
if fixture_ledger.is_file():
    fixture_record=json.loads(fixture_ledger.read_bytes())
    fixture_paths=fixture_record['fixture_paths']
    fixture_audit['completed_fixture_smoke']=fixture_record['smoke']
    fixture_audit['completed_primary_suite']=fixture_record.get('primary',{})
    fixture_audit['completed_test_file_count']=fixture_record.get('test_files',57)
    fixture_audit['completed_test_case_count']=fixture_record.get('passed',152)
    fixture_audit['focused_added_reviews']=fixture_record.get('focused_added_reviews',[])
    fixture_audit['preparation_metadata_loss']=fixture_record.get('preparation_metadata_loss',{})
    fixture_audit['fixture_complete_regression_proved']=fixture_record['smoke']['exit_code']==0
    for name in fixture_paths:select(name,'compact regression fixture cache or direct owning receipt; not a physical matching input')
    for name in fixture_record['evidence_paths']:select(name,'executed unchanged regression or precisely scoped preparation evidence')
    select(fixture_ledger.relative_to(ROOT).as_posix(),'compact cache owner/digest and incomplete diagnostic-parent scope')
    fixture_audit['diagnostic_per_family_fixtures_without_finished_parent_receipt']=fixture_record['diagnostic_per_family_fixtures_without_finished_parent_receipt']
consumer_audit=dict(classification='SOURCE_CLOCK_HELPER_CONSUMER_SCOPE_AUDIT',
    old_helper_production_consumers=['scripts/evaluate_muon_common_domain_charge_transport.py',
                                    'scripts/evaluate_muon_common_domain_charge_source_clock.py (legacy reconstruction)'],
    old_helper_consumed_by_Cauchy_current_or_source_energy=False,
    corrected_projection='full six C6 charge/current directions and charged-neutral return blocks only',
    actual_point_body_and_frame_values_changed=False,
    correction_integral_norm=4.336998669698843e-18,
    correction_is_bound_on_other_source_jets_or_Pauli_derivatives=False,
    other_physical_coordinate_first_germs_require_their_own_clock_conversion=True)
ca=OUT/'charge_clock_consumer_audit.json';ca.write_text(json.dumps(consumer_audit,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
select(ca.relative_to(ROOT).as_posix(),'exact helper-consumer correction scope')
covered_tests={name for name in fixture_record['smoke']['argv']if name.startswith('tests/')}
for row in fixture_record.get('focused_added_reviews',[]):
    covered_tests.update(row.get('test_files',[row.get('test_file')]))
current_test_paths={name for name in selected if name.startswith('tests/')}
fixture_audit['selected_test_files_without_executed_coverage']=sorted(current_test_paths-covered_tests)
fixture_audit['all_selected_files_have_primary_and_isolated_coverage']=not fixture_audit['selected_test_files_without_executed_coverage']
fixture_audit['all_selected_files_run_in_one_invocation']=current_test_paths=={name for name in fixture_record['smoke']['argv']if name.startswith('tests/')}
fp=OUT/'test_fixture_audit.json';fp.write_text(json.dumps(fixture_audit,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
select(fp.relative_to(ROOT).as_posix(),'explicit primary vs seed-fixture verification scope')
ap=OUT/'accounting_snapshot_scope.json';ap.write_text(json.dumps(accounting_scope,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
select(ap.relative_to(ROOT).as_posix(),'explicit historical-reference exclusion for the ONE reviewed accounting snapshot')
select(Path(__file__).relative_to(ROOT).as_posix(),'additive read-only publication selection producer')
helper=OUT/'prepare_seed_only_regeneration.py'
if helper.is_file():select(helper.relative_to(ROOT).as_posix(),'optional unexecuted exact seed/code setup')

ordered=[];pending_commands=list(commands)
while pending_commands:
    outputs={r['output']+'/result.json'for r in pending_commands}
    ready=next((r for r in pending_commands if not(set(r['depends_on'])&outputs)),None)
    if ready is None:raise ValueError('producer DAG cycle')
    ordered.append(ready);pending_commands.remove(ready)
mapped={r['output']+'/result.json'for r in commands}
unmapped=[p for p in receipts if p.endswith('/result.json')and p not in mapped and p not in TRACKED]
conflicts=[]
for path,versions in expected.items():
    now=identity(path)
    for digest,consumers in versions.items():
        if now['sha256']!=digest:conflicts.append(dict(path=path,expected=digest,current=now['sha256'],consumers=sorted(consumers)))
array_failures=[];array_count=0
for row in selected.values():
    p=ROOT/row['path'];owner=p.parent/'result.json'
    if p.suffix=='.npz'and owner.is_file():
        record=json.loads(owner.read_bytes()).get('archives',{}).get(p.name)
        if record:
            array_count+=1
            if record['sha256']!=row['sha256']or record['bytes']!=row['bytes']:array_failures.append(row['path'])
files=[selected[p]for p in sorted(selected)]
generated_dependency_frontier=[]
for name in sorted(expected):
    if name in TRACKED or name in selected or not name.startswith('artifacts/'):
        continue
    owner=name if name.endswith('/result.json')else(Path(name).parent/'result.json').as_posix()
    generated_dependency_frontier.append(dict(path=name,sha256=identity(name)['sha256'],
        owner_receipt=owner if (ROOT/owner).is_file()else None,
        owner_producer_command_mapped=owner in mapped,
        scope='local numerical producer operand; omitted bulk regenerates only if its mapped producer chain is executed'))
oversized=[p['path']for p in files if p['bytes']>=10*1024**2]
if oversized:raise ValueError('do not publish over-cap arrays: '+repr(oversized))
test_paths=[p['path']for p in files if p['path'].startswith('tests/')]
copy_paths=sorted(code|{p for p in expected if p in TRACKED})
plan=dict(classification='ADDITIVE_EXPANDED_COMMON_DOMAIN_SELECTIVE_PUBLICATION_PLAN',
    preserved_old_plan_sha256=sha256(old_path.read_bytes()).hexdigest(),preserved_old_file_count=264,
    selected_files=files,selected_file_count=len(files),selected_total_bytes=sum(r['bytes']for r in files),
    selected_max_file_bytes=max(r['bytes']for r in files),selected_over_cap_paths=oversized,
    new_roots=new_roots,computed_receipt_ancestor_count=len(receipts),input_hash_conflicts=conflicts,
    selected_arrays_matching_owner_receipts=array_count,selected_array_identity_failures=array_failures,
    receipts_without_mapped_producer_command=sorted(unmapped),producer_commands=ordered,
    auxiliary_metadata_commands=additional.get('metadata_commands',[]),
    producer_commands_topologically_ordered=True,selected_test_paths=test_paths,
    selected_test_file_count=len(test_paths),primary_suite=fixture_audit,
    seed_only_regeneration_copy_paths=copy_paths,coordinate_cache_reuse=old['coordinate_cache_reuse'],
    regression_fixture_copy_paths=fixture_paths,
    regression_fixture_owner_code_pins=fixture_owner_code_pins,
    regression_fixture_predecessor_numerical_regeneration_proved=False,
    omitted_generated_dependency_frontier=generated_dependency_frontier,
    compact_publication_is_full_local_hash_manifest_closure=False,
    tracked_seed_frontier=[identity(p)for p in sorted(expected)if p in TRACKED and p.startswith('artifacts/')],
    pending_finalized_applications=pending,local_hash_closure_distinct_from_publication_regeneration=True,
    clean_checkout_regeneration_executed=False,publication_dependency_closure_proved=False,
    raw_streams_checkpoints_original_arrays_preserved=True,no_files_staged_or_committed=True,
    scientific_sources_frozen_predictions_and_old_plan_modified=False,
    reviewed_accounting_snapshot_scope=accounting_scope,
    report_historical_accounting_references_are_local_context_not_selected_dependencies=True,
    charge_clock_correction_scope=consumer_audit,
    physical_pole_LSZ_common_mass_lifetime_native_Pauli_a_or_g_completed=False,
    environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
    excluded_scope=['raw current/KKT/body/point/accepted-state streams','full production heat and broad accounting updater/history beyond the selected ONE snapshot',
                    'test-fixture predecessor streams beyond compact runnable cache','unfinished reset-constrained variational streams and other ongoing applications before finalization'])
(OUT/'publication_plan.json').write_text(json.dumps(plan,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
(OUT/'selected_publication_paths.txt').write_text('\n'.join(r['path']for r in files)+'\n',encoding='utf8',newline='\n')
(OUT/'selected_test_paths.txt').write_text('\n'.join(test_paths)+'\n',encoding='utf8',newline='\n')
lines=['Run in a NEW seed-only scratch tree; every existing scientific output directory is immutable.',
       'Set PYTHONPATH=src;scripts, OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1.',
       'Commands are inspected producer APIs, not a claimed executed clean numerical replay.',
       'Reuse the selected original n0 coordinate cache; skip its window heat producer unless deliberately rebuilding that cache.','']
for i,row in enumerate(ordered,1):
    override=(' environment '+json.dumps(row['environment'],sort_keys=True))if'environment'in row else''
    lines.append(f"{i}.{override} {' '.join(row['command'])}")
    if 'environment_scope'in row:lines.append('  Environment provenance: '+row['environment_scope'])
    if 'actual_command_verification'in row:lines.append('  Executed command record: '+row['actual_command_verification'])
lines+=['','After all complete local outputs exist, these inspected metadata verifiers read their full local output membership; published compact caches alone do not substitute for that execution.']
for row in additional.get('metadata_commands',[]):lines.append(' '.join(row))
(OUT/'reproduction_commands.txt').write_text('\n'.join(lines)+'\n',encoding='utf8',newline='\n')
(OUT/'publication_plan.txt').write_text(
    f"Expanded selection: {len(files)} files / {plan['selected_total_bytes']} bytes; max {plan['selected_max_file_bytes']} bytes.\n"
    f"Input conflicts {len(conflicts)}; array conflicts {len(array_failures)}; unmapped result producers {len(unmapped)}.\n"
    f"Pending finalizations: {pending}.\n"
    'Old264 selection and all raw/scientific arrays preserved. No staging or attribute edits.\n'
    f"Selected test files {len(test_paths)}; executed primary/isolated suite {fixture_record.get('test_files',57)} files / {fixture_record.get('passed',152)} passed cases.\n"
    'Original primary152-pass and seed124/26/2 evidence retained; copied fixture controls are not clean producer regeneration.\n'
    'No physical pole/LSZ/common mass-lifetime/native Pauli completion asserted.\n',encoding='utf8',newline='\n')
print(json.dumps(dict(selected_file_count=len(files),selected_total_bytes=plan['selected_total_bytes'],
    max_file_bytes=plan['selected_max_file_bytes'],conflicts=len(conflicts),unmapped=unmapped,pending=pending,
    plan_sha256=sha256((OUT/'publication_plan.json').read_bytes()).hexdigest()),sort_keys=True))
