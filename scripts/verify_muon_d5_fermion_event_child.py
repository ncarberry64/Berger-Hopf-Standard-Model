"""Verify immutable applications, reproducibility and retained nonpasses."""
from pathlib import Path
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from scripts.evaluate_muon_d5_fermion_event_child import pin,verified_inputs,BASE


def verify(first,second):
    first,second=Path(first),Path(second);verified_inputs()
    names=sorted(p.name for p in first.iterdir() if p.is_file())
    if names!=sorted(p.name for p in second.iterdir() if p.is_file()):raise ValueError('file sets differ')
    for name in names:
        if (first/name).read_bytes()!=(second/name).read_bytes():raise ValueError('materializations differ '+name)
    r=json.loads((first/'result.json').read_bytes())
    for rel,h in r['input_sha256'].items():
        if pin(ROOT/rel)!=h:raise ValueError('input changed '+rel)
    if pin(first/'application.npz')!=r['arrays']['sha256']:raise ValueError('constraint arrays changed')
    with np.load(first/'application.npz',allow_pickle=False) as z:
        if sorted(z.files)!=r['arrays']['keys']:raise ValueError('array identities changed')
        if any(z[k].dtype.hasobject or not np.isfinite(z[k]).all() for k in z.files):raise ValueError('nonfinite array')
        pivots=z['parent_incoming_h_pivot_columns']
        free=z['parent_incoming_remaining_h_columns']
        if pivots.shape!=(40,) or free.shape!=(3620,) or not np.array_equal(
                np.sort(np.r_[pivots,free]),np.arange(3660)):
            raise ValueError('incoming40 and remaining3620 do not retain the original h chart')
        if z['parent_incoming_incoming_datum_value_rows'].shape!=(40,40):
            raise ValueError('independent incoming datum equations lost')
        if z['parent_incoming_incoming_free_value_rows'].shape!=(40,3620):
            raise ValueError('free h equations lost')
        if (z['targeted_r17_times'].shape,z['targeted_r17_radii'].shape,
            z['targeted_r17_new_radial_indices'].shape,
            z['targeted_r17_higher_birth_free_lift'].shape)!=((6,),(17,),(14,),(17,14)):
            raise ValueError('one targeted t6/r17 chart or additional birth ports changed')
        if not np.array_equal(z['targeted_r17_shared_radial_indices'],[0,8,16]):
            raise ValueError('old radial nodes not explicitly retained')
    if r['parent_head']!='f9285d08a79c5b440168214d59b599b2097afee6':raise ValueError('ancestry changed')
    ranks=r['fermion_ranks']
    if (ranks['parent_h_coordinates'],ranks['combined_fixed_chart_rank_per_collar'],
        ranks['remaining_child_data_per_collar'],ranks['both_collars_with_shared_parent_h_free_coordinates'])!=(3660,480,2592,8844):
        raise ValueError('represented freedoms changed')
    if ranks['parent_h_state_selected_rank']!=0 or ranks['proven_gauge_dimension'] is not None:
        raise ValueError('unresolved state labeled selected or gauge')
    for key in ('physical_outer_residual','normal_profile_normalization','full_formation_residual',
                'physical_Cauchy_norm_residual','physical_trace_error_bound'):
        if r[key] is not None:raise ValueError('unexecuted physical quantity promoted '+key)
    if r['physical_guard']!=2e-10 or r['physical_admission'] or r['complete_physical_derivative']:
        raise ValueError('physical guard or scope changed')
    incoming=r['parent_incoming_child_application'];scope=r['parent_incoming_coordinate_scope']
    if (scope['incoming_data'],scope['remaining_h'],scope['total_parent_free_coordinates'])!=(40,3620,3660):
        raise ValueError('free incoming data replaced by a selected parent state')
    if scope['physical_incoming_data_selected'] or scope['physical_h_selected']:
        raise ValueError('unknown incoming or homogeneous physical data selected')
    if incoming['physical_d_in'] is not None or incoming['physical_h_selected'] or incoming['physical_admission']:
        raise ValueError('incoming coefficient response promoted to a physical state')
    if incoming['physical_guard']!=2e-10 or incoming['parent_free_coordinates']!=3660:
        raise ValueError('incoming guard or full parent freedom changed')
    if len(r['consumed_incoming_child_coefficients'])!=4:
        raise ValueError('one orientation family or eta collar lost from incoming child application')
    for row in r['consumed_incoming_child_coefficients']:
        name='candidate'+str(row['candidate'])+'_'+row['side']+'_homogeneous.npz'
        with np.load(BASE/'core/PARENT_INCOMING_CHILD_v1'/name,allow_pickle=False) as z:
            value=z['value_incoming_datum_coefficient'];source=z['value_incoming_datum_source_coefficient']
            if value.shape!=(3,3,384,40) or source.shape!=value.shape:
                raise ValueError('actual incoming40 child response layout changed')
            if not np.max(abs(value))>0 or not np.max(abs(source))>0:
                raise ValueError('actual nonnull incoming child response removed')
            if int(z['original_h_column_count'])!=3660 or z['h_pivot_columns'].shape!=(40,):
                raise ValueError('original parent homogeneous coordinates lost')
    chart=r['coordinate_chart_scope'];trial=r['targeted_radial_trial']
    if (chart['original_child_radial_nodes'],chart['original_remaining_child_data_per_collar'],
        chart['original_both_collars_shared_parent_free_coordinates'],
        chart['targeted_trial_radial_nodes'],chart['extra_birth_complex_coordinates_per_target_branch'])!=(3,2592,8844,17,112):
        raise ValueError('original chart counts confused with targeted refined birth ports')
    if chart['extra_birth_coordinates_selected'] or not chart['unconsumed_full_family_preserved']:
        raise ValueError('targeted trial discarded uncomputed physical data or full family')
    if trial['physical_guard']!=2e-10 or trial['physical_admission'] or len(trial['reports'])!=16:
        raise ValueError('targeted trial scope or admission changed')
    nonzero_cases=0
    for row in trial['reports']:
        if row['higher_birth_coordinates_unassigned']!=112 or not row['other_fullcarrier_ports_unassigned']:
            raise ValueError('higher birth or other full-carrier data assigned')
        if row['physical_admission'] or len(row['sources'])!=9:
            raise ValueError('targeted source directions lost or physically admitted')
        source=row['sources'][0]
        if source['before_value_max']>0:
            nonzero_cases+=1
            if not (2e-10<source['after_value_max']<source['before_value_max'] and
                    2e-10<source['after_source_max']<source['before_source_max']):
                raise ValueError('targeted improvement or its original nonpass removed')
    if nonzero_cases!=12:
        raise ValueError('actual nonzero weak8 consumed comparisons changed')
    failures=r['original_consumed_checks']['reports']
    if not max(x['independent_original_value_max'] for x in failures)>1e8:
        raise ValueError('recorded original child nonpass removed')
    if not max(x['independent_original_source_max'] for x in failures)>1e10:
        raise ValueError('recorded original source nonpass removed')
    return dict(schema='bhsm.fermion-event-child-verification.v1',byte_identical=True,
        arrays_sha256=r['arrays']['sha256'],result_sha256=pin(first/'result.json'),
        represented_parent_h=3660,complex_event_corner_rank_per_collar=480,
        remaining_joint_coordinates_both_collars=8844,free_parent_incoming_data=40,
        remaining_parent_h=3620,targeted_radial_nodes=17,
        extra_birth_ports_per_target_branch=112,targeted_trial_still_nonpass=True,
        physical_admission=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);a=p.parse_args()
    print(json.dumps(verify(a.first,a.second),sort_keys=True,indent=2))
