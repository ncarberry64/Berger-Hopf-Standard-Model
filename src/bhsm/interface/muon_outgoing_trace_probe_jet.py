"""Unsquared outgoing trace E/B pairings with every moving-domain contact.

This consumer does not produce a physical domain. Matrices are caller-owned
values and literal E, B, EB derivatives (no Taylor coefficients). The mixed
pairing holds R, L fixed; derivatives of moving pole frames are not inferred.
"""
from __future__ import annotations

import numpy as np


def outgoing_trace_two_parameter_pairing(*, annihilator,
        annihilator_energy, annihilator_magnetic, annihilator_energy_magnetic,
        allowed_trace, allowed_trace_energy, allowed_trace_magnetic,
        allowed_trace_energy_magnetic, joined_trace, joined_trace_energy,
        joined_trace_magnetic, joined_trace_energy_magnetic,
        right_mode, left_mode, allowed_coordinates):
    """Apply exact same-domain E/B/EB trace pairings, retaining off-pole rows.

    Gamma=C T, C V=0, T R=V a at a pole. With D_j=T_j R-V_j a,
    Gamma_j R=C D_j+C_j(T R-V a)+(C_j V+C V_j)a.
    For EB the transverse contribution is
      C(T_EB R-V_EB a)+C_E D_B+C_B D_E.
    Omitting either first-domain contact generally gives the wrong mixed
    derivative. All annihilator identities and trace discrepancies remain
    explicit, so none need be asserted zero for numerical coefficients.
    """
    values = (annihilator, annihilator_energy, annihilator_magnetic,
        annihilator_energy_magnetic, allowed_trace, allowed_trace_energy,
        allowed_trace_magnetic, allowed_trace_energy_magnetic, joined_trace,
        joined_trace_energy, joined_trace_magnetic,
        joined_trace_energy_magnetic, right_mode, left_mode,
        allowed_coordinates)
    C,CE,CB,CEB,V,VE,VB,VEB,T,TE,TB,TEB,R,L,a = (
        np.asarray(x,complex) for x in values)
    all_matrices=(C,CE,CB,CEB,V,VE,VB,VEB,T,TE,TB,TEB,R,L,a)
    if any(x.ndim != 2 or not x.size or not np.isfinite(x).all()
           for x in all_matrices):
        raise ValueError('finite explicit same-domain matrix jets required')
    m,n=C.shape
    if (any(x.shape!=C.shape for x in (CE,CB,CEB))
            or V.shape[0]!=n or any(x.shape!=V.shape for x in (VE,VB,VEB))
            or T.shape[0]!=n or any(x.shape!=T.shape for x in (TE,TB,TEB))
            or R.shape[0]!=T.shape[1] or L.shape!=(R.shape[1],m)
            or a.shape!=(V.shape[1],R.shape[1])):
        raise ValueError('same original boundary, allowed-frame and mode axes required')
    identity0=C@V
    identityE=CE@V+C@VE
    identityB=CB@V+C@VB
    identityEB=CEB@V+CE@VB+CB@VE+C@VEB
    delta=T@R-V@a
    dE=TE@R-VE@a
    dB=TB@R-VB@a
    dEB=TEB@R-VEB@a
    transverseE=L@C@dE
    transverseB=L@C@dB
    transportEB=L@C@dEB
    contactEB=L@(CE@dB+CB@dE)
    offE=L@(CE@delta+identityE@a)
    offB=L@(CB@delta+identityB@a)
    offEB=L@(CEB@delta+identityEB@a)
    gamma=C@T
    gammaE=CE@T+C@TE
    gammaB=CB@T+C@TB
    gammaEB=CEB@T+CE@TB+CB@TE+C@TEB
    directE=L@gammaE@R
    directB=L@gammaB@R
    directEB=L@gammaEB@R
    return dict(energy_pairing=directE,magnetic_pairing=directB,
        fixed_frame_energy_magnetic_pairing=directEB,
        transverse_energy_pairing=transverseE,
        transverse_magnetic_pairing=transverseB,
        mixed_joined_transport_and_allowed_trace_pairing=transportEB,
        mixed_first_domain_contacts=contactEB,
        off_pole_or_nonannihilating_energy_contacts=offE,
        off_pole_or_nonannihilating_magnetic_contacts=offB,
        off_pole_or_nonannihilating_mixed_contacts=offEB,
        energy_chain_rule_rows=directE-transverseE-offE,
        magnetic_chain_rule_rows=directB-transverseB-offB,
        energy_magnetic_chain_rule_rows=directEB-transportEB-contactEB-offEB,
        allowed_trace_rows=identity0,allowed_trace_energy_rows=identityE,
        allowed_trace_magnetic_rows=identityB,
        allowed_trace_energy_magnetic_rows=identityEB,
        reached_trace_coordinate_rows=delta,right_boundary_rows=gamma@R,
        left_boundary_rows=L@gamma,gamma=gamma,gamma_energy=gammaE,
        gamma_magnetic=gammaB,gamma_energy_magnetic=gammaEB,
        outgoing_domain_and_pole_are_caller_supplied=True,
        mixed_pairing_is_total_pole_path_derivative=False,
        physical_resonance_normalization_or_moment_admitted=False,
        no_missing_domain_source_or_quantum_contact_assumed_zero=True)
