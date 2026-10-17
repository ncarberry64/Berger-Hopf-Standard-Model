"""Action charge transport on a declared chronological source chart.

The Higgs-selected generator is holomorphic in the four continued real
coordinates. Its derivative and the analytic source dual use no complex
conjugation. A computational change of basis supplies neither a physical
external state nor a pole residue.
"""
from __future__ import annotations
import numpy as np


def holomorphic_charge_first(h, dh, generators):
    """Apply the exact quotient derivative of the retained neutral line."""
    h, dh, G = (np.asarray(x, complex) for x in (h, dh, generators))
    if (h.shape != (4,) or dh.shape != h.shape or G.ndim != 3
            or G.shape[0] != 4 or G.shape[1] != G.shape[2]
            or not all(np.isfinite(x).all() for x in (h, dh, G))):
        raise ValueError('four continued Higgs coordinates and complete generators required')
    q, dq = h @ h, 2*(h @ dh)
    if q == 0:
        raise ValueError('the inherited Higgs-selected chart requires nonzero holomorphic norm')
    n = np.array([2*(h[0]*h[1]+h[2]*h[3]),
                  2*(h[0]*h[3]-h[2]*h[1]),
                  h[0]**2+h[2]**2-h[1]**2-h[3]**2])
    dn = np.array([2*(dh[0]*h[1]+h[0]*dh[1]+dh[2]*h[3]+h[2]*dh[3]),
                   2*(dh[0]*h[3]+h[0]*dh[3]-dh[2]*h[1]-h[2]*dh[1]),
                   2*(h[0]*dh[0]+h[2]*dh[2]-h[1]*dh[1]-h[3]*dh[3])])
    s = np.r_[-np.sqrt(2)*n/q, np.sqrt(10/3)]
    ds = np.r_[-np.sqrt(2)*(dn/q-n*dq/q**2), 0j]
    return dict(charge=1j*np.einsum('c,cij->ij',s,G),
                charge_first=1j*np.einsum('c,cij->ij',ds,G),
                charge_coefficients=s, charge_coefficients_first=ds)


def source_clock_higgs_first(coordinate_first, lifted_field_coordinate_rate,
                             coordinate_slope, right_clock, lapse):
    """Separate inherited chart motion from the nodal field derivative.

    On constant-coordinate connectors the first term vanishes; the actual
    nodal derivative survives. The producer's field rate is iN/w D_s x.
    Dividing the reconstructed D_s H by the original complex w gives the
    derivative in the same source clock as D_s/w + H_can.
    """
    a, b = (np.asarray(x, complex) for x in
            (coordinate_first, lifted_field_coordinate_rate))
    if a.shape != (4,) or b.shape != a.shape or right_clock == 0 or lapse == 0:
        raise ValueError('complete field and coordinate germs with nonsingular original clock required')
    return (coordinate_slope*(a-b)+right_clock*b/(1j*lapse))/right_clock


def transported_charge_application(charge, charge_first, point_body,
                                   represented_generator, right_map,
                                   analytic_left_map):
    """Evaluate charge transport and the declared map's weak-action defect.

    right_map solves the declared generator, which can differ from the
    pointwise interacting action. This difference is exported rather than
    silently treating an edge average as an exact action continuation.
    """
    Q, Q1, H, A, F, L = (np.asarray(x, complex) for x in
                         (charge, charge_first, point_body,
                          represented_generator, right_map, analytic_left_map))
    if (Q.ndim != 2 or Q.shape[0] != Q.shape[1]
            or any(x.shape != Q.shape for x in (Q1,H,A,F,L))
            or not all(np.isfinite(x).all() for x in (Q,Q1,H,A,F,L))):
        raise ValueError('one complete common-domain charge, body and independent source-dual map required')
    comm = lambda X,Y: X@Y-Y@X
    qbar = np.linalg.solve(F, Q@F)
    represented = np.linalg.solve(F, (Q1+comm(A,Q))@F)
    action = np.linalg.solve(F, (Q1+comm(H,Q))@F)
    weak = (H-A)@F
    return dict(transported_charge=qbar,
                represented_source_chart_charge_first=represented,
                actual_action_covariant_charge_first=action,
                action_minus_represented_charge_first=action-represented,
                actual_source_chart_weak_action_residual=weak,
                original_charge_exchange=comm(H,Q),
                analytic_dual_pairing_residual=L.T@F-np.eye(len(F)),
                computational_Hilbert_metric=F.conj().T@F,
                physical_charge_or_residue_normalization_assigned=False)
