"""Full18 normal-coordinate applications of the changing magnetic kernel.

The constant and first-input-momentum arrays must be applications of one
source/domain action. Spin-major ordering is explicit; the old scalar
Higgs-only C6 tensors are not substituted. Lorentz/domain matching remains
with the operator producer, rather than being assigned by this projection.
"""
from __future__ import annotations
import numpy as np

from .muon_intrinsic_normal_coordinate_readout import _evaluation,local_matched_spin_functional
from .muon_intrinsic_covariant_open_current_jet import normal_coordinate_first_momentum_lift,round_spatial_spin_connection
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation,fixed_y_higgs_hamiltonian
from .muon_magnetic_open_lepton_vertex import PAULI
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation


def _finite(value,name,shape=None,*,real=False):
    a=np.asarray(value)
    if a.dtype.kind not in 'fciu' or(real and not np.isrealobj(a)):
        raise ValueError(name+' requires actual finite numerical coefficients')
    a=np.asarray(a,float if real else complex)
    if (shape is not None and a.shape!=shape)or not np.isfinite(a).all():
        raise ValueError(name+' is missing, nonfinite or incomplete')
    return a


def changing_normal_current_readout(constant_forward,tangent_forward,constant_reverse,tangent_reverse,
        *,radius,wall_connection,H,matched_mass_action,electric_charge,family=1):
    """Execute both directions and the authorized local matched spin ratio.

    Axis order is magnetic, full18 spin/family, then angular. Constant
    output is spin18*4+h1; tangent output is spin18*10+h02 and its input
    spin18*4+h1. No charge, Gaussian sign or supertrace weight is reinserted.
    Unit point input/output Haar factors cancel in this operator action.

    The three local coordinate inputs X_j=R*q_j are computational first
    jets, not a global plane-wave state. In particular this finite moment
    is not by itself the complete Wilson-transformed Wigner operator.
    """
    R=_finite(radius,'actual radius',(),real=True);m=_finite(matched_mass_action,'matched mass in same action units',(),real=True)
    e=_finite(electric_charge,'matched positive electric charge',(),real=True)
    if min(float(R),float(m),float(e))<=0:raise ValueError('positive actual geometry and independent matching required')
    C=_finite(constant_forward,'same-source constant forward',(3,72,18))
    T=_finite(tangent_forward,'same-source tangent forward',(3,180,72))
    Cr=_finite(constant_reverse,'same-source constant reverse',(3,18,72))
    Tr=_finite(tangent_reverse,'same-source tangent reverse',(3,72,180))
    a=_finite(wall_connection,'actual complete material wall connection',(5,4),real=True)
    h=_finite(H,'actual Higgs doublet',(2,))
    y1,d1=_evaluation((1,),float(R));ye,de=_evaluation((0,2),float(R))
    Q=normal_coordinate_first_momentum_lift(float(R))['scalar_coordinate_coefficients']
    c=C.reshape(3,18,4,18);t=T.reshape(3,18,10,18,4)
    cr=Cr.reshape(3,18,18,4);tr=Tr.reshape(3,18,4,18,10)
    point=np.einsum('h,Aihj->Aij',y1,c)
    gradient=np.einsum('ah,Aihj->Aaij',d1,c)
    coordinate=np.einsum('e,Aiejh,hb->Abij',ye,t,Q)
    coordinate_gradient=np.einsum('ae,Aiejh,hb->Aabij',de,t,Q)
    reverse_point=np.einsum('h,Aijh->Aij',y1,cr)
    reverse_coordinate=np.einsum('e,Aihje,hb->Abij',ye,tr,Q)
    omega=round_spatial_spin_connection(float(R))['connection']+np.einsum('ac,cij->aij',a[2:],lepton_unit_trace_gauge_representation()['generators'])/float(R)
    covariant=gradient+omega[None]@point[:,None]-point[:,None]@omega[None]
    J=charged_dirac_injection(h,family=family)['charged']
    project=lambda x:np.einsum('ui,...uv,vj->...ij',J.conj(),x,J)
    cp,cd=project(point),project(covariant)
    spin=local_matched_spin_functional(cp,cd,mass=float(m),electric_charge=float(e))
    return dict(full_constant_symbol=point,full_reverse_constant_symbol=reverse_point,
        full_source_spatial_first_jet=gradient,full_Wilson_source_spatial_first_jet=covariant,
        full_coordinate_response=coordinate,full_first_input_momentum_response=1j*coordinate,
        full_coordinate_response_spatial_jet=coordinate_gradient,
        full_reverse_coordinate_response=reverse_coordinate,
        full_spatial_spin_gauge_connection=omega,
        forward_reverse_value_adjoint_difference=reverse_point-point.conj().swapaxes(-1,-2),
        charged_constant_symbol=cp,charged_Wilson_source_spatial_first_jet=cd,
        charged_first_input_momentum_response=project(1j*coordinate),
        charged_reverse_coordinate_response=project(reverse_coordinate),charged_injection=J,
        local_matched_spin_functional=spin['matched_dimensionless_spin_functional'],
        local_matched_positive_band=spin['matched_positive_band'],
        source_spatial_Wilson_contact=project(covariant-gradient),
        scalar_coordinate_coefficients=Q,
        matching=dict(mass_action=float(m),electric_charge=float(e),minimal_Dirac_denominator=float(e)/(2*float(m))),
        coefficient_order='spin-major output/input; exact inherited real n1 and n0+n2 harmonic maps',
        normalization='unit point input sqrt(2pi²) and output1/sqrt(2pi²) cancel; actual source charge and supplied operator sign retained once',
        first_momentum_equation='derivative_pj S[exp(i p.X)] at p0=i S[X_j], X_j=R*q_j',
        full18_transport_before_charged_projection=True,charged_subspace_invariance_assumed=False,
        complete_Wilson_bilocal_or_energy_LSZ_derivative_supplied=False,
        positive_factor_kernel_relabelled_as_Lorentz_Sigma=False,
        physical_signed_soft_Pauli=None,physical_a_mu=None,physical_g_mu=None)


