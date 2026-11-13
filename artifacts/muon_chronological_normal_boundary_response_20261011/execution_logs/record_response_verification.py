from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'artifacts/muon_chronological_normal_boundary_response_20261011'
sources=['src/bhsm/interface/muon_birth_chronological_normal_boundary_response.py']
tests=['tests/test_muon_birth_chronological_normal_boundary_response.py']
paths=[ROOT/p for p in sources+tests]+list((base/'execution_logs').glob('*.py'))
executions=[];pairs=[]
for side in ('incoming','outgoing'):
 for steps in (1,2,4):
  identical={}
  for name in ('result.json','application.npz'):
   a=base/f'{side}_{steps}steps_run_1'/name;b=base/f'{side}_{steps}steps_run_2'/name
   identical[name]=a.read_bytes()==b.read_bytes()
   paths.extend((a,b))
  if not all(identical.values()):raise RuntimeError('independent replay mismatch')
  pairs.append(dict(side=side,steps=steps,byte_identical=identical))
  for run in (1,2):
   stem=f'{side}_{steps}steps_run_{run}'
   e=base/'execution_logs'/(stem+'.execution.json');executions.append(json.loads(e.read_text()))
   paths.extend(base/'execution_logs'/(stem+suffix) for suffix in ('.execution.json','.stdout.txt','.stderr.txt'))
test=dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',*tests],environment={'PYTHONPATH':'src'},
 exit_code=0,stdout='....                                                                     [100%]\n4 passed in 3.68s\n',stderr='',
 capture_method='literal completed exec tool receipt; no producer/test rerun for packaging')
test_path=base/'execution_logs/tests.execution.json';test_path.write_text(json.dumps(test,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n');paths.append(test_path)
rows=[]
for p in sorted(set(paths)):
 b=p.read_bytes()
 if len(b)>10*1024**2:raise ValueError('publication size exceeded')
 rows.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha256(b).hexdigest()))
receipt=dict(scope='REPLAYED_COMPLETE_BIRTH_TRACE_AND_MIXED_CANONICAL_NORMAL_APPLICATION',source_paths=sources,test_paths=tests,
 tests=test,executions=executions,independent_process_comparisons=pairs,publication_files=rows,
 true_Lyy_and_all_algebraic_rows_retained=True,physical_E0_or_finalchild_boundary_selected=False, numerical_far_canonical_load_application=True, spatial_slice_Jacobi_not_full_worldvolume_Jacobi=True,
 full_chain_DtN_inverse_claimed=False,physical_inertia_cutoff_formation_or_Pauli_selected=False,
 far_face_role='full two-face action relation retained; a fixed far trace is a numerical application argument',
 chain_role='interior node and all Gauss/multiplier action rows exported without spectral deletion',
 normal_role='actual proper normal covector C_wall D_x chi/sqrt(1-U^2), with geometry motion; frozen trial is not a selected formation mode', named_central_gauge_generators_including_Higgs_velocity=True, scalar_invariant_space_not_disproved_by_internal_image=True, physical_formation_r_i_drive_not_selected=True)
p=base/'verification.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha256(p.read_bytes()).hexdigest(),files=len(rows),pairs=len(pairs))))
