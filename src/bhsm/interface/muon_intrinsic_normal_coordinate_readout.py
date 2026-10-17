"""Normal-coordinate current applications on the completed image domain.

Constant and momentum-tangent columns must come from one mixed image
action.  This applies their actual full six-component kernels before
charged injection.  The output is a represented operator-action symbol,
not an identification of a proper-time factor Green with Lorentz Sigma.
"""
from __future__ import annotations

import numpy as np

from .muon_magnetic_mixed_green import _finite, _positive, family_fiber_indices
from .muon_intrinsic_covariant_open_current_jet import (
    normal_coordinate_first_momentum_lift, round_spatial_spin_connection,
)
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection, PAULI
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from .muon_intrinsic_scalar_discretization import scalar_s3_discretization


def _evaluation(levels, radius):
    """Inherited Haar-average basis value and physical right-frame jet."""
    d=scalar_s3_discretization(max(levels));ids=[j for j,l in enumerate(d['real_basis_labels']) if l[0] in levels]
    # The identity is present in the quadrature but its position is not a
    # basis convention. Evaluate it with the same explicit value map.
    from .muon_intrinsic_scalar_discretization import scalar_basis_values, real_scalar_basis_transform
    y=(scalar_basis_values(np.eye(2,dtype=complex)[None],max(levels))@real_scalar_basis_transform(max(levels)))[0]
    if np.max(abs(y.imag))>16*np.finfo(float).eps:raise ArithmeticError('real inherited evaluation map required')
    dy=np.einsum('h,ahk->ak',y.real,d['real_angular_derivative_matrices'])[:,ids]/radius
    return y.real[ids],dy


def normal_coordinate_operator_action(constant_forward, tangent_forward,
        constant_reverse, tangent_reverse, *, radius, wall_connection, H, family):
    """Apply complete constant and first-momentum columns on one image action.

    A unit physical constant input has coefficient sqrt(V) in phi0;
    output evaluation has 1/sqrt(V), so no residual Haar-volume factor
    remains. The same cancellation applies to X_j=R*q_j tangent inputs.
    d_pj S= i S[X_j] follows from e^(i p.X), with the inherited real
    coordinate lift. All n0+n2 output rows participate in S[X_j].

    Reverse kernels are retained independently: a temporal anti-Hermitian
    source does not justify forcing them to be conjugate transposes.
    """
    r=_positive(radius,'actual current round radius')
    C,T,Cr,Tr=[_finite(x,n)for x,n in zip((constant_forward,tangent_forward,constant_reverse,tangent_reverse),
        ('same-image constant forward','same-image tangent forward','same-image constant reverse','same-image tangent reverse'))]
    if C.shape!=(3,24,6) or T.shape!=(3,60,24) or Cr.shape!=(3,6,24) or Tr.shape!=(3,24,60):
        raise ValueError('complete common-domain three-axis C6 constant/n1/n0+n2 blocks required')
    a=_finite(wall_connection,'actual total material wall connection',real=True)
    if a.shape!=(5,4):raise ValueError('all five actual wall connection components required')
    normal=normal_coordinate_first_momentum_lift(r)
    y1,d1=_evaluation((1,),r);ye,de=_evaluation((0,2),r)
    if len(y1)!=4 or len(ye)!=10:raise ArithmeticError('complete inherited normal input and image required')
    Cs=C.reshape(3,4,6,6);Ts=T.reshape(3,10,6,4,6)
    Crs=Cr.reshape(3,6,4,6);Trs=Tr.reshape(3,4,6,10,6)
    Q=normal['scalar_coordinate_coefficients']
    value=np.einsum('h,Ahij->Aij',y1,Cs)
    gradient=np.einsum('ah,Ahij->Aaij',d1,Cs)
    coordinate=np.einsum('e,Aeihj,hk->Akij',ye,Ts,Q)
    coordinate_gradient=np.einsum('ae,Aeihj,hk->Aakij',de,Ts,Q)
    # Reverse endpoint coordinate moments remain separate. This is the
    # corresponding left test application, not an asserted adjoint.
    reverse_value=np.einsum('h,Aihj->Aij',y1,Crs)
    reverse_coordinate=np.einsum('e,Ahiej,hk->Akij',ye,Trs,Q)
    ids=family_fiber_indices(family)
    omega=(round_spatial_spin_connection(r)['connection']+
        np.einsum('ac,cij->aij',a[2:],lepton_unit_trace_gauge_representation()['generators'])/r)[:,ids][:,:,ids]
    covariant_gradient=gradient+omega[None]@value[:,None]-value[:,None]@omega[None]
    J=charged_dirac_injection(H,family=family)['charged'][ids]
    charged=lambda x:np.einsum('ui,...uv,vj->...ij',J.conj(),x,J)
    return dict(full_constant_symbol=value,full_coordinate_response=coordinate,
        full_first_momentum_symbol=1j*coordinate,
        full_source_spatial_first_jet=gradient,
        full_Wilson_source_spatial_first_jet=covariant_gradient,
        full_coordinate_response_spatial_jet=coordinate_gradient,
        full_reverse_constant_symbol=reverse_value,
        full_reverse_coordinate_response=reverse_coordinate,
        forward_reverse_value_difference=reverse_value-value.conj().swapaxes(-1,-2),
        full_spatial_connection=omega,
        charged_constant_symbol=charged(value),charged_first_momentum_symbol=charged(1j*coordinate),
        charged_Wilson_source_spatial_first_jet=charged(covariant_gradient),
        charged_coordinate_response=charged(coordinate),
        charged_injection=J,normal_coordinate_lift=normal['incoming_C6_first_momentum_lift'],
        canonical_density_and_Haar_factors='unit input sqrt(V), output1/sqrt(V) cancel; no additional2pi²',
        first_momentum_equation='d_pj S[e^(i p.X)]|p=0=i S[X_j], X_j=R*q_j',
        coordinate_extension_scope='actual represented chord-coordinate input on S3; first local germ equals normal coordinate; no claim of full differential Wigner symbol or omitted incoming modes',
        finite_factor_kernel_identified_with_Lorentz_self_energy=False,
        physical_a_mu=None,physical_g_mu=None)