def changing_family_normal_current_readout(constant_forward,tangent_forward,
        constant_reverse,tangent_reverse,*,family_indices,radius,wall_connection,H,
        matched_mass_action,electric_charge,family):
    """Use the exact family restriction without completing an unknown family.

    All six charged/neutral fibers and the complete supplied angular
    columns remain.  The eighteen-dimensional representation checks that
    the actual spin/gauge/mass maps preserve this restriction.  An omitted
    tau block is not produced or assigned zero.
    """
    if type(family)is not int or family not in (1,2):
        raise ValueError('explicit middle or light family restriction required')
    ids=np.asarray(family_indices)
    owned=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
    if ids.dtype.kind not in 'iu' or ids.shape!=(6,) or not np.array_equal(ids,owned):
        raise ValueError('literal retained full18 family indices required')
    R=_finite(radius,'actual radius',(),real=True);m=_finite(matched_mass_action,'matched mass',(),real=True)
    e=_finite(electric_charge,'matched charge',(),real=True)
    if min(float(R),float(m),float(e))<=0:raise ValueError('positive explicit geometry and matching required')
    C=_finite(constant_forward,'same family constant forward',(3,24,6))
    T=_finite(tangent_forward,'same family tangent forward',(3,60,24))
    Cr=_finite(constant_reverse,'same family constant reverse',(3,6,24))
    Tr=_finite(tangent_reverse,'same family tangent reverse',(3,24,60))
    a=_finite(wall_connection,'actual complete wall connection',(5,4),real=True)
    h=_finite(H,'actual Higgs doublet',(2,))
    embedding=np.eye(18)[:,ids];other=np.setdiff1d(np.arange(18),ids)
    fullomega=round_spatial_spin_connection(float(R))['connection']+np.einsum('ac,cij->aij',a[2:],lepton_unit_trace_gauge_representation()['generators'])/float(R)
    maps=[*fullomega,*lepton_current_hilbert_representation()['alpha'],fixed_y_higgs_hamiltonian(h[None])[0]]
    if any(np.any(x[np.ix_(ids,other)])or np.any(x[np.ix_(other,ids)])for x in maps):
        raise ValueError('actual spin/gauge/fixed-Y action does not preserve this family')
    omega=fullomega[:,ids][:,:,ids]
    y1,d1=_evaluation((1,),float(R));ye,de=_evaluation((0,2),float(R))
    Q=normal_coordinate_first_momentum_lift(float(R))['scalar_coordinate_coefficients']
    c=C.reshape(3,6,4,6);t=T.reshape(3,6,10,6,4)
    cr=Cr.reshape(3,6,6,4);tr=Tr.reshape(3,6,4,6,10)
    value=np.einsum('h,Aihj->Aij',y1,c)
    gradient=np.einsum('ah,Aihj->Aaij',d1,c)
    coordinate=np.einsum('e,Aiejh,hb->Abij',ye,t,Q)
    covariant=gradient+omega[None]@value[:,None]-value[:,None]@omega[None]
    J=embedding.T@charged_dirac_injection(h,family=family)['charged']
    project=lambda x:np.einsum('ui,...uv,vj->...ij',J.conj(),x,J)
    spin=local_matched_spin_functional(project(value),project(covariant),mass=float(m),electric_charge=float(e))
    return dict(family_constant_symbol=value,family_coordinate_response=coordinate,
        family_first_input_momentum_response=1j*coordinate,
        family_source_spatial_first_jet=gradient,family_Wilson_source_spatial_first_jet=covariant,
        family_coordinate_response_spatial_jet=np.einsum('ae,Aiejh,hb->Aabij',de,t,Q),
        family_reverse_constant_symbol=np.einsum('h,Aijh->Aij',y1,cr),
        family_reverse_left_test_coordinate_moment=np.einsum('e,Aihje,hb->Abij',ye,tr,Q),
        family_spatial_connection=omega,full18_family_embedding=embedding,family_indices=ids.copy(),
        charged_constant_symbol=project(value),charged_Wilson_source_spatial_first_jet=project(covariant),
        charged_first_input_momentum_response=project(1j*coordinate),charged_injection=J,
        local_matched_spin_functional=spin['matched_dimensionless_spin_functional'],
        local_matched_positive_band=spin['matched_positive_band'],
        scalar_coordinate_coefficients=Q,exact_action_family_invariance_checked=True,
        neutral_return_retained_before_charge_projection=True,unevaluated_families_filled_zero=False,
        complete_Wilson_bilocal_or_energy_LSZ_derivative_supplied=False,
        positive_factor_kernel_relabelled_as_Lorentz_Sigma=False,
        physical_signed_soft_Pauli=None,physical_a_mu=None,physical_g_mu=None)


