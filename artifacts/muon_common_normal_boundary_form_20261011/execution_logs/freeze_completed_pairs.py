from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];folder=Path(__file__).resolve().parents[1]
files=[ROOT/'src/bhsm/interface/muon_common_normal_boundary_form.py',ROOT/'tests/test_muon_common_normal_boundary_form.py',folder/'verification.json']
files.extend(sorted((folder/'execution_logs').glob('*')))
dependencies={};values=[]
for family in ('base','area'):
    for run in (1,2):
        for name in ('result.json','application.npz'):files.append(folder/f'{family}_run_{run}'/name)
    md=json.loads((folder/f'{family}_run_1/result.json').read_text());dependencies.update(md['input_hashes'])
    values.append(dict(family=family,common_trace_lift=md['common_trace_lift'],common_action=md['combined_signed_action_pairing'],
        independently_eliminated_arm_sum=md['separately_eliminated_arm_normal_sum'],incoming_same_trace_proper_inertia=md['incoming_proper_inertia_on_common_trace'],
        child_same_trace_proper_inertia=md['child_proper_inertia_on_common_trace']))
for p,h in dependencies.items():
    if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
pins={}
for p in files:
    data=p.read_bytes()
    if len(data)>10*1024**2:raise ValueError('publication cap exceeded')
    if p.suffix in ('.json','.txt','.py')and b'\r\n'in data:raise ValueError('canonical LF required')
    pins[p.relative_to(ROOT).as_posix()]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
out=folder/'publication_manifest.json'
if out.exists():raise FileExistsError(out)
md=dict(classification='FROZEN_SHARED_ATTACHMENT_CONDITIONAL_NORMAL_BOUNDARY_ACTION',files=pins,dependencies=dependencies,values=values,
    common_attachment_owner='muon_birth_finite_geometric_trace_endpoint.projected_birth_cotangent.common_trial_map duplicates both attachments across the two arms before dual summation',
    scope='Actual arm field/y equations solved before composing the conditional common proper-normal three-trace graph. Numerical far canonical covectors remain explicit.',
    shared_attachment_elimination_not_sum_of_independent_Schurs=True,
    independent_internal_responses_may_define_distinct_reduced_operators=True,
    same_trace_inertia_not_proved_to_be_the_physical_reduced_inertia=True,
    physical_formation_or_cutoff_or_Pauli_selected=False,
    error_scope='Independent byte replay of binary64 contractions/shared-trace solves; no physical domain, action-rounding or continuum certificate')
out.write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(files=len(pins),manifest_sha256=sha256(out.read_bytes()).hexdigest(),values=values),sort_keys=True))
