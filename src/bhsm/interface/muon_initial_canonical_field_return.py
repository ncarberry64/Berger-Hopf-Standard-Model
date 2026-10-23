"""Initial canonical boundary correction on the original coupled field chain.

The full natural action inverse is used only as a computational Green.
Its final admissible dynamic source is solved to impose zero initial
canonical momentum.  Every At/Gauss and named frame row remains in the
original action; no final natural condition is silently retained as an IVP.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_solve
from .muon_chronological_current_factor import (
    factor_literal_current_chain, solve_literal_current_chain)
from .muon_native_reset_friedrichs_return import chain_apply


def named_admissible_dynamic_map(frame_rows, *, gauss_count, field_count):
    """Remove only the explicitly named coordinate frame constraints.

    These owner rows are coordinate selectors, not numerical small
    eigenvectors.  Their reaction cotangents remain available below.
    """
    C=np.asarray(frame_rows,complex)
    if (C.ndim!=2 or C.shape[1]!=field_count or not 0<=gauss_count<field_count
            or np.any(C[:,:gauss_count]) or not np.isfinite(C).all()):
        raise ValueError('explicit complete named frame rows and At count required')
    at=[]
    for row in C:
        nz=np.flatnonzero(row)
        if len(nz)!=1 or row[nz[0]]!=1:
            raise ValueError('the actual coordinate frame rows must be retained, not inferred')
        at.append(int(nz[0]))
    if len(set(at))!=len(at):raise ValueError('independent named frame coordinates required')
    ids=np.array([j for j in range(gauss_count,field_count)if j not in at],int)
    return dict(field_map=np.eye(field_count,dtype=complex)[:,ids],
        original_dynamic_indices=ids,named_frame_indices=np.array(at,int),
        numerical_null_eigenvectors_deleted=False)


def initial_canonical_field_return(diagonal,upper,lower,right,left,initial_to_first,
        *,frame_rows,gauss_count,field_count,consume_diagonal=False,
        evaluate_original_residual=True):
    """Solve the actual initial conormal by a small final-source map.

    F injects the final admissible dynamic force, C0=J.T H01 reads the
    opposite initial cotangent, and
      x_C=G b-G F (C0 G F)^-1 C0 G b.
    The independent analytic transpose is evaluated on this SAME inverse.
    A singular/ill-conditioned boundary map is reported, never regularized.
    This is a finite represented Cauchy-boundary application; its before-
    source defect determines whether a retarded interpretation is justified.
    """
    D,U,L=map(lambda a:np.asarray(a,complex),(diagonal,upper,lower))
    b,l=map(lambda a:np.asarray(a,complex),(right,left))
    H01=np.asarray(initial_to_first,complex)
    n,d,_=D.shape
    if (b.ndim!=3 or b.shape[:2]!=(n,d)or l.shape!=b.shape
            or not 0<gauss_count<field_count<d or H01.shape!=(field_count,field_count)):
        raise ValueError('all original source, transpose and initial action rows required')
    named=named_admissible_dynamic_map(frame_rows,gauss_count=gauss_count,field_count=field_count)
    J=named['field_map'];C0=J.T@H01
    fac=factor_literal_current_chain(D,U,L,consume_diagonal=consume_diagonal)
    natural=solve_literal_current_chain(fac,b)
    # Only the first block of G*F is needed.  Stream backwards through
    # the exact LU without materializing N*field_count*128 columns.
    F=np.zeros((d,J.shape[1]),complex);F[:field_count]=J
    LU,P=(fac[k]for k in('LU_diagonal','pivots'))
    GF0=lu_solve((LU[-1],P[-1]),F)
    for j in range(n-2,-1,-1):
        GF0=-lu_solve((LU[j],P[j]),U[j]@GF0)
    A=C0@GF0[:field_count]
    s=np.linalg.svd(A,compute_uv=False)
    amplitude=-np.linalg.solve(A,C0@natural[0,:field_count])
    correction_rhs=np.zeros_like(b);correction_rhs[-1]=F@amplitude
    returned=solve_literal_current_chain(fac,correction_rhs)
    causal=natural+returned
    pN=solve_literal_current_chain(fac,l,transpose=True)
    adjoint_amplitude=np.linalg.solve(A.T,F.T@pN[-1])
    adjoint_rhs=l.copy();adjoint_rhs[0,:field_count]-=C0.T@adjoint_amplitude
    pC=solve_literal_current_chain(fac,adjoint_rhs,transpose=True)
    current=np.einsum('nic,nij->cj',l,causal)
    transpose_current=np.einsum('nic,nij->cj',pC,b)
    initial_full=H01@causal[0,:field_count]
    out=dict(natural_response=natural,initial_canonical_response=causal,
        final_force_response=returned,initial_canonical_literal_adjoint=pC,
        final_dynamic_force=F@amplitude,final_dynamic_force_amplitude=amplitude,
        initial_admissible_conormal=C0@causal[0,:field_count],
        initial_complete_action_cotangent=initial_full,
        initial_Gauss_trace_cotangent=initial_full[:gauss_count],
        initial_named_frame_cotangent=np.asarray(frame_rows)@initial_full,
        initial_canonical_source_Green=current,independent_transpose_source_Green=transpose_current,
        source_transpose_pairing_difference=current-transpose_current,
        adjoint_initial_boundary_reaction=adjoint_amplitude,
        adjoint_final_admissible_trace=F.T@pC[-1],
        final_source_to_initial_conormal=A,
        final_source_to_initial_conormal_singular_values=s,
        final_source_to_initial_conormal_condition=float(s[0]/s[-1]),
        final_source_to_initial_conormal_numeric_rank=int(np.linalg.matrix_rank(A)),
        admissible_dynamic_map=J,original_dynamic_indices=named['original_dynamic_indices'],
        named_frame_indices=named['named_frame_indices'],
        original_final_natural_condition_replaced_by_initial_canonical_condition=True,
        every_original_Gauss_and_named_frame_row_retained=True,
        source_or_adjoint_coefficients_conjugated=False,
        finite_Cauchy_boundary_application_is_physical_retarded_response=False)
    if evaluate_original_residual:
        if consume_diagonal:raise ValueError('residual must read unconsumed original diagonal')
        out.update(original_action_rows=chain_apply(D,U,L,causal)-b,
            expected_original_action_boundary_rows=correction_rhs,
            original_transpose_rows=chain_apply(D.transpose(0,2,1),L.transpose(0,2,1),
                U.transpose(0,2,1),pC)-l,
            expected_original_transpose_boundary_rows=adjoint_rhs-l)
    return out