def local_matched_spin_functional(point_symbol, spatial_jet, *, mass, electric_charge):
    """Execute the authorized local matched Dirac spin linear functional.

    The result is complex unless the supplied action symbol is Hermitian.
    It is the spin projection of V - i[alpha_j,d_j V]/(4m) on the matched
    positive band, divided by e/(2m). Its use as a native Pauli value
    additionally requires a demonstrated Lorentz action symbol; this
    function does not perform that operator identification.
    """
    V=_finite(point_symbol,'actual charged symbol');D=_finite(spatial_jet,'actual charged covariant spatial jet')
    m=_positive(mass,'independently matched pole mass in the SAME action units');e=_positive(electric_charge,'independently matched electric charge')
    if V.shape!=(3,4,4) or D.shape!=(3,3,4,4):raise ValueError('complete magnetic axes and charged Dirac jets required')
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac'];alpha=np.array([gamma[0]@g for g in gamma[1:]])
    contact=-1j*sum(alpha[j]@D[:,j]-D[:,j]@alpha[j]for j in range(3))/(4*m)
    band=(V+contact)[:,:2,:2];spin=np.einsum('kij,Aji->Ak',PAULI,band)/2
    return dict(matched_positive_band=band,matched_spin_component=spin,
        matched_dimensionless_spin_functional=2*m*spin/e,
        Hermitian_symbol_remainder=V-V.conj().swapaxes(-1,-2),
        Hermitian_spatial_jet_remainder=D-D.conj().swapaxes(-1,-2),
        normalized_minimal_Dirac_denominator=e/(2*m),
        normalization_equation='2m/e * spin[P+(V-i sum[alpha_j,D_jV]/(4m))P+]',
        operator_identification_performed=False,physical_a_mu=None,physical_g_mu=None)
