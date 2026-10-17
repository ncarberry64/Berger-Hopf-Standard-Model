"""Joined unsquared finite causal D5 action, with its literal transpose.

The temporal operator retains every supplied field block. The once-only
Higgs bridge is a supplied low-rank action term, not a mass appended in
the D5 bulk. This finite causal prefix returns its final field remainder;
it does not select a physical outgoing annihilator or normalized trace.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import lu_factor, lu_solve


def original_radial_time_principal(point_time_principal, point_time_first,
        volume, volume_first, weights, radial_values, time_clifford):
    """Assemble the ORIGINAL coordinate-time coefficient, not Gamma_E.

    Source-density and source-principal contacts enter before any field
    elimination. The surface proper-phase clock belongs to K_E, not M_t.
    """
    T,dT,mu,dmu,w,B,G0=[np.asarray(a,complex) for a in
        (point_time_principal,point_time_first,volume,volume_first,weights,radial_values,time_clifford)]
    q,d,_=T.shape if T.ndim==3 else (0,0,0)
    if (T.shape!=(q,d,d) or dT.shape!=T.shape or mu.shape!=(q,) or dmu.shape!=mu.shape
            or w.shape!=mu.shape or B.ndim!=2 or B.shape[0]!=q or G0.shape!=(d,d)
            or not all(np.isfinite(a).all() for a in (T,dT,mu,dmu,w,B,G0))):
        raise ValueError('all original time principal, source-density and fixed radial tests required')
    M=np.einsum('q,qm,qn,qij->minj',w*mu,B,B,np.einsum('ij,qjk->qik',G0,T)).reshape(B.shape[1]*d,B.shape[1]*d)
    dM=np.einsum('q,qm,qn,qij->minj',w,B,B,
        np.einsum('ij,qjk->qik',G0,dmu[:,None,None]*T+mu[:,None,None]*dT)).reshape(M.shape)
    return dict(original_coordinate_time_action=M,coordinate_time_action_source=dM,
        field_elimination_energy_coefficient_not_used_as_time_mass=True)


def _block_apply(A, x):
    return np.einsum('bij,bj...->bi...', A, x)


def _joined_apply(A, C, S, B, x):
    trace = np.einsum('rbi,bi...->r...', B, x)
    return _block_apply(A, x)+np.einsum('bir,r...->bi...', C, S@trace)


def _joined_factor(A, C, S, B, *, transpose=False):
    if transpose:
        A, C, S, B = A.transpose(0, 2, 1), B.transpose(1, 2, 0), S.T, C.transpose(2, 0, 1)
    # Exact duplicate family blocks share a factor; no spectral quotient.
    unique, factors, block_ids = [], [], []
    for a in A:
        found = next((j for j,u in enumerate(unique) if np.array_equal(a,u)), None)
        if found is None:
            found = len(unique); unique.append(a); factors.append(lu_factor(a))
        block_ids.append(found)
    def block_solve(rhs):
        return np.array([lu_solve(factors[j], r) for j,r in zip(block_ids,rhs)])
    L = block_solve(C)
    small = np.eye(len(S), dtype=complex)+S@np.einsum('rbi,bis->rs', B, L)
    small_factor = lu_factor(small)
    def solve(rhs):
        q = block_solve(rhs)
        coefficient = lu_solve(small_factor, S@np.einsum('rbi,bi...->r...', B, q))
        return q-np.einsum('bir,r...->bi...', L, coefficient)
    return solve


def _validate(mass, zero, steps, seam_left, seam, seam_right, initial, sources, left):
    M, K, h, C, S, B, x, j, ell = [np.asarray(a,complex) for a in
        (mass,zero,steps,seam_left,seam,seam_right,initial,sources,left)]
    if M.ndim!=4 or M.shape[-1]!=M.shape[-2]:
        raise ValueError('all original full temporal field blocks required')
    nc,nb,d,_=M.shape; r=S.shape[-1] if S.ndim==3 else -1
    if (K.shape!=M.shape or h.shape!=(nc,) or np.any(h==0)
            or C.shape!=(nc,nb,d,r) or S.shape!=(nc,r,r) or B.shape!=(nc,r,nb,d)
            or x.ndim!=3 or x.shape[:2]!=(nb,d) or j.shape!=(nc,)+x.shape
            or ell.ndim!=3 or ell.shape[1:]!=(nb,d)
            or not all(np.isfinite(a).all() for a in (M,K,h,C,S,B,x,j,ell))):
        raise ValueError('same finite original blocks, seam, clocks, source columns and independent literal target required')
    return M,K,h,C,S,B,x,j,ell


def joined_d5_causal_prefix(mass, zero_order, steps, seam_left, seam_matrix,
        seam_right, initial_right, sources, final_literal_left):
    """Apply M xdot+(K0+C S B)x=J on each actual midpoint slab.

    Hcc_i=M_i+h_i K_i/2, Hcp_i=-M_i+h_i K_i/2 are independently
    produced unsquared action rows. Retarded support means no response
    before its supplied initial/source support. The analytic target is
    pulled by Hcc.T, never a Hilbert adjoint. Initial data and the final
    remainder are explicit; neither is replaced by a zero outer selector.
    """
    M,K,h,C,S,B,x,J,ell=_validate(mass,zero_order,steps,seam_left,seam_matrix,
        seam_right,initial_right,sources,final_literal_left)
    states=[x.copy()]; rows=[]
    for i in range(len(h)):
        A=M[i]+h[i]*K[i]/2; Q=M[i]-h[i]*K[i]/2
        solve=_joined_factor(A,C[i],h[i]*S[i]/2,B[i])
        rhs=_joined_apply(Q,C[i],-h[i]*S[i]/2,B[i],states[-1])+h[i]*J[i]
        after=solve(rhs)
        rows.append(_joined_apply(A,C[i],h[i]*S[i]/2,B[i],after)-rhs)
        states.append(after)
    adjoints=[None]*(len(h)+1); adjoints[-1]=ell.transpose(1,2,0).copy()
    dual_cells=[None]*len(h); dual_rows=[None]*len(h); source_returns=[]
    for i in range(len(h)-1,-1,-1):
        A=M[i]+h[i]*K[i]/2; Q=M[i]-h[i]*K[i]/2
        solve=_joined_factor(A,C[i],h[i]*S[i]/2,B[i],transpose=True)
        y=solve(adjoints[i+1]); dual_cells[i]=y
        dual_rows[i]=_joined_apply(A.transpose(0,2,1),B[i].transpose(1,2,0),
            h[i]*S[i].T/2,C[i].transpose(2,0,1),y)-adjoints[i+1]
        adjoints[i]=_joined_apply(Q.transpose(0,2,1),B[i].transpose(1,2,0),
            -h[i]*S[i].T/2,C[i].transpose(2,0,1),y)
    for i,y in enumerate(dual_cells):
        source_returns.append(h[i]*np.einsum('bil,bir->lr',y,J[i]))
    final=ell.reshape(len(ell),-1)@states[-1].reshape(-1,states[-1].shape[-1])
    birth=adjoints[0].reshape(-1,len(ell)).T@states[0].reshape(-1,states[0].shape[-1])
    source=sum(source_returns,np.zeros_like(final))
    return dict(field_states=np.asarray(states),literal_adjoint_states=np.asarray(adjoints),
        literal_transpose_cell_tests=np.asarray(dual_cells),original_causal_slab_rows=np.asarray(rows),
        original_literal_transpose_slab_rows=np.asarray(dual_rows),
        actual_initial_right=states[0],actual_final_field_remainder=states[-1],
        actual_final_literal_target=ell,returned_birth_literal_target=adjoints[0].transpose(2,0,1),
        actual_final_target_contraction=final,actual_birth_target_contraction=birth,
        complete_causal_source_return=source,per_slab_causal_source_return=np.asarray(source_returns),
        literal_causal_pairing_rows=final-birth-source,
        original_retarded_child_diagonal_blocks=M+h[:,None,None,None]*K/2,
        original_child_parent_coupling_blocks=-M+h[:,None,None,None]*K/2,
        original_once_only_seam_matrix=S,
        source_or_target_coefficients_conjugated=False,
        no_field_complement_deleted=True,finite_future_remainder_retained=True,
        physical_outgoing_annihilator_or_normalization_selected=False)


def joined_d5_causal_prefix_first(base, mass, zero_order, steps,
        seam_left, seam_matrix, seam_right, sources, *, mass_first,
        zero_order_first, steps_first, seam_left_first, seam_matrix_first,
        seam_right_first, initial_right_first, sources_first,
        final_literal_left_first):
    """Differentiate the SAME slab and both independent boundary maps.

    Every source/energy/domain operand is mandatory, including chart-owned
    exact zero firsts. No physical trace or outer derivative is inferred.
    """
    ell=base['actual_final_literal_target'];initial=base['actual_initial_right']
    M,K,h,C,S,B,_,J,_=_validate(mass,zero_order,steps,seam_left,seam_matrix,
        seam_right,initial,sources,ell)
    dM,dK,dh,dC,dS,dB,dx,dJ,dell=[np.asarray(a,complex) for a in
        (mass_first,zero_order_first,steps_first,seam_left_first,seam_matrix_first,
         seam_right_first,initial_right_first,sources_first,final_literal_left_first)]
    if any(a.shape!=b.shape for a,b in zip((dM,dK,dh,dC,dS,dB,dx,dJ,dell),
            (M,K,h,C,S,B,initial,J,ell))) or not all(np.isfinite(a).all() for a in (dM,dK,dh,dC,dS,dB,dx,dJ,dell)):
        raise ValueError('every finite same-domain slab/source/clock/independent-target first required')
    def seam_first(i,x):
        return (_joined_apply(np.zeros_like(M[i]),dC[i],S[i],B[i],x)
            +_joined_apply(np.zeros_like(M[i]),C[i],dS[i],B[i],x)
            +_joined_apply(np.zeros_like(M[i]),C[i],S[i],dB[i],x))
    def seam_transpose_first(i,x):
        zero=np.zeros_like(M[i])
        return (_joined_apply(zero,dB[i].transpose(1,2,0),S[i].T,C[i].transpose(2,0,1),x)
            +_joined_apply(zero,B[i].transpose(1,2,0),dS[i].T,C[i].transpose(2,0,1),x)
            +_joined_apply(zero,B[i].transpose(1,2,0),S[i].T,dC[i].transpose(2,0,1),x))
    xs=base['field_states']; first=[dx]; rows=[]
    for i in range(len(h)):
        A=M[i]+h[i]*K[i]/2; Q=M[i]-h[i]*K[i]/2
        before,after=xs[i],xs[i+1]
        dA=dM[i]+dh[i]*K[i]/2+h[i]*dK[i]/2
        dQ=dM[i]-dh[i]*K[i]/2-h[i]*dK[i]/2
        dAb=_block_apply(dA,after)+dh[i]*_joined_apply(np.zeros_like(M[i]),C[i],S[i],B[i],after)/2+h[i]*seam_first(i,after)/2
        dQb=_block_apply(dQ,before)-dh[i]*_joined_apply(np.zeros_like(M[i]),C[i],S[i],B[i],before)/2-h[i]*seam_first(i,before)/2
        rhs=_joined_apply(Q,C[i],-h[i]*S[i]/2,B[i],first[-1])+dQb-dAb+dh[i]*J[i]+h[i]*dJ[i]
        answer=_joined_factor(A,C[i],h[i]*S[i]/2,B[i])(rhs)
        rows.append(_joined_apply(A,C[i],h[i]*S[i]/2,B[i],answer)-rhs)
        first.append(answer)
    dtarget=dell.reshape(len(ell),-1)@xs[-1].reshape(-1,xs[-1].shape[-1])+ell.reshape(len(ell),-1)@first[-1].reshape(-1,first[-1].shape[-1])
    dal=[None]*(len(h)+1);dal[-1]=dell.transpose(1,2,0)
    dycells=[None]*len(h);dualrows=[None]*len(h)
    for i in range(len(h)-1,-1,-1):
        A=M[i]+h[i]*K[i]/2;Q=M[i]-h[i]*K[i]/2
        y=base['literal_transpose_cell_tests'][i]
        dA=dM[i]+dh[i]*K[i]/2+h[i]*dK[i]/2
        dQ=dM[i]-dh[i]*K[i]/2-h[i]*dK[i]/2
        seamT=_joined_apply(np.zeros_like(M[i]),B[i].transpose(1,2,0),S[i].T,C[i].transpose(2,0,1),y)
        dy_rhs=dal[i+1]-_block_apply(dA.transpose(0,2,1),y)-dh[i]*seamT/2-h[i]*seam_transpose_first(i,y)/2
        dy=_joined_factor(A,C[i],h[i]*S[i]/2,B[i],transpose=True)(dy_rhs)
        dycells[i]=dy
        dualrows[i]=_joined_apply(A.transpose(0,2,1),B[i].transpose(1,2,0),h[i]*S[i].T/2,C[i].transpose(2,0,1),dy)-dy_rhs
        dal[i]=(_joined_apply(Q.transpose(0,2,1),B[i].transpose(1,2,0),-h[i]*S[i].T/2,C[i].transpose(2,0,1),dy)
            +_block_apply(dQ.transpose(0,2,1),y)-dh[i]*seamT/2-h[i]*seam_transpose_first(i,y)/2)
    dsource=sum((dh[i]*np.einsum('bil,bir->lr',y,J[i])+h[i]*np.einsum('bil,bir->lr',dycells[i],J[i])
        +h[i]*np.einsum('bil,bir->lr',y,dJ[i]) for i,y in enumerate(base['literal_transpose_cell_tests'])),np.zeros_like(dtarget))
    dbirth=dal[0].reshape(-1,len(ell)).T@initial.reshape(-1,initial.shape[-1])+base['literal_adjoint_states'][0].reshape(-1,len(ell)).T@dx.reshape(-1,dx.shape[-1])
    return dict(field_state_firsts=np.asarray(first),actual_final_field_remainder_first=first[-1],
        original_causal_slab_first_rows=np.asarray(rows),actual_final_target_contraction_first=dtarget,
        literal_adjoint_state_firsts=np.asarray(dal),literal_transpose_cell_test_firsts=np.asarray(dycells),
        original_literal_transpose_slab_first_rows=np.asarray(dualrows),
        returned_birth_literal_target_first=dal[0].transpose(2,0,1),
        actual_birth_target_contraction_first=dbirth,complete_causal_source_return_first=dsource,
        literal_causal_pairing_first_rows=dtarget-dbirth-dsource,
        both_boundary_source_clock_and_seam_firsts_retained=True,
        physical_outer_or_normal_trace_first_not_inferred_zero=True)
