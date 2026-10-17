"""Intrinsic Dirac action application on the unprojected inherited wall image.

The original intrinsic action factors exactly through its twenty wall
connection coordinates. A trace realization below is computational only;
it never replaces the bulk gauge action or its radial conormal contact.
"""
from __future__ import annotations
import numpy as np
from .muon_primal_trace_enriched_lepton_operator import intrinsic_wall_coordinate_reduction
from .muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator
from .muon_parent_maxwell_full_weak import FIELD_ORDER
from .muon_parent_retarded_hypercharge import WALL,regular_radial_basis


def inherited_wall_lepton_application(independent_raw, full_independent_wall, representation):
    """Apply the same normal-chart Dirac operator with the extra wall image.

    full_independent_wall includes the profile increment. The intrinsic
    action adds its mechanical connection once. It must not be included
    a second time in the supplied independent wall slot. No derivative
    of a held-wall-coordinate realization is promoted to a total jet.
    """
    raw=np.asarray(independent_raw);wall=np.asarray(full_independent_wall)
    nr=108+2*len(representation['gauge_labels'])
    if not np.isrealobj(raw) or raw.shape!=(nr,) or not np.isfinite(raw).all():
        raise ValueError('complete finite real independent raw coefficient vector required')
    if not np.isrealobj(wall) or wall.shape!=(5,4) or not np.isfinite(wall).all():
        raise ValueError('complete unprojected independent wall image required')
    reduction=intrinsic_wall_coordinate_reduction(representation)
    legacy=reduction['raw_action_map']@raw;rep=reduction['original_representation']
    basis,_=regular_radial_basis(np.array([WALL]),rep['radial_order'])
    trace=np.zeros((5,4,60));section=np.zeros((60,20))
    for j,label in enumerate(rep['gauge_labels']):
        f=FIELD_ORDER.index(label['field']);c=label['internal'];b=basis[0,label['radial']]
        trace[f,c,j]=b
        if label['wall_lift']:
            if b==0:raise ValueError('nondegenerate inherited wall lift required')
            section[j,4*f+c]=1/b
    if np.max(abs(trace.reshape(20,60)@section-np.eye(20)))>8*np.finfo(float).eps:
        raise ArithmeticError('complete wall image realization failed')
    previous=np.einsum('fcj,j->fc',trace,legacy[100:160])
    addendum=wall-previous
    legacy[100:160]+=section@addendum.reshape(20)
    represented=np.einsum('fcj,j->fc',trace,legacy[100:160])
    actual=primal_intrinsic_lepton_operator(legacy,rep)
    old=primal_intrinsic_lepton_operator(reduction['raw_action_map']@raw,rep)
    actual.update(independent_raw=raw.copy(),inherited_full_wall=wall.copy(),
        omitted_profile_wall=addendum,trace_realization=section,
        reconstructed_wall=represented,
        inherited_trace_residual=float(np.max(abs(represented-wall))),
        W_if_profile_omitted=old['W'],H_can_if_profile_omitted=old['H_can'],
        W_profile_contact=actual['W']-old['W'],H_can_profile_contact=actual['H_can']-old['H_can'],
        inherited_wall_image_applied_once=True,mechanical_connection_added_by_original_action_once=True,
        normal_geometry_and_current_pairing_from_original_intrinsic_action=True,
        raw_first_jet_scope='held independent wall-coordinate realization; total inherited geometry/profile/domain jets must use the composed graph action',
        bulk_gauge_action_or_conormal_projected=False,physical_formation_or_LSZ_or_Pauli_evaluated=False)
    return actual
