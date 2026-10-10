"""Exact material one-form pullback for the retained intrinsic Higgs action.

Maxwell's independent one-forms already live on rho_phys=J*rho_ref.  At a
fixed material wall their temporal trace is A_t,ref.  The existing scalar
backend consumes Eulerian components and explicitly adds rho_phys_dot A_rho.
Applying that addition to reference components would count advection twice.
Only that extra connection-advection slot is removed here; all physical
metric, measure, radius, normal and velocity two-jets remain unchanged.
"""
from __future__ import annotations

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_intrinsic_higgs_gauge_action import intrinsic_higgs_gauge_action_jet


def material_intrinsic_higgs_gauge_action_jet(weights, **arguments):
    """Apply S_H to gauge trace maps already pulled back to the moving chart.

    A_t,phys=A_t,ref-rho_phys_dot*A_rho,ref/J and
    A_rho,phys=A_rho,ref/J.  Thus
    A_t,phys+rho_phys_dot*A_rho,phys=A_t,ref, including every derivative.
    Here rho_phys_dot=2*wall_rate.  Independent reference coefficient maps
    are material maps; Eulerian variation and embedding variation have
    already been combined by this exact pullback, once.

    The existing dictionary's wall_rate slot is used solely for its EXTRA
    gauge advection, after the complete geometric weights were constructed.
    A constant zero in that slot is not a zero physical wall velocity.
    """
    physical_rate=weights['wall_rate']
    count=len(weights['wT'].gradient)
    if len(physical_rate.gradient)!=count:
        raise ValueError('one common geometric two-jet coordinate domain required')
    pulled=dict(weights,wall_rate=Jet.constant(0.,count))
    result=intrinsic_higgs_gauge_action_jet(pulled,**arguments)
    result.update(gauge_trace_chart='MATERIAL_REFERENCE_ONE_FORM',
        temporal_gauge_trace='A_t_ref; Eulerian radial advection cancels its coordinate conversion',
        physical_wall_rate=physical_rate,
        physical_wall_velocity_set_to_zero=False,
        extra_reference_trace_advection_count=0,
        material_pullback_motion_count=1,
        pullback_owner='muon_parent_maxwell_geometry_weak.geometric_connection_coefficient_jets',
        intrinsic_scalar_derivatives='material scalar coefficient maps on the same chart')
    return result
