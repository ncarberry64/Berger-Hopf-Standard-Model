"""Wilson-transported local jets of the actually reached open-current blocks.

The current kernel is kept in the complete C6 family fiber until its
charged injection at the observation point.  This removes spin/gauge
frame terms without declaring the charged subspace dynamically invariant.
The finite positive-factor kernel is not identified with a Lorentz
self-energy or an amputated on-shell vertex by this application.
"""
from __future__ import annotations

import numpy as np

from .muon_magnetic_mixed_green import _finite, _positive, family_fiber_indices
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection
from .muon_magnetic_open_lepton_vertex import matched_symbol_magnetic_spin_reduction
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .muon_intrinsic_scalar_discretization import (
    scalar_basis_values, real_scalar_basis_transform, real_scalar_basis_labels,
    scalar_angular_derivative_matrices,
)

VOLUME=2*np.pi**2


def round_spatial_spin_connection(radius):
    """The Levi-Civita spin lift of the retained right round coframe.

    [E_i,E_j]=-2 epsilon_ijk E_k and the round metric give the unique
    torsion-free lift Omega_spin,i=-gamma_j gamma_k/(2R4).
    In the retained18 Weyl fiber this is i alpha_i gamma5/(2R4).
    Its contraction -i sum(alpha_i Omega_spin,i) is exactly the owned
    3 gamma5/(2R4).  It is not a connection inferred only from that sum.
    """
    R=_positive(radius,'actual round radius')
    frame=lepton_current_hilbert_representation()
    result=.5j*np.einsum('aij,jk->aik',frame['alpha'],frame['gamma5'])/R
    contraction=-1j*np.einsum('aij,ajk->ik',frame['alpha'],result)
    return dict(connection=result,contracted_round_spin=contraction,
        owned_contracted_spin_difference=contraction-1.5*frame['gamma5']/R,
        coframe='right body frame; [E_i,E_j]=-2 epsilon_ijk E_k',
        connection_coordinates='physical orthonormal spatial derivatives E_i/R4')


def normal_coordinate_first_momentum_lift(radius):
    """Exact inherited n1 lifts of the three local coordinates X_j=R4*q_j.

    Y1 contains the four Haar-average-normalized quaternion coordinates.
    At identity the derivative rows are orthogonal with squared norm4.
    The coefficient columns R4*dY_j/4 therefore have value0 and physical
    derivative delta_ij.  Tensor I6 gives eighteen FIRST momentum tangent
    columns, not a physical incoming state or a global plane-wave choice.
    """
    R=_positive(radius,'actual round radius')
    labels=real_scalar_basis_labels(1);ids=[j for j,l in enumerate(labels) if l[0]==1]
    U=real_scalar_basis_transform(1)
    y=(scalar_basis_values(np.eye(2,dtype=complex)[None],1)@U)[0].real
    E=scalar_angular_derivative_matrices(1)
    Er=np.einsum('ij,ajk,kl->ail',U.conj().T,E,U).real
    dy=np.einsum('h,ahk->ak',y,Er)[:,ids]
    coefficients=(R/4)*dy.T
    return dict(harmonic_labels=[labels[j] for j in ids],n1_value_at_identity=y[ids],
        n1_unit_coframe_derivative_at_identity=dy,
        scalar_coordinate_coefficients=coefficients,
        incoming_C6_first_momentum_lift=np.kron(coefficients,np.eye(6)),
        value_at_identity=y[ids]@coefficients,
        physical_gradient_at_identity=dy@coefficients/R,
        domain_scope='local normal-coordinate first jet in the inherited scalar n1 space; no global external pole or momentum state selected')


