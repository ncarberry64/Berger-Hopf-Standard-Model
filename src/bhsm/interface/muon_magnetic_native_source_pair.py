"""Actual magnetic direct/mean fermion ledger, with its scope intact."""
from __future__ import annotations
import numpy as np
from .muon_attached_native_source_pair import combine_executed_fermion_pair
from .muon_primal_cell_native_heat import actual_cell_heat_polynomial
from .muon_primal_native_phase_adjoint import contract_phase_native_target
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def combine_magnetic_direct_and_verified_mean(direct,mean_lower,mean_upper):
    """Insert the complex Grassmann +1/2 once, retaining exact-stored mean bounds.

    The bounds enclose addition of the stored direct real entries and the
    certified stored mean.  Direct heat assembly/contour/temporal errors
    remain separate.  Imaginary direct rounding is retained explicitly.
    """
    lo,hi=(np.asarray(v) for v in (mean_lower,mean_upper))
    if (lo.shape!=(8,8) or hi.shape!=(8,8) or not np.isrealobj(lo) or not np.isrealobj(hi)
            or not np.isfinite(lo).all() or not np.isfinite(hi).all() or np.any(lo>hi)):
        raise ValueError('all same-source exact-stored mean entry bounds required')
    if np.any(lo[3:]) or np.any(lo[:,3:]) or np.any(hi[3:]) or np.any(hi[:,3:]):
        raise ValueError('only three actual magnetic axes were inserted')
    mean=lo+(hi-lo)/2
    result=combine_executed_fermion_pair(direct,mean)
    D=result['direct_source_pair']
    if np.any(D[3:]) or np.any(D[:,3:]):raise ValueError('direct and mean magnetic support differs')
    lower=np.zeros((8,8));upper=lower.copy()
    lower[:3,:3]=np.nextafter((D[:3,:3].real+lo[:3,:3])/2,-np.inf)
    upper[:3,:3]=np.nextafter((D[:3,:3].real+hi[:3,:3])/2,np.inf)
    result.update(graded_exact_stored_mean_plus_stored_direct_real_lower=lower,
        graded_exact_stored_mean_plus_stored_direct_real_upper=upper,
        graded_direct_imaginary_rounding=result['graded_source_pair'].imag.copy(),
        active_source_indices=[0,1,2],inactive_padded_source_indices=[3,4,5,6,7],
        arithmetic_bound_scope='certified exact-stored mean plus stored direct real coefficient; excludes direct assembly/contour/temporal/domain errors',
        common_birth_second_mean_transfer_completed=False,
        induced_mean_scope='per-arm complete chronological phase with second-mean initial variation held; common-birth source second transfer not inserted',
        complete_physical_native_source_form=False)
    return result


def magnetic_finite_core_overlap_moment(fields,representation,polynomial,raw_mean_load,
        chronological_jacobian,chronological_step,*,length,frame='temporal'):
    """Execute the finite short-heat moment on the actual active source.

    Its Y² direct term is Tr P_AB,2.  Gauge/H cross and gauge-square
    contacts live in coefficients one/zero; their effects on heat survive
    in the spectral coefficient, but are not silently moved into Tr P2.
    This finite moment does not supply the full continuum local overlap.
    """
    base=actual_cell_heat_polynomial(fields['raw_fields'],representation,length=length)
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;dy=Y[1]**2-Y[2]**2
    direct=dy*np.trace(polynomial['contact'][2],axis1=-2,axis2=-1)
    target=dy*np.trace(base['P2_raw_first_jet'],axis1=1,axis2=2).real
    induced=contract_phase_native_target(chronological_jacobian,representation,chronological_step,
        target,raw_mean_load,frame=frame)
    mean=induced['native_mean_response_pair'];complete=direct+mean
    return dict(paired_TrP_Y2_direct_contact=direct,paired_TrP_Y2_raw_target=target,
        paired_TrP_Y2_mean_contact=mean,paired_TrP_Y2_complete_contact=complete,
        paired_first_short_heat_coefficient=-.5*complete,mean_application=induced,
        common_family_central_overlap=np.zeros((8,8)),
        central_cancellation_equation='same Y0 background/source/domain/mean graph on two family copies cancels before subtraction',
        finite_short_heat_equation='delta_AB Tr0 exp(-sP)=-s delta_AB Tr0 P+O(s^2)',
        local_open_H1_overlap_zero_scope='closed delta_A delta_A determinant source legs differ from open delta_barPsi delta_Psi delta_A one-loop scalar vertex',
        continuum_local_QED_VP_overlap_not_this_moment=True,
        finite_moment_subtracted=False,physical_native_overlap_completed=False)
