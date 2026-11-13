"""Assemble executed two-sided field constraints and known weak action rows.

The fixed-E1 chart has no physical outer or fermion-state selection. Its
kernel is a coordinate kernel, never a declaration of gauge freedom.
Uncomputed action terms are listed, not filled with numerical zeroes.
"""
from __future__ import annotations
import numpy as np
from .muon_d5_higgs_temporal_bundle_application import complex_higgs,real_higgs


def realified_higgs_matrix(matrix):
    U=np.asarray(matrix,complex)
    if U.shape!=(2,2):raise ValueError('actual associated Higgs map required')
    return np.column_stack([real_higgs(U@complex_higgs(e)) for e in np.eye(4)])


def combine_constraint_gradient(C13_gradient,Higgs_middle,Higgs_free_field_sources):
    """Full17 fixed-point rows in chart546+H_parent4+H_child4+phase1.

    The existing six rotation coordinates are columns540:546; the returned
    Higgs source response supplies the negative map derivative there.
    Its seventh column is the independent Higgs-representation phase.
    Moving event-point contacts are independent additional ports.
    """
    A=np.asarray(C13_gradient,complex);F=np.asarray(Higgs_free_field_sources)
    if A.shape!=(13,546) or F.shape!=(4,7):raise ValueError('full13 chart and7 map source columns required')
    J=np.zeros((17,555),complex);J[:13,:546]=A
    J[13:,546:550]=-realified_higgs_matrix(Higgs_middle)
    J[13:,550:554]=np.eye(4);J[13:,540:546]=-F[:,:6];J[13:,554]=-F[:,6]
    return J


def explicit_constraint_kernel(gradient,pivot_columns):
    """Retain every free coordinate; solve only the declared square pivot."""
    J=np.asarray(gradient);p=np.asarray(pivot_columns,int)
    if J.ndim!=2 or len(p)!=len(J) or len(set(p))!=len(p):raise ValueError('one named pivot per actual row required')
    free=np.setdiff1d(np.arange(J.shape[1]),p)
    K=np.eye(J.shape[1],dtype=complex)[:,free]
    K[p]=-np.linalg.solve(J[:,p],J[:,free])
    return K,free


def assemble_two_sided_rows(constraint_append,joint_sources,historical_Higgs):
    """Consume both corrected directions and the actual same-action two-jets."""
    out={};reports=[]
    for i,index in enumerate(joint_sources['initial_candidate_index']):
        index=int(index);p='candidate_'+str(index)+'_'
        raw=constraint_append[p+'actual_own_raw_sources']
        if raw.shape!=(2,268):raise ValueError('both actual corrected original directions required')
        U=joint_sources['Higgs_middle'][i]
        F=joint_sources['child_raw_field_Higgs_free_rotation_phase_coefficients'][i,260:264]
        J=combine_constraint_gradient(constraint_append[p+'gradient'],U,F)
        xi=np.r_[constraint_append[p+'actual_chart_source'],raw[0,260:264],raw[1,260:264],0.]
        source_rows=J@xi
        values=np.r_[constraint_append[p+'value'],real_higgs(joint_sources['original_Higgs_value_rows'][i])]
        pivots=np.r_[constraint_append[p+'constraint_pivot_columns'],np.arange(550,554)]
        kernel,free=explicit_constraint_kernel(J,pivots)
        # Same source state and its independent phase-rate placements,
        # evaluated once by the original action owner, are reused exactly.
        known=np.r_[constraint_append[p+'parent_known_geometry_actual_source_weak_Jacobi_contacts'][:,2],
                    constraint_append[p+'child_known_geometry_actual_source_weak_Jacobi_contacts'][:,2]]
        area=np.r_[constraint_append[p+'parent_surface_per_gamma_actual_source_weak_Jacobi_contacts'][:,2],
                   constraint_append[p+'child_surface_per_gamma_actual_source_weak_Jacobi_contacts'][:,2]]
        area0=np.r_[constraint_append[p+'parent_surface_per_gamma_normal_first_action_coefficients'],
                    constraint_append[p+'child_surface_per_gamma_normal_first_action_coefficients']]
        M=constraint_append[p+'normal_constraint_multiplier_complete_source']
        C=constraint_append[p+'normal_constraint_multiplier_first_variation_coefficient']
        weak=np.c_[known,area,area0,M,C]
        out.update({p+k:v for k,v in dict(full17_values=values,full17_source=source_rows,
            full17_gradient=J,full17_chart_source=xi,full17_pivot_columns=pivots,
            full17_free_columns=free,full17_kernel=kernel,full17_kernel_original_rows=J@kernel,
            known_normal_weak_source_affine_coefficients=weak,
            Higgs_independent_total_time_field_response_coefficients=historical_Higgs['Higgs_total_time_pullback_coefficients'][index]).items()})
        reports.append(dict(candidate_index=index,executed_constraint_rows=17,chart_dimension=555,
            exact_pivot_rank=17,remaining_coordinate_kernel_dimension=len(free),
            pivot_condition=float(np.linalg.cond(J[:,pivots])),
            constraint_value_max=float(np.max(abs(values))),constraint_source_max=float(np.max(abs(source_rows))),
            kernel_row_max=float(np.max(abs(J@kernel))),known_weak_source_row_count=4,
            direct_h_constraint_rank=0,parent_h_coordinates_retained=3660,
            complete_physical_constraint_rank=None,kernel_classified_as_gauge=False))
    return out,dict(classification='EXECUTED_TWO_SIDED17_ROW_ASSEMBLY_AND_KNOWN_WEAK_ACTION_CONTACT',
        candidates=reports,known_weak_column_order='1,gamma,delta_gamma,lambda13,delta_lambda13',
        known_weak_equation='b_geometry+gamma*b_area_source+delta_gamma*b_area_value+D(Cpsi.T)*lambda+Cpsi.T*delta_lambda+uncomputed_terms',
        known_weak_scope='psi/coordinate-psi-rate test coefficients, with original state and phase-rate placements; not completed Euler or formation stationarity',
        uncomputed_terms=['native/reference/state/domain and interacting fermion action',
            'Higgs/time-bundle constraint Hessians and their multipliers',
            'physical outer, normal normalization, endpoints and full time-Euler assembly',
            'physical-unit and implicit-cutoff equations and derivatives'],
        moving_point_scope='rank is at fixed E1; independent total parent/child time and normal/base pullback ports are retained separately, not zeroed or added twice to child chart sources',
        all_h_and_delta_h_unassigned=True,complete_action_Hessian=None,
        full_event_residual=None,full_formation_residual=None,physical_norm_residual=None,
        physical_guard=2e-10,physical_admission=False)