def covariant_bilocal_first_jet(forward,reverse,values,physical_derivatives,connection):
    """Coincidence jet after Wilson transport to one observation frame.

    K=phi1(x)D10 phi0(y)^*+phi0(x)D01 phi1(y)^*, with
    phi=Y/sqrt(2pi²).  Wilson transport gives center derivative
    dxK+dyK+[Omega,K] and relative derivative
    (dxK-dyK+Omega K+K Omega)/2.  Both endpoint derivatives are
    retained even when the kernel is non-Hermitian.
    """
    F=_finite(forward,'actual n1 output/n0 input current kernel')
    B=_finite(reverse,'actual n0 output/n1 input current kernel')
    y=_finite(values,'inherited real n1 values',real=True)
    dy=_finite(physical_derivatives,'inherited physical n1 derivative',real=True)
    O=_finite(connection,'actual full spin and gauge spatial connection')
    if (y.shape!=(4,) or dy.shape!=(3,4) or F.shape!=(3,24,6) or B.shape!=(3,6,24)
            or O.shape!=(3,6,6)):
        raise ValueError('complete three magnetic axes, C6 family and scalar n0/n1 blocks required')
    if np.max(abs(O+O.conj().transpose(0,2,1)))>64*np.finfo(float).eps*max(1.,np.max(abs(O))):
        raise ValueError('anti-Hermitian full spin/gauge connection required')
    F=F.reshape(3,4,6,6);B=B.reshape(3,6,4,6).transpose(0,2,1,3)
    kf=np.einsum('h,Ahij->Aij',y,F)/VOLUME
    kb=np.einsum('h,Ahij->Aij',y,B)/VOLUME
    dx=np.einsum('ah,Ahij->Aaij',dy,F)/VOLUME
    dyK=np.einsum('ah,Ahij->Aaij',dy,B)/VOLUME
    K=kf+kb
    left=O[None]@K[:,None];right=K[:,None]@O[None]
    return dict(point_kernel=K,forward_point_kernel=kf,reverse_point_kernel=kb,
        coordinate_left_derivative=dx,coordinate_right_derivative=dyK,
        Wilson_center_first_jet=dx+dyK+left-right,
        Wilson_relative_first_jet=(dx-dyK+left+right)/2,
        endpoint_Hermitian_pair_difference=B-F.conj().transpose(0,1,3,2),
        point_Hermiticity_difference=K-K.conj().transpose(0,2,1),
        Wilson_equations=('K_W=U(X,x)K(x,y)U(y,X)',
            'd_center K_W=dxK+dyK+Omega K-K Omega',
            'd_relative K_W=(dxK-dyK+Omega K+K Omega)/2'),
        local_normal_frame_connection_removed=True,
        full_differential_kernel_reconstructed=False)


def source_image_covariant_current_jet(current,wall_gauge,radius,H,*,family):
    """Execute the actual represented Wilson jet and Dirac Clifford readout.

    The source directions are the same three physical magnetic axes.
    No extra charge, source profile or Haar normalization is inserted.
    Gamma-matrix components are evaluated algebraically; an unamputated
    positive-factor Green insertion is not assigned an F2 coefficient.
    """
    R=_positive(radius,'actual round radius');ids=family_fiber_indices(family)
    a=_finite(wall_gauge,'actual total wall gauge connection',real=True)
    if a.shape!=(5,4):raise ValueError('all five actual wall connection components required')
    spin=round_spatial_spin_connection(R)
    gauge=np.einsum('ac,cij->aij',a[2:],lepton_unit_trace_gauge_representation()['generators'])/R
    Omega=(spin['connection']+gauge)[:,ids][:,:,ids]
    normal=normal_coordinate_first_momentum_lift(R)
    result=covariant_bilocal_first_jet(current.get('forward_full_Green_insertion'),
        current.get('reverse_full_Green_insertion'),normal['n1_value_at_identity'],
        normal['n1_unit_coframe_derivative_at_identity']/R,Omega)
    J=charged_dirac_injection(H,family=family)['charged'][ids]
    project=lambda x:np.einsum('ui,...uv,vj->...ij',J.conj(),x,J)
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    point=project(result['point_kernel']);center=project(result['Wilson_center_first_jet'])
    relative=project(result['Wilson_relative_first_jet'])
    sigma=np.array([1j*gamma[2]@gamma[3],1j*gamma[3]@gamma[1],1j*gamma[1]@gamma[2]])
    # These are actual Clifford contractions, not an amputation or an
    # assertion that a nonstationary positive-factor inverse is Lorentz G.
    point_spin=np.einsum('kij,Aji->Ak',sigma,point)/4
    center_spin=np.einsum('kij,Aaji->Aak',sigma,center)/4
    relative_spin=np.einsum('kij,Aaji->Aak',sigma,relative)/4
    result.update(full_spatial_connection=Omega,round_spin_connection=spin['connection'],
        owned_contracted_spin_difference=spin['owned_contracted_spin_difference'],
        charged_point_kernel=point,charged_Wilson_center_first_jet=center,
        charged_Wilson_relative_first_jet=relative,
        charged_Dirac_spin_component=point_spin,
        charged_Dirac_spin_center_jet=center_spin,
        charged_Dirac_spin_relative_jet=relative_spin,
        incoming_C6_first_momentum_lift=normal['incoming_C6_first_momentum_lift'],
        physical_normal_coordinate_gradient=normal['physical_gradient_at_identity'],
        statistics_or_native_Sigma_sign_assigned=False,
        normalized_signed_soft_Pauli=None,
        Pauli_scope='No F2 tensor assigned: these are covariant jets of the reached unamputated finite factor-current blocks, not a demonstrated Lorentz open vertex.',
        physical_a_mu=None,physical_g_mu=None)
    return result


