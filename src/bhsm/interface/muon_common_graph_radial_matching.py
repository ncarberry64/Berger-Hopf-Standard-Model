"""Canonical radial source/adjoint on the original common n1 action graph."""
from __future__ import annotations
import numpy as np
from .muon_chronological_current_factor import factor_literal_current_chain,solve_literal_current_chain


def common_graph_radial_application(diagonal,upper,lower,right,left,*,birth_index,gauss_count,field_count):
    """Apply the complete boundary inverse with all Gauss/frame/corner rows.

    The left is an independently supplied analytic source. Both u=H^-1 R
    and p=H^-T L are evaluated; a source Gram is never used as a residue.
    All values/rates at the final natural face and the held initial reaction
    belong to the calling original graph, not a zero-Cauchy substitute.
    """
    D,U,L=map(np.asarray,(diagonal,upper,lower));R,SL=map(np.asarray,(right,left))
    n,d,_=D.shape
    if (R.ndim!=2 or R.shape[0]!=d or SL.shape!=R.shape or
        not 0<=birth_index<n or not 0<gauss_count<field_count<d):
        raise ValueError('complete original saddle and same radial birth sources required')
    rhs=np.zeros((n,d,R.shape[1]),complex);lhs=rhs.copy();rhs[birth_index]=R;lhs[birth_index]=SL
    fac=factor_literal_current_chain(D,U,L);u=solve_literal_current_chain(fac,rhs);p=solve_literal_current_chain(fac,lhs,transpose=True)
    def apply(x,transpose=False):
        if not transpose:
            y=np.einsum('nij,njc->nic',D,x);y[:-1]+=np.einsum('nij,njc->nic',U,x[1:]);y[1:]+=np.einsum('nij,njc->nic',L,x[:-1])
        else:
            y=np.einsum('nji,njc->nic',D,x);y[:-1]+=np.einsum('nji,njc->nic',L,x[1:]);y[1:]+=np.einsum('nji,njc->nic',U,x[:-1])
        return y
    residual=apply(u)-rhs;adjoint_residual=apply(p,True)-lhs
    green=SL.T@u[birth_index];check=p[birth_index].T@R
    return dict(full_field_response=u,full_literal_adjoint=p,
        canonical_radial_boundary_Green=green,independent_transpose_radial_Green=check,
        source_transpose_pairing_difference=green-check,
        original_dynamic_Gauss_frame_residual=residual,original_transpose_residual=adjoint_residual,
        original_Gauss_residual=residual[:,:gauss_count],original_frame_residual=residual[:,field_count:],
        named_frame_reactions=u[:,field_count:],final_natural_field=u[-1,:field_count],
        original_rows_retained=True,BRST_quotient_or_external_LSZ_claimed=False,
        source_Gram_division_used=False,zero_Cauchy_inverse_substituted=False)
