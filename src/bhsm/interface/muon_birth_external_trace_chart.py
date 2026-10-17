"""Energy-envelope reset on the same physical canonical birth trace."""
from __future__ import annotations
import numpy as np
from .muon_shifted_boundary_source import canonical_reset_chart


def birth_external_trace_chart(parent_radius,child_radius,parent_clock,child_clock,
                               *,raw_reset,energy=0.):
    """Apply half-density and arm-origin phases, including independent dual.

    chi_point=R**(3/2)psi_point/V.  The shared angular normalization drops
    out of C_child U_raw C_parent^-1.  The lapse changes the proper clock,
    not this amplitude.  chi=e^-E*tau phi then gives
    phi_c=e^(E*(tau_c-tau_p))*T*phi_p and its inverse-transpose analytic
    left map.  No energy is selected as an exterior mass or physical pole.
    """
    Rp,Rc,tp,tc,E=map(complex,(parent_radius,child_radius,parent_clock,child_clock,energy))
    U=np.asarray(raw_reset,complex)
    if U.ndim!=2 or U.shape[0]!=U.shape[1]or Rp.real<=0 or Rc.real<=0 or not np.isfinite([Rp,Rc,tp,tc,E]).all():
        raise ValueError('same positive-radius trace chart and actual arm clocks required')
    d=len(U);base=canonical_reset_chart(Rp**1.5*np.eye(d),Rc**1.5*np.eye(d),U)
    delta=tc-tp;T=base['canonical_value_reset'];dual=base['analytic_covector_reset']
    Tr=np.exp(E*delta)*T;Tl=np.exp(-E*delta)*dual
    physicalR=np.exp(-E*tc)*Tr*np.exp(E*tp)
    physicalL=np.exp(E*tc)*Tl*np.exp(-E*tp)
    return dict(base,source_clock_jump=np.array(delta),
        envelope_value_reset=Tr,envelope_value_reset_energy_first=delta*Tr,
        envelope_literal_left_reset=Tl,envelope_literal_left_reset_energy_first=-delta*Tl,
        physical_value_reset_from_envelopes=physicalR,
        physical_literal_left_reset_from_envelopes=physicalL,
        physical_value_reset_energy_first=np.zeros_like(T),
        physical_literal_left_reset_energy_first=np.zeros_like(dual),
        analytic_trace_pairing_residual=Tl.T@Tr-np.eye(d),
        physical_value_chart_residual=physicalR-T,
        physical_literal_left_chart_residual=physicalL-dual,
        lapse_inserted_into_spinor_density=False,
        envelope_origin_twist_is_independent_seam_phase=False,
        physical_exterior_band_or_mass_selected=False)
