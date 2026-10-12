"""Additive source-clock correction for the chronological charge application.

Part zero is an actual proper Euclidean source cell. Its saved zero
coordinate slope is graph bookkeeping, whereas its coefficient germ obeys
dz/dtau_E=-i/N. Parts one and two are the two connector legs and retain
their saved coordinate slope divided by the original right clock. The
nodal field derivative is independent of that inherited coefficient germ.
No exterior state, physical charge residue or Pauli projection is selected.
"""
from __future__ import annotations
import numpy as np


def corrected_source_clock_higgs_first(coordinate_first, lifted_field_coordinate_rate,
                                      graph_part, coordinate_slope, right_clock, lapse):
    """Return the same-clock Higgs germ with both actual motions retained."""
    a, b = (np.asarray(x, complex) for x in
            (coordinate_first, lifted_field_coordinate_rate))
    scalars = np.asarray([graph_part, coordinate_slope, right_clock, lapse], complex)
    if (a.shape != (4,) or b.shape != a.shape or
            not all(np.isfinite(x).all() for x in (a, b, scalars)) or
            right_clock == 0 or lapse == 0 or graph_part not in (0, 1, 2)):
        raise ValueError('complete Higgs germs, original nonsingular clocks and graph part 0/1/2 required')
    coefficient_clock_rate = (-1j/lapse if graph_part == 0
                              else coordinate_slope/right_clock)
    inherited = coefficient_clock_rate*(a-b)
    nodal = b/(1j*lapse)
    # Keep the frozen connector operation order exactly; only part zero's
    # previously omitted inherited coefficient derivative is corrected.
    first = (inherited+nodal if graph_part == 0 else
             (coordinate_slope*(a-b)+right_clock*b/(1j*lapse))/right_clock)
    return dict(H_source_clock_first=first,
                inherited_H_source_clock_first=inherited,
                nodal_H_source_clock_first=nodal,
                analytic_coordinate_source_clock_rate=coefficient_clock_rate)


def charge_clock_direction_effect(charge, charge_first_correction, right_map,
                                  analytic_left_map):
    """Apply the correction to every C6 source direction and charge block.

The independent analytic dual remains literal transpose. Charged and
neutral blocks are the instantaneous transported Higgs-selected projector
blocks, with no deletion of their off-diagonal return.
    """
    Q, dQ, F, L = (np.asarray(x, complex) for x in
                   (charge, charge_first_correction, right_map, analytic_left_map))
    if (Q.shape != (6, 6) or any(x.shape != Q.shape for x in (dQ, F, L)) or
            not all(np.isfinite(x).all() for x in (Q, dQ, F, L))):
        raise ValueError('complete same-domain C6 charge, correction and independent source maps required')
    transported = np.linalg.solve(F, dQ@F)
    analytic = L.T@dQ@F
    P = -np.linalg.solve(F, Q@F)
    Pn = np.eye(6)-P
    return dict(source_direction_clock_correction=transported,
                analytic_dual_direction_clock_correction=analytic,
                analytic_dual_direction_difference=analytic-transported,
                charged_to_charged_clock_correction=P@transported@P,
                neutral_to_charged_clock_correction=P@transported@Pn,
                charged_to_neutral_clock_correction=Pn@transported@P,
                neutral_to_neutral_clock_correction=Pn@transported@Pn)