def matched_kinetic_residue_contact(positive_band_vertex,charged_energy_first,
        *,matched_mass_action,electric_charge):
    """Apply the linear pole-Gram contact to the same-frequency local band.

    With the mass already matched, the local pencil is
    ``(I-Z)(E-m)-B_A(H_B,A+V_A)``. Its symmetric canonical normalization
    adds ``{Z,H_B,A}/2`` to the magnetic band. This is a linear-order
    counterterm identity, not a continuation of the supplied Green or an
    assignment of an interacting pole. The caller must bind identical
    source, clock, external frequency and differential domain first.

    Complex coefficients remain complex. Their Hermitian defects are
    returned; a positive physical pole-Gram is not inferred from them.
    """
    band=_finite(positive_band_vertex,'same-frequency positive magnetic band',(3,2,2))
    energy=_finite(charged_energy_first,'same-frequency charged energy derivative',(4,4))
    mass=_finite(matched_mass_action,'matched mass in same action units',(),real=True)
    charge=_finite(electric_charge,'matched positive charge',(),real=True)
    if min(float(mass),float(charge))<=0:
        raise ValueError('positive independent mass and charge matching required')
    Z=energy[:2,:2]
    minimal=float(charge)/(2*float(mass))*PAULI
    contact=(Z[None]@minimal+minimal@Z[None])/2
    total=band+contact
    spin=lambda x:2*float(mass)/float(charge)*np.einsum('kij,Aji->Ak',PAULI,x)/2
    return dict(positive_band_energy_coefficient=Z,minimal_magnetic_band=minimal,
        kinetic_residue_magnetic_contact=contact,
        residue_corrected_positive_band=total,
        vertex_spin_functional=spin(band),kinetic_residue_spin_contact=spin(contact),
        residue_corrected_spin_functional=spin(total),
        energy_coefficient_Hermitian_defect=Z-Z.conj().T,
        magnetic_band_Hermitian_defect=band-band.conj().swapaxes(-1,-2),
        equation='V_B^canonical=V_B+{Sigma_E,+, e sigma_B/(2m)}/2',
        pure_wavefunction_equation='Sigma=z(E-H0) => Sigma_B=-z H_B, Sigma_E=z; the two magnetic contacts cancel',
        approximation_order='linear supplied loop coefficient; no resummed pole-Gram or higher-order product',
        same_frequency_domain_binding_performed_by_caller=True,
        mass_or_charge_counterterm_applied=False,internal_operator_continuation_performed=False,
        physical_Pauli_or_LSZ_identification_performed=False,
        physical_signed_soft_Pauli=None,physical_a_mu=None,physical_g_mu=None)


