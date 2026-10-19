"""Affected source rows at the jointly solved connection/Higgs value maps."""
from __future__ import annotations
import numpy as np
from .muon_d5_spatial_bundle_application import (
    spatial_connection_row,spatial_rotation_jacobian,known_spin_gauge_factor,
)
from .muon_d5_higgs_temporal_bundle_application import (
    complex_higgs,real_higgs,temporal_bundle_jet,
)
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation


def apply_joint_map_sources(parent_coefficients,child_coefficients,joint,
        previous_spatial,previous_higgs,wall):
    """Solve16 original field-source rows, preserving7 map-source columns.

    The inputs contain both corrected normal directions but none of the old
    compensating spatial/Higgs source corrections. New totals and exact
    increments relative to the saved older map applications are returned.
    """
    p,c=parent_coefficients,child_coefficients
    Ap,Ac=(np.asarray(a['gauge_connection_material'][0,2:]) for a in (p,c))
    Apx,Acx=(np.asarray(a['gauge_connection_material_first'][0,0,2:]) for a in (p,c))
    if any(np.any(a.imag!=0) for a in (Ap,Ac,Apx,Acx)):
        raise ValueError('real original coefficient sources required')
    Ap,Ac,Apx,Acx=(a.real for a in (Ap,Ac,Apx,Acx))
    Hp,Hc=(complex_higgs(a['intrinsic_H_realified']) for a in (p,c))
    Hpx,Hcx=(complex_higgs(a['intrinsic_H_realified_first'][0]) for a in (p,c))
    B=previous_spatial['child_spatial_wall_trace_pivot'];indices=previous_spatial['child_spatial_wall_field_raw_indices']
    generators=higgs_u2_real_representation()['complex_generators'];J2=np.sqrt(2)*generators[:3]
    A0p,A0c,A0px,A0cx=(np.einsum('a,aij->ij',a,generators) for a in
        (p['gauge_connection_material'][0,0],c['gauge_connection_material'][0,0],
         p['gauge_connection_material_first'][0,0,0],c['gauge_connection_material_first'][0,0,0]))
    k,kx=(complex(wall[a]) for a in ('material_clock_differential','material_clock_differential_first'))
    values=[];reports=[]
    for j,index in enumerate(joint['initial_candidate_index']):
        index=int(index);O,R,K,U=(joint[a][j] for a in ('base_rotation','gauge_rotation','gauge_SU2_lift','Higgs_middle'))
        value=spatial_connection_row(Ap,Ac,O,R);load=spatial_connection_row(Apx,Acx,O,R)
        target=Ac-value.reshape(3,4);J=spatial_rotation_jacobian(target)
        delta_field=np.linalg.solve(B,-load);free_field=-np.linalg.solve(B,J)
        Hload=Hcx-U@Hpx;delta_H=-Hload
        raw=np.zeros(268);raw[indices]=delta_field;raw[260:264]=real_higgs(delta_H)
        free=np.zeros((268,7));free[indices,:6]=free_field
        Ufree=np.zeros((7,2,2),complex);Ufree[3:6]=np.array([a@U for a in J2]);Ufree[6]=1j*U
        free[260:264]=np.column_stack([real_higgs(a@Hp) for a in Ufree])
        after=np.r_[load+B@delta_field,real_higgs(Hload+delta_H)]
        jet=temporal_bundle_jet(A0p,A0c,U,k,Ap_first=A0px,Ac_first=A0cx,kappa_first=kx,U_first=np.zeros((2,2),complex))
        middle=known_spin_gauge_factor(O,R)
        oldraw=previous_spatial['child_raw_field_source_corrections'][index]+previous_higgs['child_Higgs_raw_source_corrections'][index]
        out=dict(initial_candidate_index=np.array(index),base_rotation=O,gauge_rotation=R,
            gauge_SU2_lift=K,Higgs_middle=U,Higgs_unit_phase=joint['Higgs_unit_phase'][j],
            original_spatial_value_rows=value,original_Higgs_value_rows=Hc-U@Hp,
            original_source_rows_before=np.r_[load,real_higgs(Hload)],original_source_rows_after=after,
            child_raw_field_Higgs_source_correction=raw,
            child_raw_field_Higgs_source_increment=raw-oldraw,
            child_raw_field_Higgs_free_rotation_phase_coefficients=free,
            temporal_bundle_time=jet['time'],temporal_bundle_time_first_particular=jet['time_first'],
            temporal_original_matrix_row=jet['original_row'],temporal_original_matrix_first_row=jet['original_first_row'],
            **middle)
        values.append(out)
        reports.append(dict(initial_candidate_index=index,spatial_value_max=float(np.max(abs(value))),
            Higgs_value_max=float(np.max(abs(Hc-U@Hp))),source_before_max=float(np.max(abs(out['original_source_rows_before']))),
            source_after_max=float(np.max(abs(after))),source_increment_max=float(np.max(abs(raw-oldraw))),
            known_temporal_bundle_row_max=float(np.max(abs(jet['original_row']))),
            known_temporal_bundle_source_row_max=float(np.max(abs(jet['original_first_row']))),
            original_field_source_pivot_rank=16,map_source_coordinates_free=7,physical_map_selected=False))
    arrays={key:np.array([a[key] for a in values]) for key in values[0]}
    report=dict(classification='EXECUTED_ORIGINAL16_SOURCE_ROWS_AT_JOINT_NONLINEAR_VALUE_MAPS',
        original_equations='full12 spatial connection rows plus4 real Higgs-section rows',
        candidates=reports,background_value_or_geometry_changed=False,
        all7_rotation_phase_source_coordinates_retained=True,
        temporal_scope='local original Higgs-representation connection jet with moving clock; not full physical Spin/normal/outer completion',
        source_extension='additional raw wall-gauge and intrinsic-H source coefficients constant in the finite child cell, extra coordinate-time derivative zero; provisional initializer only',
        physical_admission=False,parent_homogeneous_coordinates_retained=3660,
        full_SM_phase_lift_and_strong_factor_unassigned=True,normal_profile_normalization=None,
        NEXT_OPERAND='consume new totals or exact increments only in affected existing child gauge/body and once-only intrinsic Higgs seam applications, retaining free columns and unresolved outer/reference/normal equations')
    return arrays,report
