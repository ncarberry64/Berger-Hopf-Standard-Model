"""Verify and pin completed Jacobi pairs; no producer invocation."""
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parents[1]
files=[];dependencies={};values=[]
for family in ('base','area'):
    for filename in ('result.json','application.npz'):
        paths=[folder/f'{family}_run_{run}'/filename for run in (3,4)]
        if paths[0].read_bytes()!=paths[1].read_bytes():raise ValueError('independent replay differs')
        files.extend(paths)
    md=json.loads((folder/f'{family}_run_3/result.json').read_text())
    dependencies.update(md['input_hashes'])
    values.extend(dict(family=family,side=row['side'],stratum=row['stratum'],
        constant_normal_curvature_coefficient=row['constant_normal_curvature_coefficient'],
        second_fundamental_squared=row['second_fundamental_squared'],ambient_Ric_normal_normal=row['ambient_Ric_normal_normal'])for row in md['rows'])
for p,h in dependencies.items():
    if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed source changed: '+p)
files.append(folder/'canonical_verification.json')
for p in sorted((folder/'execution_logs').glob('*')):
    if p.name.startswith(('base_run_3.','base_run_4.','area_run_3.','area_run_4.','canonical_tests.'))or p.name in ('run_canonical_pair.py','freeze_canonical_packets.py'):
        files.append(p)
files.extend([ROOT/'src/bhsm/interface/muon_finite_normal_worldvolume_jacobi.py',ROOT/'tests/test_muon_finite_normal_worldvolume_jacobi.py'])
pins={}
for p in files:
    data=p.read_bytes()
    if len(data)>10*1024**2:raise ValueError('publication cap exceeded')
    if p.suffix in ('.json','.txt','.py')and b'\r\n'in data:raise ValueError('canonical LF required')
    pins[p.relative_to(ROOT).as_posix()]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
out=folder/'publication_manifest.json'
if out.exists():raise FileExistsError(out)
md=dict(classification='FROZEN_FINITE_MOVING_WORLDVOLUME_CURVATURE_APPLICATION',files=pins,dependencies=dependencies,values=values,
    math_review='Independent source review found the outward spacelike orientation, trace(S^2), warped Ricci contraction and declared affine wall acceleration consistent.',
    definition='Only the zeroth geometric term -(|II|^2+Ric(n,n)); no principal Jacobi operator, local restoring density or physical acceleration identified.',
    same_germ_scope='First converged midpoint of each phase, affine q/s with m/v/y held in the represented cell; M8 and M5 strata kept separate.',
    physical_formation_or_mode_or_cutoff_or_Pauli_selected=False,
    error_scope='Independent byte replay of analytic twojets in binary64; no physical-history or action-rounding enclosure.',
    materializer_correction='Duplicate stratum keyword repaired before canonical runs; failed base_run_1 and its logs preserved outside this reviewed manifest.')
out.write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(files=len(pins),manifest_sha256=sha256(out.read_bytes()).hexdigest(),source_sha256=pins['src/bhsm/interface/muon_finite_normal_worldvolume_jacobi.py']['sha256'],values=values),sort_keys=True))
