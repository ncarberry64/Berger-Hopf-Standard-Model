"""Original static radial-field return on normalized charged-current tests."""
from __future__ import annotations
import numpy as np
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices

VOLUME=2*np.pi**2


def static_coupled_charged_current(wall_green,H,*,radius,lapse,family,out_family=None):
    """All24 field legs, literal analytic left placement and full remainder.

    The homogeneous wall field has angular value1.  External constant
    spinors use phi0=1/sqrt(VOLUME); the actual current angular integral
    is VOLUME*phi0**2=1.  No new cap or volume factor is inserted here.
    """
    G=np.asarray(wall_green,complex);h=np.asarray(H)
    out_family=family if out_family is None else out_family
    if (G.shape!=(24,24)or h.shape!=(2,)or not np.isfinite(G).all()
        or not np.isfinite(h).all()or np.linalg.norm(h)==0
        or family not in(0,1,2)or out_family not in(0,1,2)):
        raise ValueError('full24 wall Green, actual nonzero Higgs and retained family required')
    v=canonical_open_field_vertices(radius,lapse)
    vertices=np.concatenate((v['gauge'].reshape(20,18,18),v['scalar']),axis=0)
    ids=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
    out_ids=np.array([2*out_family,2*out_family+1,6+2*out_family,7+2*out_family,12+2*out_family,13+2*out_family])
    V=vertices[:,ids][:,:,ids]
    Vout=vertices[:,out_ids][:,:,out_ids]
    e=h/np.linalg.norm(h);nu=np.array([-e[1].conjugate(),e[0].conjugate()])
    J=np.zeros((6,4),complex);J[:2,0]=e;J[2:4,1]=e;J[4,2]=J[5,3]=1
    N=np.zeros((6,2),complex);N[:2,0]=nu;N[2:4,1]=nu
    right=np.einsum('ij,ajk,kl->ail',N.conj().T,V,J)
    # Derived from the second original canonical action vertex.  This
    # literal placement remains valid without enforcing a Hermitian V.
    left=np.einsum('ij,ajk,kl->ail',J.conj().T,Vout,N)
    def apply(a,b):
        return np.einsum('aij,ab,bkl->ijkl',right[a],G[np.ix_(a,b)],left[b])
    all_ids=np.arange(24);gauge=np.arange(20);scalar=np.arange(20,24)
    total=apply(all_ids,all_ids);gg=apply(gauge,gauge);hh=apply(scalar,scalar)
    gh=apply(gauge,scalar);hg=apply(scalar,gauge)
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    currents=np.zeros((4,2,4),complex);currents[0,:,:2]=np.eye(2)
    currents[1:,:,:2]=-sigma
    template=np.einsum('a,aij,akl->ijkl',np.array([1,-1,-1,-1]),currents,currents.conj().transpose(0,2,1))
    coefficient=np.vdot(template,total)/np.vdot(template,template)
    remainder=total-coefficient*template
    return dict(charged_current_right_vertices=right,charged_current_left_vertices=left,
        canonical_family_vertices=V,canonical_left_family_vertices=Vout,
        charged_injection=J,neutral_left_injection=N,
        full_charged_current_tensor=total,gauge_gauge_tensor=gg,scalar_scalar_tensor=hh,
        gauge_scalar_tensor=gh,scalar_gauge_tensor=hg,
        VA_template=template,VA_projection_coefficient=np.array(coefficient),
        VA_tensor_remainder=remainder,
        VA_relative_remainder=float(np.linalg.norm(remainder)/np.linalg.norm(total)),
        exact_sector_sum_difference=total-gg-hh-gh-hg,
        literal_left_minus_vertex_adjoint=left-right.conj().transpose(0,2,1),
        family_indices=ids,out_family_indices=out_ids,constant_angular_mode_amplitude=1/np.sqrt(VOLUME),
        constant_angular_current_integral=VOLUME*(1/np.sqrt(VOLUME))**2,
        current_normalization='unit L2(dOmega) constant external spinors, homogeneous field value1; canonical At/N and Ai/R vertices; original cap/radial wall Green, no additional cap factor',
        matching_equation='G_F_measured=c_F[complete matched charged-current contraction]/E_kappa^2; this static restriction retains its complete V-A remainder',
        physical_GF_or_unit_selected=False,physical_F2=None)
