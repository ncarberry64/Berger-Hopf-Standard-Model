import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,numpy as np
R=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');W=Path(__file__).parent;O=W/'CHILD_RADIAL17_v1';O.mkdir(exist_ok=False)
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.muon_d5_child_radial_consumed_trial import *
from bhsm.interface.muon_d5_child_characteristic_field import original_child_cell_coefficients
from bhsm.interface.muon_d5_child_corner_compatibility import apply_child_corner_to_data
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
core=json.loads((W/'CHILD_CELL_v2/core_result.json').read_bytes());app={}
for fn,a in core['archives'].items():
 path=W/'CHILD_CELL_v2'/fn
 if pin(path)!=a['sha256']:raise ValueError('old child input changed')
 app.update(load(path))
chart=radial_trial_chart(app['times'],app['radii']);indices=np.array([6,7,22,23,38,39,54,55]);outside=np.setdiff1d(np.arange(64),indices)
oldcase=W/'EVENT_CHILD_CORNER_v1';caserecord=json.loads((oldcase/'result.json').read_bytes());oldmeta=load(oldcase/'metadata.npz');rawpath=W/'RAW_WALL_EVENT_v1/application.npz';raw=load(rawpath);corner=load(W/'CHILD_CORNER_v1/application.npz')
J=Path(r'C:/Users/carbe/Downloads/BHSM_D5_TWO_SIDED_EVENT_20261019/JOINT_MAP_SOURCE_v1/application.npz');joint=load(J)
_,hist,pins=inputs();history,receipt=recovered_export_history(R,'outgoing',*hist['outgoing']);pins.update(receipt['input_sha256'])
owner=R/'src/bhsm/interface/muon_d5_child_radial_consumed_trial.py'
for path in (owner,W/'CHILD_CELL_v2/core_result.json',oldcase/'result.json',oldcase/'metadata.npz',rawpath,W/'CHILD_CORNER_v1/application.npz',J):pins[str(path)]=pin(path)
dump(O/'BEFORE.json',dict(input_sha256=pins,equation='same original future time6cell; one boundary-refined Chebyshevr17 trial on actual MUONfamily1 leptonweak8 consumedh/seed coefficients',original_time_cell_reused=True,old_birth_degree2_embedding=True,higher_new_birth_coordinates=None,future_incoming_polynomial_data_changed=False,physical_guard=2e-10,no_E1_native_parent_solve_replayed=True))
write_npz(O/'chart.npz',chart)
coeff={};block_numbers={};closure={}
for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate'):
 bi=next(i for i in range(int(app[label+'_block_count'])) if np.array_equal(app[label+'_block'+str(i)+'_indices'],indices));block_numbers[label]=bi;p=label+'_block'+str(bi)+'_'
 coeff[label]={}
 for key in ('time','radial','body','time_source','radial_source','body_source'):
  old=app[p+'original_coefficient_'+key];shape=list(old.shape);shape[-3]=17
  a=np.zeros(shape,complex)
  for j,newj in enumerate(chart['shared_radial_indices']):a[...,newj,:,:]=old[...,j,:,:]
  coeff[label][key]=a
 closure[label]=0.
newrho=chart['radii'][chart['new_radial_indices']]
for ti,time in enumerate(chart['times']):
 fresh,aux=original_child_cell_coefficients(history,[time],newrho,joint,17.98966013686085)
 for label,c in fresh.items():
  for key,a in c.items():
   v=a[...,indices,:][...,indices]
   off=max(float(np.max(abs(a[...,indices,:][...,outside]))),float(np.max(abs(a[...,outside,:][...,indices]))))
   closure[label]=max(closure[label],off)
   if off!=0:raise ValueError('targetblock not closed under consumed operator/source')
   for j,newj in enumerate(chart['new_radial_indices']):
    if key.endswith('_source'):coeff[label][key][:,ti,newj]=v[:,0,j]
    else:coeff[label][key][ti,newj]=v[0,j]
 print(json.dumps(dict(stage='NEW_RADIAL_COEFFICIENTS',time_node=ti,new_radial_points=len(newrho))),flush=True)
