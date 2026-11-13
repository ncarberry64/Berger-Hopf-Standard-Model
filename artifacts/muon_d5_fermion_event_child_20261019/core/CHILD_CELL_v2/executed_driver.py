import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys,json,numpy as np
ROOT=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent;PREVIOUS=BASE/'CHILD_CELL_v1';OUT=BASE/'CHILD_CELL_v2';OUT.mkdir(exist_ok=False)
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_d5_child_characteristic_field import solve_child_characteristic_cell
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
old=json.loads((PREVIOUS/'core_result.json').read_bytes());app0={};pins={str(PREVIOUS/'core_result.json'):pin(PREVIOUS/'core_result.json')}
for filename,receipt in old['archives'].items():
 p=PREVIOUS/filename
 if pin(p)!=receipt['sha256']:raise ValueError('executed child coefficient/initializer identity changed: '+filename)
 pins[str(p)]=pin(p)
 with np.load(p,allow_pickle=False) as z:app0.update({k:z[k].copy(order='K') for k in z.files})
owner=ROOT/'src/bhsm/interface/muon_d5_child_characteristic_field.py';pins[str(owner)]=pin(owner)
failed=dict(classification='FAILED_CHARACTERISTIC_OUTPUT_COVECTOR_APPLICATION_PRESERVED',core_result_sha256=pin(PREVIOUS/'core_result.json'),checks_result_sha256=pin(PREVIOUS/'checks_result.json'),error='v1 outgoing boundary rows used Qout^dagger L, but radial characteristic spaces are covectors of evolution equation T^-1 L',source_error='missing derivative of inverse time principal at boundary outgoing rows',replacement='v2 retains exact original coefficients and uses Qout^dagger T^-1 L plus full inverse-time source derivative',no_v1_physical_admission=True)
dump(PREVIOUS/'FAILED_APPLICATION.json',failed)
dump(OUT/'BEFORE.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),input_sha256=pins,equation='same original coefficients; corrected outgoing covectors Qout^dagger T^-1 L and full delta(T^-1)=-T^-1 deltaT T^-1',previous_field_initializer='completed failedv1 response and all17 source responses; corrected by new complete stage equations',fixed_grid=True,physical_data=None,ancestor_callbacks_or_native_solves_replayed=False,physical_guard=2e-10))
t,r=app0['times'],app0['radii'];nt,nr=len(t),len(r);coeff={}
for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate'):
 coeff[label]={}
 for key in ('time','radial','body','time_source','radial_source','body_source'):
  ns=17 if key.endswith('_source') else None
  shape=((ns,) if ns else ())+ (nt,nr,64,64)
  a=np.zeros(shape,complex)
  for bi in range(int(app0[label+'_block_count'])):
   p=label+'_block'+str(bi)+'_';idx=app0[p+'indices'];v=app0[p+'original_coefficient_'+key]
   for i,ii in enumerate(idx):
    for j,jj in enumerate(idx):a[...,ii,jj]=v[...,i,j]
  coeff[label][key]=a
app,report=solve_child_characteristic_cell(coeff,t,r,initializer=app0)
report.update(characteristic_positive_margin=old['report']['characteristic_positive_margin'],characteristic_speed_max=old['report']['characteristic_speed_max'],time_extent=old['report']['time_extent'],radial_extent=old['report']['radial_extent'],value_and_source_coefficients_reused_bitwise=True,prior_v1_failed_outgoing_covectors_preserved=True,source_inverse_time_vertex_complete=True)
archives={}
for label,c in coeff.items():
 for bi in range(int(app[label+'_block_count'])):
  p=label+'_block'+str(bi)+'_';idx=app[p+'indices'];arrays={k:v for k,v in app.items() if k.startswith(p)}
  for k,a in c.items():arrays[p+'original_coefficient_'+k]=a[...,idx,:][...,idx]
  path=OUT/(label+'_block'+str(bi)+'.npz');write_npz(path,arrays);archives[path.name]=dict(sha256=pin(path),bytes=path.stat().st_size)
metadata={k:v for k,v in app.items() if '_block' not in k or k.endswith('_block_count')}
metadata.update({k:app0[k] for k in ('original_metrics','original_raw_source_columns')})
write_npz(OUT/'metadata.npz',metadata);archives['metadata.npz']=dict(sha256=pin(OUT/'metadata.npz'),bytes=(OUT/'metadata.npz').stat().st_size)
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'core_result.json',dict(input_sha256=pins,archives=archives,source_names=old['source_names'],report=report,executed_owner_sha256=pin(OUT/'executed_source_owner.py'),executed_driver_sha256=pin(OUT/'executed_driver.py'),NEXT_OPERAND='consume actual raw event required trace coefficients in birth-wall slot2 with remainingbirth/futureincoming data explicit; use those combinations for original independent checks before refinement'))
print(json.dumps(dict(stage='CORRECTED_CHILD_FIELD_CORE_SAVED',result_sha256=pin(OUT/'core_result.json'),max_stage=max(a['equation_scaled_stage_max'] for a in report['blocks'].values()),max_source_stage=max(a['equation_scaled_source_stage_max'] for a in report['blocks'].values()),max_condition=max(a['matrix_condition2'] for a in report['blocks'].values()),largest_archive=max(x['bytes'] for x in archives.values()))),flush=True)
