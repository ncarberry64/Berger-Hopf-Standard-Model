"""Actual magnetic variation of the reached Higgs/lepton factor graph.

This extends the evaluated intrinsic-Higgs Gaussian component with the
complete source product image.  Its common-total-cutoff Green derivative
is an open operator application.  No graded P_cycle, quantum statistics,
external pole, LSZ residue, or Pauli normalization is inferred from it.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import eigh

from .muon_common_cutoff_green_kernel import (
    common_total_cutoff_green_kernel,contraction_series_tail_upper,outward_positive_product_sum,
)
from .muon_intrinsic_higgs_positive_source import intrinsic_higgs_positive_source_application
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_primal_cell_reached_source_heat import actual_reached_cell_vertices


def _finite(value, name, *, real=False):
    if value is None:
        raise ValueError(name+' is required')
    raw=np.asarray(value)
    if raw.dtype.kind not in 'iufc' or raw.dtype==object:
        raise ValueError(name+' requires numeric point coefficients, not intervals or strings')
    if real and not np.isrealobj(raw):
        raise ValueError(name+' requires real coefficients')
    result=np.asarray(raw,float if real else complex)
    if result.size==0 or not np.isfinite(result).all():
        raise ValueError(name+' requires finite nonempty coefficients')
    return result


def _positive(value, name, *, zero=False):
    a=_finite(value,name,real=True)
    if a.shape!=() or a<0 or (a==0 and not zero):
        raise ValueError(name+' requires an explicit positive scalar' if not zero else name+' requires an explicit nonnegative scalar')
    return float(a)


def family_fiber_indices(family):
    """Exact fixed-Y family restriction of the inherited eighteen-component fiber."""
    if type(family) is not int or family not in (0,1,2):
        raise ValueError('one of the three retained family indices required')
    return np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])


def _mixed_vertices(gaunt, mass_vertices):
    """Both open placements of the bare real-linear fixed-Y scalar vertex."""
    G=_finite(gaunt,'complete Gaunt product',real=True)
    M=_finite(mass_vertices,'four fixed-Y scalar vertices')
    ne,no,nx=G.shape;d=M.shape[-1]
    if M.shape!=(4,d,d):raise ValueError('four same-fiber real scalar vertices required')
    B0=np.zeros((4*no,no*d,d),complex)
    for c in range(4):
        for h in range(no):B0[c*no+h,h*d:(h+1)*d]=.75*M[c]
    B1odd=.75*np.einsum('ehx,cuv->cheuxv',G,M).reshape(4*no,ne*d,nx*d)
    B1even=.75*np.einsum('ehx,cuv->cehuxv',G,M).reshape(4*ne,no*d,nx*d)
    return B0,B1odd,B1even


def _family_operator_data(vertices, scalar, angular, family, length):
    """Build actual A/P and magnetic directions, rather than accepting a pencil."""
    ids=family_fiber_indices(family);op=vertices['operator'];d=6
    frame=lepton_current_hilbert_representation();alpha=frame['alpha'][:,ids][:,:,ids]
    B=op['W'][np.ix_(ids,ids)]+op['Omega_tau'][np.ix_(ids,ids)]
    def factor(E):
        count=E.shape[1]
        A=-1j*sum(np.kron(E[i],alpha[i]) for i in range(3))/op['R4']+np.kron(np.eye(count),B)
        P=12/(op['N']**2*length**2)*np.eye(len(A))+A.conj().T@A
        p,V=eigh(P)
        if p[0]<=0:raise ArithmeticError('actual reached product factor is not positive')
        return A,P,p,V
    Ao,Po,po,Vo=factor(scalar['odd_derivative_matrices'])
    Ae,Pe,pe,Ve=factor(scalar['even_derivative_matrices'])
    source_ids=[i for i,l in enumerate(angular['harmonic_labels']) if l[0]<=scalar['source_maximum_level']]
    X=vertices['vertex_n0_to_angular'][:3,source_ids][:,:,ids][:,:,:,ids]
    G=scalar['gaunt_even_odd_source'];ne,no,nx=G.shape
    Xi=np.einsum('eos,Asuv->Aeuov',G,X).reshape(3,ne*d,no*d)
    # Temporal Xi is anti-Hermitian.  Reverse block adjoint must act on
    # coefficient matrices, not be replaced by the forward Xi block.
    Xi_reverse_dagger=np.einsum('eos,Asvu->Aeuov',G,X.conj()).reshape(Xi.shape)
    square_left=np.einsum('ij,Ajk->Aik',Ae.conj().T,Xi)
    square_right=np.einsum('Aij,jk->Aik',Xi_reverse_dagger,Ao)
    mass=canonical_open_field_vertices(op['R4'],op['N'])['scalar'][:,ids][:,:,ids]
    B0,B1odd,B1even=_mixed_vertices(G,mass)
    return dict(A_odd=Ao,P_odd=Po,eigenvalues_odd=po,eigenvectors_odd=Vo,
        A_even=Ae,P_even=Pe,eigenvalues_even=pe,eigenvectors_even=Ve,
        Xi_even_odd=Xi,Xi_reverse_dagger_even_odd=Xi_reverse_dagger,
        delta_P_square_left=square_left,delta_P_square_right=square_right,
        delta_P_even_odd=square_left+square_right,
        mixed_vertex_n0_odd=B0,mixed_vertex_n1_Hodd=B1odd,mixed_vertex_n1_Heven=B1even,
        family=family,fiber_indices=ids,external_harmonic_count=nx,
        squared_factor_minimum_eigenvalue=min(float(pe[0]),float(po[0])))


def mixed_green_spectral_derivative(data, scalar, cutoff, *, series_terms=4):
    """Apply both propagator variations and the left numerator derivative.

    For the left inverse G_F=P_F^-1 A^dagger,
    delta G_F=-P_F^-1(delta P_F)P_F^-1 A^dagger+P_F^-1 delta A^dagger.
    Common-cutoff L3 replaces the three inverse factors and L2 replaces
    the numerator-contact two factors.  Both open placements are retained.
    This equation is for the explicitly projected factor graph, not a
    derivation of its embedding in the complete graded native P_cycle.
    """
    c=_positive(cutoff,'common total cutoff',zero=True)
    # This arithmetic helper is also independently tested with controls;
    # the public physical application below supplies only owned producers.
    for key in ('A_odd','A_even','eigenvalues_odd','eigenvalues_even','eigenvectors_odd',
        'eigenvectors_even','mixed_vertex_n0_odd','mixed_vertex_n1_Hodd','mixed_vertex_n1_Heven',
        'delta_P_square_left','delta_P_square_right','Xi_reverse_dagger_even_odd','Xi_even_odd'):
        _finite(data.get(key),'reached '+key)
    for key in ('positive_H_odd','positive_H_even','delta_positive_H_even_odd'):
        _finite(scalar.get(key),'reached '+key,real=True)
    Ao,Ae,po,pe,Vo,Ve=(data[k] for k in ('A_odd','A_even','eigenvalues_odd','eigenvalues_even','eigenvectors_odd','eigenvectors_even'))
    ho,Uo=eigh(scalar['positive_H_odd']);he,Ue=eigh(scalar['positive_H_even'])
    if min(ho[0],he[0])<=0:raise ArithmeticError('actual source-image Higgs Jacobi is not positive')
    gram=_positive(scalar['action_Gram_scalar'],'actual scalar action Gram')
    B0,B1,B1H=(data[k] for k in ('mixed_vertex_n0_odd','mixed_vertex_n1_Hodd','mixed_vertex_n1_Heven'))
    transform=lambda U,B:np.einsum('ab,bij->aij',U.T,B)
    B0h,B1h,B1eh=transform(Uo,B0),transform(Uo,B1),transform(Ue,B1H)
    left1=B1h.conj().transpose(0,2,1)@Ve
    right0=(Vo.conj().T@Ao.conj().T)@B0h
    left0=B0h.conj().transpose(0,2,1)@Vo
    right1=(Ve.conj().T@Ae.conj().T)@B1h
    right0_plain=Vo.conj().T@B0h;right1_plain=Ve.conj().T@B1h
    squares=[np.einsum('ij,Ajk,kl->Ail',Ve.conj().T,data[key],Vo)
        for key in ('delta_P_square_left','delta_P_square_right')]
    numerator=np.einsum('ij,Ajk,kl->Ail',Ve.conj().T,data['Xi_reverse_dagger_even_odd'],Vo)
    reverse_numerator=np.einsum('ij,Ajk,kl->Ail',Vo.conj().T,data['Xi_even_odd'].conj().transpose(0,2,1),Ve)
    shape=(3,B1.shape[-1],B0.shape[-1]);forward={};reverse={};tail={};outward_terms={}
    names=('fermion_square_left','fermion_square_right','fermion_numerator_contact','scalar_propagator_insertion')
    for name in names:
        forward[name]=np.zeros(shape,complex);reverse[name]=np.zeros((3,shape[2],shape[1]),complex);tail[name]=0.;outward_terms[name]=[]
    def add_outward(name,kernel,left,middle,right):
        bound=contraction_series_tail_upper(kernel,left,middle,right,gram)
        outward_terms[name].append((bound,))
    kernel_max_tail=0.
    for a,h in enumerate(ho):
        k3=common_total_cutoff_green_kernel(pe[:,None],po[None,:],h,cutoff=c,terms=series_terms)
        k2e=common_total_cutoff_green_kernel(pe,h,cutoff=c,terms=series_terms)
        k2o=common_total_cutoff_green_kernel(po,h,cutoff=c,terms=series_terms)
        kernel_max_tail=max(kernel_max_tail,k3['positive_series_truncation_upper'],k2e['positive_series_truncation_upper'],k2o['positive_series_truncation_upper'])
        for source in range(3):
            for name,square in zip(names[:2],squares):
                forward[name][source]-=left1[a]@(k3['value']*square[source])@right0[a]/gram
                reverse[name][source]-=left0[a]@(k3['value'].T*square[source].conj().T)@right1[a]/gram
                tail[name]+=k3['positive_series_truncation_upper']*(
                    np.linalg.norm(left1[a])*np.linalg.norm(square[source])*np.linalg.norm(right0[a])+
                    np.linalg.norm(left0[a])*np.linalg.norm(square[source])*np.linalg.norm(right1[a]))/gram
                add_outward(name,k3['positive_series_truncation_upper'],left1[a],square[source],right0[a])
                add_outward(name,k3['positive_series_truncation_upper'],left0[a],square[source].conj().T,right1[a])
            forward[names[2]][source]+=left1[a]@(k2e['value'][:,None]*numerator[source])@right0_plain[a]/gram
            reverse[names[2]][source]+=left0[a]@(k2o['value'][:,None]*reverse_numerator[source])@right1_plain[a]/gram
            tail[names[2]]+=(k2e['positive_series_truncation_upper']*np.linalg.norm(left1[a])*np.linalg.norm(numerator[source])*np.linalg.norm(right0_plain[a])+
                k2o['positive_series_truncation_upper']*np.linalg.norm(left0[a])*np.linalg.norm(reverse_numerator[source])*np.linalg.norm(right1_plain[a]))/gram
            add_outward(names[2],k2e['positive_series_truncation_upper'],left1[a],numerator[source],right0_plain[a])
            add_outward(names[2],k2o['positive_series_truncation_upper'],left0[a],reverse_numerator[source],right1_plain[a])
    dH=np.einsum('ij,Ajk,kl->Ail',Ue.T,scalar['delta_positive_H_even_odd'][:3],Uo)
    leftH=B1eh.conj().transpose(0,2,1)@Vo
    rightH=(Vo.conj().T@Ao.conj().T)@B1eh
    for j,f in enumerate(po):
        k3=common_total_cutoff_green_kernel(he[:,None],ho[None,:],f,cutoff=c,terms=series_terms)
        kernel_max_tail=max(kernel_max_tail,k3['positive_series_truncation_upper'])
        L=leftH[:,:,j].T;R=right0[:,j,:]
        Lr=left0[:,:,j].T;Rr=rightH[:,j,:]
        for source in range(3):
            forward[names[3]][source]-=L@(k3['value']*dH[source])@R/gram
            reverse[names[3]][source]-=Lr@(k3['value'].T*dH[source].T)@Rr/gram
            tail[names[3]]+=k3['positive_series_truncation_upper']*np.linalg.norm(dH[source])*(np.linalg.norm(L)*np.linalg.norm(R)+np.linalg.norm(Lr)*np.linalg.norm(Rr))/gram
            add_outward(names[3],k3['positive_series_truncation_upper'],L,dH[source],R)
            add_outward(names[3],k3['positive_series_truncation_upper'],Lr,dH[source].T,Rr)
    forward['total']=sum(forward.values());reverse['total']=sum(reverse.values())
    return dict(forward=forward,reverse=reverse,scalar_eigenvalues_odd=ho,scalar_eigenvalues_even=he,
        kernel_positive_series_tail_upper=kernel_max_tail,
        contracted_series_tail_majorant_estimates=tail,
        exact_stored_contracted_series_tail_upper={name:outward_positive_product_sum(terms) for name,terms in outward_terms.items()},
        exact_stored_series_tail_norm_products_outward=True,
        contracted_tail_norm_arithmetic_outward=False,
        positive_series_tail_scope='exact-stored spectra series truncation only; binary contraction/norms/eigenvectors and upstream assembly excluded',
        cutoff=c,series_terms=series_terms,
        bare_fixed_Y_mixed_vertex_first_derivatives_zero=True,
        vertex_zero_provenance='fixed-Y Yukawa action is linear in real H; d(delta_H M)/dH=d(delta_H M)/dA=0 at fixed coframe and real4 field coordinates',
        temporal_source_derivative_removed_by_operator_identity=False,
        temporal_projection='existing tent only; int b² bprime=0 does not eliminate its full differential complement')


def magnetic_mixed_green_application(fields,representation,angular,*,length,cutoff,series_terms=4):
    """Execute actual all-family magnetic mixed Green insertions on complete images."""
    L=_positive(length,'existing cell length');c=_positive(cutoff,'shared cutoff probe',zero=True)
    vertices=actual_reached_cell_vertices(fields,representation)
    scalar=intrinsic_higgs_positive_source_application(fields['raw_fields'],representation,angular,
        length=L,first_wall_gauge=fields['first_wall_gauge'],first_H=fields['first_H'])
    op=vertices['operator'];families={};full={};reverse={}
    for family in range(3):
        data=_family_operator_data(vertices,scalar,angular,family,L)
        result=mixed_green_spectral_derivative(data,scalar,c,series_terms=series_terms)
        families[str(family)]=dict(operators=data,contraction=result)
        for name,value in result['forward'].items():
            if name not in full:
                full[name]=np.zeros((3,data['external_harmonic_count'],18,18),complex)
                reverse[name]=np.zeros_like(full[name])
            ids=data['fiber_indices']
            full[name][:,:,ids[:,None],ids]=value.reshape(3,data['external_harmonic_count'],6,6)
            reverse[name][:,:,ids[:,None],ids]=result['reverse'][name].reshape(3,6,data['external_harmonic_count'],6).transpose(0,2,1,3)
    # Fixed Y is diagonal and all represented connections are family blind.
    # This is an invariant family restriction, not a charged-only projection.
    for matrix in (op['W'],op['Omega_tau']):
        check=matrix.copy()
        for f in range(3):
            ids=family_fiber_indices(f);check[np.ix_(ids,ids)]=0
        if np.any(check):raise ArithmeticError('actual family off-diagonal block cannot be omitted')
    paired={name:families['1']['contraction']['forward'][name]-families['2']['contraction']['forward'][name] for name in full}
    paired_reverse={name:families['1']['contraction']['reverse'][name]-families['2']['contraction']['reverse'][name] for name in full}
    return dict(families=families,full18_forward=full,full18_reverse=reverse,
        paired_middle_minus_light_forward=paired,paired_middle_minus_light_reverse=paired_reverse,
        scalar_source=scalar,vertices=vertices,length=L,common_cutoff_probe=c,
        active_source_indices=[0,1,2],all_three_fixed_Y_families=True,
        external_output_harmonic_labels=scalar['source_harmonic_labels'],external_input_harmonic_label=(0,0,0,'self'),
        exact_family_restriction=True,charged_and_neutral_Weyl_components_retained=True,
        both_squared_factor_derivative_placements=True,both_open_vertex_placements_retained=True,
        scalar_propagator_variation_and_left_numerator_contact_retained=True,
        source_e_already_included=True,quantum_statistics_factor_inserted=False,
        current_cell_graph_complete_P_cycle_derived=False,
        square_contact_of_complete_mixed_P_cycle_evaluated=False,
        proper_time_cutoff_physically_selected=False,
        full_differential_temporal_complement_evaluated=False,
        full_graded_quantum_Sigma_or_external_pole_or_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None)
