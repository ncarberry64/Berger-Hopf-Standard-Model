"""Reached energy pairing from an independently produced outgoing trace jet.

This does not select an outgoing subspace. C, V and V_E must come from the
same action-owned physical tail/domain. For Gamma=C T and T R=V a at a pole,
C_E V=-C V_E gives L Gamma_E R=L C(T_E R-V_E a). Only transverse motion of
the allowed subspace is needed; arbitrary changes of its basis cancel.
The energy derivative here is not a source-only envelope-clock derivative.
"""
from __future__ import annotations

import numpy as np


def outgoing_energy_pairing(*, annihilator, allowed_trace, allowed_trace_energy,
                            joined_trace, joined_trace_energy, right_mode,
                            left_mode, allowed_coordinates):
    """Apply the full scalar/matrix pairing without choosing modes or a tail.

    A single simple pole uses one R column/L row. A semisimple multiplet is
    supported only when independently established at that same energy.
    Compatibility rows are returned, never removed by projection or fitting.
    The supplied L is an analytic left covector, not a prescribed adjoint.
    """
    C,V,VE,T,TE,R,L,a = [np.asarray(x,complex)for x in (
        annihilator,allowed_trace,allowed_trace_energy,joined_trace,
        joined_trace_energy,right_mode,left_mode,allowed_coordinates)]
    if any(x.ndim!=2 or not x.size or not np.isfinite(x).all()
           for x in (C,V,VE,T,TE,R,L,a)):
        raise ValueError('finite nonempty explicit action-tail matrices required')
    m,n=C.shape
    if (V.shape[0]!=n or VE.shape!=V.shape or T.shape[0]!=n or TE.shape!=T.shape
            or R.shape[0]!=T.shape[1] or L.shape!=(R.shape[1],m)
            or a.shape!=(V.shape[1],R.shape[1])):
        raise ValueError('same original trace, mode and allowed-subspace axes required')
    transport=C@TE@R
    subspace=-C@VE@a
    return dict(energy_pairing=L@(transport+subspace),
                joined_transport_contribution=L@transport,
                outgoing_subspace_contribution=L@subspace,
                allowed_trace_rows=C@V,
                right_boundary_rows=C@T@R,
                left_boundary_rows=L@C@T,
                reached_trace_coordinate_rows=V@a-T@R,
                outgoing_subspace_or_pole_selected=False,
                energy_pairing_is_positive_current_Gram=False,
                source_only_clock_jet_substituted=False)


def boundary_row_energy_change(*, gamma, gamma_energy, right_mode, left_mode,
                               row_change, row_change_energy):
    """Keep the off-pole term in an energy-dependent annihilator-row change.

    Gamma'=S Gamma; Gamma'_E=S_E Gamma+S Gamma_E; L'=L S^-1.
    The changed pairing equals the original plus L S^-1 S_E Gamma R.
    A small trace-center alone does not remove this full-matrix term.
    """
    G,GE,R,L,S,SE=[np.asarray(x,complex)for x in (
        gamma,gamma_energy,right_mode,left_mode,row_change,row_change_energy)]
    if (G.ndim!=2 or G.shape[0]!=G.shape[1] or GE.shape!=G.shape
            or S.shape!=G.shape or SE.shape!=G.shape or R.ndim!=2
            or R.shape[0]!=len(G) or L.shape!=(R.shape[1],len(G))
            or any(not np.isfinite(x).all()for x in (G,GE,R,L,S,SE))):
        raise ValueError('same finite full boundary matrix and independent mode rows required')
    transformed_left=np.linalg.solve(S.T,L.T).T
    original=L@GE@R
    changed=transformed_left@(SE@G+S@GE)@R
    contact=transformed_left@SE@(G@R)
    return dict(original_pairing=original,changed_pairing=changed,
                off_pole_row_contact=contact,
                exact_chain_rule_rows=changed-original-contact,
                right_null_rows=G@R,left_null_rows=L@G,
                missing_physical_boundary_jet_inferred=False)
