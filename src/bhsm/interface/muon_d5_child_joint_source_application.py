"""Append only changed joint-map gauge source to the completed child cell."""
from __future__ import annotations
import numpy as np

from .muon_d5_child_spatial_source_application import evaluate_child_spatial_source
from .muon_d5_child_same_direction_application import _differential_columns
from .muon_d5_event_bundle_incidence import original_event_coefficients
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def append_joint_child_source(history,child,previous,spatial,joint):
    """Reuse old gauge source arrays and append linear map-dependent deltas.

    Both joint nonlinear value-map families remain unselected. H4 changes
    are owned by the once-only intrinsic seam; an original bulk derivative
    evaluates their absence explicitly. No chart/value solve is repeated.
    """
    indices=tuple(map(int,joint['initial_candidate_index']))
    field=np.zeros_like(spatial['child_raw_field_source_corrections'])
    free=np.zeros_like(spatial['child_raw_field_free_rotation_coefficients'])
    Hcols=[]
    for j,index in enumerate(indices):
        new=np.asarray(joint['child_raw_field_Higgs_source_correction'][j])
        nx=np.asarray(joint['child_raw_field_Higgs_free_rotation_phase_coefficients'][j])
        field[index,168:180]=new[168:180]-spatial['child_raw_field_source_corrections'][index,168:180]
        free[index,168:180]=nx[168:180,:6]-spatial['child_raw_field_free_rotation_coefficients'][index,168:180]
        if np.any(nx[168:180,6]!=0):raise ValueError('phase changes a bulk gauge source and needs an additional application')
        h=np.zeros((268,8));h[260:264]=np.column_stack((new[260:264],nx[260:264]))
        Hcols.append(h)
    increment,receipt=evaluate_child_spatial_source(history,child,field,free,candidate_indices=indices)
    out=dict(child_joint_candidate_indices=np.asarray(indices),
        child_joint_raw_source_corrections=joint['child_raw_field_Higgs_source_correction'],
        child_joint_raw_free_source_coefficients=joint['child_raw_field_Higgs_free_rotation_phase_coefficients'])
    changed=0.
    for index in indices:
      for sign in ('plus','minus'):
       for branch in ('particle','conjugate'):
        tag='candidate'+str(index)+'_child_'+sign+'_'+branch+'_'
        for key in ('time','normal','body'):
            name=tag+key+'_spatial_field_additional_source64'
            delta=increment[name];old=previous[name]
            total=np.concatenate((old+delta,np.zeros_like(old[:1])),axis=0)
            out[tag+key+'_joint_field_additional_source64']=total
            out[tag+key+'_joint_field_exact_increment_source64']=delta
            out[tag+key+'_corrected_particular_source64']=previous[tag+key+'_corrected_particular_source64']+delta[0]
            changed=max(changed,float(np.max(abs(delta))))
    # H is intrinsically/seam-owned in the original D5 action. Evaluate
    # its actual source columns rather than append an invented bulk mass.
    h=np.concatenate(Hcols,axis=1);count=h.shape[1]
    t,r=child['original_child_coordinates']
    c=original_event_coefficients(history,float(t),[r],side='child',directions=dict(
        raw=h,parent=np.zeros((268,count)),references=np.zeros((2,268,count))))
    d=_differential_columns(c,full_d5_localized_lepton_trace(),count)
    proof=[]
    for eps in (1,-1):
      for j in range(count):
       for branch in ('particle','conjugate'):
        proof.extend(float(np.max(abs(d[eps][j]['first']['blocks'][branch][key]))) for key in ('time','radial','body'))
    if max(proof)!=0:raise ValueError('Higgs changes this bulk owner; seam-only accounting must be reconsidered')
    out['original_Higgs_bulk_source_columns268']=h
    out['original_Higgs_bulk_source_maxima']=np.asarray(proof)
    report=dict(classification='APPENDED_FINAL_JOINT_MAP_CHILD_SOURCE_WITHOUT_CHART_OR_VALUE_REPLAY',
        candidate_indices=list(indices),original_callback_gauge_increment_max=changed,
        original_bulk_Higgs_source_exact_max=max(proof),Higgs_columns_evaluated=count,
        phase_bulk_gauge_source_exact_max=0.,original_pure_gauge_receipt=receipt,
        free_map_source_coordinates=7,child_normal_source_and_free_normal_rate_reused=True,
        field_extension='constant original own raw spatial wall-lift source coefficients through the child cell; extra raw time and velocity source held zero only for the provisional finite extension',
        inherited_additional_field_source_unassigned=True,no_extra_bulk_Higgs_mass=True,
        normal_chart_recomputed=False,child_value_operator_solved=False,child_D5_solution_residual=None,
        physical_map_selected=False,complete_physical_derivative=False,physical_admission=False,physical_guard=2e-10,
        NEXT_OPERAND='consume these final-map child operator/source coefficients with ordered event maps, once-only Higgs seam, free normal rates, and original outer/formation equations')
    return out,report