archives={};systems={}
for label,c in coeff.items():
 path=O/(label+'_coefficients.npz');write_npz(path,c);archives[path.name]=dict(sha256=pin(path),bytes=path.stat().st_size)
 side,branch=label.split('_');values={k:c[k] for k in ('time','radial','body')};sources={k:c[k+'_source'] for k in values}
 systems[label]=compile_consumed_trial(values,sources,chart,indices,branch,1 if side=='plus' else -1)
probe_folder=W/'CHILD_COEFFICIENT_PROBES_v1';proberecord=json.loads((probe_folder/'result.json').read_bytes());probes={}
for label,bi in block_numbers.items():
 fn=label+'_block'+str(bi)+'.npz';path=probe_folder/fn
 if pin(path)!=proberecord['archives'][fn]['sha256']:raise ValueError('probe input changed')
 probes[label]=load(path);pins[str(path)]=pin(path)
tp,rp=oldmeta['independent_times'],oldmeta['independent_radii'];reports=[]
for ci,candidate in enumerate((2,3)):
 prefix='candidate'+str(candidate)+'_';K=raw[prefix+'middle96'];Kx=raw[prefix+'middle_free7_first96'];lift=raw[prefix+'child_raw_lift384x96']
 for label in ('plus_seed','minus_seed','plus_homogeneous','minus_homogeneous'):
  fn=prefix+label+'.npz';path=oldcase/fn
  if pin(path)!=caserecord['archives'][fn]['sha256']:raise ValueError('consumed child data changed')
  old=load(path);pins[str(path)]=pin(path);side=label.split('_')[0];slot=8*ci;active=old['original_parent_column_indices'];data=old['corner_input_value'];datas=old['corner_input_source']
  target=raw[prefix+label+'_required_child_coordinates96'];qproj=np.linalg.solve(K,target)
  free_raw=np.einsum('ij,xjk,kl->xil',lift,Kx,qproj,optimize=True)[:,:,active]
  source_data=[datas]
  for j in range(7):
   dx=np.zeros_like(data);dx[2]=free_raw[j]
   _,cdx,_=apply_child_corner_to_data(app,corner,side,data,dx,source_slot=slot+1+j);source_data.append(cdx)
  dx=np.zeros_like(data);dx[2]=raw['child_material_spin_normal_rate384']@raw['colorless_lift384x96']@target[:,active]
  _,cdx,_=apply_child_corner_to_data(app,corner,side,data,dx,source_slot=16);source_data.append(cdx)
  slots=[slot,*range(slot+1,slot+8),16]
  for branch in ('particle','conjugate'):
   op=side+'_'+branch;system=systems[op];rows=(2+(branch=='conjugate'))*64+indices
   dz,_,_=extend_actual_data(data,datas,indices,branch,1 if side=='plus' else -1,chart)
   guess=old_field_initializer(old['child_value'][:,:,rows],old['child_time'][:,:,rows],tp,rp,chart)
   value,vreport=solve_consumed_trial(system,dz,guess);arrays=dict(value_nodal=value,data_extended=dz,global_carrier_indices=rows,original_parent_column_indices=active,original_parent_column_count=old['original_parent_column_count']);sreports=[]
   for sj,source_slot in enumerate(slots):
    sx=source_data[sj];_,dsource,_=extend_actual_data(data,sx,indices,branch,1 if side=='plus' else -1,chart)
    if sj==0:key='child_'
    elif sj<=7:key='child_free_map'+str(sj-1)+'_'
    else:key='child_normal_rate_'
    initx=old_field_initializer(old[key+'source'][:,:,rows],old[key+'time_source'][:,:,rows],tp,rp,chart)
    source,sreport=solve_consumed_trial_source(system,value,dsource,source_slot,initx)
    field=evaluate_consumed_trial(system,value,source,tp,rp)
    if sj==0:arrays['source_nodal']=source
    for k,a in field.items():
     if sj==0 or k.endswith('source'):arrays['direction'+str(sj)+'_'+k]=a
    p=op+'_block'+str(block_numbers[op])+'_';pc=probes[op]
    T,Rc,Kc=(pc[p+'original_coefficient_'+k] for k in ('time','radial','body'))
    Tx,Rx,Kxx=(pc[p+'original_coefficient_'+k+'_source'][source_slot] for k in ('time','radial','body'))
    strong=T@field['time']+Rc@field['radial']+Kc@field['value']
    strongx=Tx@field['time']+Rx@field['radial']+Kxx@field['value']+T@field['time_source']+Rc@field['radial_source']+Kc@field['source']
    before=T@old['child_time'][:,:,rows]+Rc@old['child_radial'][:,:,rows]+Kc@old['child_value'][:,:,rows]
    beforex=Tx@old['child_time'][:,:,rows]+Rx@old['child_radial'][:,:,rows]+Kxx@old['child_value'][:,:,rows]+T@old[key+'time_source'][:,:,rows]+Rc@old[key+'radial_source'][:,:,rows]+Kc@old[key+'source'][:,:,rows]
    arrays['direction'+str(sj)+'_original_strong']=strong;arrays['direction'+str(sj)+'_original_strong_source']=strongx
    sreport.update(before_value_max=float(np.max(abs(before))),after_value_max=float(np.max(abs(strong))),before_source_max=float(np.max(abs(beforex))),after_source_max=float(np.max(abs(strongx))));sreports.append(sreport)
   output=O/(prefix+label+'_'+branch+'.npz');write_npz(output,arrays);archives[output.name]=dict(sha256=pin(output),bytes=output.stat().st_size)
   row=dict(candidate=candidate,label=label,branch=branch,global_carrier_indices=rows.tolist(),original_columns=int(old['original_parent_column_count']),computed_columns=len(active),higher_birth_coordinates_unassigned=112,other_fullcarrier_ports_unassigned=True,value=vreport,sources=sreports,physical_admission=False)
   reports.append(row);print(json.dumps(dict(stage='ACTUAL_R17_CONSUMED_CASE_SAVED',candidate=candidate,label=label,branch=branch,before=sreports[0]['before_value_max'],after=sreports[0]['after_value_max'],source_before=sreports[0]['before_source_max'],source_after=sreports[0]['after_source_max'])),flush=True)
