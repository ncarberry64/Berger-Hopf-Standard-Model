import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import sys,json,numpy as np
R=Path(r'C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');W=Path(r'C:/Users/carbe/Downloads/BHSM_CAUSAL_DATA_20261019');W.mkdir(parents=True,exist_ok=True);O=W/'RESPONSE_DIAGNOSTICS_v1';O.mkdir(exist_ok=False)
P=R/'artifacts/muon_d5_fermion_event_child_20261019/core'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.muon_d5_saved_response_diagnostics import *
from bhsm.interface.retained_response.finite_time_response import write_npz

def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def load(p):
 with np.load(p,allow_pickle=False) as z:return {k:z[k].copy(order='K') for k in z.files}
def verified(p,md):
 if pin(p)!=md['sha256']:raise ValueError('saved operand changed: '+str(p))
 return load(p)
def stats_add(acc,items):
 for key,a in items.items():
  v=magnitude(a);old=acc.setdefault(key,dict(max_abs=0.,Frobenius_squared=0.))
  old['max_abs']=max(old['max_abs'],v['max_abs']);old['Frobenius_squared']+=v['frobenius']**2

def finished(acc):return {k:dict(max_abs=v['max_abs'],frobenius=float(np.sqrt(v['Frobenius_squared']))) for k,v in acc.items()}

def fieldkeys(j):
 if j==0:return 'child_'
 if j<=7:return 'child_free_map'+str(j-1)+'_'
 return 'child_normal_rate_'

