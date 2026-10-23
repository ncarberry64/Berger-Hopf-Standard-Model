"""Original two-collar weak domain, with one geometric and one SH map.

The variables are the ORIGINAL two d-valued traces x=Psi_plus and
z=Psi_minus. U maps the plus fiber to the minus fiber, so y=U^-1 z.
The action trace is q=P_L b_plus x+P_R b_minus z. Its weak row is
J_plus(y-x)=C_sum T q. Isotropy makes q single-valued and determines
z=U(I+J_plus^-1 C_sum T B_sum)x. This is a d-dimensional graph in
2d trace coordinates; no transfer is applied to an already doubled field.

This corrects the inference that one global bundle alone forces hard
interacting field continuity. The historical hard graph is the T=0
limit. It changes that free operator domain when T is nonzero, rather
than claiming both domains are the same. Native continuation, a common
graded operator, outgoing evolution and physical source jets remain
separate action applications.
"""
from __future__ import annotations

import numpy as np

from .muon_isotropic_seam_transfer import (
    KEYS, _identity, _jet, _product, _difference, isotropic_seam_transfer_jets,
)


def _add(a, b):
    return {key: a[key] + b[key] for key in KEYS}


def _constant(matrix):
    matrix = np.asarray(matrix, complex)
    return {key: matrix.copy() if key == 'value' else np.zeros_like(matrix)
            for key in KEYS}


def two_collar_weak_domain_jets(*, plus_green, minus_green,
        geometric_right, geometric_right_inverse, geometric_left_dual,
        plus_normalized_trace, minus_normalized_trace,
        plus_canonical_source, minus_canonical_source,
        surface_kernel, left_chiral_projector):
    """Construct all value/x/y/xy domain rows on the two ORIGINAL traces.

    J_plus/minus are the original outward Green densities. The supplied
    geometric left dual pulls a minus canonical SOURCE COLUMN to the plus
    chart; on its real physical family it is U^dagger. A plus canonical
    row maps to the minus chart by right multiplication by this matrix.
    Its analytic source jets
    are independent, never inferred by conjugating source weights.
    Canonical source incidences already include the original Dirac-bar
    conversion once. T is the once-only rho*M18 surface kernel.

    All input shapes, inverse, Green-alignment, isotropy and original
    weak equations are checked or returned explicitly. Nonzero returned
    admission rows are not silently accepted as a physical domain.
    The jets are supplied total contacts on this chosen branch; the
    function does not produce the physical E/B/outgoing jets itself.
    """
    p0 = np.asarray(left_chiral_projector, complex)
    j0 = np.asarray(plus_green.get('value'), complex)
    if j0.ndim != 2 or j0.shape[0] != j0.shape[1] or not len(j0):
        raise ValueError('one nonempty full-fiber square plus Green map required')
    d = len(j0)
    if (p0.ndim != 2 or p0.shape[0] != p0.shape[1] or not len(p0)
            or not np.isfinite(p0).all()
            or np.max(abs(p0@p0-p0)) > 1e-12
            or np.max(abs(p0.conj().T-p0)) > 1e-12):
        raise ValueError('fixed Hermitian chiral projector required')
    n = len(p0)
    pl, pr = _constant(p0), _constant(np.eye(n)-p0)
    jp, jm, u, ui, us = (_jet(value, (d,d), name) for value, name in (
        (plus_green, 'plus_green'), (minus_green, 'minus_green'),
        (geometric_right, 'geometric_right'),
        (geometric_right_inverse, 'geometric_right_inverse'),
        (geometric_left_dual, 'geometric_left_dual')))
    bp, bm = (_jet(value, (n,d), name) for value, name in (
        (plus_normalized_trace, 'plus_normalized_trace'),
        (minus_normalized_trace, 'minus_normalized_trace')))
    cp, cm = (_jet(value, (d,n), name) for value, name in (
        (plus_canonical_source, 'plus_canonical_source'),
        (minus_canonical_source, 'minus_canonical_source')))
    t = _jet(surface_kernel, (n,n), 'surface_kernel')
    bl, br = _product(pl,bp), _product(pr,bm)
    b = _add(bl, _product(br,u))
    c = _add(_product(cp,pl), _product(_product(us,cm),pr))
    local = isotropic_seam_transfer_jets(jp,c,t,b)
    s, ns = local['transfer'], local['N']
    right = _product(u,s)
    left = _product(local['independent_dual_transfer'],us)
    identity = _identity(d)
    q = _add(bl,_product(br,right))
    weak = _difference(_product(jp,_difference(_product(ui,right),identity)),
                       _product(_product(c,t),q))
    graph = {key: np.vstack((identity[key],right[key])) for key in KEYS}
    rows = {key: np.hstack((-right[key],identity[key])) for key in KEYS}
    left_graph = {key: np.hstack((identity[key],left[key])) for key in KEYS}
    return dict(
        right_minus_from_plus=right, independent_left_minus_from_plus=left,
        original_two_trace_graph=graph, original_two_trace_domain_rows=rows,
        independent_left_two_trace_graph=left_graph,
        common_frame_transfer=s, common_frame_inverse_transfer=local['inverse_transfer'],
        common_frame_normalized_trace=b, common_frame_canonical_source=c,
        original_split_trace_on_graph=q,
        original_weak_surface_rows=weak,
        original_split_trace_rows=_difference(q,b),
        original_two_trace_domain_graph_rows=_product(rows,graph),
        original_two_trace_green_rows=_add(jp,_product(_product(left,jm),right)),
        geometric_green_alignment_rows=_add(jp,_product(_product(us,jm),u)),
        geometric_inverse_rows=_difference(_product(ui,u),identity),
        geometric_reverse_inverse_rows=_difference(_product(u,ui),identity),
        plus_selected_trace_jump_rows=_product(bl,ns),
        minus_selected_trace_jump_rows=_product(_product(br,u),ns),
        isotropy_rows=local['isotropy'], nilpotence_rows=local['nilpotence_rows'],
        original_free_graph_surface_defect=_product(_product(c,t),b),
        Higgs_left_left_rows=_product(_product(pl,t),pl),
        Higgs_right_right_rows=_product(_product(pr,t),pr),
        full_fiber_count=d, original_boundary_trace_count=2*d,
        graph_free_coordinates=d, selected_trace_count=n,
        additional_boundary_trace_copies=0, full_fiber_rows_deleted=0,
        fixed_source_coefficients_conjugated=False,
        geometric_dual_inferred_by_conjugating_jets=False,
        free_hard_trace_domain_retained_for_nonzero_surface_source=False,
        surface_kernel_copies=1, bulk_Higgs_mass_added=False,
        scope='original two-collar weak SH domain on supplied regular-wall jets',
        local_equations_returned_without_global_physical_admission=True,
        common_native_positive_domain_identified=False,
        physical_outgoing_energy_field_jets_evaluated=False,
        full_physical_derivative_gate_passed=False,
        original_coupled_corrections_applied=0,
    )
