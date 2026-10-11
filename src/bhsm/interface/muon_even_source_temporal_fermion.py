"""Complete even fermion image of the changing magnetic source application.

The n0/n2/n4 scalar angular images multiply all eighteen canonical fibers.
All eight independent source-directed temporal functions are retained.
Family and Wigner spectator identities reorganize the 5040-dimensional
form; they do not select a state, remove a numerical mode, or finish the
physical stratified operator or external Pauli matching.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import cholesky, eigh, solve_triangular

from .muon_even_coupled_temporal_field import complete_even_angular_blocks
from .muon_intrinsic_scalar_discretization import (
    real_scalar_basis_transform, scalar_section_labels, scalar_angular_derivative_matrices)
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_source_directed_temporal_green import source_product_temporal_values


def complete_even_fermion_blocks():
    """Entire even35 angular space, in literal complex Wigner spectators."""
    angular=complete_even_angular_blocks()
    labels=scalar_section_labels(4)
    ids=np.array([i for i,l in enumerate(labels)if l[0]in(0,2,4)])
    U=real_scalar_basis_transform(4)[np.ix_(ids,ids)]
    transformed=np.array([U@a@U.conj().T for a in angular['derivatives']])
    # Use the retained literal complex coefficient representation, whose
    # spectator zeros are structural. A rounded real/complex round trip
    # is measured separately, never thresholded into an exact zero.
    E=scalar_angular_derivative_matrices(4)[:,ids][:,:,ids]
    blocks=[];mask=np.ones((35,35),bool);offset=0
    for n in (0,2,4):
        for k in range(n+1):
            hi=offset+np.arange(n+1)*(n+1)+k
            blocks.append(dict(level=n,spectator=k,harmonic_indices=hi))
            mask[np.ix_(hi,hi)]=False
        offset+=(n+1)**2
    if np.any(E[:,mask]):
        raise ValueError('even angular operator violates its exact Wigner spectators')
    families=[np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f])for f in range(3)]
    return dict(complex_harmonic_labels=[labels[i]for i in ids],
        real_harmonic_labels=angular['harmonic_labels'],real_to_complex=U,
        complex_derivatives=E,angular_blocks=blocks,family_indices=families,
        spectator_off_block_max=float(np.max(abs(E[:,mask]))),
        real_to_complex_derivative_residual=float(np.linalg.norm(transformed-E)),
        complex_frame_unitary_residual=float(np.linalg.norm(U@U.conj().T-np.eye(35))))


def integrated_fermion_weak_form(N,operators,weights,values,rates):
    """Literal sampled integral Ndt (A V)^dagger(A V), not a frozen square.

    The temporal derivative is in the same coordinate as Ndt. Cross terms
    from changing/non-normal B remain in the weak form, including the
    one-sided source-tent rate. This ordinary finite calculation is also
    used by the actual phase application below.
    """
    N=np.asarray(N);B=np.asarray(operators);w=np.asarray(weights)
    p=np.asarray(values);dp=np.asarray(rates)
    if (N.ndim!=1 or not np.isrealobj(N)or np.any(N<=0)or w.shape!=N.shape
            or not np.isrealobj(w)or np.any(w<=0)or B.ndim!=3
            or B.shape[0]!=len(N)or B.shape[1]!=B.shape[2]
            or p.ndim!=2 or p.shape[0]!=len(N)or dp.shape!=p.shape
            or any(not np.isfinite(a).all()for a in(N,B,w,p,dp))):
        raise ValueError('finite positive same-clock measure and complete weak images required')
    d=B.shape[1];size=p.shape[1]*d;I=np.eye(d)
    K=np.zeros((size,size),complex);G=K.copy()
    for n,b,wt,v,dv in zip(N,B,w,p,dp):
        value=np.concatenate([a*I for a in v],axis=1)
        image=np.concatenate([da*I/n+a*b for a,da in zip(v,dv)],axis=1)
        K+=wt*n*(image.conj().T@image)
        G+=wt*n*(value.conj().T@value)
    return dict(weak_form=K,Gram=G)


def changing_even_fermion_application(phase,*,length,quadrature_order=12,progress=None):
    """Bind all5040 even source-image coordinates to one changing phase."""
    L=float(length)
    if (not np.isfinite(L)or L<=0 or phase['receipt']['steps']!=1
            or abs(phase['receipt']['span'])!=L or type(quadrature_order)is not int
            or quadrature_order<8):
        raise ValueError('same chronological one-cell source trial required')
    angular=complete_even_fermion_blocks();z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    tf=source_product_temporal_values(times,L)
    points=[];keep=np.zeros((18,18),bool)
    for f in angular['family_indices']:keep[np.ix_(f,f)]=True
    alpha=lepton_current_hilbert_representation()['alpha']
    if np.any(alpha[:,~keep]):raise ValueError('full canonical angular action mixes family blocks')
    for u in times:
        t=float(u-L if phase['receipt']['side']=='incoming'else u)
        a=profile_preserving_lepton_sample(phase,t);op=a['operator']
        if np.any(op['W'][~keep])or np.any(op['Omega_tau'][~keep]):
            raise ValueError('actual changing background does not preserve fixed families')
        points.append(dict(N=op['N'],R=op['R4'],W=op['W'],Omega=op['Omega_tau'],t=t,
            W_coordinate_rate_norm=np.linalg.norm(a['time_derivatives']['W']['coordinate_time']),
            inherited_clock_rate_norm=np.linalg.norm(a['time_derivatives']['W']['explicit_inherited_clock'])))
    N=np.array([a['N']for a in points]);measure=weights*N
    temporal=np.einsum('t,ta,tb->ab',measure,tf['value'],tf['value'])
    T=solve_triangular(cholesky(temporal,lower=True).T,np.eye(8),lower=False)
    p=tf['value']@T;dp=tf['coordinate_rate']@T
    arrays=[];records=[]
    for family,fi in enumerate(angular['family_indices']):
        for block in angular['angular_blocks']:
            hi=block['harmonic_indices'];d=6*len(hi);E=angular['complex_derivatives'][:,hi][:,:,hi]
            operators=np.array([np.kron((a['W']+a['Omega'])[np.ix_(fi,fi)],np.eye(len(hi)))-1j*sum(
                np.kron(v[np.ix_(fi,fi)],e)for v,e in zip(alpha,E))/a['R']for a in points])
            form=integrated_fermion_weak_form(N,operators,weights,p,dp)
            K,G=form['weak_form'],form['Gram'];chol=cholesky(G,lower=True)
            P=solve_triangular(chol,K,lower=True)
            P=solve_triangular(chol,P.conj().T,lower=True).conj().T
            ev,V=eigh(P);U=solve_triangular(chol.conj().T,V,lower=False)
            if ev[0]<=0:raise ArithmeticError('even form failed positivity; no shift or deletion')
            record=dict(family=family,level=block['level'],spectator=block['spectator'],dimension=8*d,
                minimum_generalized_eigenvalue=float(ev[0]),maximum_generalized_eigenvalue=float(ev[-1]),
                generalized_eigen_residual=float(np.linalg.norm(K@U-(G@U)*ev)/np.linalg.norm(K@U)),
                Gram_orthonormal_residual=float(np.linalg.norm(U.conj().T@G@U-np.eye(8*d))),
                normalized_symmetry_defect=float(np.linalg.norm(P-P.conj().T)/np.linalg.norm(P)))
            arrays.append(dict(weak_form=K,Gram=G,eigenvectors=U,generalized_eigenvalues=ev,
                normalized_operator=P,harmonic_indices=hi,family_indices=fi))
            records.append(record)
            if progress is not None:progress(record)
    return dict(block_arrays=arrays,block_records=records,
        real_to_complex=angular['real_to_complex'],complex_derivatives=angular['complex_derivatives'],
        temporal_basis_values=p,temporal_basis_coordinate_rates=dp,source_temporal_Gram=temporal,
        source_temporal_congruence=T,chronological_quadrature_times=times,
        chronological_quadrature_weights=weights,coordinate_times=np.array([a['t']for a in points]),
        coefficient_N_R=np.array([[a['N'],a['R']]for a in points]),
        coefficient_W=np.array([a['W']for a in points]),coefficient_Omega=np.array([a['Omega']for a in points]),
        coefficient_rate_norms=np.array([[a['W_coordinate_rate_norm'],a['inherited_clock_rate_norm']]for a in points]),
        temporal_Gram_condition=float(np.linalg.cond(temporal)),
        full_fermion_FE_dimension=5040,full_angular_harmonic_count=35,temporal_basis_count=8,
        spectator_off_block_max=angular['spectator_off_block_max'],
        real_to_complex_derivative_residual=angular['real_to_complex_derivative_residual'],
        complex_frame_unitary_residual=angular['complex_frame_unitary_residual'],
        numerical_rank_or_mode_deletion=False,variable_coefficient_differential_closure_claimed=False,
        physical_P_strat_or_LSZ_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None)
