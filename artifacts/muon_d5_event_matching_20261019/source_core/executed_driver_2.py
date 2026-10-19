import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json
from hashlib import sha256
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history,original_d5_coefficient_callback,independent_residual_application
from bhsm.interface.muon_d5_temporal_bulk_refinement import evaluate_refined_field
from bhsm.interface.muon_d5_event_normal_source_application import solve_event_normal_source_application,evaluate_event_normal_source
from bhsm.interface.retained_response.finite_time_response import write_npz
OUT=Path(__file__).parent/'SOURCE_ONLY_NORMAL_PIVOT_v2'
OUT.mkdir(exist_ok=True)
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
old=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/run_3'
core=json.loads((old/'core_result.json').read_bytes())
saved=load_groups(old,core['archives'])
_,histories,pins=inputs()
history,receipt=recovered_export_history(ROOT,'incoming',*histories['incoming'])
pins.update(receipt['input_sha256'])
pins.update({(old/'core_result.json').relative_to(ROOT).as_posix():pin(old/'core_result.json')})
pins.update({(old/name).relative_to(ROOT).as_posix():record['sha256'] for name,record in core['archives'].items()})
formation=Path(__file__).parent/'FORMATION_WALL_TANGENCY_v1/application.npz'
with np.load(formation,allow_pickle=False) as z:psi=float(z['provisional_normal_displacement_source_correction'][0].real)
if psi != -.47802575718819384:raise ValueError('executed event-normal parent pivot identity changed')
pins[str(formation)]=pin(formation)
for name in ('muon_d5_event_normal_source_application.py','muon_d5_event_formation_constraints.py','muon_actual_normal_shape_source.py'):
    p=ROOT/'src/bhsm/interface'/name;pins[p.relative_to(ROOT).as_posix()]=pin(p)
dump(OUT/'RECOVERY_BEFORE.json',dict(input_sha256=pins,parent_head='bdd993d9',executed_parent_psi_E1=psi,
    equation='D5 V_newXi=-(D_newXi D5)V_saved',saved_values_resolved=False))
from bhsm.interface.muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
from bhsm.interface.muon_d5_complement_bulk_response import _fresh_endpoint,_wall_maps
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
from bhsm.interface.muon_d5_temporal_bulk_refinement import time_evaluation_matrix
with np.load(OUT/'source_application.npz.tmp',allow_pickle=False) as z:arrays={k:z[k].copy(order='K') for k in z.files}
newhistory=ProvisionalNormalSourceHistory(history,psi)
arrays['times']=saved['times'].copy()
arrays['source_label_codes']=np.arange(4,dtype=np.int64)
endpoints=[]
for time in saved['times']:
 raw,xi=(np.asarray(a) for a in (history.value(time)[0],newhistory.source(time)[0]))
 if np.any(raw.imag!=0) or np.any(xi.imag!=0):raise ValueError('real original endpoint operands required')
 endpoints.append(_fresh_endpoint(raw.real,xi.real))
wallmaps=_wall_maps(endpoints,full_d5_localized_lepton_trace())
wall_value_difference=0.
for key,value in wallmaps.items():
 if not key.startswith('wall_'):continue
 if key.endswith('_source'):arrays[key]=value
 else:
  wall_value_difference=max(wall_value_difference,float(np.max(abs(value-saved[key]))))
  arrays[key]=saved[key].copy(order='K')
for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
 for branch in ('particle','conjugate'):
  op=label.split('_')[0]+'_'+branch
  count=int(arrays[op+'_block_count'])
  for bi in range(count):
   prefix=label+'_'+op+'_block'+str(bi)+'_'
   if not all(prefix+k in arrays for k in ('indices','source_initial','source_slopes')):raise ValueError('incomplete executed source polynomial')
