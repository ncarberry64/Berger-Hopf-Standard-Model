"""Complete normal/area first jet of the inherited magnetic endpoint action.

This consumes the source-on parent/child action states. It does not select
the physical formation event, exterior rows, pole, or Pauli covector.
"""
from __future__ import annotations
import numpy as np


def inherited_magnetic_endpoint_cotangent(data):
    """Differentiate q_p.T Pi_p-q_c.T Pi_c before a trace projection.

    The supplied direct source-first term is dQ_p.T Pi_p-dQ_c.T Pi_c.
    Both Pi responses then complete the prescribed-source first jet. All
    source coefficients and left placements are analytic, not conjugated.
    High and low source columns remain separate throughout the products.
    """
    names=('parent_total_field','child_total_field','parent_canonical_momentum','child_canonical_momentum',
        'parent_total_field_first','child_total_field_first','parent_canonical_momentum_first','child_canonical_momentum_first',
        'parent_known_wall_field','child_known_wall_field','direct_source_first_endpoint_cotangent')
    a={n:np.asarray(data[n],complex)for n in names}
    qp,qc,pp,pc=(a[n]for n in names[:4]);dqp,dqc,dpp,dpc=(a[n]for n in names[4:8]);sp,sc,direct=(a[n]for n in names[8:])
    if qp.ndim!=2 or qc.shape!=qp.shape or pp.shape!=qp.shape or pc.shape!=qp.shape or sp.shape!=qp.shape or sc.shape!=qp.shape:
        raise ValueError('same full parent/child original action source rows required')
    k=len(dqp);ns=qp.shape[1]
    if any(x.shape!=(k,*qp.shape)for x in(dqp,dqc,dpp,dpc))or direct.shape!=(k,ns,ns)or any(not np.isfinite(x).all()for x in a.values()):
        raise ValueError('every independent analytic source column and full cotangent required')
    full=qp.T@pp-qc.T@pc
    value_motion=np.array([dq.T@p-dr.T@r for dq,p,dr,r in zip(dqp,[pp]*k,dqc,[pc]*k)])
    momentum_motion=np.array([qp.T@dp-qc.T@dc for dp,dc in zip(dpp,dpc)])
    source=sp.T@pp-sc.T@pc
    source_momentum=np.array([sp.T@dp-sc.T@dc for dp,dc in zip(dpp,dpc)])
    return dict(full_interface_action_cotangent=full,
        full_interface_value_motion=value_motion,full_interface_momentum_motion=momentum_motion,
        full_interface_action_cotangent_first=value_motion+momentum_motion,
        prescribed_source_action_cotangent=source,prescribed_source_direct_motion=direct,
        prescribed_source_momentum_motion=source_momentum,prescribed_source_action_cotangent_first=direct+source_momentum,
        full_minus_source_action_cotangent=full-source,
        full_minus_source_action_cotangent_first=value_motion+momentum_motion-direct-source_momentum,
        independent_source_columns_conjugated=False,
        physical_full_birth_event_exterior_Gamma2_pole_or_Pauli_selected=False)
