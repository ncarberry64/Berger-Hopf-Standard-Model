"""Source-directed temporal enrichment on the changing finite field core.

The polynomial source products, rather than a numerical singular vector,
choose the trial functions.  Family and Wigner spectator reductions are
literal invariant blocks of this homogeneous angular background.  Neither
the remaining projection norm nor this Gaussian reference exchange is an
interacting soft Pauli or completed stratified quantum observable.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.legendre import Legendre
from scipy.linalg import cholesky, eigh, solve, solve_triangular

from .muon_changing_coupled_open_current import positive_factor_open_vertices
from .muon_corrected_profile_magnetic_response import corrected_wall_reference
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_parent_positive_coupled_field import coupled_wall_maps
from .muon_parent_positive_coupled_temporal import paired_scalar_orbit_maps
from .muon_parent_positive_brst_ghost import smooth_ghost_temporal_values, ghost_radial_values
from .muon_intrinsic_scalar_discretization import real_scalar_basis_transform, scalar_section_labels
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_intrinsic_scalar_temporal_image import temporal_image_green_kernel
from .muon_parent_retarded_hypercharge import WALL


def source_product_temporal_values(times, length):
    """b*P_k(2u/L-1), k=0..6, plus b², and literal coordinate rates.

    The seven polynomial functions contain b*g_i, b*g_i', u*b*g_i
    for both retained degree-four/five ghost bubbles, and the affine
    scalar-H products. b² is independent because b has an interior kink.
    There is no sampled-rank deletion. Coefficient functions 1/N, 1/R and
    the inherited connection still have their measured projection residual.
    """
    t=np.asarray(times);L=float(length)
    if t.ndim!=1 or not np.isrealobj(t) or not np.isfinite(t).all() or not np.isfinite(L) or L<=0 or np.any(t<0) or np.any(t>L):
        raise ValueError('same finite chronological source interval required')
    x=2*t/L-1;b=1-abs(x);bp=np.where(t<L/2,2/L,-2/L)
    values=[];rates=[]
    for k in range(7):
        p=Legendre.basis(k);v=p(x)
        values.append(b*v);rates.append(bp*v+b*p.deriv()(x)*2/L)
    values.append(b*b);rates.append(2*b*bp)
    return dict(value=np.array(values).T,coordinate_rate=np.array(rates).T,
        labels=['b*P'+str(k)for k in range(7)]+['b²'],
        source_product_polynomial_image_exact=True,variable_coefficient_image_exact=False,
        interior_kink_rate_scope='one-sided at the midpoint; weak derivative away from that measure-zero face')


def invariant_source_blocks(angular):
    """Exact family and complex-Wigner spectator subspaces, no small-mode cut."""
    labels=scalar_section_labels(3);ids=[i for i,l in enumerate(labels)if l[0]in(1,3)]
    U=real_scalar_basis_transform(3)[np.ix_(ids,ids)]
    E=np.array([U@a@U.conj().T for a in angular['derivative_matrices']])
    blocks=[];mask=np.ones((20,20),bool)
    for n,offset in ((1,0),(3,4)):
        for spectator in range(n+1):
            h=np.array([offset+m*(n+1)+spectator for m in range(n+1)])
            mask[np.ix_(h,h)]=False
            blocks.append(dict(level=n,spectator=spectator,harmonic_indices=h))
    if np.any(E[:,mask]):raise ValueError('background angular derivative does not preserve the literal Wigner spectators')
    families=[np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f])for f in range(3)]
    return dict(real_to_complex=U,complex_derivatives=E,angular_blocks=blocks,family_indices=families,
        spectator_off_block_max=float(np.max(abs(E[:,mask]))),unitary_residual=float(np.linalg.norm(U@U.conj().T-np.eye(20))))


def _source_point(phase,u,L,angular,blocks):
    t=float(u-L if phase['receipt']['side']=='incoming'else u)
    a=profile_preserving_lepton_sample(phase,t);raw=a['sample']['raw_fields'];op=a['operator']
    kwargs={}
    if phase['receipt']['side']=='outgoing':kwargs=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
    wall=corrected_wall_reference(raw,phase['representation'],coordinate_time=t,**kwargs)['background_values'][0]
    b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else-2/L
    g=smooth_ghost_temporal_values(np.array([u]),L)[0]
    tf=np.array([b,bp,g[0,0],g[0,1],g[1,0],g[1,1]])
    maps=coupled_wall_maps(wall,angular['derivative_matrices'],length=L)['wall_time_profile_value_maps']
    gauge=np.zeros((400,1200));gauge[:,:1120]=np.einsum('t,tij->ij',tf,maps)
    scalar=paired_scalar_orbit_maps(raw[-8:-4],raw[-4:],tf,ghost_radial_values(np.array([WALL]))[0])['value']
    fields=np.concatenate((gauge,scalar)).reshape(24,20,1200)
    right=np.einsum('gh,chf->cgf',blocks['real_to_complex'],fields)
    left=np.einsum('gh,chf->cgf',blocks['real_to_complex'].conj(),fields)
    v=positive_factor_open_vertices(op['R4'],op['N'])
    vertices=np.concatenate((v['gauge'].reshape(20,18,18),v['scalar']))
    keep=np.zeros((18,18),bool)
    for f in blocks['family_indices']:keep[np.ix_(f,f)]=True
    if np.any(op['W'][~keep])or np.any(op['Omega_tau'][~keep])or np.any(vertices[:,~keep]):
        raise ValueError('actual lepton source/background violates the fixed-family block')
    return dict(N=op['N'],R=op['R4'],W=op['W'],Omega=op['Omega_tau'],
        left_fields=left,right_fields=right,vertices=vertices,b=b,
        W_coordinate_rate_norm=np.linalg.norm(a['time_derivatives']['W']['coordinate_time']),
        inherited_clock_rate_norm=np.linalg.norm(a['time_derivatives']['W']['explicit_inherited_clock']))


def source_directed_temporal_exchange(phase,angular,field_eigenvalues,field_eigenvectors,*,length,quadrature_order=12,cutoff=1e-11,field_block_size=48,progress=None):
    """Enrich the actual source image before the fermion inverse.

    The coupled field spectrum remains one complete1200 form. The fermion
    trials contain all18 components and all odd20 angular harmonics through
    the exact family/spectator decomposition. Each source moment is literal;
    temporal At remains anti-Hermitian on the positive factor side.
    """
    L=float(length);c=float(cutoff);lb=np.asarray(field_eigenvalues);UB=np.asarray(field_eigenvectors)
    if (lb.shape!=(1200,)or UB.shape!=(1200,1200)or not np.isrealobj(lb)or not np.isrealobj(UB)
        or any(not np.isfinite(a).all()for a in(lb,UB))or np.min(lb)<=0 or not np.isfinite([L,c]).all()or L<=0 or c<0
        or phase['receipt']['steps']!=1 or abs(phase['receipt']['span'])!=L
        or type(quadrature_order)is not int or quadrature_order<8 or type(field_block_size)is not int or field_block_size<1):
        raise ValueError('complete positive coupled field spectrum and same one-cell source trial required')
    blocks=invariant_source_blocks(angular);z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    tf=source_product_temporal_values(times,L);p=tf['value'];dp=tf['coordinate_rate']
    points=[_source_point(phase,u,L,angular,blocks)for u in times]
    measure=weights*np.array([a['N']for a in points]);extnorm=float(measure@np.array([a['b']**2 for a in points]));extscale=np.sqrt(extnorm)
    temporal=np.einsum('t,ta,tb->ab',measure,p,p);conditioning=float(np.linalg.cond(temporal))
    ct=cholesky(temporal,lower=True);T=solve_triangular(ct.T,np.eye(8),lower=False)
    # Invertible congruence preconditions all8 proved independent functions.
    p=p@T;dp=dp@T
    alpha=lepton_current_hilbert_representation()['alpha']
    exchange=np.zeros((18,18),complex);projection=np.zeros(1200);norm=np.zeros(1200);records=[];eigen=[];forms=[];maxkernel=0.
    for family,fi in enumerate(blocks['family_indices']):
        for ab in blocks['angular_blocks']:
            hi=ab['harmonic_indices'];d=6*len(hi);size=8*d;I=np.eye(d)
            KF=np.zeros((size,size),complex);GF=KF.copy();left=np.zeros((6,size,1200),complex);right=np.zeros((size,6,1200),complex);value=right.copy();actual=[]
            for j,a in enumerate(points):
                E=blocks['complex_derivatives'][:,hi][:,:,hi]
                W=np.kron(a['W'][np.ix_(fi,fi)],np.eye(len(hi)))-1j*sum(np.kron(v[np.ix_(fi,fi)],e)for v,e in zip(alpha,E))/a['R']
                A=W+np.kron(a['Omega'][np.ix_(fi,fi)],np.eye(len(hi)))
                V=np.concatenate([v*I for v in p[j]],axis=1);AV=np.concatenate([r*I/a['N']+v*A for v,r in zip(p[j],dp[j])],axis=1)
                sr=np.einsum('chf,cij->hfij',a['right_fields'][:,hi],a['vertices'][:,fi][:,:,fi])
                sl=np.einsum('chf,cij->hfij',a['left_fields'][:,hi],a['vertices'][:,fi][:,:,fi])
                R=sr.transpose(2,0,3,1).reshape(d,6,1200)*a['b']/extscale
                B=sl.transpose(2,3,0,1).reshape(6,d,1200)*a['b']/extscale
                KF+=measure[j]*(AV.conj().T@AV);GF+=measure[j]*(V.conj().T@V)
                right+=measure[j]*(AV.conj().T@R.reshape(d,-1)).reshape(size,6,1200)
                value+=measure[j]*(V.conj().T@R.reshape(d,-1)).reshape(size,6,1200)
                left+=measure[j]*np.einsum('iJa,JI->iIa',B,V);actual.append(R)
            coefficients=value.reshape(8,d,6,1200)
            for j,R in enumerate(actual):
                residual=R-np.einsum('t,thja->hja',p[j],coefficients)
                projection+=measure[j]*np.sum(abs(residual)**2,axis=(0,1));norm+=measure[j]*np.sum(abs(R)**2,axis=(0,1))
            cf=cholesky(GF,lower=True);PF=solve_triangular(cf,KF,lower=True);PF=solve_triangular(cf,PF.conj().T,lower=True).conj().T
            lf,VF=eigh(PF);UF=solve_triangular(cf.conj().T,VF,lower=False)
            if lf[0]<=0:raise ArithmeticError('enriched positive form failed; no spectrum shift or rank deletion')
            local=np.zeros((6,6),complex)
            for start in range(0,1200,field_block_size):
                end=min(start+field_block_size,1200);ub=UB[:,start:end]
                l=(left.reshape(-1,1200)@ub).reshape(6,size,-1);l=np.einsum('iJa,JI->iIa',l,UF)
                r=(right.reshape(-1,1200)@ub).reshape(size,6,-1);r=(UF.conj().T@r.reshape(size,-1)).reshape(r.shape)
                kernel=temporal_image_green_kernel(lf[:,None],lb[None,start:end],cutoff=c)
                local-=np.einsum('iIa,Ija,Ia->ij',l,r,kernel['value']);maxkernel=max(maxkernel,float(kernel['kernel_approximation_upper']))
            exchange[np.ix_(fi,fi)]+=local
            record=dict(family=family,level=ab['level'],spectator=ab['spectator'],dimension=size,
                minimum_generalized_eigenvalue=float(lf[0]),generalized_eigen_residual=float(np.linalg.norm(KF@UF-(GF@UF)*lf)/np.linalg.norm(KF@UF)),exchange_norm=float(np.linalg.norm(local)))
            records.append(record);eigen.append(lf);forms.append(dict(weak_form=KF,Gram=GF,eigenvectors=UF));
            if progress is not None:progress(record)
    return dict(signed_gaussian_open_exchange=exchange,source_projection_residual_norm_squared=projection,source_norm_squared=norm,
        source_projection_relative_norm=float(np.sqrt(projection.sum()/norm.sum())),independent_scalar_projection_relative_norm=float(np.sqrt(projection[1120:].sum()/norm[1120:].sum())),
        external_tent_Gram=extnorm,source_temporal_Gram=temporal,source_temporal_congruence=T,temporal_Gram_condition=conditioning,
        temporal_basis_count=8,total_fermion_FE_dimension=2880,maximum_invariant_block_dimension=192,
        block_records=records,block_eigenvalues=eigen,block_forms=forms,chronological_quadrature_times=times,chronological_quadrature_weights=weights,
        spectator_off_block_max=blocks['spectator_off_block_max'],complex_frame_unitary_residual=blocks['unitary_residual'],common_kernel_approximation_upper=maxkernel,
        independent_source_polynomial_products_retained=True,variable_coefficient_image_closure_claimed=False,
        numerical_rank_deletion=False,one_coupled_field_inverse=True,completed_P_strat_or_LSZ_Pauli=False,physical_a_mu=None,physical_g_mu=None)
