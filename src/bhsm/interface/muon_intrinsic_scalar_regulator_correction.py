"""Action-level scalar Schur reduction and its finite-cutoff correction.

The retained intrinsic fermion operator A(H) is affine in its real Higgs coordinates.
Ordinary Gaussian elimination fixes the open exchange and its sign, but
does not commute with applying the canonical finite proper-time cutoff.
This module evaluates that correction on the actual reached mixed Green
operators.  It does not select an elliptic reduction of the full P_strat.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import eigh

from .muon_common_cutoff_green_kernel import common_total_cutoff_green_kernel
from .muon_magnetic_mixed_green import _finite, _positive


def scalar_reduced_kernel(p, q, cutoff):
    """Scalar-first Schur cutoff: exp(-c q)/(p q), not common-total L2."""
    p = _finite(p, 'positive fermion spectrum', real=True)
    q = _finite(q, 'positive scalar spectrum', real=True)
    c = _positive(cutoff, 'explicit common cutoff', zero=True)
    if np.any(p <= 0) or np.any(q <= 0):
        raise ValueError('positive spectra required')
    return np.exp(-c*q)/(p*q)


def two_green_regulator_correction(p, q, cutoff):
    """Positive missing region with scalar time below c and total time >=c.

    C2=exp(-c min(p,q))*[-expm1(-c abs(p-q))]/[p abs(p-q)].
    Its continuous coincident value is c exp(-c p)/p.
    """
    p = _finite(p, 'positive fermion spectrum', real=True)
    q = _finite(q, 'positive scalar spectrum', real=True)
    c = _positive(cutoff, 'explicit common cutoff', zero=True)
    if np.any(p <= 0) or np.any(q <= 0):
        raise ValueError('positive spectra required')
    p, q = np.broadcast_arrays(p, q)
    difference = np.abs(p-q)
    ratio = np.empty_like(difference)
    np.divide(-np.expm1(-c*difference), difference, out=ratio,
              where=difference != 0)
    ratio[difference == 0] = c
    return np.exp(-c*np.minimum(p,q))*ratio/p


def _subtractive_positive_correction(full, reduced, cutoff):
    """Guard loss of a small correction; the retained probes are well resolved."""
    if cutoff == 0:
        return np.zeros_like(full)
    difference = full-reduced
    scale = np.maximum(full,reduced)
    unresolved = (scale > 0) & (difference <= 1024*np.finfo(float).eps*scale)
    if np.any(unresolved):
        raise ArithmeticError('small finite-cutoff correction requires positive-region evaluation')
    return difference


def scalar_regulator_source_application(data, scalar, cutoff, *, series_terms=6):
    """Evaluate scalar-first and omitted-region source contacts on owned data.

    Both open placements, both derivatives of A dagger A, delta A dagger,
    and the actual scalar Jacobi insertion are retained.  The correction
    is evaluated at kernel level, not by subtracting two open matrices.
    Input arrays are pinned physical coefficient applications in the
    companion producer; this arithmetic helper also accepts test controls.
    """
    c = _positive(cutoff, 'explicit cutoff', zero=True)
    Ao,Ae,po,pe,Vo,Ve = (data[k] for k in (
        'A_odd','A_even','eigenvalues_odd','eigenvalues_even',
        'eigenvectors_odd','eigenvectors_even'))
    for key,value in data.items():
        if isinstance(value,np.ndarray): _finite(value,key)
    ho,Uo = eigh(_finite(scalar['positive_H_odd'],'actual odd Higgs form',real=True))
    he,Ue = eigh(_finite(scalar['positive_H_even'],'actual even Higgs form',real=True))
    if min(np.min(po),np.min(pe),ho[0],he[0]) <= 0:
        raise ValueError('actual positive factor forms required')
    gram = _positive(scalar['action_Gram_scalar'],'scalar action Gram')
    B0,B1,B1H = (data[k] for k in (
        'mixed_vertex_n0_odd','mixed_vertex_n1_Hodd','mixed_vertex_n1_Heven'))
    transform = lambda U,B: np.einsum('ab,bij->aij',U.T,B)
    B0h,B1h,B1eh = transform(Uo,B0),transform(Uo,B1),transform(Ue,B1H)
    left1 = B1h.conj().transpose(0,2,1)@Ve
    right0 = (Vo.conj().T@Ao.conj().T)@B0h
    left0 = B0h.conj().transpose(0,2,1)@Vo
    right1 = (Ve.conj().T@Ae.conj().T)@B1h
    plain0,plain1 = Vo.conj().T@B0h,Ve.conj().T@B1h
    squares = [np.einsum('ij,Ajk,kl->Ail',Ve.conj().T,data[k],Vo)
               for k in ('delta_P_square_left','delta_P_square_right')]
    numerator = np.einsum('ij,Ajk,kl->Ail',Ve.conj().T,
        data['Xi_reverse_dagger_even_odd'],Vo)
    reverse_numerator = np.einsum('ij,Ajk,kl->Ail',Vo.conj().T,
        data['Xi_even_odd'].conj().transpose(0,2,1),Ve)
    names = ('fermion_square_left','fermion_square_right',
             'fermion_numerator_contact','scalar_propagator_insertion')
    shape = (3,B1.shape[-1],B0.shape[-1])
    outputs = {kind: {place: {k: np.zeros(shape if place=='forward'
        else (3,shape[2],shape[1]),complex) for k in names}
        for place in ('forward','reverse')}
        for kind in ('scalar_first_reduction','finite_cutoff_correction')}
    maximum_kernel_tail = 0.
    for a,h in enumerate(ho):
        full = common_total_cutoff_green_kernel(pe[:,None],po[None,:],h,
            cutoff=c,terms=series_terms)
        reduced = np.exp(-c*h)/(pe[:,None]*po[None,:]*h)
        correction = _subtractive_positive_correction(full['value'],reduced,c)
        maximum_kernel_tail = max(maximum_kernel_tail,full['positive_series_truncation_upper'])
        for kind,k3 in (('scalar_first_reduction',reduced),
                        ('finite_cutoff_correction',correction)):
            out = outputs[kind]
            for source in range(3):
                for name,square in zip(names[:2],squares):
                    out['forward'][name][source] -= left1[a]@(k3*square[source])@right0[a]/gram
                    out['reverse'][name][source] -= left0[a]@(k3.T*square[source].conj().T)@right1[a]/gram
        for kind,k2e,k2o in (
            ('scalar_first_reduction',scalar_reduced_kernel(pe,h,c),scalar_reduced_kernel(po,h,c)),
            ('finite_cutoff_correction',two_green_regulator_correction(pe,h,c),two_green_regulator_correction(po,h,c))):
            out = outputs[kind]
            for source in range(3):
                out['forward'][names[2]][source] += left1[a]@(k2e[:,None]*numerator[source])@plain0[a]/gram
                out['reverse'][names[2]][source] += left0[a]@(k2o[:,None]*reverse_numerator[source])@plain1[a]/gram
    dH = np.einsum('ij,Ajk,kl->Ail',Ue.T,
        _finite(scalar['delta_positive_H_even_odd'],'actual scalar source',real=True)[:3],Uo)
    leftH = B1eh.conj().transpose(0,2,1)@Vo
    rightH = (Vo.conj().T@Ao.conj().T)@B1eh
    scalar_kernel = common_total_cutoff_green_kernel(he[:,None],ho[None,:],
        cutoff=c,terms=series_terms)
    maximum_kernel_tail = max(maximum_kernel_tail,scalar_kernel['positive_series_truncation_upper'])
    for j,f in enumerate(po):
        full = common_total_cutoff_green_kernel(he[:,None],ho[None,:],f,
            cutoff=c,terms=series_terms)
        reduced = scalar_kernel['value']/f
        correction = _subtractive_positive_correction(full['value'],reduced,c)
        maximum_kernel_tail = max(maximum_kernel_tail,full['positive_series_truncation_upper'])
        L,R = leftH[:,:,j].T,right0[:,j,:]
        Lr,Rr = left0[:,:,j].T,rightH[:,j,:]
        for kind,k3 in (('scalar_first_reduction',reduced),
                        ('finite_cutoff_correction',correction)):
            out = outputs[kind]
            for source in range(3):
                out['forward'][names[3]][source] -= L@(k3*dH[source])@R/gram
                out['reverse'][names[3]][source] -= Lr@(k3.T*dH[source].T)@Rr/gram
    for out in outputs.values():
        for place in ('forward','reverse'):out[place]['total'] = sum(out[place].values())
    return dict(**outputs,cutoff=c,maximum_input_kernel_series_tail_upper=maximum_kernel_tail,
        correction_subtraction_resolved=True,correction_evaluated_before_open_matrix_contraction=True,
        series_tail_scope='exact stored input kernels only; reduced-kernel subtraction and contractions are binary64',
        complete_adopted_D_strat_or_squared_mixed_contact_derived=False,
        scalar_Schur_graph_promoted_to_Gamma=False,physical_Pauli_completed=False)


def intrinsic_scalar_gaussian_embedding_contract():
    """Literal signed-action proof and angular/temporal normalization convention."""
    return dict(
        action='S_b[H]+barPsi A(H)Psi; A(H)=A0+sum_i H_i V_i',
        quadratic_action='h K h/2+bar_eta A eta+bar_eta V_i Psi h_i+barPsi V_i eta h_i',
        intrinsic_first_order_two_H_contact='A_ij=0 at fixed coframe; affine fixed-Y Yukawa',
        fermion_eliminated_scalar_Hessian='K_eff,ij=K_ij-barPsi(V_i A^-1 V_j+V_j A^-1 V_i)Psi',
        unregulated_open_exchange='D_barPsi D_Psi Gamma_Gaussian=-sum_ij (K^-1)_ji V_i A^-1 V_j',
        gaussian_open_exchange_statistics_coefficient=-1,
        closed_C6_fermion_statistics_factor_copied=False,
        finite_cutoff_Schur_equivalence=False,
        native_squared_contact='P_barPsi=Dbar_dagger Dpsi+Dpsi_dagger Dbar+D0_dagger Dbarpsi+Dbarpsi_dagger D0, with graded coefficient ordering',
        scalar_first_cutoff='R2(p,q;c)=exp(-c q)/(p q)',
        unreduced_common_cutoff='L2(p,q;c)=R2+C2; C2>0 for c>0',
        temporal_product='b^2=(3/4)b+b_perp; norm(b_perp)^2=L/80; norm(b^2)^2=L/5',
        temporal_source_complement_fraction=1/16,
        angular_normalization='V=2pi^2; normalized-Haar scalar Y_h; fermion phi_h=Y_h/sqrt(V), phi0=1/sqrt(V)',
        pointwise_fermion='chi=R4^(3/2)psi/V with kinetic integral dOmega chi_dagger A chi',
        mixed_angular_pairing='integral dOmega phi_h_dagger*(Y_j V_i)*phi0=delta_hj V_i',
        scalar_action_Gram='2 V wV L/(3 V^2); bare fixed-Y mixed vertex has no extra V',
        no_independent_fermion_state_selected=True,
        action_definition_ambiguity_established=False,
        background_intrinsic_D_Psi_dependence='A(H) has no explicit external Psi at fixed geometry, gauge and H; the mixed fluctuation terms and stationary mean response arise from the same signed action',
        adopted_D_strat_identified_with_fluctuation_Hessian_square_root=False,
        next_action_application='apply the action-owned field-current Green consumer and its source/mean derivatives on the same native domain; recover the actual adopted D_strat dependence before any graded square-contact or relative completion promotion')
