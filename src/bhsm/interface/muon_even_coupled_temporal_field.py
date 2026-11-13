"""Complete even angular field image on the same changing phase.

The n0+n2+n4 image of the retained n1 magnetic direction is integrated
with the literal coupled gauge/Higgs point form before any inverse. The
real Wigner |k| spectators only reorganize the full2100 coordinates.
This declared positive ADM component is not asserted to be full P_strat.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import cholesky,cho_solve,eigh,solve,solve_triangular
from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
from .muon_coupled_field_angular_images import one_form_angular_point,intrinsic_coupled_angular_point
from .muon_parent_positive_coupled_field import corrected_positive_parent_reference
from .muon_parent_positive_brst_ghost import ghost_radial_values,smooth_ghost_temporal_values
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_positive_gauge_form import stored_inverse_neumann_majorant
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_corrected_profile_magnetic_response import corrected_wall_reference
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .muon_parent_retarded_hypercharge import WALL


def complete_even_angular_blocks():
    """All35 scalar harmonics and exact real |k| invariant blocks."""
    scalar=scalar_s3_discretization(4)
    ids=np.array([i for i,l in enumerate(scalar['real_basis_labels'])if l[0]in(0,2,4)])
    labels=[scalar['real_basis_labels'][i]for i in ids]
    E=scalar['real_angular_derivative_matrices'][:,ids][:,:,ids]
    blocks=[];mask=np.ones((35,35),bool)
    for n in (0,2,4):
        for k in range(0,n+1,2):
            hi=np.array([i for i,l in enumerate(labels)if l[0]==n and abs(l[2])==k])
            mask[np.ix_(hi,hi)]=False
            blocks.append(dict(level=n,absolute_spectator=k,harmonic_indices=hi,
                field_indices=(np.arange(60)[:,None]*35+hi).ravel(),derivatives=E[:,hi][:,:,hi]))
    if np.any(E[:,mask]):raise ValueError('real right coframe mixes the declared exact |k| spectators')
    return dict(harmonic_labels=labels,derivatives=E,blocks=blocks,
        full_harmonic_count=35,full_coupled_coordinate_count=2100,off_block_derivative_max=float(np.max(abs(E[:,mask]))))


def changing_even_coupled_field_application(phase,*,length,quadrature_order=6,progress=None):
    """Integrate the changing complete even gauge/H action and Lorenz map.

    Each angular block contains the full gauge, dependent DG scalar and
    independent scalar coordinates. Curvature/off-shell DH contacts are
    retained. The inverse is joint in those sectors; the only decomposition
    is the exact homogeneous angular spectator identity.
    """
    L=float(length);r=phase['receipt']
    if not np.isfinite(L)or L<=0 or r['steps']!=1 or abs(r['span'])!=L or type(quadrature_order)is not int or quadrature_order<6:
        raise ValueError('same complete chronological one-cell field trial required')
    rep=phase['representation'];nu=r['action_parameters']['nu_squared_action'];lam=rep['scalar_matching']['lambda_H']
    if nu is None:raise ValueError('explicit same action member nu squared is required')
    angular=complete_even_angular_blocks();z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    gs=smooth_ghost_temporal_values(times,L);radial=ghost_radial_values(rep['rho']);wrad=ghost_radial_values(np.array([WALL]))[0]
    points=[]
    for u,g in zip(times,gs):
        t=float(u-L if r['side']=='incoming'else u);raw=profile_preserving_raw_sample(phase,t)['raw_fields'];kwargs={}
        if r['side']=='outgoing':kwargs=dict(initial_pair=phase['arrays']['initial_pair'],reference_pair=phase['arrays']['reference_pair'])
        ref=corrected_positive_parent_reference(raw,rep,coordinate_time=t,**kwargs)
        wall=corrected_wall_reference(raw,rep,coordinate_time=t,**kwargs)
        geo=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else-2/L
        points.append(dict(reference=ref,wall=wall['background_values'][0],raw=raw,
            scalar_weights=np.array([geo[k].value for k in ('wT','wS','wV')]),
            temporal=np.array([b,bp,g[0,0],g[0,1],g[1,0],g[1,1]]),N=geo['induced_lapse'].value,R=geo['R4'].value,t=t))
    outputs=[];records=[]
    for b in angular['blocks']:
        nh=len(b['harmonic_indices']);ng=56*nh;nc=60*nh;ghost=16*nh;E=b['derivatives']
        K=np.zeros((nc,nc));G=K.copy();C=K.copy();HS=K.copy();gaugeGram=np.zeros((ng,ng));ghostGram=np.zeros((ghost,ghost))
        for a,tw in zip(points,weights):
            ref=a['reference'];tf=a['temporal'];raw=a['raw']
            for j,(A,At,Ar,metric,dens,rw)in enumerate(zip(ref['background_values'],ref['background_time_derivatives'],ref['background_radial_derivatives'],ref['positive_metric_coefficients'],ref['positive_two_form_densities'],ref['radial_weights'])):
                p=one_form_angular_point(A,At,Ar,E,radial[j],metric,dens,tf);weight=tw*rw
                K[:ng,:ng]+=weight*MAXWELL_TO_CAP*p['Hessian'];C[:ng,:ng]+=weight*MAXWELL_TO_CAP*p['curvature_contact']
                G[:ng,:ng]+=weight*MAXWELL_TO_CAP*p['Gram'];gaugeGram+=weight*p['Gram'];ghostGram+=weight*p['ghost_Gram']
            h=intrinsic_coupled_angular_point(a['scalar_weights'],raw[-8:-4],raw[-4:],a['wall'],E,tf,wrad,lambda_H=lam,nu_squared_action=nu)
            K+=tw*h['Hessian'];G+=tw*h['Gram'];HS+=tw*h['Hessian']
        B=gaugeGram[40*nh:];F=cho_solve((cholesky(ghostGram,lower=True),True),B)
        K[:ng,:ng]+=MAXWELL_TO_CAP*(B.T@F)
        chol=cholesky(G,lower=True);P=solve_triangular(chol,K,lower=True);P=solve_triangular(chol,P.T,lower=True).T
        ev,V=eigh(P)
        if ev[0]<=0:raise ArithmeticError('complete even field form not positive; no shift or mode deletion')
        U=solve_triangular(chol.T,V,lower=False);inverse=solve(P,np.eye(nc),assume_a='gen')
        Green=solve_triangular(chol.T,inverse,lower=False);Green=solve_triangular(chol.T,Green.T,lower=False).T
        record=dict(level=b['level'],absolute_spectator=b['absolute_spectator'],harmonic_count=nh,coordinate_count=nc,
            minimum_generalized_eigenvalue=float(ev[0]),maximum_generalized_eigenvalue=float(ev[-1]),
            normalized_inverse_residual=float(np.linalg.norm(P@inverse-np.eye(nc))),
            original_inverse_residual=float(np.linalg.norm(K@Green-np.eye(nc))),
            generalized_eigen_residual=float(np.linalg.norm(K@U-(G@U)*ev)/np.linalg.norm(K@U)),
            normalized_symmetry_defect=float(np.linalg.norm(P-P.T)/np.linalg.norm(P)),
            exact_stored_normalized_inverse_neumann_diagnostic=stored_inverse_neumann_majorant(P,inverse))
        outputs.append(dict(field_indices=b['field_indices'],harmonic_indices=b['harmonic_indices'],coupled_action_Hessian=K,coupled_action_Gram=G,
            normalized_operator=P,normalized_inverse=inverse,coupled_action_Green=Green,generalized_eigenvalues=ev,
            Gram_orthonormal_eigenvectors=U,one_form_curvature_contact=C,intrinsic_scalar_complete_Hessian=HS,
            one_form_Gram_per_kappa=gaugeGram,ghost_Gram_per_kappa=ghostGram,weak_Lorenz_map=F))
        records.append(record)
        if progress is not None:progress(record)
    return dict(block_arrays=outputs,block_records=records,harmonic_labels=angular['harmonic_labels'],
        full_harmonic_count=35,full_coupled_coordinate_count=2100,off_block_derivative_max=angular['off_block_derivative_max'],
        chronological_samples=np.array([[a['t'],a['N'],a['R']]for a in points]),quadrature_times=times,quadrature_weights=weights,
        one_coupled_inverse_before_sector_contraction=True,exact_angular_spectator_reduction=True,
        small_mode_or_statistical_rank_deletion=False,completed_P_strat_Wick_or_LSZ_Pauli=False,physical_a_mu=None,physical_g_mu=None)
