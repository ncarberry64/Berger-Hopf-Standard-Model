"""Source-directed n5 fermion return of the represented even-field loop.

Even field n4 times the constant external leg reaches fermion n4.
The magnetic n1 insertion can then reach fermion n5 and return through
the external n1 leg. This extends the internal source image, without
enlarging the starting odd/even field-loop domain or choosing a state.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import cholesky,eigh,solve_triangular
from .muon_even_source_temporal_fermion import integrated_fermion_weak_form
from .muon_intrinsic_scalar_discretization import (
    scalar_section_labels,scalar_angular_derivative_matrices,real_scalar_basis_transform)
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_source_directed_temporal_green import source_product_temporal_values


def n5_return_angular_blocks():
    labels=scalar_section_labels(5);ids=np.array([i for i,l in enumerate(labels)if l[0]==5])
    E=scalar_angular_derivative_matrices(5)[:,ids][:,:,ids]
    U=real_scalar_basis_transform(5)[np.ix_(ids,ids)]
    blocks=[dict(level=5,spectator=k,harmonic_indices=np.arange(6)*6+k)for k in range(6)]
    mask=np.ones((36,36),bool)
    for b in blocks:mask[np.ix_(b['harmonic_indices'],b['harmonic_indices'])]=False
    if np.any(E[:,mask]):raise ValueError('literal n5 Wigner spectator identity failed')
    return dict(complex_derivatives=E,real_to_complex=U,
        complex_harmonic_labels=[labels[i]for i in ids],angular_blocks=blocks,
        family_indices=[np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f])for f in range(3)],
        spectator_off_block_max=float(np.max(abs(E[:,mask]))))


def changing_n5_return_fermion_application(phase,*,length,quadrature_order=12,progress=None):
    L=float(length)
    if (not np.isfinite(L)or L<=0 or phase['receipt']['steps']!=1 or abs(phase['receipt']['span'])!=L
            or type(quadrature_order)is not int or quadrature_order<8):
        raise ValueError('same chronological one-cell magnetic return trial required')
    angular=n5_return_angular_blocks();z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    tf=source_product_temporal_values(times,L);alpha=lepton_current_hilbert_representation()['alpha']
    keep=np.zeros((18,18),bool)
    for f in angular['family_indices']:keep[np.ix_(f,f)]=True
    points=[]
    for u in times:
        t=float(u-L if phase['receipt']['side']=='incoming'else u)
        a=profile_preserving_lepton_sample(phase,t);op=a['operator']
        if np.any(op['W'][~keep])or np.any(op['Omega_tau'][~keep])or np.any(alpha[:,~keep]):
            raise ValueError('actual complete return operator mixes the fixed families')
        points.append(dict(N=op['N'],R=op['R4'],W=op['W'],Omega=op['Omega_tau'],t=t))
    N=np.array([a['N']for a in points]);measure=weights*N
    temporal=np.einsum('t,ta,tb->ab',measure,tf['value'],tf['value'])
    T=solve_triangular(cholesky(temporal,lower=True).T,np.eye(8),lower=False)
    p,dp=tf['value']@T,tf['coordinate_rate']@T;arrays=[];records=[]
    for family,fi in enumerate(angular['family_indices']):
        for b in angular['angular_blocks']:
            hi=b['harmonic_indices'];E=angular['complex_derivatives'][:,hi][:,:,hi]
            A=np.array([np.kron((a['W']+a['Omega'])[np.ix_(fi,fi)],np.eye(6))-1j*sum(
                np.kron(v[np.ix_(fi,fi)],e)for v,e in zip(alpha,E))/a['R']for a in points])
            f=integrated_fermion_weak_form(N,A,weights,p,dp);K,G=f['weak_form'],f['Gram']
            chol=cholesky(G,lower=True);P=solve_triangular(chol,K,lower=True)
            P=solve_triangular(chol,P.conj().T,lower=True).conj().T
            ev,V=eigh(P);U=solve_triangular(chol.conj().T,V,lower=False)
            if ev[0]<=0:raise ArithmeticError('n5 return failed positivity; no shift or deletion')
            record=dict(family=family,level=5,spectator=b['spectator'],dimension=288,
                minimum_generalized_eigenvalue=float(ev[0]),maximum_generalized_eigenvalue=float(ev[-1]),
                generalized_eigen_residual=float(np.linalg.norm(K@U-(G@U)*ev)/np.linalg.norm(K@U)),
                Gram_orthonormal_residual=float(np.linalg.norm(U.conj().T@G@U-np.eye(288))))
            arrays.append(dict(weak_form=K,Gram=G,eigenvectors=U,generalized_eigenvalues=ev,
                normalized_operator=P,harmonic_indices=hi,family_indices=fi))
            records.append(record)
            if progress is not None:progress(record)
    return dict(block_arrays=arrays,block_records=records,real_to_complex=angular['real_to_complex'],
        complex_derivatives=angular['complex_derivatives'],temporal_basis_values=p,
        temporal_basis_coordinate_rates=dp,source_temporal_Gram=temporal,source_temporal_congruence=T,
        chronological_quadrature_times=times,chronological_quadrature_weights=weights,
        coordinate_times=np.array([a['t']for a in points]),coefficient_N_R=np.array([[a['N'],a['R']]for a in points]),
        coefficient_W=np.array([a['W']for a in points]),coefficient_Omega=np.array([a['Omega']for a in points]),
        temporal_Gram_condition=float(np.linalg.cond(temporal)),full_n5_return_dimension=5184,
        full_n5_harmonic_count=36,spectator_off_block_max=angular['spectator_off_block_max'],
        starting_field_loop_domain_enlarged=False,source_return_not_filled_zero=True,
        physical_P_strat_or_LSZ_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None)
