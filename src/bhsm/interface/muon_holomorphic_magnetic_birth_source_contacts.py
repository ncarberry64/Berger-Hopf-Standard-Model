"""Prescribed-source endpoint cotangents, retaining named reactions."""
import numpy as np


def magnetic_birth_source_contacts(parent,child,constraint,interior_lift,wall_lift,frame,source_parent,source_child):
    C,S,L,F=[np.asarray(x,complex)for x in(constraint,interior_lift,wall_lift,frame)]
    pp,pc=[np.asarray(a['canonical_momentum'],complex)for a in(parent,child)]
    jump=pp-pc;n=len(jump);nh=n//84
    gauss=np.zeros_like(jump);gauss[:16*nh]=child['original_action_force'][:16*nh]
    multipliers=np.linalg.solve(C@C.T,C@jump);gauss_multipliers=np.linalg.solve(C@C.T,C@gauss)
    qp,qc=[np.asarray(q,complex).reshape(L.shape[1],jump.shape[1])for q in(source_parent,source_child)]
    sourcep,sourcec=L@qp,L@qc
    full_work=parent['total_field'].T@pp-child['total_field'].T@pc
    source_work=sourcep.T@pp-sourcec.T@pc
    common_source_work=sourcec.T@jump
    return dict(momentum_jump=jump,momentum_named_constraint_multipliers=multipliers,
        momentum_named_constraint_range_defect=jump-C.T@multipliers,
        momentum_full_free_projection=S.T@jump,
        original_all_At_Gauss_embedded=gauss,Gauss_named_constraint_multipliers=gauss_multipliers,
        Gauss_named_constraint_range_defect=gauss-C.T@gauss_multipliers,Gauss_full_free_projection=S.T@gauss,
        full_interface_action_cotangent=full_work,prescribed_source_action_cotangent=source_work,
        full_minus_source_action_cotangent=full_work-source_work,
        common_source_action_cotangent=common_source_work,
        source_action_from_named_multipliers=(C@sourcec).T@multipliers,
        source_At_Gauss_pairing=sourcec.T@gauss,
        named_frame_source_rows=F@sourcec,
        source_value_jump=qp-qc,
        free_Higgs_momentum_jump=jump[-4*nh:])
