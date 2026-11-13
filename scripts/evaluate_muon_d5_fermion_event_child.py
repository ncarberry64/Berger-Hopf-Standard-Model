"""Reassemble the executed fermion event/corner constraints from saved fields.

All field applications and failed trials are immutable inputs. This consumer
does not rerun the Cauchy solves, pole transport, native or compatibility work.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.retained_response.finite_time_response import write_npz
BASE=ROOT/'artifacts/muon_d5_fermion_event_child_20261019'
CORES=('RAW_WALL_EVENT_v1','RAW_EVENT_TEMPORAL_v1','CHILD_CELL_v1','CHILD_CELL_v2',
 'CHILD_COEFFICIENT_PROBES_v1','CHILD_CORNER_v1','EVENT_CHILD_v1','EVENT_CHILD_CORNER_v1',
 'PARENT_POLE_SHORT_v1','PARENT_LEPTON_POLE_GLOBAL_v1','PARENT_CHARACTERISTIC_v1',
 'PARENT_INCOMING_CHILD_v1','CHILD_RADIAL17_v1')


def pin(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def dump(path,value):
    Path(path).write_bytes((json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())


def load(path):
    with np.load(path,allow_pickle=False) as z:
        return {k:z[k].copy(order='K') for k in z.files}


def verified_inputs():
    pins={}
    for name in CORES:
        p=BASE/'core'/name/'canonical_binding.json';r=json.loads(p.read_bytes())
        if r['application']!=name:raise ValueError('application identity changed')
        for group in ('input_sha256','files_sha256'):
            for rel,h in r[group].items():
                path=Path(rel)
                if path.is_absolute() or '..' in path.parts:raise ValueError('nonrepository input '+rel)
                if pin(ROOT/path)!=h:raise ValueError('executed application changed '+rel)
                if rel in pins and pins[rel]!=h:raise ValueError('conflicting input '+rel)
                pins[rel]=h
        pins[p.relative_to(ROOT).as_posix()]=pin(p)
    return pins


def run(output):
    output=Path(output).resolve()
    if output.exists():raise FileExistsError('preserve previous applications')
    pins=verified_inputs();core=BASE/'core'
    corner=load(core/'CHILD_CORNER_v1/application.npz')
    # Full coordinate index metadata is retained; every response column is
    # a coordinate derivative, never a choice of unknown physical data.
    metadata=load(core/'CHILD_CELL_v2/metadata.npz')
    report=json.loads((core/'EVENT_CHILD_CORNER_v1/result.json').read_bytes())
    data_indices={}
    for label in ('plus_particle','plus_conjugate','minus_particle','minus_conjugate'):
        for block in range(int(metadata[label+'_block_count'])):
            p=label+'_block'+str(block)+'_'
            with np.load(core/'CHILD_CELL_v2'/(label+'_block'+str(block)+'.npz'),allow_pickle=False) as z:
                data_indices[p]=z[p+'data_indices']
    out={};rows=[]
    for row in report['reports']:
        name='candidate'+str(row['candidate'])+'_'+row['label']
        with np.load(core/'EVENT_CHILD_CORNER_v1'/(name+'.npz'),allow_pickle=False) as z:
            data=z['corner_input_value'];dx=z['corner_input_source'];side=row['label'].split('_')[0]
            values=[];sources=[]
            for family in range(3):
                for b,branch in enumerate(('particle','conjugate')):
                    label=side+'_'+branch;sl=slice((2*family+b)*64,(2*family+b+1)*64)
                    d=data[:,sl].reshape(512,-1);s=dx[:,sl].reshape(512,-1)
                    for block in range(int(metadata[label+'_block_count'])):
                        p=label+'_block'+str(block)+'_'
                        # Independent data-index metadata belongs to the
                        # saved full characteristic field, not a rank quotient.
                        indices=data_indices[p];C=corner[p+'corner']
                        Cx=corner[p+'corner_source'][row['source_slot']]
                        values.append(C@d[indices]);sources.append(C@s[indices]+Cx@d[indices])
            a=np.concatenate(values);ax=np.concatenate(sources)
            event=z['original_event_value_rows'];eventx=z['original_event_supplied_source_rows']
            if a.shape[0]!=384 or event.shape[0]!=96:raise ValueError('original row counts changed')
            prefix=name+'_'
            out[prefix+'event_value_rows']=event.copy(order='K')
            out[prefix+'event_supplied_source_rows']=eventx.copy(order='K')
            out[prefix+'corner_value_rows']=a;out[prefix+'corner_supplied_source_rows']=ax
            out[prefix+'original_parent_column_indices']=z['original_parent_column_indices']
            if row['event_h_rank'] is not None:
                singular=z['event_parent_h_singular_values']
                if np.sum(singular>1e-12)!=78:raise ValueError('h block rank changed')
                out[prefix+'event_parent_h_singular_values']=singular
            rows.append(dict(candidate=row['candidate'],label=row['label'],
                event_value_max=float(np.max(abs(event))),event_supplied_source_max=float(np.max(abs(eventx))),
                corner_value_max=float(np.max(abs(a))),corner_supplied_source_max=float(np.max(abs(ax))),
                nonnull_child_field_max=float(np.max(abs(z['child_value']))),
                nonnull_child_source_max=float(np.max(abs(z['child_source']))),
                h_block_rank=row['event_h_rank']))
    incoming=json.loads((core/'PARENT_INCOMING_CHILD_v1/result.json').read_bytes())
    incoming_equations=load(core/'PARENT_INCOMING_CHILD_v1/equations.npz')
    for key,value in incoming_equations.items():
        out['parent_incoming_'+key]=value
    incoming_coefficients=[]
    for row in incoming['reports']:
        name='candidate'+str(row['candidate'])+'_'+row['side']+'_homogeneous.npz'
        with np.load(core/'PARENT_INCOMING_CHILD_v1'/name,allow_pickle=False) as z:
            value=z['value_incoming_datum_coefficient']
            source=z['value_incoming_datum_source_coefficient']
            if value.shape!=(3,3,384,40) or source.shape!=value.shape:
                raise ValueError('actual40 incoming child coefficient layout changed')
            incoming_coefficients.append(dict(candidate=row['candidate'],side=row['side'],
                incoming_coordinates=value.shape[-1],remaining_h=row['remaining_h'],
                original_h_columns=int(z['original_h_column_count']),
                nonnull_value_max=float(np.max(abs(value))),
                nonnull_source_max=float(np.max(abs(source)))))
    radial=json.loads((core/'CHILD_RADIAL17_v1/result.json').read_bytes())
    radial_chart=load(core/'CHILD_RADIAL17_v1/chart.npz')
    for key in ('times','radii','shared_radial_indices','new_radial_indices','higher_birth_free_lift'):
        out['targeted_r17_'+key]=radial_chart[key]
    output.mkdir(parents=True);write_npz(output/'application.npz',out)
    for rel in ('scripts/evaluate_muon_d5_fermion_event_child.py','scripts/verify_muon_d5_fermion_event_child.py'):
        pins[rel]=pin(ROOT/rel)
    previous=ROOT/'artifacts/muon_d5_two_sided_event_20261019/core/TWO_SIDED_ROWS_v2/application.npz'
    pins[previous.relative_to(ROOT).as_posix()]=pin(previous)
    result=dict(schema='bhsm.fermion-event-child-consumption.v1',
        parent_head='f9285d08a79c5b440168214d59b599b2097afee6',input_sha256=pins,
        arrays=dict(sha256=pin(output/'application.npz'),keys=sorted(out)),executed_rows=rows,
        fermion_ranks=dict(number_field='complex',event_rows_per_collar=96,necessary_C1_corner_rows_per_collar=384,
            combined_fixed_chart_rank_per_collar=480,child_data_per_collar=3072,remaining_child_data_per_collar=2592,
            parent_h_coordinates=3660,event_h_block_rank=78,event_h_block_kernel=3582,
            parent_h_state_selected_rank=0,joint_free_coordinates_per_collar=6252,
            both_collars_with_shared_parent_h_free_coordinates=8844,proven_gauge_dimension=None),
        bosonic_compatibility=dict(number_field='real',rank=17,chart=555,kernel=538,reused_without_resolve=True),
        parent_incoming_child_application=incoming,
        consumed_incoming_child_coefficients=incoming_coefficients,
        parent_incoming_coordinate_scope=dict(incoming_data=40,remaining_h=3620,
            total_parent_free_coordinates=3660,physical_incoming_data_selected=False,
            physical_h_selected=False,
            rule='40 original incoming equations express40 h pivots in terms of40 still-free incoming data; no physical input dimension is removed'),
        targeted_radial_trial=radial,
        coordinate_chart_scope=dict(original_child_radial_nodes=3,original_child_time_nodes=6,
            original_child_data_per_collar=3072,original_event_corner_rank_per_collar=480,
            original_remaining_child_data_per_collar=2592,
            original_both_collars_shared_parent_free_coordinates=8844,
            targeted_trial_radial_nodes=17,targeted_trial_time_nodes=6,
            targeted_trial_family='original MUON family index1, weak8, both charge copies and eta collars',
            extra_birth_radial_nodes_per_target_branch=14,
            extra_birth_complex_coordinates_per_target_branch=112,
            extra_birth_coordinates_selected=False,
            trial_rule='olddegree2 birth embedding is a coordinate partial; extra112 birth ports per targetbranch remain free; original3rho chart counts are not promoted to a full17rho family count',
            unconsumed_full_family_preserved=True),
        original_consumed_checks=json.loads((core/'EVENT_CHILD_CORNER_v1/ORIGINAL_CHECKS_v2/result.json').read_bytes()),
        previous_consumed_checks=json.loads((core/'EVENT_CHILD_v1/ORIGINAL_CHECKS_v1/result.json').read_bytes()),
        original_parent_nonpasses=dict(independent9_value=0.00029703256213433525,
            independent9_source=0.011468949235373024,original6times_value=0.0005261351330086378,
            original6times_source=0.020666003340392133,
            scope='saved original residual operators on all h columns retained; not a selected physical state error'),
        source_scope='same corrected sides, seven map directions and child normal-rate field responses; independent state/base and remaining physical contacts retained',
        equation='Gamma0_child-U_R (Gamma0_parent composed with F_B)=0 on the proved raw colorless96 wall carrier',
        Jacobi='deltaGamma_child-deltaU_R Gamma_parent-U_R(deltaGamma_parent+dGamma_parent total_deltaF_B)=0',
        remaining=['fullcap incidence and color288 bundle map','physical parent Cauchy/outer incoming sections from the adopted preparation and interacting transition',
            'unbound child birth and future incoming data','normal integrals and shared-g amplitude selection',
            'complete Higgs/time constraint curvature, Euler/endpoints and interacting formation Hessian',
            'native/reference/state, physical-unit and cutoff obligations and complete source/domain derivatives'],
        global_spin_sign=None,orientation_family_selected=False,local_native_accounting_changed=False,
        physical_outer_residual=None,normal_profile_normalization=None,full_formation_residual=None,
        physical_Cauchy_norm_residual=None,physical_trace_error_bound=None,
        physical_guard=2e-10,complete_physical_derivative=False,physical_admission=False,
        NEXT_OPERAND='supply the actual same-action Cauchy and incoming characteristic data, complete fullcap/formation incidence, and consume them in the retained child family; target demonstrated event-driven boundary-layer errors without deleting free columns or selecting a vacuum')
    dump(output/'result.json',result)
    return dict(arrays_sha256=result['arrays']['sha256'],result_sha256=pin(output/'result.json'),
        event_complex_rank=96,corner_complex_rank=384,parent_h_selected=False,physical_admission=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(run(a.output),sort_keys=True,indent=2))
