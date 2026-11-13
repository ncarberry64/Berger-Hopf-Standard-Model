import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys,json,subprocess,numpy as np
ROOT=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(r'C:/Users/carbe/Downloads/BHSM_D5_FERMION_OUTER_CHILD_20261019');OUT=BASE/'CHILD_CELL_v1';OUT.mkdir(exist_ok=False)
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_child_characteristic_field import original_child_cell_coefficients,solve_child_characteristic_cell,independent_child_cell_checks
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
_,hist,pins=inputs();history,receipt=recovered_export_history(ROOT,'outgoing',*hist['outgoing']);pins.update(receipt['input_sha256'])
OLD=Path(r'C:/Users/carbe/Downloads/BHSM_D5_TWO_SIDED_EVENT_20261019')
paths=dict(child=OLD/'CHILD_SAME_DIRECTION_v1/application.npz',joint=OLD/'JOINT_MAP_SOURCE_v1/application.npz')
child,joint=(load(paths[k]) for k in ('child','joint'));owner=ROOT/'src/bhsm/interface/muon_d5_child_characteristic_field.py'
for p in (*paths.values(),owner):pins[str(p)]=pin(p)
psi=17.98966013686085
inner=float(child['child_birth_radius']);wall=float(np.pi/2);r=np.array([inner,(inner+wall)/2,wall])
dump(OUT/'BEFORE.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=pins,psi_child_E1=psi,free_child_normal_rate=None,domain_rule='t0=0; tmax=min(cached consumed t,0.05*(WALL-birth_rho)/max(abs(N/C)+abs(z)))',birth_and_future_incoming_data=None,physical_guard=2e-10,ancestor_or_native_calculations_replayed=False))
c0,m0=original_child_cell_coefficients(history,[0.],r,joint,psi)
metric=m0['metrics'][0];N,C,z,mu=metric
if any(np.max(abs(a.imag))>1e-12 for a in (N,C,z,mu)):raise ValueError('real actual geometry required')
if min(np.min(N.real),np.min(C.real),np.min(mu.real))<=0:raise ValueError('positive Cauchy geometry required')
speed=np.max(abs(N/C)+abs(z));margin=np.min((N/C).real-abs(z))
if margin<=0:raise ValueError('both radial faces not timelike; this characteristic split not valid')
tmax=min(float(child['original_child_coordinates'][0]),float(.05*(wall-inner)/speed))
t=tmax*(1-np.cos(np.pi*np.arange(6)/5))/2
crest,mrest=original_child_cell_coefficients(history,t[1:],r,joint,psi)
coeff={}
for label,a in c0.items():
 coeff[label]={k:np.concatenate((a[k],crest[label][k]),axis=1 if k.endswith('_source') else 0) for k in a}
meta=dict(metrics=np.concatenate((m0['metrics'],mrest['metrics'])),raw_source_columns=np.concatenate((m0['raw_source_columns'],mrest['raw_source_columns'])),source_names=m0['source_names'])
app,report=solve_child_characteristic_cell(coeff,t,r)
report.update(characteristic_positive_margin=float(margin),characteristic_speed_max=float(speed),time_extent=tmax,radial_extent=wall-inner,independent_future_boundary_history_not_selected=True,complete_event_cap_extension_not_assumed=True)
archives={}
for label,c in coeff.items():
 for bi in range(int(app[label+'_block_count'])):
  p=label+'_block'+str(bi)+'_';idx=app[p+'indices']
  arrays={k:v for k,v in app.items() if k.startswith(p)}
  for k,a in c.items():arrays[p+'original_coefficient_'+k]=a[...,idx,:][...,idx]
  path=OUT/(label+'_block'+str(bi)+'.npz');write_npz(path,arrays);archives[path.name]=dict(sha256=pin(path),bytes=path.stat().st_size)
metadata={k:v for k,v in app.items() if '_block' not in k or k.endswith('_block_count')}
metadata.update(original_metrics=meta['metrics'],original_raw_source_columns=meta['raw_source_columns'])
write_npz(OUT/'metadata.npz',metadata);archives['metadata.npz']=dict(sha256=pin(OUT/'metadata.npz'),bytes=(OUT/'metadata.npz').stat().st_size)
(OUT/'executed_source_owner.py').write_bytes(owner.read_bytes());(OUT/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
dump(OUT/'core_result.json',dict(input_sha256=pins,archives=archives,source_names=meta['source_names'],report=report,executed_owner_sha256=pin(OUT/'executed_source_owner.py'),executed_driver_sha256=pin(OUT/'executed_driver.py'),NEXT_OPERAND='substitute proved raw E1 event coordinates only into birth-wall slot2; retain other birth values/future incoming characteristic data and all physical outer/formation conditions'))
print(json.dumps(dict(stage='CHILD_FIELD_CORE_SAVED',result_sha256=pin(OUT/'core_result.json'),time_extent=tmax,margin=float(margin),max_stage=max(a['equation_scaled_stage_max'] for a in report['blocks'].values()),max_source_stage=max(a['equation_scaled_source_stage_max'] for a in report['blocks'].values()),archive_count=len(archives))),flush=True)
# Full original nodal strong rows are checks, not the defining stage residual.
nodal,nreport=independent_child_cell_checks(app,coeff,t,r)
write_npz(OUT/'nodal_checks.npz',nodal)
tp=tmax*np.array([.137,.419,.863]);rp=inner+(wall-inner)*np.array([.083,.377,.911])
ci,mi=original_child_cell_coefficients(history,tp,rp,joint,psi)
ind,ireport=independent_child_cell_checks(app,ci,tp,rp)
write_npz(OUT/'independent_checks.npz',ind)
dump(OUT/'checks_result.json',dict(core_result_sha256=pin(OUT/'core_result.json'),nodal=nreport,independent9=ireport,arrays={p:dict(sha256=pin(OUT/p),bytes=(OUT/p).stat().st_size) for p in ('nodal_checks.npz','independent_checks.npz')},physical_admission=False,physical_guard=2e-10))
print(json.dumps(dict(stage='CHILD_FIELD_ORIGINAL_CHECKS_SAVED',result_sha256=pin(OUT/'checks_result.json'),nodal_value=nreport['original_strong_max'],nodal_source=nreport['original_source_max'],independent_value=ireport['original_strong_max'],independent_source=ireport['original_source_max'])),flush=True)
