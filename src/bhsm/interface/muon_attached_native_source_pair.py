"""Direct and induced fermion source pair on the SAME attached coefficient cell.

This applies the executed source fields and chronological mean adjoint,
retains contact and both insertion orders, and inserts the complex fermion
statistics factor once.  The overlap test evaluates the actual first local
short-heat moment of this finite core; it does not import a continuum local
counterterm into a partial angular trace.
"""
from __future__ import annotations

import numpy as np
from .muon_current_source_motion_mean_load import enriched_reached_first_fields
from .muon_primal_cell_reached_source_heat import actual_midpoint_reached_source_heat
from .muon_primal_cell_native_heat import actual_cell_heat_polynomial
from .muon_primal_native_phase_adjoint import contract_phase_native_target


COMPLEX_FERMION_STATISTICS_FACTOR=.5


def combine_executed_fermion_pair(direct,mean):
    """Combine the reached Y2 terms, with Gamma_F=+Tr E1/2 exactly once.

    The source Hessian is complex-bilinear on real source directions.  No
    transpose, conjugation, source-pair doubling or charge-conjugate copy is
    inserted.  The three direct pieces are separately retained.
    """
    required=('source_square_contact','ordered_two_insertion','opposite_order_two_insertion')
    arrays={k:np.asarray(direct[k]) for k in required}
    m=np.asarray(mean)
    if m.shape!=(8,8) or any(a.shape!=(8,8) for a in arrays.values()):
        raise ValueError('all64 same-source direct and mean entries required')
    if not np.isfinite(m).all() or any(not np.isfinite(a).all() for a in arrays.values()):
        raise ValueError('finite executed direct and mean pairings required')
    direct_total=arrays[required[0]]+arrays[required[1]]+arrays[required[2]]
    ungraded=direct_total+m
    return dict(**arrays,direct_source_pair=direct_total,induced_mean_operator_contact=m,
        ungraded_source_pair=ungraded,fermion_statistics_factor=COMPLEX_FERMION_STATISTICS_FACTOR,
        graded_source_pair=COMPLEX_FERMION_STATISTICS_FACTOR*ungraded,
        complex_fermion_copy_count=1,charge_conjugate_doubling_applied=False,
        both_source_orders_retained=True,mean_contact_count=1,
        complete_relative_native_or_Pauli=False)


def actual_finite_core_overlap_moment(fields,representation,angular,raw_mean_load,
        chronological_jacobian,chronological_step,*,length,frame='temporal'):
    """Evaluate the first short-heat source coefficient, rather than subtract it.

    On this SAME finite core, Tr_0 exp(-sP)=6-s Tr_0 P+O(s²).
    The leading rank6 coefficient has no source variation, and the entire
    Y-independent operator, source and induced mean map are identical in
    the two family copies.  Their relative contraction is exactly zero.
    The Y2 term is not central: its direct Xi-dagger Xi and actual induced
    mean variation of Tr P2 are evaluated below and generally survive.

    This is the finite-core Taylor moment, NOT a continuum a2/a4 heat
    coefficient.  Thus no M8/M5/M4 local action is subtracted from it.
    """
    polynomial=actual_cell_heat_polynomial(fields['raw_fields'],representation,length=length)
    from .muon_primal_cell_reached_source_heat import actual_reached_cell_vertices
    from .muon_native_mean_core_heat_target import _unit_lepton_mass6
    from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
    source=actual_reached_cell_vertices(fields,representation)
    if fields['profile']!=0 or fields['profile_rate']!=0 or np.any(fields['first_wall_gauge']):
        raise ValueError('same derived zero midpoint wall trace required')
    H=source['complex_H_response']
    X=np.array([_unit_lepton_mass6(h) for h in H.reshape(160,2)]).reshape(8,20,6,6)
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real
    dy=Y[1]**2-Y[2]**2
    gram=np.einsum('Ahij,Bhij->AB',X.conj(),X)
    direct=dy*(gram+gram.T)
    target=dy*np.trace(polynomial['P2_raw_first_jet'],axis1=1,axis2=2).real
    induced=contract_phase_native_target(chronological_jacobian,representation,chronological_step,
        target,raw_mean_load,frame=frame)
    mean=induced['native_mean_response_pair'];complete=direct+mean
    return dict(common_family_central_mixed_overlap=np.zeros((8,8)),
        leading_rank_coefficient_source_mixed_variation=np.zeros((8,8)),
        paired_TrP_Y2_direct_contact=direct,paired_TrP_Y2_raw_target=target,
        paired_TrP_Y2_mean_contact=mean,paired_TrP_Y2_complete_contact=complete,
        paired_first_short_heat_coefficient=-COMPLEX_FERMION_STATISTICS_FACTOR*complete,
        mean_application=induced,
        central_cancellation_equation='Gamma0[background,source,domain]-Gamma0[background,source,domain]=0, including the SAME raw mean chain rule',
        first_short_heat_equation='delta_AB Tr0 exp(-sP)=-s delta_AB Tr0 P+O(s²); rank6 term has zero source variation',
        first_short_heat_coefficient_scope='finite normalized tent/constant-angular C6 trace only; not continuum a2/a4',
        evaluated_mass_dependent_local_moment_is_subtracted=False,
        full_bosonic_Maxwell_or_Higgs_action_subtracted=False,
        physical_overlap_or_soft_Pauli_completion=False)


def attached_same_cell_source_pair(inputs,angular,mean,*,cutoff):
    """Apply the executed total wall source and its SAME-cell mean contact."""
    fields=enriched_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
    length=abs(inputs['receipt']['actual_phase_span'])
    direct=actual_midpoint_reached_source_heat(fields,inputs['representation'],angular,length=length,cutoff=cutoff)
    combined=combine_executed_fermion_pair(direct['paired_middle_minus_light_Y2_source_pair'],mean)
    return dict(fields=fields,direct_application=direct,combined=combined,length=length,cutoff_probe=float(cutoff),
        source_coordinate_clock=fields['source_coordinate_clock'],
        determinant_owner='ae4_stratified_dirac_zeta_induced_owner.microscopic_owner_contract',
        statistics_equation='Gamma=-STr E1/2; complex Grassmann fermion STr=-Tr; Gamma_F=+Tr E1/2',
        relative_eta_phase_is_second_determinant=False,
        relative_eta_phase_evaluated=False,continuum_local_overlap_subtraction_evaluated=False,
        source_pulse_is_physical_soft_transfer=False,physical_cutoff_selected=False,
        no_independent_covariance_or_measured_anomaly=True,complete_native_or_Pauli=False)
