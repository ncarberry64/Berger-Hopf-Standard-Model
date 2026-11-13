"""Verify the saved partial event application without promoting its domain."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def pin(p):return sha256(p.read_bytes()).hexdigest()

def verify(first,second):
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from scripts.evaluate_muon_d5_event_matching import cached,BASE
    first,second=Path(first),Path(second)
    names=sorted(p.name for p in first.iterdir() if p.is_file())
    if names!=sorted(p.name for p in second.iterdir() if p.is_file()):raise ValueError('materialized file sets differ')
    for name in names:
        if (first/name).read_bytes()!=(second/name).read_bytes():raise ValueError('materializations differ '+name)
    r=json.loads((first/'result.json').read_bytes())
    if r['parent_head']!='bdd993d9afe33f8cbe3181ba452ffac5e5d85976':raise ValueError('ancestry changed')
    for rel,h in r['input_sha256'].items():
        if pin(ROOT/rel)!=h:raise ValueError('input changed '+rel)
    for folder in ('formation_core','affine_core','affine6_core','source_core','source6_core',
            'consistent_source2_core','consistent_source4_core','represented_source_core'):
        cached(BASE/folder)
    if pin(first/'application.npz')!=r['arrays']['sha256']:raise ValueError('event arrays changed')
    with np.load(first/'application.npz',allow_pickle=False) as z:
        if sorted(z.files)!=r['arrays']['keys']:raise ValueError('array keys changed')
        for key in z.files:
            if z[key].dtype.hasobject or not np.isfinite(z[key]).all():raise ValueError('nonfinite/non-numeric array '+key)
        for side in ('plus','minus'):
            if z[side+'_new_partial_Xi_h_wall_source'].shape!=(384,3660):
                raise ValueError('homogeneous wall coordinate/source coefficient omitted')
    f=r['formation_tangency']
    if f['normal_coordinate_Jacobian_rank']!=2:raise ValueError('normal chart rank changed')
    if f['source_pivot_unknowns']!=['parent_psi','child_psi']:raise ValueError('pivot selection changed')
    if not f['supplied_Xi_constraint_before_max']>f['original_callback_corrected_Xi_constraint_max']>0:
        raise ValueError('recorded unresolved compatibility audit changed')
    for name in ('physical_event_residual','physical_outer_residual','normal_profile_normalization',
            'full_formation_residual','original_physical_admission_norm_residual'):
        if r[name] is not None:raise ValueError('unexecuted physical equation promoted '+name)
    for name in ('normalized_physical_child_reconstructed','base_map_selected','middle_lift_selected',
        'complete_physical_derivative','physical_admission','local_native_accounting_changed','background_or_value_response_recomputed'):
        if r[name] is not False:raise ValueError('scope changed '+name)
    if r['physical_guard']!=2e-10 or r['remaining_parent_homogeneous_coordinates']!=3660:
        raise ValueError('guard or boundary freedom changed')
    for side in ('plus','minus'):
        row=r['actual_partial_event_source_consumption'][side+'_homogeneous']
        if row['new_bulk_source_response'] is not None or row['h_values_assigned'] or row['h_source_values_assigned']:
            raise ValueError('unknown physical homogeneous source assigned')
    source=r['represented_source_application']['report']
    if source['source_original_coefficient_offblock_max']!=0 or not source['same_represented_source_nodes_in_stages_and_dense_output']:
        raise ValueError('source carrier or original-rho stage/evaluation consistency changed')
    if not r['original_value_history_bitwise_identical'] or not r['source_direction_bitwise_identical']:
        raise ValueError('background/source identity changed')
    return dict(schema='bhsm.d5-event-matching-verification.v1',byte_identical=True,file_count=len(names),
        result_sha256=pin(first/'result.json'),arrays_sha256=pin(first/'application.npz'),
        unscaled_compatibility_source_before=f['supplied_Xi_constraint_before_max'],
        unscaled_compatibility_source_after=f['original_callback_corrected_Xi_constraint_max'],
        compatibility_norm_scope=r['formation_tangency_norm_scope'],
        original_callback_reconstruction_max=f['original_callback_source_reconstruction_max'],
        remaining_parent_homogeneous_coordinates=3660,physical_guard=2e-10,physical_admission=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path)
    a=p.parse_args();print(json.dumps(verify(a.first,a.second),sort_keys=True,indent=2))