def normal_first_weyl_contact(value,source_gradient,coordinate_gradient,coordinate_hessian):
    """Reach the first right-symbol to Weyl-symbol contact in normal space.

    At the normal point ``a_R=S[1]`` and
    ``d_pj a_R=i*S[X_j-x_j]``. Thus the first Weyl contact is
    ``-.5*(sum D_j S[X_j]-3*S[1])``. The moving-input-center term is
    required even for an identity or multiplication operator. The
    higher bilocal/Weyl series is not bounded by this finite first jet.
    """
    v=np.asarray(value);n=v.shape[-1]if v.ndim==3 else 0
    v=_finite(v,'actual magnetic value',(3,n,n))
    d=_finite(source_gradient,'covariant source gradient',(3,3,n,n))
    dm=_finite(coordinate_gradient,'coordinate response gradient',(3,3,3,n,n))
    ddm=_finite(coordinate_hessian,'normal covariant coordinate response Hessian',(3,3,3,3,n,n))
    trace=sum(dm[:,j,j]for j in range(3))
    trace_gradient=sum(ddm[:,:,j,j]for j in range(3))
    contact=-.5*(trace-3*v)
    # Differentiating the remaining -x_j D_j S[1] term contributes
    # one more source derivative at x=0, in addition to the three
    # derivatives of the value-level moving-center contact.
    gradient_contact=-.5*(trace_gradient-4*d)
    return dict(first_Weyl_contact=contact,first_Weyl_source_gradient_contact=gradient_contact,
        first_Weyl_value=v+contact,first_Weyl_source_gradient=d+gradient_contact,
        equation='a_W=a_R+(i/2) sum D_xj d_pj a_R+higher bilocal terms',
        moving_input_center_contact_included=True,complete_bilocal_Weyl_series_evaluated=False)


def _normal_second_evaluation(radius):
    """Round normal second jet in the retained physical right coframe."""
    from .muon_intrinsic_scalar_discretization import scalar_s3_discretization
    d=scalar_s3_discretization(2);ids=[i for i,l in enumerate(d['real_basis_labels'])if l[0]in(0,2)]
    y,_=_evaluation((0,1,2),radius);E=d['real_angular_derivative_matrices']
    epsilon=np.zeros((3,3,3));epsilon[0,1,2]=epsilon[1,2,0]=epsilon[2,0,1]=1
    epsilon[1,0,2]=epsilon[2,1,0]=epsilon[0,2,1]=-1
    # [E_i,E_j]=-2 epsilon_ijk E_k, so the normal Hessian is
    # (E_i E_j+epsilon_ijk E_k)/R² at the identity.
    out=np.array([[(y@(E[i]@E[j]+sum(epsilon[i,j,k]*E[k]for k in range(3))))[ids]/radius**2
        for j in range(3)]for i in range(3)])
    return out,epsilon