report=dict(classification='RECOVERED_COMPLETED_SOURCE_ONLY_EVENT_NORMAL_TANGENCY_APPLICATION',
 source_equation='D5 V_newXi=-(D_newXi D5)V_saved; value polynomials held unchanged',
 source_direction='original Xi plus explicit provisional constant-psi proper-normal extension',
 constant_psi_parent_E1=psi,executed_source_labels=['plus_seed','minus_seed','minus_LR','minus_RL'],
 complete_source_polynomials_recovered_without_source_resolve=True,value_equations_resolved=False,
 original_value_fields_reused=True,wall_value_difference_max=wall_value_difference,
 source_stage_arithmetic_report=None,source_stage_report_scope='source polynomials were fully written before the metadata writer failure; the transient stage arithmetic report was not serialized; independent original-equation checks follow',
 homogeneous_value_coordinates_per_time_node=366,old_homogeneous_value_family_retained=True,
 new_homogeneous_bulk_source_response=None,homogeneous_wall_basis_source_evaluated=True,
 free_psi_time_coordinate_determined=False,physical_g_or_normal_profiles_assigned=False,
 amplitude_scope='unit amplitude input slots held fixed only for this response; physical g/profile/h source derivatives remain open',
 mechanical_formation_mode_selected=False,outer_equations_solved=False,
 complete_physical_derivative=False,physical_admission=False,finite_application_is_continuum_bound=False,
 recovery_proof_sha256=pin(OUT/'RECOVERY_PROOF.json'),executed_source_owner_sha256=pin(OUT/'executed_source_owner.py'))

write_npz(OUT/'source_application.npz',arrays)
dump(OUT/'source_result.json',dict(input_sha256=pins,report=report,arrays=dict(sha256=pin(OUT/'source_application.npz'),bytes=(OUT/'source_application.npz').stat().st_size)))
print(json.dumps(dict(stage='SOURCE_ONLY_NORMAL_PIVOT_SAVED',sha256=pin(OUT/'source_result.json'),report=report)),flush=True)
tf=np.array([.079,.413,.913]);rf=np.array([.043,.319,.947]);t=saved['times'];width=float(saved['computational_strip_width']);wall=float(saved['radial_boundaries'][0])
pts=np.array([(time,r) for time in t[0]+(t[-1]-t[0])*tf for r in wall-width*rf])
oldpts=np.array([(time,r) for time in saved['amplitude_times'] for r in wall-width*rf])
coef=original_d5_coefficient_callback(lambda time:(newhistory.value(time)[0],newhistory.source(time)[0]),
    sheet_orientation=-1,gauge_basis_evaluate=newhistory.gauge_basis)
reports={};rows={}
for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
    coef=original_d5_coefficient_callback(lambda time:(newhistory.value(time)[0],newhistory.source(time)[0]),sheet_orientation=1 if label.startswith('plus_') else -1,gauge_basis_evaluate=newhistory.gauge_basis)
    def before(time,rho):return {key:a[0,0] for key,a in evaluate_refined_field(saved,label,[time],[rho]).items()}
    def after(time,rho):
        f=before(time,rho)
        f.update({key:a[0,0] for key,a in evaluate_event_normal_source(arrays,label,[time],[rho]).items()})
        return f
    for name,field,points in (('before_new_source',before,pts),('after_new_source',after,pts),
            ('before_new_source_old6times',before,oldpts),('after_new_source_old6times',after,oldpts)):
        values,check=independent_residual_application(field,coef,points)
        tag=label+'_'+name;reports[tag]=check
        for key in ('points','strong','strong_source','source_vertex','source_field'):rows[tag+'_'+key]=values[key]
        print(json.dumps(dict(stage='SOURCE_ORIGINAL_CHECK',label=tag,report=check)),flush=True)
write_npz(OUT/'independent_rows.npz',rows)
dump(OUT/'result.json',dict(input_sha256=pins,source_result_sha256=pin(OUT/'source_result.json'),report=report,
    independent_checks=reports,independent_rows=dict(sha256=pin(OUT/'independent_rows.npz'),bytes=(OUT/'independent_rows.npz').stat().st_size),
    derivative_scope='original affine-history Xi plus provisional constant-psi event-normal extension; physical psiDot, g/profile derivatives and every homogeneous source remain open',
    full_homogeneous_source_response=None,physical_admission=False,physical_guard=2e-10,
    NEXT_OPERAND='use corrected source application with full event/base/bundle and outer/formation equations; source-only LR/RL response is not a selected physical section'))
print(json.dumps(dict(stage='SOURCE_ORIGINAL_CHECKPOINT_SAVED',sha256=pin(OUT/'result.json'))),flush=True)
