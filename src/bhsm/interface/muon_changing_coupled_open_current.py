"""Changing same-phase fermion/field Green and literal open insertions.

The source adjoint is applied before the fermion inverse.  One coupled
gauge/Higgs field form is consumed.  The finite product reference and its
Gaussian open exchange are not identified with the completed P_strat or
with an interacting pole, statistics completion, or normalized Pauli form.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import cholesky,eigh,solve,solve_triangular

from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_corrected_profile_magnetic_response import corrected_wall_reference
from .muon_parent_positive_coupled_field import coupled_wall_maps
from .muon_parent_positive_coupled_temporal import paired_scalar_orbit_maps
from .muon_parent_positive_brst_ghost import smooth_ghost_temporal_values,ghost_radial_values
from .muon_parent_retarded_hypercharge import WALL
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_intrinsic_scalar_temporal_image import temporal_image_green_kernel


def positive_factor_open_vertices(radius,lapse):
    """Unit action vertices for A=partial_t/N+Omega_tau+W.

    The temporal connection is anti-Hermitian in A. Its Lorentz Hcan
    counterpart has the extra -i, so this conversion is explicit.
    """
    vertices=canonical_open_field_vertices(radius,lapse)
    gauge=vertices['gauge'].copy();gauge[0]*=1j
    return dict(gauge=gauge,scalar=vertices['scalar'].copy())


def literal_source_pairings(trial,acted_trial,source,weight):
    """Two distinct placements of a literal, possibly non-Hermitian vertex.

    source[h,field,i,j] acts internal i <- external j on the right and
    external i <- internal j on the left.  No Hermitian replacement of
    the temporal gauge vertex is made. acted_trial=A V, hence the right
    pairing is (A V)^dagger source, not A^dagger after an inverse.
    """
    V=np.asarray(trial);AV=np.asarray(acted_trial);S=np.asarray(source);w=float(weight)
    if (V.ndim!=2 or AV.shape!=V.shape or S.ndim!=4 or S.shape[2]!=S.shape[3]
        or V.shape[0]!=S.shape[0]*S.shape[2] or not np.isfinite(w)
        or any(not np.isfinite(a).all() for a in (V,AV,S))):
        raise ValueError('complete same source/trial/action pairings required')
    h,a,n,_=S.shape
    right=S.transpose(2,0,3,1).reshape(n*h,n,a)
    left=S.transpose(2,3,0,1).reshape(n,n*h,a)
    return dict(left=w*np.einsum('iJa,JI->iIa',left,V),
        right=w*(AV.conj().T@right.reshape(n*h,-1)).reshape(V.shape[1],n,a),
        value=w*(V.conj().T@right.reshape(n*h,-1)).reshape(V.shape[1],n,a))


def _point(phase,u,L,angular):
    origin=-L if phase['receipt']['side']=='incoming' else 0.;t=float(u+origin)
    sample=profile_preserving_lepton_sample(phase,t);op=sample['operator'];raw=sample['sample']['raw_fields']
    kw={}
    if phase['receipt']['side']=='outgoing':kw=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
    wall=corrected_wall_reference(raw,phase['representation'],coordinate_time=t,**kw)['background_values'][0]
    E=np.asarray(angular['derivative_matrices']);N,R=op['N'],op['R4'];I=np.eye(360)
    alpha=lepton_current_hilbert_representation()['alpha']
    W=np.kron(op['W'],np.eye(20))-1j*sum(np.kron(a,e)for a,e in zip(alpha,E))/R
    O=np.kron(op['Omega_tau'],np.eye(20))
    b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else -2/L
    values=np.array([b,b*b]);rates=np.array([bp,2*b*bp])
    V=np.concatenate([v*I for v in values],axis=1)
    AV=np.concatenate([d*I/N+v*(W+O)for v,d in zip(values,rates)],axis=1)
    ghost=smooth_ghost_temporal_values(np.array([u]),L)[0]
    tf=np.array([b,bp,ghost[0,0],ghost[0,1],ghost[1,0],ghost[1,1]])
    wm=coupled_wall_maps(wall,E,length=L)['wall_time_profile_value_maps']
    gauge=np.zeros((400,1200));gauge[:,:1120]=np.einsum('t,tij->ij',tf,wm)
    scalar=paired_scalar_orbit_maps(raw[-8:-4],raw[-4:],tf,ghost_radial_values(np.array([WALL]))[0])['value']
    vertices=positive_factor_open_vertices(R,N)
    vertex=np.concatenate((vertices['gauge'].reshape(20,18,18),vertices['scalar']))
    fields=np.concatenate((gauge,scalar)).reshape(24,20,1200)
    source=np.einsum('chf,cij->hfij',fields,vertex)
    return dict(V=V,AV=AV,source=source,b=b,N=N,R=R,W=W,Omega=O,
        W_coordinate_rate_norm=np.linalg.norm(sample['time_derivatives']['W']['coordinate_time']),
        inherited_clock_rate_norm=np.linalg.norm(sample['time_derivatives']['W']['explicit_inherited_clock']))


def changing_coupled_open_current_application(phase,angular,field_Hessian,field_Gram,*,
        length,quadrature_order,cutoff,field_block_size=48):
    """Apply both Green factors and complete literal open-field insertions.

    The left and right source moments are integrated independently on
    the same chronological nodes as the coupled1200 field form. The
    common total-time cutoff kernel is applied after Gram congruences.
    The source Hilbert projection remainder is evaluated directly,
    rather than subtracted from two nearly equal norms.
    """
    L=float(length);c=float(cutoff);KB=np.asarray(field_Hessian);GB=np.asarray(field_Gram)
    if (KB.shape!=(1200,1200)or GB.shape!=KB.shape or any(not np.isrealobj(a)or not np.isfinite(a).all()for a in(KB,GB))
        or not np.isfinite([L,c]).all()or L<=0 or c<0 or phase['receipt']['steps']!=1
        or abs(phase['receipt']['span'])!=L or type(quadrature_order)is not int or quadrature_order<6
        or type(field_block_size)is not int or field_block_size<1):
        raise ValueError('same complete coupled form and chronological one-cell trial required')
    z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    K=np.zeros((720,720),complex);G=K.copy();left=np.zeros((18,720,1200),complex);right=np.zeros((720,18,1200),complex);value=right.copy()
    external_norm=0.;snapshots=[]
    for u,weight in zip(times,weights):
        p=_point(phase,u,L,angular);V,AV,N,b=p['V'],p['AV'],p['N'],p['b']
        K+=weight*N*(AV.conj().T@AV);G+=weight*N*(V.conj().T@V)
        s=literal_source_pairings(V,AV,p['source'],weight*N*b)
        left+=s['left'];right+=s['right'];value+=s['value'];external_norm+=weight*N*b*b
        snapshots.append((u,N,p['R'],p['W_coordinate_rate_norm'],p['inherited_clock_rate_norm']))
    scale=np.sqrt(external_norm);left/=scale;right/=scale;value/=scale
    # The exact finite temporal Gram is shared by all360 angular/fiber entries.
    temporal=G[np.ix_([0,360],[0,360])].real
    coeff=(solve(temporal,value.reshape(2,360,-1).reshape(2,-1),assume_a='gen')).reshape(2,360,18,1200)
    projection=np.zeros(1200);source_norm=np.zeros(1200)
    for u,weight in zip(times,weights):
        p=_point(phase,u,L,angular);b=p['b'];source=p['source'].transpose(2,0,3,1).reshape(360,18,1200)*b/scale
        fitted=b*coeff[0]+b*b*coeff[1];residual=source-fitted
        projection+=weight*p['N']*np.sum(abs(residual)**2,axis=(0,1));source_norm+=weight*p['N']*np.sum(abs(source)**2,axis=(0,1))
    cf=cholesky(G,lower=True);PF=solve_triangular(cf,K,lower=True);PF=solve_triangular(cf,PF.conj().T,lower=True).conj().T
    lamF,VF=eigh(PF);UF=solve_triangular(cf.conj().T,VF,lower=False)
    cb=cholesky(GB,lower=True);PB=solve_triangular(cb,KB,lower=True);PB=solve_triangular(cb,PB.T,lower=True).T
    lamB,VB=eigh(PB);UB=solve_triangular(cb.T,VB,lower=False)
    if min(lamF[0],lamB[0])<=0:raise ArithmeticError('same finite positive forms required; no spectral shift')
    exchange=np.zeros((18,18),complex)
    max_kernel_error=0.
    for start in range(0,1200,field_block_size):
        stop=min(start+field_block_size,1200);ub=UB[:,start:stop]
        l=(left.reshape(-1,1200)@ub).reshape(18,720,-1)
        l=np.einsum('iJa,JI->iIa',l,UF)
        r=(right.reshape(-1,1200)@ub).reshape(720,18,-1)
        r=(UF.conj().T@r.reshape(720,-1)).reshape(r.shape)
        kernel=temporal_image_green_kernel(lamF[:,None],lamB[None,start:stop],cutoff=c)
        exchange-=np.einsum('iIa,Ija,Ia->ij',l,r,kernel['value'])
        max_kernel_error=max(max_kernel_error,float(kernel['kernel_approximation_upper']))
    return dict(fermion_weak_form=K,fermion_proper_time_Gram=G,
        fermion_normalized_operator=PF,fermion_generalized_eigenvalues=lamF,fermion_Gram_orthonormal_eigenvectors=UF,
        field_generalized_eigenvalues=lamB,field_Gram_orthonormal_eigenvectors=UB,
        literal_left_vertex_map=left,source_adjoint_right_vertex_map=right,source_value_projection_map=value,
        source_projection_residual_norm_squared=projection,source_norm_squared=source_norm,
        signed_gaussian_open_exchange=exchange,
        external_tent_Gram=float(external_norm),chronological_quadrature_samples=np.array(snapshots),cutoff=c,
        source_projection_relative_norm=float(np.sqrt(np.sum(projection)/np.sum(source_norm))),
        independent_scalar_source_projection_relative_norm=float(np.sqrt(np.sum(projection[1120:])/np.sum(source_norm[1120:]))),
        temporal_derivative_images_retained=True,positive_temporal_vertex_matches_factor=True,
        fermion_source_adjoint_before_inverse=True,literal_non_Hermitian_left_placement=True,
        one_coupled_field_inverse=True,full_odd_angular_image_dimension=360,fermion_FE_dimension=720,
        source_product_projection_is_full_differential_domain_closure=False,
        common_kernel_approximation_upper=max_kernel_error,
        fermion_generalized_eigen_residual=float(np.linalg.norm(K@UF-(G@UF)*lamF)/np.linalg.norm(K@UF)),
        field_generalized_eigen_residual=float(np.linalg.norm(KB@UB-(GB@UB)*lamB)/np.linalg.norm(KB@UB)),
        normalized_fermion_symmetry_defect=float(np.linalg.norm(PF-PF.conj().T)/np.linalg.norm(PF)),
        physical_P_strat_statistics_or_LSZ_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None)
