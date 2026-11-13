"""Joined canonical current factor and its exact finite boundary return.

One canonical birth trace joins the two chronological arms.  The squared
form keeps the actual free final face; its Dirichlet interior compression
and Poisson/Schur return are exported separately.  This action application
does not identify the finite numerical outer faces with E0 or infinity.
"""
from __future__ import annotations

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import splu
from .muon_continued_current_factor import _first_order_matrix


def join_current_coefficients(incoming,outgoing,birth_transport):
    """Compose an explicit unit-current trace frame before any inverse.

    The current executed homogeneous common-frame restriction uses T=I.
    A general unitary T is retained here so that the boundary action and
    current target are transformed together.  No global F_B/U graph is
    inferred from this computational frame relation.
    """
    p,c=incoming,outgoing;T=np.asarray(birth_transport,complex)
    if T.shape!=(6,6)or not np.isfinite(T).all()or np.max(abs(T.conj().T@T-np.eye(6)))>2e-13:
        raise ValueError('explicit canonical unit-current C6 birth frame required')
    for key in('canonical_Gram_I6','family_indices','family_Y','alpha6'):
        if not np.array_equal(p[key],c[key]):raise ValueError('same current/family representation required')
    n=len(p['proper_cell_weights']);out={}
    for key in('A0_diagonal','A0_lower','A1_diagonal','A1_lower','proper_cell_weights',
               'source_right_map','target_left_map','common_Hcan0','common_Hcan1','R4','N'):
        out[key]=np.concatenate((p[key],c[key]))
    out['A0_lower']=out['A0_lower'].copy();out['A1_lower']=out['A1_lower'].copy()
    out['A0_lower'][n]=out['A0_lower'][n]@T;out['A1_lower'][n]=out['A1_lower'][n]@T
    out.update(birth_index=n,birth_transport=T,initial_trace='incoming numerical initial-zero inverse',
        final_trace='outgoing final trace free; its adjoint face retained',
        coordinate_nodes=np.r_[p['coordinate_nodes']-p['coordinate_nodes'][-1],c['coordinate_nodes'][1:]],
        far_faces_are_E0_or_infinity=False,physical_full_birth_transport_selected=False)
    return out


def joined_squared_current_application(coefficients,*,Y=0.):
    """Apply the direct inverse, squared inverse, and boundary Schur return.

    The boundary return is derived from K=A†G_source A.  Compressing K to
    its interior alone imposes an additional final Dirichlet condition;
    the rank-six Schur return restores the original first-order domain.
    All current left placements are literal analytic rows.
    """
    c=coefficients;n=len(c['proper_cell_weights']);m=6;split=c['birth_index'];T=c['birth_transport']
    A=_first_order_matrix(c['A0_diagonal']+Y*c['A1_diagonal'],c['A0_lower']+Y*c['A1_lower'])
    weights=c['proper_cell_weights'];G=diags(np.repeat(weights,m),format='csc')
    K=(A.conj().T@G@A).tocsc();R=c['source_right_map'].reshape(n*m,m)
    rhs=A.conj().T@(G@R);direct=splu(A).solve(R);full=splu(K).solve(rhs)
    interior=K[:-m,:-m].tocsc();IB=K[:-m,-m:].toarray();BI=K[-m:,:-m].toarray();BB=K[-m:,-m:].toarray()
    factor=splu(interior);dirichlet=factor.solve(rhs[:-m]);extension=-factor.solve(IB)
    schur=BB+BI@extension;boundary=np.linalg.solve(schur,rhs[-m:]-BI@dirichlet)
    returned=np.r_[extension@boundary,boundary];reconstructed=np.r_[dirichlet,np.zeros((m,m))]+returned
    L=np.asarray(c['target_left_map'],complex);weighted=weights[:,None,None]*L/2
    nodal=weighted.copy();nodal[:-1]+=weighted[1:]
    # The first child midpoint's preceding value is T times the parent
    # birth trace, so its left target uses the SAME canonical pullback.
    nodal[split-1]+=weighted[split]@(T-np.eye(m))
    target=nodal.transpose(1,0,2).reshape(m,n*m)
    dual=splu(A.T.tocsc()).solve(target.T)
    value=target@direct;dvalue=target[:,:-m]@dirichlet;rvalue=target@returned
    original=A@reconstructed-R;variational=K@reconstructed-rhs
    return dict(first_order_response=direct.reshape(n,m,m),squared_response=full.reshape(n,m,m),
        Dirichlet_interior_response=dirichlet.reshape(n-1,m,m),boundary_return_response=returned.reshape(n,m,m),
        boundary_Schur=schur,boundary_final_trace=boundary,boundary_Poisson_extension=extension,
        current_literal_target=target,current_source_right=R,source_transpose_adjoint=dual,
        current_total=value,current_Dirichlet_interior=dvalue,current_boundary_return=rvalue,
        first_order_identity_max=float(np.max(abs(full-direct))),
        boundary_reconstruction_identity_max=float(np.max(abs(reconstructed-direct))),
        current_boundary_decomposition_max=float(np.max(abs(value-dvalue-rvalue))),
        current_source_adjoint_max=float(np.max(abs(value-dual.T@R))),
        original_first_order_rows=original.reshape(n,m,m),squared_variational_rows=variational.reshape(n,m,m),
        actual_birth_canonical_trace=direct.reshape(n,m,m)[split-1],
        actual_outgoing_initial_trace=T@direct.reshape(n,m,m)[split-1],
        squared_birth_dual_row=variational.reshape(n,m,m)[split-1],
        squared_natural_final_face_row=variational.reshape(n,m,m)[-1],
        joined_initial_zero_only=True,outgoing_inverse_restarted_zero=False,
        identity='full current=Dirichlet interior current+Poisson/Schur boundary return on K=A†G_source A',
        finite_relative_return_is_full_P_strat_exterior_completion=False,
        physical_Pauli_or_finite_cutoff_readout_completed=False)
