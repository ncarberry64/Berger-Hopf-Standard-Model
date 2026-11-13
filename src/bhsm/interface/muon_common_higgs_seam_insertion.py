"""Common Higgs/Yukawa coefficients of the original two-eta-sheet seam.

All ambient matrices here are NORMALIZATION NUMERATORS. No u_L/u_R is
assigned. Their exact inverse factors and independent source jets must be
applied for an ambient field realization. The intrinsic normalized18 seam
coefficient follows without those factors, by exact mode/trace cancellation.
"""
from __future__ import annotations
import numpy as np


def fixed_intrinsic_higgs_vertices():
    """Four real-coordinate matrices; complex sources combine them linearly."""
    from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
    e=np.eye(4)
    return fixed_y_higgs_hamiltonian(e[:,:2]+1j*e[:,2:])


def common_higgs_seam_maps(H,Hdot,temporal,wall_radial):
    """Original1200 scalar image, including dependent -eta H and Hdot."""
    from .muon_parent_positive_coupled_temporal import paired_scalar_orbit_maps
    return paired_scalar_orbit_maps(H,Hdot,temporal,wall_radial)


def full_higgs_seam_numerator_jet(H,Hdot,material_velocity,material_velocity_time,
        surface_density,surface_density_time,*,full_representation=None):
    """Actual384 cross-sheet coefficients, with Gamma0 exactly once.

    The proper side boosts use helper argument -eps U, as fixed by the
    originating signed D5 principal. The scalar density is ell_L R^3,
    with the ORIGINAL timelike Lorentz wall clock, not positive ell_E,
    before a once-only unit-S3 angular volume. Supplied time is a real axis.
    """
    from .muon_full_d5_localized_lepton_trace import (
        full_d5_localized_lepton_trace,moving_d5_material_trace_frame,
        lift_localized_analytic_source)
    h,hd=np.asarray(H),np.asarray(Hdot)
    if h.shape!=(4,)or hd.shape!=(4,)or any(not np.isrealobj(a)or not np.isfinite(a).all()for a in(h,hd)):
        raise ValueError('same REAL H/Hdot wall coefficients required')
    vals=[material_velocity,material_velocity_time,surface_density,surface_density_time]
    if any(not np.isreal(v)or not np.isfinite(v)for v in vals)or abs(material_velocity)>=1 or surface_density<=0:
        raise ValueError('actual real timelike wall and positive original surface measure required')
    f=full_d5_localized_lepton_trace()if full_representation is None else full_representation
    W=f['localized_lepton18_trace_lift'];D=f['localized_lepton18_literal_dual']
    G0=np.kron(np.eye(3),f['gamma5D_self_dual128'][0]);P=np.diag(np.r_[np.ones(12),np.zeros(6)]);Q=np.eye(18)-P
    V=fixed_intrinsic_higgs_vertices();M=np.einsum('c,cij->ij',h,V);Md=np.einsum('c,cij->ij',hd,V)
    frames={}
    for label,eps in(('plus',1),('minus',-1)):
        b=moving_d5_material_trace_frame(-eps*material_velocity,-eps*material_velocity_time,full_representation=f)
        S=np.kron(np.eye(3),b['spin_boost128']);Si=np.kron(np.eye(3),b['spin_boost_inverse128'])
        St=np.kron(np.eye(3),b['spin_boost_first128']);Sit=np.kron(np.eye(3),b['spin_boost_inverse_first128'])
        frames[label]=dict(right_numerator=D@Si,right_numerator_time=D@Sit,
            Dirac_bar_left_numerator=S@G0@W,Dirac_bar_left_numerator_time=St@G0@W,
            mode_right_numerator=S@W,mode_right_numerator_time=St@W,
            mode_Dirac_bar_left_numerator=D@G0@Si,mode_Dirac_bar_left_numerator_time=D@G0@Sit,
            spin_boost=S,spin_boost_time=St,spin_boost_inverse=Si,spin_boost_inverse_time=Sit)
    channels={};rho=float(surface_density);rhot=float(surface_density_time)
    for label,left,right,A,B in(('LR','plus','minus',P,Q),('RL','minus','plus',Q,P)):
        l,r=frames[left],frames[right]
        # Existing analytic source lift is the canonical384 numerator; the
        # left Gamma0 and actual distinct side boosts are applied ONCE.
        lifted=np.array([lift_localized_analytic_source(A@v@B,full_representation=f)for v in V])
        N=-rho*np.einsum('ij,cjk,kl->cil',l['spin_boost']@G0,lifted,r['spin_boost_inverse'],optimize=True)
        Nt=-rhot*np.einsum('ij,cjk,kl->cil',l['spin_boost']@G0,lifted,r['spin_boost_inverse'],optimize=True)
        Nt-=rho*np.einsum('ij,cjk,kl->cil',l['spin_boost_time']@G0,lifted,r['spin_boost_inverse'],optimize=True)
        Nt-=rho*np.einsum('ij,cjk,kl->cil',l['spin_boost']@G0,lifted,r['spin_boost_inverse_time'],optimize=True)
        channels[label]=dict(ambient_vertex_numerators=N,ambient_vertex_numerators_time=Nt,
            ambient_background_numerator=np.einsum('c,cij->ij',h,N),
            ambient_background_numerator_time=np.einsum('c,cij->ij',hd,N)+np.einsum('c,cij->ij',h,Nt),
            left_sheet=left,right_sheet=right,left_chiral_projector=A,right_chiral_projector=B,
            unknown_normal_factor='1/(u_L_'+left+'*u_R_'+right+')',
            unknown_normal_factor_time='-alpha*(u_Ldot_'+left+'/u_L_'+left+'+u_Rdot_'+right+'/u_R_'+right+')')
    return dict(fixed_real_Higgs_vertices=V,background_intrinsic_mass=M,background_intrinsic_mass_time=Md,
        intrinsic_normalized_vertex=-rho*V,intrinsic_normalized_vertex_time=-rhot*V,
        intrinsic_normalized_background=-rho*M,intrinsic_normalized_background_time=-rhot*M-rho*Md,
        frames=frames,channels=channels,surface_density=rho,surface_density_time=rhot,
        normal_mode_values_and_source_jets=None,original_Dirac_bar_Gamma0_count=1,
        once_only_intrinsic_Higgs_seam_no_extra_D4_kinetic_or_bulk_D5_mass=True,
        physical_native_or_outgoing_seam_identified=False)


