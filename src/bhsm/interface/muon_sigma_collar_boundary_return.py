"""Signed broken-collar surface work on an already evaluated field Poisson."""
from __future__ import annotations
import numpy as np


def collar_surface_work_projection(initial_green,final_green,after_minus_before,
        field_Poisson,field_Poisson_energy,*,full):
    """Apply final−initial−sum(after−before) with the literal left test.

    This is the integration-by-parts work of the broken interval trial.
    It neither selects transmission equations nor adds a counterterm to
    the bulk operator. All complete Poisson rows are consumed unchanged.
    """
    Gi,Gf,J=map(lambda a:np.asarray(a,complex),(initial_green,final_green,after_minus_before))
    P,PE=np.asarray(field_Poisson,complex),np.asarray(field_Poisson_energy,complex)
    if Gi.shape!=(2,2,64,64)or Gf.shape!=Gi.shape or J.ndim!=5 or J.shape[1:]!=Gi.shape or P.shape!=(768,18)or PE.shape!=P.shape:
        raise ValueError('complete two-sheet/particle-conjugate Green work and768 field Poisson rows required')
    D=full['localized_lepton18_literal_dual'];PL=np.diag(np.r_[np.ones(12),np.zeros(6)]);PR=np.eye(18)-PL
    left=np.c_[PL@D,PR@D]
    def lift(a):
        branch=lambda b:np.block([[b[0],np.zeros((64,64),complex)],[np.zeros((64,64),complex),b[1]]])
        a0,a1=(np.kron(np.eye(3),branch(x))for x in a)
        return np.block([[a0,np.zeros((384,384),complex)],[np.zeros((384,384),complex),a1]])
    matrices=[-lift(Gi),lift(Gf)]+[-lift(j)for j in J]
    terms=np.array([left@a@P for a in matrices]);energy=np.array([left@a@PE for a in matrices])
    return dict(signed_initial_surface_work=terms[0],signed_final_surface_work=terms[1],
        signed_interface_surface_work=terms[2:],total_broken_trial_surface_work=np.sum(terms,axis=0),
        signed_initial_surface_work_energy=energy[0],signed_final_surface_work_energy=energy[1],
        signed_interface_surface_work_energy=energy[2:],total_broken_trial_surface_work_energy=np.sum(energy,axis=0),
        analytic_left_test=left,signed_full_field_surface_matrix=np.sum(matrices,axis=0),
        field_Poisson_energy_is_only_E_dependence_in_this_fixed_trial_flux=True,
        boundary_transmission_or_physical_source_jet_not_selected=True,
        work_not_added_as_a_fitted_bulk_or_boundary_counterterm=True)