def normal_frame_magnetic_principal_symbol_application(point_vertex,physical_gradient,
        connection,H,*,family,electric_charge):
    """Normalize the actual magnetic action first jet on its local symbol.

    A spin/gauge normal frame removes Omega(X) from the kinetic symbol;
    it changes the source derivative to dV+[Omega,V].  The full C18
    transported source is projected only afterwards.  M(H(X)) on the
    H-selected charged fiber is the fixed-Y mass times beta, while its
    neutral complement is retained by the upstream current solve.

    This executes the first-gradient local positive-band contraction.
    It is not the finite Green kernel's Lorentz amputation, its physical
    pole residue, or the full higher-gradient background expansion.
    """
    V=_finite(point_vertex,'actual complete canonical magnetic point vertex')
    dV=_finite(physical_gradient,'actual complete canonical source spatial gradient')
    O=_finite(connection,'actual complete spin and gauge connection')
    if V.shape!=(3,18,18) or dV.shape!=(3,3,18,18) or O.shape!=(3,18,18):
        raise ValueError('three physical magnetic axes and complete C18 point/gradient/connection required')
    if np.max(abs(O+O.conj().transpose(0,2,1)))>64*np.finfo(float).eps*max(1.,np.max(abs(O))):
        raise ValueError('anti-Hermitian full spin/gauge connection required')
    covariant=dV+O[None]@V[:,None]-V[:,None]@O[None]
    h=_finite(H,'actual Higgs value')
    if h.shape!=(2,):raise ValueError('actual complex Higgs doublet required')
    J=charged_dirac_injection(h,family=family)['charged']
    project=lambda x:np.einsum('ui,...uv,vj->...ij',J.conj(),x,J)
    Y=lepton_current_hilbert_representation()['family_Y'][family,family].real
    mass=float(Y*np.linalg.norm(h))
    result=matched_symbol_magnetic_spin_reduction(project(V),project(covariant),
        matched_mass_action=mass,electric_charge=electric_charge)
    result.update(full_source_Wilson_spatial_jet=covariant,
        ordinary_to_covariant_source_jet_contact=covariant-dV,
        local_normal_frame_principal_symbol='alpha.p+M(H(X)); H-selected charged mass=Y_family*norm(H(X))*beta',
        background_connections_transported_before_charged_projection=True,
        minimal_Dirac_coefficient_sign='electron energy shift +e sigma.B/(2m)',
        external_positive_factor_Green_identified_with_Lorentz_propagator=False,
        native_loop_or_LSZ_amputation_completed=False,
        physical_a_mu=None,physical_g_mu=None)
    return result


def reached_first_momentum_source_image(source_vertices,gaunt,even_labels,radius):
    """Apply the SAME n1 magnetic insertion to the minimal momentum columns.

    Gaunt is the actual complete even×odd×n1 product already consumed by
    the fixed-background mixed Green.  The newly reached output is n0+n2,
    not zero.  These columns specify the next Green source application;
    they do not complete it with an arbitrary matrix extension.
    """
    X=_finite(source_vertices,'actual magnetic first-order insertion')
    G=_finite(gaunt,'actual even odd n1 Gaunt product',real=True)
    if X.shape!=(3,4,6,6) or G.ndim!=3 or G.shape[1]<4 or G.shape[2]!=4 or len(even_labels)!=G.shape[0]:
        raise ValueError('complete n1 magnetic C6 insertion and inherited Gaunt image required')
    lift=normal_coordinate_first_momentum_lift(radius)['incoming_C6_first_momentum_lift']
    n02=[j for j,l in enumerate(even_labels) if l[0] in (0,2)]
    if len(n02)!=10:raise ValueError('complete even n0+n2 scalar image required')
    Xi=np.einsum('ehx,Axuv->Aeuhv',G[n02,:4],X).reshape(3,60,24)
    reached=Xi@lift
    return dict(incoming_first_momentum_lift=lift,
        complete_n0_n2_source_image=reached,
        source_image_n0=reached[:,:6],source_image_n2=reached[:,6:],
        complete_n0_n2_harmonic_labels=[even_labels[j] for j in n02],
        required_next_application='same enlarged temporal mixed Green derivative on incoming18 normal-momentum tangent columns and complete even60 output rows; both open placements, squares, numerator and scalar insertion',
        new_scalar_mixed_vertices='PHodd(n1+n3) times externaln2 reaches fermionodd n1+n3+n5; PHimage_even(n0+n2+n4) times externaln2 reaches fermioneven through n6',
        existing_reverse_n0_rows_sufficient_for_complete_first_momentum_jet=False,
        full_external_current_matrix_universally_required=False)
