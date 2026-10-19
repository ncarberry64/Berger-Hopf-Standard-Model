"""Verify exact saved D5 applications and separate numerical/physical scope."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from hashlib import sha256
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_complement_bulk_response import load_groups,pin

def verify(first,second):
    first,second=Path(first),Path(second)
    names=sorted(p.name for p in first.iterdir() if p.is_file())
    if names!=sorted(p.name for p in second.iterdir() if p.is_file()):raise ValueError('materialized file sets differ')
    for name in names:
        if (first/name).read_bytes()!=(second/name).read_bytes():raise ValueError('materializations differ: '+name)
    record=json.loads((first/'result.json').read_bytes());core=json.loads((first/'core_result.json').read_bytes())
    if pin(first/'core_result.json')!=record['core_record_sha256']:raise ValueError('core record changed')
    for rel,h in record['input_sha256'].items():
        if pin(ROOT/rel)!=h:raise ValueError('published input changed '+rel)
    for name,md in record['archives'].items():
        if pin(first/name)!=md['sha256']:raise ValueError('consumer archive changed '+name)
    if pin(first/'independent_rows.npz')!=record['independent_rows']['sha256']:raise ValueError('independent rows changed')
    arrays=load_groups(first,core['archives'])
    nt=len(arrays['times']);B=arrays['wall_selected_Bhat'];Bx=arrays['wall_selected_Bhat_source']
    U=arrays['wall_geometric_right'];Ux=arrays['wall_geometric_right_source']
    Ui=np.linalg.inv(U);Uix=-Ui@Ux@Ui
    collar=collarx=hom=homx=0.
    for label in ('plus_seed','minus_seed','minus_LR','minus_RL'):
        V=arrays[label+'_value'][0];Vx=arrays[label+'_source'][0]
        collar=max(collar,float(np.max(abs(V-arrays[label+'_wall']))))
        collarx=max(collarx,float(np.max(abs(Vx-arrays[label+'_wall_source']))))
    for side in ('plus','minus'):
        Q=arrays['wall_'+side+'_complement_basis'];Qx=arrays['wall_'+side+'_complement_basis_source']
        if Q.shape!=(nt,384,366):raise ValueError('homogeneous space changed')
        if side=='minus':Q,Qx=Ui@Q,Uix@Q+Ui@Qx
        hom=max(hom,float(np.max(abs(B@Q))))
        homx=max(homx,float(np.max(abs(Bx@Q+B@Qx))))
    if max(collar,collarx,hom,homx)>2e-10:raise ValueError('finite collar identity failed')
    if record['physical_guard']!=2e-10 or record['physical_admission'] is not False:raise ValueError('admission scope changed')
    consumed=record['consumed']
    for key in ('event_equations_solved','U_R_assigned','base_incidence_F_B_assigned',
        'parent_child_numeric_rho_identified','homogeneous_coordinates_assigned',
        'physical_outer_equations_solved','mechanical_formation_equations_solved','physical_admission'):
        if consumed[key] is not False:raise ValueError('unexecuted physical equation promoted: '+key)
    child=consumed['child_fitted_operator_application']
    if child['minimum_evaluated_child_time']<0:raise ValueError('pre-birth coefficient evaluation')
    if child['child_D5_solution_residual'] is not None:raise ValueError('operator application called child solution')
    if child['event_residual'] is not None:raise ValueError('unknown event data assigned')
    return dict(schema='bhsm.d5-valid-domain-verification.v1',byte_identical=True,file_count=len(names),
        result_sha256=pin(first/'result.json'),core_sha256=pin(first/'core_result.json'),
        collar_value_max=collar,collar_source_max=collarx,homogeneous_BQ_max=hom,
        homogeneous_source_BQ_max=homx,homogeneous_coordinates_per_node=366,
        child_minimum_evaluated_time=child['minimum_evaluated_child_time'],
        physical_guard=2e-10,physical_admission=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path)
    a=p.parse_args();print(json.dumps(verify(a.first,a.second),sort_keys=True,indent=2))
