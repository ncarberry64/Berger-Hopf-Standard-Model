"""Explicit cutoff derivative of the SAME chronological mean heat target."""
from __future__ import annotations
import numpy as np
from .muon_primal_cell_native_heat import actual_cell_even_y_target
from .muon_common_cutoff_green_kernel import common_total_cutoff_boundary_kernel
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def actual_cell_even_y_cutoff_target(polynomial,cutoff,*,series_terms=4):
    """Evaluate partial_c D Gamma at fixed actual fields and mean direction.

    For g=-exp(-c lambda)/lambda, partial_c g=exp(-c lambda),
    partial_c g[1]=-boundary_L2 and partial_c g[2]=boundary_L3.
    The same normalized Gram jets and sign-preserving eigenbasis are used.
    This is a partial derivative, not a physical branch cutoff jet.
    """
    t=actual_cell_even_y_target(polynomial,cutoff)
    c=float(cutoff);lam=t['normalized_P0_eigenvalues'];V=t['normalized_eigenvectors']
    C=t['normalized_P1'];B=t['normalized_P2']
    b2=common_total_cutoff_boundary_kernel(lam[:,None],lam[None,:],cutoff=c,terms=series_terms)
    b3=common_total_cutoff_boundary_kernel(lam[:,None,None],lam[None,:,None],lam[None,None,:],cutoff=c,terms=series_terms)
    first=-b2['value'];second=b3['value'];g=np.exp(-c*lam)
    D=first*C;Z=first*B+np.einsum('ijk,ij,jk->ik',second,C,C)
    Z=(Z+Z.conj().T)/2;D=(D+D.conj().T)/2
    d=[np.einsum('ij,bjk,kl->bil',V.conj().T,polynomial[k],V) for k in
        ('P0_raw_first_jet','P1_raw_first_jet','P2_raw_first_jet')]
    gradient=(np.einsum('ij,bji->b',Z,d[0])+np.einsum('ij,bji->b',D,d[1])+np.einsum('i,bii->b',g,d[2])).real
    value=float((g@np.diag(B).real+.5*np.sum(first*abs(C)**2)).real)
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;factor=Y[1]**2-Y[2]**2
    return dict(cutoff_probe=c,paired_middle_minus_light_cutoff_value_derivative=factor*value,
        paired_middle_minus_light_raw_cutoff_cotangent=factor*gradient,
        boundary_L2_positive_series_tail_upper=b2['positive_series_truncation_upper'],
        boundary_L3_positive_series_tail_upper=b3['positive_series_truncation_upper'],
        cutoff_derivative_is_partial_at_fixed_fields_and_mean=True,
        normalized_Gram_contacts_included=True,
        physical_cutoff_value_or_jet_selected=False,
        full_native_overlap_cutoff_cancellation_claimed=False,
        error_scope='exact-stored-spectrum boundary-kernel series tails only; target formation, binary contraction and physical domain errors excluded')
