"""Original full wall current using the retained charged/neutral spin maps.

The six-fiber order is weak-major, each weak coefficient carrying spin2.
The four external charged columns are chiral Lspin2,Rspin2.  This replaces
the earlier spin/weak-swapped diagnostic injection, without changing its
original field Green, canonical vertices or normalization.
"""
from __future__ import annotations
import numpy as np
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices,charged_dirac_injection
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .muon_piecewise_euclidean_action import FAMILY_INDICES
from .muon_primal_electromagnetic_source import higgs_aligned_charge


def owned_chiral_charge_injection(H,*,family):
    a=charged_dirac_injection(H,family=family);fi=FAMILY_INDICES[family]
    U=retained_higgs_spin_charge_representation()['Dirac_to_LR_columns']
    J=a['charged'][fi]@U;N=a['neutral'][fi]
    Q=higgs_aligned_charge(np.asarray(H,complex),np.zeros(2,complex))['charge'][np.ix_(fi,fi)]
    return dict(charged_chiral=J,neutral_left=N,family_indices=fi,
        charge_alignment_residual=Q@J+J,neutral_charge_residual=Q@N,
        current_Gram_residual=J.conj().T@J-np.eye(4),
        charged_neutral_orthogonality=J.conj().T@N,
        angular_constant_current_normalization=1.)


def owned_static_charged_current(wall_green,H,*,radius,lapse,family=1,out_family=2):
    G=np.asarray(wall_green,complex)
    if G.shape!=(24,24)or not np.isfinite(G).all():raise ValueError('original complete24 joint wall Green required')
    a=owned_chiral_charge_injection(H,family=family);b=owned_chiral_charge_injection(H,family=out_family)
    v=canonical_open_field_vertices(radius,lapse)
    vertices=np.concatenate((v['gauge'].reshape(20,18,18),v['scalar']),axis=0)
    fi,fo=a['family_indices'],b['family_indices'];V=vertices[:,fi][:,:,fi];Vo=vertices[:,fo][:,:,fo]
    right=np.einsum('ij,ajk,kl->ail',a['neutral_left'].conj().T,V,a['charged_chiral'])
    left=np.einsum('ij,ajk,kl->ail',b['charged_chiral'].conj().T,Vo,b['neutral_left'])
    con=lambda i,j:np.einsum('aij,ab,bkl->ijkl',right[i],G[np.ix_(i,j)],left[j])
    allrows=np.arange(24);g=np.arange(20);h=np.arange(20,24)
    total=con(allrows,allrows);gg,gh,hg,hh=con(g,g),con(g,h),con(h,g),con(h,h)
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    currents=np.zeros((4,2,4),complex);currents[0,:,:2]=np.eye(2);currents[1:,:,:2]=-sigma
    template=np.einsum('a,aij,akl->ijkl',np.array([1,-1,-1,-1]),currents,currents.conj().transpose(0,2,1))
    coeff=np.vdot(template,total)/np.vdot(template,template);rem=total-coeff*template
    return dict(charged_current_right_vertices=right,charged_current_left_vertices=left,
        full_charged_current_tensor=total,gauge_gauge_tensor=gg,gauge_scalar_tensor=gh,scalar_gauge_tensor=hg,scalar_scalar_tensor=hh,
        VA_template=template,VA_projection_coefficient=np.array(coeff),VA_tensor_remainder=rem,
        VA_relative_remainder=float(np.linalg.norm(rem)/np.linalg.norm(total)),exact_sector_sum_difference=total-gg-gh-hg-hh,
        right_charge_injection=a['charged_chiral'],right_neutral_injection=a['neutral_left'],
        left_charge_injection=b['charged_chiral'],left_neutral_injection=b['neutral_left'],
        right_charge_residual=a['charge_alignment_residual'],right_neutral_charge_residual=a['neutral_charge_residual'],
        left_charge_residual=b['charge_alignment_residual'],left_neutral_charge_residual=b['neutral_charge_residual'],
        literal_left_minus_vertex_adjoint=left-right.conj().transpose(0,2,1),
        external_chiral_order='Lspin_up,Lspin_down,Rspin_up,Rspin_down; C6=weak0spin2,weak1spin2,Rspin2',
        angular_current_integral=1.,new_cap_or_Haar_factor_inserted=False,
        physical_exterior_LSZ_or_decay_or_unit_identified=False)