def apply_intrinsic_common_higgs_seam(direction,scalar_map,vertices,gaunt,value):
    """Complete normalized18 operator coefficient on arbitrary common1200.

    vertices already include the original -rho. Angular Gaunt uses unit Haar;
    multiply2pi² once ONLY when forming the angularly integrated weak action.
    Complex sources combine fixed real basis matrices without conjugation.
    """
    z=np.asarray(direction);V=np.asarray(vertices);u=np.asarray(value)
    if z.shape!=(1200,)or scalar_map.shape!=(80,1200)or V.shape!=(4,18,18)or u.shape[0]!=18:
        raise ValueError('original common1200/scalar80/intrinsic18 maps required')
    h=(scalar_map@z).reshape(4,20)
    return np.einsum('ch,cij,ohk,jkn->ion',h,V,gaunt,u,optimize=True)


def apply_ambient_common_higgs_channel(direction,scalar_map,numerator_vertices,gaunt,value):
    """One384 cross-sheet numerator, no implicit normal factor or other side."""
    z=np.asarray(direction);h=(scalar_map@z).reshape(4,20)
    V=np.asarray(numerator_vertices);u=np.asarray(value)
    if z.shape!=(1200,)or V.shape!=(4,384,384)or u.shape[0]!=384:
        raise ValueError('complete384 source-sheet/common1200 coefficient maps required')
    return np.einsum('ch,cij,ohk,jkn->ion',h,V,gaunt,u,optimize=True)