def changing_family_current_inverse_covectors(constant_forward,tangent_forward,
        constant_reverse,tangent_reverse,*,family_indices,radius,wall_connection,H,
        electric_charge,family):
    """Apply the normal current covector without assigning a self-energy.

    This linear map applies to either a current inverse component or a
    magnetic self-energy application. Its use does not identify the two.
    A nonmagnetic self-energy residue is not an argument of this map and
    is not completed with a zero. The first normal Weyl contact and both
    momentum endpoints are retained before any action mass is assigned.
    """
    # A unit *formal algebra parameter* extracts the existing full C6
    # germ. It is not an input to its operator, action, or calibration.
    germ=changing_family_normal_current_readout(constant_forward,tangent_forward,
        constant_reverse,tangent_reverse,family_indices=family_indices,radius=radius,
        wall_connection=wall_connection,H=H,matched_mass_action=1.,
        electric_charge=electric_charge,family=family)
    e=float(electric_charge);R=float(radius)
    J=germ['charged_injection'];omega=germ['family_spatial_connection']
    t=_finite(tangent_forward,'complete same-domain momentum return',(3,60,24)).reshape(3,6,10,6,4)
    Q=germ['scalar_coordinate_coefficients']
    ye,de=_evaluation((0,2),R);dd,epsilon=_normal_second_evaluation(R)
    M=germ['family_coordinate_response'];dM=germ['family_coordinate_response_spatial_jet']
    hess=np.einsum('ace,Auevh,hb->Aacbuv',dd,t,Q)
    covd=dM+omega[None,:,None]@M[:,None]-M[:,None]@omega[None,:,None]
    for i in range(3):
        for j in range(3):
            hess[:,i,j]+=omega[i][None,None]@dM[:,j]-dM[:,j]@omega[i][None,None]
            hess[:,i,j]+=omega[j][None,None]@dM[:,i]-dM[:,i]@omega[j][None,None]
            comm=omega[j][None,None]@M-M@omega[j][None,None]
            hess[:,i,j]+=omega[i][None,None]@comm-comm@omega[i][None,None]
            frame=sum(epsilon[i,j,k]*omega[k]/R for k in range(3))
            hess[:,i,j]+=frame[None,None]@M-M@frame[None,None]
    weyl=normal_first_weyl_contact(germ['family_constant_symbol'],
        germ['family_Wilson_source_spatial_first_jet'],covd,hess)
    project=lambda x:np.einsum('ui,...uv,vj->...ij',J.conj(),x,J)
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    alpha=np.array([gamma[0]@g for g in gamma[1:]])
    spin=lambda x:np.einsum('kij,Aji->Ak',PAULI,x)/2
    coefficients={}
    for name,V,D in(('right_symbol',germ['family_constant_symbol'],germ['family_Wilson_source_spatial_first_jet']),
            ('first_Weyl_symbol',weyl['first_Weyl_value'],weyl['first_Weyl_source_gradient'])):
        v,d=project(V),project(D)
        comm=sum(alpha[j]@d[:,j]-d[:,j]@alpha[j]for j in range(3))
        coefficients[name]=dict(mass_coefficient=2*spin(v[:,:2,:2])/e,
            FW_constant_coefficient=-1j*spin(comm[:,:2,:2])/(2*e),
            constant_coefficient=-1j*spin(comm[:,:2,:2])/(2*e))
    return dict(germ={k:v for k,v in germ.items()if k not in('local_matched_spin_functional','local_matched_positive_band')},
        first_Weyl_application=weyl,normal_covariant_coordinate_hessian=hess,
        mass_affine_signed_soft_covectors=coefficients,
        equation='represented current spin(m)=m*mass_coefficient+FW_constant_coefficient',
        action_mass_selected=False,tree_mass_promoted_to_interacting_pole=False,
        nonmagnetic_self_energy_residue_applied=False,matched_charge=e,
        complete_Wilson_bilocal_series_or_Lorentz_domain_identification=False,
        local_overlap_subtracted=False,physical_F2=None,physical_a_mu=None,physical_g_mu=None)


def changing_family_mass_affine_covectors(constant_forward,tangent_forward,
        constant_reverse,tangent_reverse,*,family_indices,radius,wall_connection,H,
        charged_current_energy_first,electric_charge,family):
    """Add the SAME-frequency self-energy pole-Gram contact exactly once.

    The caller must bind the supplied magnetic application to that actual
    self-energy graph before using this contact. No action mass is selected
    and a local tree-symbol mass is not assigned as an interacting pole.
    """
    answer=changing_family_current_inverse_covectors(constant_forward,tangent_forward,
        constant_reverse,tangent_reverse,family_indices=family_indices,radius=radius,
        wall_connection=wall_connection,H=H,electric_charge=electric_charge,family=family)
    energy=_finite(charged_current_energy_first,'same-E0 complete family energy derivative',(6,6))
    J=answer['germ']['charged_injection'];charged=J.conj().T@energy@J
    Z=charged[:2,:2]
    residue=np.einsum('kij,Aji->Ak',PAULI,(Z[None]@PAULI+PAULI@Z[None])/2)/2
    for row in answer['mass_affine_signed_soft_covectors'].values():
        row['kinetic_residue_constant_coefficient']=residue
        row['constant_coefficient']=row['FW_constant_coefficient']+residue
    answer.update(charged_energy_first=charged,
        equation='represented spin(m)=m*mass_coefficient+FW_constant_coefficient+kinetic_residue_constant_coefficient',
        nonmagnetic_self_energy_residue_applied=True,same_external_frequency_required=0.)
    return answer
