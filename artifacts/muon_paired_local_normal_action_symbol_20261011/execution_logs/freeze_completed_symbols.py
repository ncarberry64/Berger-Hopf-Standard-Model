"""Verify and pin completed same-base sources and full action symbols."""
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
target=Path(__file__).resolve().parents[1]
groups={
 'muon_positive_area_endpoint_response_20261011':[''],
 'muon_local_normal_action_symbol_20261011':['incoming','outgoing'],
 'muon_paired_local_normal_action_symbol_20261011':[''],
}
modules=['muon_positive_area_endpoint_response','muon_local_normal_action_symbol','muon_paired_local_normal_action_symbol']
files=[];pairs=[];dependencies={}
for folder,prefixes in groups.items():
    path=ROOT/'artifacts'/folder
    for prefix in prefixes:
        first=path/(prefix+'_run_1'if prefix else'run_1')
        second=path/(prefix+'_run_2'if prefix else'run_2')
        for name in ('result.json','application.npz'):
            a,b=(first/name).read_bytes(),(second/name).read_bytes()
            if a!=b:raise ValueError('independent replay differs: '+str(first/name))
            pairs.append(dict(application=folder,side=prefix or'joint',filename=name,bytes=len(a),sha256=sha256(a).hexdigest(),byte_identical=True))
            files.extend([first/name,second/name])
        dependencies.update(json.loads((first/'result.json').read_text())['input_hashes'])
    files.append(path/'verification.json')
    files.extend(sorted((path/'execution_logs').glob('*')))
for name in modules:
    files.extend([ROOT/'src/bhsm/interface'/f'{name}.py',ROOT/'tests'/f'test_{name}.py'])
for name,digest in dependencies.items():
    if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('consumed action changed: '+name)
verification=target/'pair_verification.json'
if verification.exists():raise FileExistsError('preserve earlier frozen verification')
verification.write_text(json.dumps(dict(classification='VERIFIED_FULL_PAIRED_AND_ARM_LOCAL_ACTION_SYMBOLS',
    pairs=pairs,physical_normal_drive_or_positive_inertia_or_cutoff_or_Pauli_selected=False,
    arithmetic_scope='independent byte replays of stored binary64 action polynomial applications; no producer/domain uncertainty certificate'),
    indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
files.append(verification);pins={}
for p in files:
    data=p.read_bytes()
    if len(data)>10*1024**2:raise ValueError('publication cap: '+str(p))
    if p.suffix in ('.py','.json','.txt')and b'\r\n'in data:raise ValueError('not canonical LF: '+str(p))
    pins[p.relative_to(ROOT).as_posix()]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
manifest=target/'publication_manifest.json'
if manifest.exists():raise FileExistsError('preserve earlier publication manifest')
manifest.write_text(json.dumps(dict(classification='FROZEN_POSITIVE_BASE_SOURCE_AND_FULL_CHRONOLOGICAL_LOCAL_ACTION_SYMBOLS',
    files=pins,dependencies=dependencies,
    density_identity='Axx=Lxx+iω(Lxv−Lvx)+ω²Lvv; Axy=Lxy−iωLvy; Ayx=Lyx+iωLyv; Ayy=Lyy',
    common_graph='full inherited536 action restricted to x212/v212/y80; shared attachments/proper-normal trace before internal reduction',
    clock='single common-coordinate paired action, read in child-plus proper clock; no independent arm clock summation',
    scope='constant-coefficient reached quadratic action germ, not full physical time-dependent E0/event operator',
    actual_physical_R_I_drive_c_or_Pauli_selected=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(files=len(pins),manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),pairs=len(pairs)),sort_keys=True))