(O/'executed_source_owner.py').write_bytes(owner.read_bytes());(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
archives['chart.npz']=dict(sha256=pin(O/'chart.npz'),bytes=(O/'chart.npz').stat().st_size)
dump(O/'result.json',dict(input_sha256=pins,archives=archives,reports=reports,exact_target_closure_max=closure,classification='ONE_TARGETED_ORIGINAL_CHILD_R17_TRIAL_ON_ACTUAL_MUON_WEAK8_EVENT_COEFFICIENTS',unchanged='time6,physicalcell,background,adoptedpreparation,conditionalincomingselector,normalprofiles,calibration,hcoordinates',new_birth_ports='14additionalradialbirthcoordinates times8 pertargetbranch remainfree; oldquadraticembedding is a coordinatepartial, not a physicalzerochoice',future_incoming_data_reused_unchanged=True,other_fullcarrier_response_family_preserved=True,sign_parameter_unselected=True,physical_guard=2e-10,physical_admission=False,error_scope='same9independentoriginaloperatorpoints; finite targetedr17 trial, no continuum or complete physical norm bound',NEXT_OPERAND='use actual before/after consumed residual comparison to localize remaining time/radial/interface errors; retain all physical birth/outer/native/state terms'))
print('RADIAL17_TRIAL_SAVED',pin(O/'result.json'),flush=True)
