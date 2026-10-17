"""Source-paired heat from the actual enriched-cell gauge and Higgs response.

The intrinsic wall restriction is applied before constructing the Dirac
vertices.  The numerical coefficient cell and cutoff probes remain
explicit; this finite source pairing is not a completed native supertrace.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh
from .muon_current_source_motion_cubic import _real
from .muon_primal_cell_native_heat import actual_cell_heat_polynomial,_positive_length
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation,fixed_y_higgs_hamiltonian
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation,_ordered_cutoff_heat_lag
from .muon_native_mean_core_heat_target import _unit_lepton_mass6


def actual_reached_cell_vertices(fields,representation):
    """Construct delta A from the total actual intrinsic trace applications.

    A=partial_t/N+W+Omega_tau.  Spatial gauge and mass variations are
    Hermitian; the temporal connection variation is anti-Hermitian.
    Consequently the two cross-block directions must retain Xi and
    Xi-adjoint separately.  No Lorentz -i Omega_tau enters this factor.
    """
    raw=_real(fields['raw_fields'],'actual raw268',(268,))
    from .muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
    op=primal_trace_enriched_lepton_operator(raw,representation)
    a=_real(fields['first_wall_gauge'],'total first wall gauge',(8,5,4,20))
    h=_real(fields['first_H'],'total first intrinsic H',(8,4,20))
    frame=lepton_current_hilbert_representation();G=lepton_unit_trace_gauge_representation()['generators']
    spatial=-1j*np.einsum('iuv,cvw,Aich->Ahuw',frame['alpha'],G,a[:,2:])/op['R4']
    temporal=np.einsum('cuv,Ach->Ahuv',G,a[:,0])/op['N']
    H=np.stack((h[:,0]+1j*h[:,2],h[:,1]+1j*h[:,3]),axis=-1)
    mass=fixed_y_higgs_hamiltonian(H.reshape(160,2)).reshape(8,20,18,18)
    vertex=spatial+temporal+mass
    return dict(operator=op,vertex_n0_to_angular=vertex,
        adjoint_vertex_n0_to_angular=vertex.conj().transpose(0,1,3,2),
        gauge_spatial_vertex=spatial,gauge_temporal_vertex=temporal,fixed_Y_H_response_vertex=mass,
        complex_H_response=H,intrinsic_wall_gauge_norm=float(np.linalg.norm(a)),
        total_solved_first_response_used=True,physical_current_or_covariance_selected=False,
        independent_scalar_EM_charge_substituted=False)


def _spectral_source_core(op,angular,Xplus,Xminus,*,length,W=None):
    """Assemble complete n1/n3 images, with the actual positive factor."""
    ids=np.array([0,1,6,7,12,13]);alpha=lepton_current_hilbert_representation()['alpha'][:,ids][:,:,ids]
    B0=(op['W'] if W is None else W)[np.ix_(ids,ids)]+op['Omega_tau'][np.ix_(ids,ids)]
    temporal=12/(op['N']**2*_positive_length(length)**2)
    P0=temporal*np.eye(6)+B0.conj().T@B0;lam,V=eigh(P0)
    if min(lam)<=0:raise ValueError('strictly positive finite factor required')
    contact=np.zeros((8,8,6),complex);shells={};labels=angular['harmonic_labels'];E=angular['derivative_matrices']
    for n in (1,3):
        hs=np.array([i for i,label in enumerate(labels) if label[0]==n]);d=len(hs)
        Bn=-1j*sum(np.kron(E[a][np.ix_(hs,hs)],alpha[a]) for a in range(3))/op['R4']+np.kron(np.eye(d),B0)
        Pn=temporal*np.eye(6*d)+Bn.conj().T@Bn;ln,Vn=eigh(Pn)
        X=Xplus[:,hs][:,:,ids][:,:,:,ids].reshape(8,6*d,6)
        Xadj=Xminus[:,hs][:,:,ids][:,:,:,ids].reshape(8,6*d,6)
        F=np.einsum('ij,Ajk->Aik',Bn.conj().T,X)+np.einsum('Aij,jk->Aik',Xadj,B0)
        C=np.einsum('Aki,Bkj->ABij',X.conj(),X);C+=C.transpose(1,0,2,3).copy()
        contact+=np.einsum('ij,ABjk,ki->ABi',V.conj().T,C,V)
        shells[str(n)]=dict(eigenvalues=ln,first_jet_n0=np.einsum('ij,Ajk,kl->Ail',Vn.conj().T,F,V),
            intermediate_mode_count=len(ln),source_vertex=X,adjoint_source_vertex=Xadj)
    return dict(n0_eigenvalues=lam,mixed_contact_n0_spectral_diagonal=contact,intermediate_shells=shells)


def _cutoff_source_pair(core,cutoff):
    c=_positive_length(cutoff);lam=core['n0_eigenvalues']
    contact=-np.einsum('i,ABi->AB',np.exp(-c*lam)/lam,core['mixed_contact_n0_spectral_diagonal'])
    ordered=np.zeros((8,8),complex);coarse=ordered.copy()
    for shell in core['intermediate_shells'].values():
        F=shell['first_jet_n0'];weight32,weight=_ordered_cutoff_heat_lag(lam,shell['eigenvalues'],c)
        ordered+=np.einsum('Aji,Bji,ji->AB',F.conj(),F,weight)
        coarse+=np.einsum('Aji,Bji,ji->AB',F.conj(),F,weight32)
    opposite=ordered.T.copy()
    return dict(source_square_contact=contact,ordered_two_insertion=ordered,
        opposite_order_two_insertion=opposite,available_source_pair=contact+ordered+opposite,
        ordered_two_insertion_rule32=coarse,
        lag_rule32_64_pair_difference_norm=float(np.linalg.norm((ordered+ordered.T)-(coarse+coarse.T))),
        lag_rule_difference_is_rigorous_enclosure=False,proper_time_upper_tail_truncated=False,
        channel_trace=float(np.trace(contact+ordered+opposite).real))


def actual_midpoint_reached_source_heat(fields,representation,angular,*,length,cutoff):
    """Stable paired Y² source heat when the owned midpoint wall trace is zero.

    The source pulse ends at L/4 while this midpoint is L/2; its wall gauge
    and Gauss directions vanish by the prescribed Dirichlet trace law.
    The solved intrinsic H response remains nonzero.  Thus Xi=Y Xi_H,
    and the exact Y² coefficient uses the zero-Y base factor: no nearby
    family subtraction and no physical zero-H background selection.
    """
    vertices=actual_reached_cell_vertices(fields,representation);op=vertices['operator']
    if fields['profile']!=0 or fields['profile_rate']!=0 or np.any(fields['first_wall_gauge']):
        raise ValueError('stable midpoint reduction requires the derived zero Dirichlet source trace')
    H=vertices['complex_H_response'];unit=np.array([_unit_lepton_mass6(h) for h in H.reshape(160,2)]).reshape(8,20,6,6)
    # Embed the common family-independent unit-Y map in the existing18 frame.
    ids=np.array([0,1,6,7,12,13]);X=np.zeros((8,20,18,18),complex)
    X[:,:,ids[:,None],ids]=unit
    W=op['W'].copy();W[:12,12:]=0;W[12:,:12]=0
    core=_spectral_source_core(op,angular,X,X, length=length,W=W)
    result=_cutoff_source_pair(core,cutoff)
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real;dy=Y[1]**2-Y[2]**2
    paired={name:dy*result[name] for name in ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion','available_source_pair')}
    return dict(vertices=vertices,zero_Y_source_core=core,unit_Y2_source_pair=result,
        paired_middle_minus_light_Y2_source_pair=paired,
        paired_middle_minus_light_Y2_channel_trace=dy*result['channel_trace'],fixed_Y_square_difference=float(dy),
        paired_middle_minus_light_lag_rule32_64_difference_norm=abs(dy)*result['lag_rule32_64_pair_difference_norm'],
        cutoff_probe=float(cutoff),length=float(length),
        source_pair_coefficient_equation='Xi(Y)=Y Xi_H; coefficient Y² equals direct Xi_H†Xi_H contact plus both ordered first-P insertions on P(0)',
        both_source_orders_retained=True,all_n1_n3_complement_modes_retained=True,
        higher_shell_zero_scope='constant-angular n0 two-insertion only; homogeneous background preserves each complete shell',
        intrinsic_wall_gauge_zero_scope='derived prescribed trace and regular interior profile vanish on wall at midpoint; bulk solved gauge/Gauss fields retained in the mean load',
        induced_mean_second_operator_contact_included=False,source_pair_Y4_remainder_outward_certified=False,
        complete_angular_geometry_first_response_claimed=False,
        inherited_source_normalization='fresh Tb/Q/Qdot applied before root Gauss solve; no extra Tb, e,QNORM or Haar volume in this normalized pairing',
        core_scope='actual solved coefficient midpoint and same length numerical Dirichlet temporal tent; no birth transmission or physical cutoff selected',
        statistics_or_relative_supertrace_coefficient_selected=False,complete_native_or_Pauli=False)