r3folder=P/'EVENT_CHILD_CORNER_v1';r3record=json.loads((r3folder/'result.json').read_bytes());r3meta=verified(r3folder/'metadata.npz',r3record['archives']['metadata.npz'])
r17folder=P/'CHILD_RADIAL17_v1';r17record=json.loads((r17folder/'result.json').read_bytes());chart=verified(r17folder/'chart.npz',r17record['archives']['chart.npz'])
cell=P/'CHILD_CELL_v2';cellrecord=json.loads((cell/'core_result.json').read_bytes());meta=verified(cell/'metadata.npz',cellrecord['archives']['metadata.npz'])
cornerfolder=P/'CHILD_CORNER_v1';cornerrecord=json.loads((cornerfolder/'result.json').read_bytes());corner=verified(cornerfolder/'application.npz',cornerrecord['arrays'])
probefolder=P/'CHILD_COEFFICIENT_PROBES_v1';proberecord=json.loads((probefolder/'result.json').read_bytes());probemeta=verified(probefolder/'metadata.npz',proberecord['archives']['metadata.npz'])
assert np.array_equal(probemeta['times'],r3meta['independent_times']) and np.array_equal(probemeta['radii'],r3meta['independent_radii'])
owner=R/'src/bhsm/interface/muon_d5_saved_response_diagnostics.py';pins={str(p):pin(p) for p in (owner,r3folder/'result.json',r17folder/'result.json',cell/'core_result.json',cornerfolder/'result.json',probefolder/'result.json',r3folder/'metadata.npz',r17folder/'chart.npz',cell/'metadata.npz',cornerfolder/'application.npz',probefolder/'metadata.npz')}
dump(O/'BEFORE.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),head='9a6c7766',input_sha256=pins,equations=['L=T Phi_t+R Phi_r+K Phi','deltaL=(deltaT)Phi_t+(deltaR)Phi_r+(deltaK)Phi+TdeltaPhi_t+RdeltaPhi_r+KdeltaPhi'],scope='saved coordinate-column diagnostics only; no field/background/coefficient solves or old field reconstruction',physical_state=None,physical_norm=None,physical_guard=2e-10))
probes={};nodes={};layouts={};target={}
for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate'):
 for bi in range(int(meta[label+'_block_count'])):
  name=label+'_block'+str(bi);p=name+'_';fn=name+'.npz';probes[p]=verified(probefolder/fn,proberecord['archives'][fn]);pins[str(probefolder/fn)]=pin(probefolder/fn)
  with np.load(cell/fn,allow_pickle=False) as z:
   layouts[p]={k:z[p+k].copy() for k in ('indices','data_indices','incoming_inner_basis','incoming_outer_basis')}
   nodes[p]={k:z[p+'original_coefficient_'+k].copy() for k in ('time','radial','body','time_source','radial_source','body_source')}
  pins[str(cell/fn)]=pin(cell/fn)
  if np.array_equal(layouts[p]['indices'],[6,7,22,23,38,39,54,55]):target[label]=p
archives={};r3summaries={};boundary_saved={};r3rows={(int(v['candidate']),v['label']):v for v in r3record['reports']}
for candidate in (2,3):
 for label in ('plus_seed','minus_seed','minus_LR','minus_RL','plus_homogeneous','minus_homogeneous'):
  filename='candidate'+str(candidate)+'_'+label+'.npz';path=r3folder/filename;old=verified(path,r3record['archives'][filename]);pins[str(path)]=pin(path)
  side=label.split('_')[0];slots=[0 if candidate==2 else 8,*range(1 if candidate==2 else 9,8 if candidate==2 else 16),16];n=int(old['original_parent_column_count']);k=len(old['original_parent_column_indices'])
  out=dict(original_parent_column_indices=old['original_parent_column_indices'],original_parent_column_count=np.array(n));directions=[]
  for direction,slot in enumerate(slots):
   fp=fieldkeys(direction);aggregate={};fieldagg={};muon={};strong_cols=np.zeros(k);source_cols=np.zeros(k);strong_points=np.zeros((3,3));source_points=np.zeros((3,3))
   for family in range(3):
    for b,branch in enumerate(('particle','conjugate')):
     oplabel=side+'_'+branch
     for bi in range(int(meta[oplabel+'_block_count'])):
      p=oplabel+'_block'+str(bi)+'_';idx=layouts[p]['indices'];rows=(2*family+b)*64+idx;c=probes[p]
      coeff={q:c[p+'original_coefficient_'+q] for q in ('time','radial','body')};coeff.update({q+'_source':c[p+'original_coefficient_'+q+'_source'][slot] for q in ('time','radial','body')})
      field=dict(value=old['child_value'][:,:,rows],time=old['child_time'][:,:,rows],radial=old['child_radial'][:,:,rows],source=old[fp+'source'][:,:,rows],time_source=old[fp+'time_source'][:,:,rows],radial_source=old[fp+'radial_source'][:,:,rows])
      parts=original_term_arrays(field,coeff);stats_add(aggregate,parts);stats_add(fieldagg,field)
      strong_cols=np.maximum(strong_cols,np.max(abs(parts['original_D5']),axis=(0,1,2)));source_cols=np.maximum(source_cols,np.max(abs(parts['original_D5_source']),axis=(0,1,2)))
      strong_points=np.maximum(strong_points,np.max(abs(parts['original_D5']),axis=(-2,-1)));source_points=np.maximum(source_points,np.max(abs(parts['original_D5_source']),axis=(-2,-1)))
      if family==1 and p==target[oplabel]:muon[branch]=term_report(field,coeff,parts)
   out['direction'+str(direction)+'_original_D5_max_by_original_column']=strong_cols;out['direction'+str(direction)+'_original_D5_source_max_by_original_column']=source_cols
   out['direction'+str(direction)+'_original_D5_max_by_point']=strong_points;out['direction'+str(direction)+'_original_D5_source_max_by_point']=source_points
   directions.append(dict(direction=direction,source_slot=slot,full384_field=finished(fieldagg),full384_terms=finished(aggregate),matched_MUON_weak8=muon))
  data,dx=old['corner_input_value'],old['corner_input_source'];corner_max=corner_xmax=0.;boundaries={}
  for family in range(3):
   for b,branch in enumerate(('particle','conjugate')):
    op=side+'_'+branch;block=slice((2*family+b)*64,(2*family+b+1)*64);z=data[:,block].reshape(512,-1);zx=dx[:,block].reshape(512,-1)
    for bi in range(int(meta[op+'_block_count'])):
     p=op+'_block'+str(bi)+'_';di=layouts[p]['data_indices'];C=corner[p+'corner'];Cx=corner[p+'corner_source'][slots[0]]
     corner_max=max(corner_max,float(np.max(abs(C@z[di]))));corner_xmax=max(corner_xmax,float(np.max(abs(C@zx[di]+Cx@z[di]))))
     if family==1 and p==target[op]:
      d=len(layouts[p]['indices']);local=z[di].reshape(8,d,-1);localx=zx[di].reshape(8,d,-1);node=nodes[p]
      c={q:node[q] for q in ('time','radial','body')};c.update({q+'_source':node[q+'_source'][slots[0]] for q in ('time','radial','body')})
      arrays,report=boundary_data_diagnostics(local[:3],localx[:3],local[3:],localx[3:],c,meta['time_derivative'],meta['radial_derivative'],layouts[p]['incoming_inner_basis'],layouts[p]['incoming_outer_basis'])
      report['value_time_representation']=time_polynomial_diagnostics(arrays['boundary_values'],meta['times'],meta['time_derivative']);report['source_time_representation']=time_polynomial_diagnostics(arrays['boundary_sources'],meta['times'],meta['time_derivative'])
      boundaries[branch]=report;boundary_saved[(candidate,label,branch)]=arrays
      for key,a in arrays.items():out['MUON_'+branch+'_'+key]=a
  row=r3rows[(candidate,label)]
  report=dict(classification='SAVED_R3_COORDINATE_COLUMN_DIAGNOSTIC',candidate=candidate,label=label,original_parent_columns=n,stored_nonzero_event_columns=k,all_h_coordinates_retained=n==3660 or None,directions=directions,
   enforced_scaled_stage_receipts=dict(value=row['consumed_value_correction'],source=row['consumed_source_correction']),
   original_unscaled_enforced_nodal_rows=None,missing_nodal_scope='actual corrected r3 nodal fields were not archived; no field reconstruction or solve performed',
   event_rows=dict(value=magnitude(old['original_event_value_rows']),source=magnitude(old['original_event_supplied_source_rows'])),
   exact_original_C1_data_germ=dict(value_max=corner_max,supplied_source_max=corner_xmax),boundary_time_data=boundaries,
   physical_state_amplitudes=None,physical_norm=None,physical_admission=False,physical_guard=2e-10)
  opath=O/filename;write_npz(opath,out);archives[filename]=dict(sha256=pin(opath),bytes=opath.stat().st_size);dump(O/filename.replace('.npz','.json'),report);r3summaries[(candidate,label)]=report
  print(json.dumps(dict(stage='R3_SAVED_OPERAND_DIAGNOSTIC',candidate=candidate,label=label,value=directions[0]['full384_terms']['original_D5']['max_abs'],source=directions[0]['full384_terms']['original_D5_source']['max_abs'],corner=corner_max,corner_source=corner_xmax)),flush=True)
  del old
r17summaries=[]
for row in r17record['reports']:
 candidate,label,branch=int(row['candidate']),row['label'],row['branch'];filename='candidate'+str(candidate)+'_'+label+'_'+branch+'.npz';path=r17folder/filename;a=verified(path,r17record['archives'][filename]);pins[str(path)]=pin(path);side=label.split('_')[0];op=side+'_'+branch;p=target[op];slot=0 if candidate==2 else 8;slots=[slot,*range(slot+1,slot+8),16];pc=probes[p]
 coefficientfile=op+'_coefficients.npz';nc=verified(r17folder/coefficientfile,r17record['archives'][coefficientfile]);pins[str(r17folder/coefficientfile)]=pin(r17folder/coefficientfile)
 arrays=dict(original_parent_column_indices=a['original_parent_column_indices'],global_carrier_indices=a['global_carrier_indices']);directions=[]
 for j,s in enumerate(slots):
  field={q:a['direction0_'+q] for q in ('value','time','radial')};field.update({q:a['direction'+str(j)+'_'+q] for q in ('source','time_source','radial_source')})
  c={q:pc[p+'original_coefficient_'+q] for q in ('time','radial','body')};c.update({q+'_source':pc[p+'original_coefficient_'+q+'_source'][s] for q in ('time','radial','body')})
  terms=original_term_arrays(field,c);rep=term_report(field,c,terms)
  rep.update(direction=j,source_slot=s,saved_value_reassembly_difference=magnitude(terms['original_D5']-a['direction'+str(j)+'_original_strong']),saved_source_reassembly_difference=magnitude(terms['original_D5_source']-a['direction'+str(j)+'_original_strong_source']))
  directions.append(rep)
  for q in ('original_D5','original_D5_source'):arrays['direction'+str(j)+'_'+q+'_max_by_original_column']=np.max(abs(terms[q]),axis=(0,1,2))
 c={q:nc[q] for q in ('time','radial','body')};c.update({q+'_source':nc[q+'_source'][slot] for q in ('time','radial','body')})
 nodearrays,nodereport,nfield,nparts=saved_nodal_partitions(a['value_nodal'],a['source_nodal'],c,chart['time_derivative'],chart['radial_derivative'],layouts[p]['incoming_inner_basis'],layouts[p]['incoming_outer_basis'])
 for q,x in nodearrays.items():arrays[q]=x
 actual_old=verified(r3folder/('candidate'+str(candidate)+'_'+label+'.npz'),r3record['archives']['candidate'+str(candidate)+'_'+label+'.npz'])
 rows=a['global_carrier_indices'];b=0 if branch=='particle' else 1;sl=slice((2+b)*64,(3+b)*64);di=layouts[p]['data_indices'];lx=actual_old['corner_input_source'][:,sl].reshape(512,-1)[di].reshape(8,8,-1)
 birthx=np.einsum('ij,jak->iak',chart['birth_degree2_extension'],lx[:3]);incx=lx[3:];z=a['data_extended'].reshape(22,8,-1);birth=z[:17];incoming=z[17:]
 barrays,breport=boundary_data_diagnostics(birth,birthx,incoming,incx,c,chart['time_derivative'],chart['radial_derivative'],layouts[p]['incoming_inner_basis'],layouts[p]['incoming_outer_basis'])
 birth_error=a['value_nodal'][0]-birth;birth_source_error=a['source_nodal'][0]-birthx;inerr=[];inxerr=[]
 for face,r,Q in ((0,0,layouts[p]['incoming_inner_basis']),(1,16,layouts[p]['incoming_outer_basis'])):
  inerr.append(Q.conj().T@a['value_nodal'][1:,r]-incoming[:,4*face:4*(face+1)])
  inxerr.append(Q.conj().T@a['source_nodal'][1:,r]-incx[:,4*face:4*(face+1)])
 trace=dict(birth_value=magnitude(birth_error),birth_source=magnitude(birth_source_error),incoming_value=magnitude(np.array(inerr)),incoming_source=magnitude(np.array(inxerr)))
 prev=boundary_saved[(candidate,label,branch)];identity=dict(value=magnitude(barrays['boundary_values']-prev['boundary_values']),source=magnitude(barrays['boundary_sources']-prev['boundary_sources']))
 for q,x in barrays.items():arrays['boundary_'+q]=x
 report=dict(classification='SAVED_R17_COORDINATE_COLUMN_DIAGNOSTIC',candidate=candidate,label=label,branch=branch,original_parent_columns=int(a['original_parent_column_count']),stored_nonzero_event_columns=len(a['original_parent_column_indices']),
  independent9=directions,original6time_nodal_partitions=nodereport,birth_and_incoming_trace_checks=trace,original_C1_data_germ=breport,r3_to_r17_incoming_data_identity=identity,
  nodal_value_time_representation=time_polynomial_diagnostics(a['value_nodal'],chart['times'],chart['time_derivative']),nodal_source_time_representation=time_polynomial_diagnostics(a['source_nodal'],chart['times'],chart['time_derivative']),
  nodal_term_magnitudes=term_report(nfield,c,nparts),source_free_map_and_nu_nodal_partition=None,
  nonparticular_nodal_scope='only their independent-probe derivatives were archived; no nodal source reconstruction',
  higher_birth_coordinates_unassigned=112,other_fullcarrier_ports_unassigned=True,physical_state_amplitudes=None,physical_norm=None,physical_admission=False,physical_guard=2e-10)
 output=O/filename;write_npz(output,arrays);archives[filename]=dict(sha256=pin(output),bytes=output.stat().st_size);dump(O/filename.replace('.npz','.json'),report);r17summaries.append(report)
 print(json.dumps(dict(stage='R17_SAVED_OPERAND_PARTITION',candidate=candidate,label=label,branch=branch,enforced=nodereport['enforced_interior_original_D5']['max_abs'],outgoing=nodereport['enforced_outgoing_evolution']['max_abs'],heldincoming=nodereport['held_incoming_evolution']['max_abs'],heldbirth=nodereport['held_birth_original_D5']['max_abs'],offnode=directions[0]['terms']['original_D5']['max_abs'],amplitude=directions[0]['field']['value']['max_abs'])),flush=True)
 del actual_old,a
(O/'executed_source_owner.py').write_bytes(owner.read_bytes());(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
summary=dict(input_sha256=pins,archives=archives,r3_cases=[dict(candidate=k[0],label=k[1],diagnostic_json='candidate'+str(k[0])+'_'+k[1]+'.json') for k in r3summaries],r17_cases=[dict(candidate=q['candidate'],label=q['label'],branch=q['branch'],diagnostic_json='candidate'+str(q['candidate'])+'_'+q['label']+'_'+q['branch']+'.json') for q in r17summaries],
 classification='DIAGNOSTIC_OF_SAVED_RESPONSE_COORDINATE_COLUMNS_NOT_A_PHYSICAL_STATE',
 physical_guard=2e-10,physical_admission=False,physical_norm=None,physical_state_amplitudes=None,
 scale_scope=dict(time_cell_width=float(chart['times'][-1]-chart['times'][0]),radial_cell_width=float(chart['radii'][-1]-chart['radii'][0]),physical_unit_scale_admitted=False,conditioning_ratios_do_not_replace_original_norms=True),
 no_new_solve_or_original_callback=True,no_old_field_reconstruction=True,no_refinement_or_data_selection=True,
 all_parent_h_coordinates_retained=3660,eta_data_families_independent_but_parent_h_shared=True,
 unresolved='physical causal birth/incoming histories and their state/current normalization, complete cap/bundle/domain contacts, complementary fields/native/formation/cutoff equations',
 NEXT_OPERAND='consume physical causal data determined by the original preparation/equations; apply saved residual operators to that joint combination rather than interpreting coordinate-column maxima as a selected state')
dump(O/'result.json',summary)
print('RESPONSE_DIAGNOSTIC_SAVED',pin(O/'result.json'),flush=True)
