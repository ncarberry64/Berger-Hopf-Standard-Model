import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import sys,json
from hashlib import sha256
import numpy as np
ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');BASE=Path(__file__).parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups
from scripts.evaluate_muon_d5_valid_domain_application import inputs
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history,original_d5_coefficient_callback,independent_residual_application
from bhsm.interface.muon_d5_temporal_bulk_refinement import evaluate_refined_field
from bhsm.interface.muon_d5_event_normal_source_application import evaluate_event_normal_source
from bhsm.interface.muon_d5_event_consumed_source_refinement import refine_consumed_event_source,evaluate_consumed_source_refinement
from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule
from bhsm.interface.retained_response.finite_time_response import write_npz
steps=int(sys.argv[1]);OUT=BASE/('SOURCE_CONSISTENT_RHS'+str(steps)+'_v1');OUT.mkdir(exist_ok=False)
initializer=BASE/('SOURCE_ONLY_NORMAL_PIVOT_v2' if steps==2 else 'SOURCE_CONSISTENT_RHS2_v1')
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
old=ROOT/'artifacts/muon_d5_valid_domain_application_20261019/run_3';core=json.loads((old/'core_result.json').read_bytes());saved=load_groups(old,core['archives'])
with np.load(initializer/'source_application.npz',allow_pickle=False) as z:initial={k:z[k].copy(order='K') for k in z.files}
_,histories,pins=inputs();history,receipt=recovered_export_history(ROOT,'incoming',*histories['incoming']);pins.update(receipt['input_sha256'])
psi=float(np.real(initial['provisional_constant_psi_E1']))
pins.update({(old/'core_result.json').relative_to(ROOT).as_posix():pin(old/'core_result.json')})
pins.update({(old/name).relative_to(ROOT).as_posix():record['sha256'] for name,record in core['archives'].items()})
for p in (initializer/'source_application.npz',initializer/'source_result.json',ROOT/'src/bhsm/interface/muon_d5_event_consumed_source_refinement.py',ROOT/'src/bhsm/interface/muon_d5_event_normal_source_application.py'):
 pins[str(p)]=pin(p)
dump(OUT/'BEFORE.json',dict(input_sha256=pins,original_value_cache_held=True,source_radial_steps=steps,
 equation='R S_r+T S_t+K S=-(R_Xi V10_r+T_Xi V10_t+K_Xi V10)',source_time_count=10))
arrays,report,newhistory=refine_consumed_event_source(saved,initial,history,psi,radial_steps=steps)
write_npz(OUT/'source_application.npz',arrays)
dump(OUT/'source_result.json',dict(input_sha256=pins,report=report,arrays=dict(sha256=pin(OUT/'source_application.npz'),bytes=(OUT/'source_application.npz').stat().st_size)))
print(json.dumps(dict(stage='CONSISTENT_SOURCE_SAVED',radial_steps=steps,sha256=pin(OUT/'source_result.json'),forcing_transfer=report['original_R_Xi_times_saved_value_radial_equation_defect_max'],stage_max=max(c['corrected_stage_residual_max'] for v in report['stage_checks'].values() for c in v))),flush=True)
t=saved['times'];width=float(saved['computational_strip_width']);wall=float(saved['radial_boundaries'][0])
it=t[0]+(t[-1]-t[0])*np.array([.079,.413,.913]);ir=wall-width*np.array([.043,.319,.947])
cn,_,_,_=_collocation_rule(int(saved['radial_order']));br=saved['radial_boundaries']
gr=np.concatenate([a+(b-a)*cn for a,b in zip(br[:-1],br[1:])])
probes=dict(independent9=np.array([(ti,r) for ti in it for r in ir]),
 old6times=np.array([(ti,r) for ti in saved['amplitude_times'] for r in ir]),
 independent_times_original_radial_Gauss=np.array([(ti,r) for ti in it for r in gr]),
 original10times_three_original_radial_Gauss=np.array([(ti,r) for ti in t for r in gr[[0,4,9]]]))
reports={};rows={}
for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
 coef=original_d5_coefficient_callback(lambda ti:(newhistory.value(ti)[0],newhistory.source(ti)[0]),sheet_orientation=1 if label.startswith('plus_') else -1,gauge_basis_evaluate=newhistory.gauge_basis)
 def field(ti,r,source):
  f={key:a[0,0] for key,a in evaluate_refined_field(saved,label,[ti],[r]).items()}
  f.update({key:a[0,0] for key,a in evaluate_event_normal_source(source,label,[ti],[r]).items()})
  return f
 for name,points in probes.items():
  for stage,source in [('after',arrays)]+([('before',initial)] if name not in ('independent9','old6times') else []):
   vals,check=independent_residual_application(lambda ti,r:field(ti,r,source),coef,points)
   key=label+'_'+stage+'_'+name;reports[key]=check
   for k in ('points','strong','strong_source'):rows[key+'_'+k]=vals[k]
   print(json.dumps(dict(stage='CONSISTENT_SOURCE_CHECK',key=key,bulk=check['original_bulk']['max_abs'],source=check['original_source']['max_abs'])),flush=True)
write_npz(OUT/'independent_rows.npz',rows)
dump(OUT/'result.json',dict(input_sha256=pins,source_result_sha256=pin(OUT/'source_result.json'),report=report,
 independent_checks=reports,independent_rows=dict(sha256=pin(OUT/'independent_rows.npz'),bytes=(OUT/'independent_rows.npz').stat().st_size),
 before_independent_checks_reused_from=str(initializer/'result.json'),
 physical_admission=False,physical_guard=2e-10,
 NEXT_OPERAND='use complete event/outer/formation equations with unassigned physical amplitudes and all366 homogeneous data; numerical source response remains provisional'))
print(json.dumps(dict(stage='CONSISTENT_SOURCE_CHECKPOINT',radial_steps=steps,sha256=pin(OUT/'result.json'))),flush=True)
