import numpy as np
import pytest
from bhsm.interface.muon_changing_normal_current_readout import changing_normal_current_readout,changing_family_normal_current_readout,matched_kinetic_residue_contact,normal_first_weyl_contact,changing_family_mass_affine_covectors,_normal_second_evaluation
from bhsm.interface.muon_intrinsic_normal_coordinate_readout import _evaluation
from bhsm.interface.muon_magnetic_open_lepton_vertex import charged_dirac_injection


def inputs():
    return dict(constant_forward=np.zeros((3,72,18),complex),tangent_forward=np.zeros((3,180,72),complex),
        constant_reverse=np.zeros((3,18,72),complex),tangent_reverse=np.zeros((3,72,180),complex),
        radius=.8,wall_connection=np.zeros((5,4)),H=np.array([0.,1.]),matched_mass_action=.2,electric_charge=.3)


def test_spin_major_coordinate_moment_uses_every_output_and_correct_input_lift():
    a=inputs();rng=np.random.default_rng(953)
    a['tangent_forward']=rng.normal(size=(3,180,72))+1j*rng.normal(size=(3,180,72))
    r=changing_normal_current_readout(**a)
    ye,_=_evaluation((0,2),a['radius']);Q=r['scalar_coordinate_coefficients']
    expected=np.zeros((3,3,18,18),complex)
    for axis in range(3):
        for k in range(3):
            for i in range(18):
                for j in range(18):
                    expected[axis,k,i,j]=sum(ye[h]*a['tangent_forward'][axis,10*i+h,4*j+g]*Q[g,k]for h in range(10)for g in range(4))
    np.testing.assert_allclose(r['full_first_input_momentum_response'],1j*expected,atol=2e-15)


def test_full_neutral_frame_contact_survives_before_charged_projection():
    a=inputs();J=charged_dirac_injection(a['H'],family=1)
    n=J['neutral'][:,0];c=J['charged'][:,0];X=np.outer(n,c.conj())
    y,_=_evaluation((1,),a['radius']);coeff=y/(y@y)
    a['constant_forward']=np.einsum('h,ij->ihj',coeff,X)[None].repeat(3,0).reshape(3,72,18)
    a['wall_connection'][2,0]=.4
    r=changing_normal_current_readout(**a)
    np.testing.assert_allclose(r['charged_constant_symbol'],0,atol=0)
    assert np.linalg.norm(r['source_spatial_Wilson_contact'])>0
    assert np.linalg.norm(r['charged_Wilson_source_spatial_first_jet'])>0
    assert not r['charged_subspace_invariance_assumed']


def test_reverse_is_independent_and_missing_momentum_not_filled_zero():
    a=inputs();a['constant_reverse'][0,0,0]=1+2j
    r=changing_normal_current_readout(**a)
    assert np.linalg.norm(r['forward_reverse_value_adjoint_difference'])>0
    assert r['physical_signed_soft_Pauli']is None
    a['tangent_forward']=None
    with pytest.raises(ValueError):changing_normal_current_readout(**a)


def test_literal_family_restriction_matches_full18_application_without_tau_completion():
    rng=np.random.default_rng(410);ids=np.array([2,3,8,9,14,15]);a=inputs()
    c=rng.normal(size=(3,24,6));t=rng.normal(size=(3,60,24));cr=rng.normal(size=(3,6,24));tr=rng.normal(size=(3,24,60))
    oi=(ids[:,None]*4+np.arange(4)).ravel();ei=(ids[:,None]*10+np.arange(10)).ravel()
    for axis in range(3):
        a['constant_forward'][axis][np.ix_(oi,ids)]=c[axis]
        a['tangent_forward'][axis][np.ix_(ei,oi)]=t[axis]
        a['constant_reverse'][axis][np.ix_(ids,oi)]=cr[axis]
        a['tangent_reverse'][axis][np.ix_(oi,ei)]=tr[axis]
    a['wall_connection'][2,0]=.2
    full=changing_normal_current_readout(**a)
    r=changing_family_normal_current_readout(c,t,cr,tr,family_indices=ids,family=1,
        **{k:a[k]for k in('radius','wall_connection','H','matched_mass_action','electric_charge')})
    np.testing.assert_allclose(r['charged_Wilson_source_spatial_first_jet'],full['charged_Wilson_source_spatial_first_jet'],rtol=0,atol=3e-15)
    np.testing.assert_allclose(r['charged_first_input_momentum_response'],full['charged_first_input_momentum_response'],rtol=0,atol=3e-15)
    assert r['exact_action_family_invariance_checked']
    assert not r['unevaluated_families_filled_zero']


def test_local_wavefunction_dirac_contact_cancels_before_pauli_assignment():
    from bhsm.interface.muon_magnetic_open_lepton_vertex import PAULI
    # Dyadic operands make this algebraic counterterm check exact in
    # binary arithmetic as well as in the stated pencil identity.
    z=.125+.0625j;mass=.25;charge=.5
    energy=z*np.eye(4);band=-z*charge/(2*mass)*PAULI
    result=matched_kinetic_residue_contact(band,energy,
        matched_mass_action=mass,electric_charge=charge)
    np.testing.assert_allclose(result['residue_corrected_spin_functional'],0,atol=0)
    assert np.linalg.norm(result['energy_coefficient_Hermitian_defect'])>0
    assert result['physical_signed_soft_Pauli']is None


def test_noncentral_residue_contact_matches_independent_canonical_gram_derivative():
    from bhsm.interface.muon_magnetic_open_lepton_vertex import PAULI
    from scipy.linalg import eigh
    Z=np.array([[.2,.04+.03j],[.04-.03j,-.1]])
    V=np.array([[[.02,.01j],[-.01j,-.03]],[[.1,.07],[.07,.02]],[[-.02,.01],[.01,.04]]])
    energy=np.zeros((4,4),complex);energy[:2,:2]=Z
    mass=.2;charge=.3;minimal=charge/(2*mass)*PAULI
    def canonical(epsilon):
        eigenvectors=eigh(np.eye(2)-epsilon*Z)
        inverse=(eigenvectors[1]/np.sqrt(eigenvectors[0]))@eigenvectors[1].conj().T
        return inverse[None]@(minimal+epsilon*V)@inverse[None]
    step=1e-4
    derivative=(canonical(step)-canonical(-step))/(2*step)
    result=matched_kinetic_residue_contact(V,energy,matched_mass_action=mass,electric_charge=charge)
    np.testing.assert_allclose(derivative,result['residue_corrected_positive_band'],rtol=1e-8,atol=2e-11)
    assert np.linalg.norm(result['kinetic_residue_magnetic_contact'])>0


def test_moving_input_center_preserves_identity_in_first_weyl_contact():
    value=np.eye(2,dtype=complex)[None].repeat(3,axis=0)
    gradient=np.zeros((3,3,2,2),complex)
    moment_gradient=np.zeros((3,3,3,2,2),complex)
    for j in range(3):moment_gradient[:,j,j]=value
    hessian=np.zeros((3,3,3,3,2,2),complex)
    r=normal_first_weyl_contact(value,gradient,moment_gradient,hessian)
    np.testing.assert_array_equal(r['first_Weyl_contact'],0)
    np.testing.assert_array_equal(r['first_Weyl_value'],value)
    assert r['moving_input_center_contact_included']
    assert not r['complete_bilocal_Weyl_series_evaluated']


def test_round_normal_scalar_hessian_includes_right_frame_connection():
    hessian,_=_normal_second_evaluation(.8)
    np.testing.assert_allclose(hessian,hessian.swapaxes(0,1),atol=3e-15,rtol=0)


def test_nonconstant_multiplication_preserves_its_first_weyl_gradient():
    rng=np.random.default_rng(110)
    value=rng.normal(size=(3,2,2));gradient=rng.normal(size=(3,3,2,2))
    dM=np.zeros((3,3,3,2,2));ddM=np.zeros((3,3,3,3,2,2))
    # S[X_b]=A(x)X_b. Normal X_b(0)=0, d_j X_b=delta_jb,
    # d_i d_j X_b(0)=0; all four D_i A terms must cancel.
    for i in range(3):
        for j in range(3):
            for b in range(3):
                ddM[:,i,j,b]=(gradient[:,i]if j==b else 0)+(gradient[:,j]if i==b else 0)
        dM[:,i,i]=value
    r=normal_first_weyl_contact(value,gradient,dM,ddM)
    np.testing.assert_allclose(r['first_Weyl_contact'],0,atol=3e-16,rtol=0)
    np.testing.assert_allclose(r['first_Weyl_source_gradient_contact'],0,atol=1e-15,rtol=0)


def test_mass_affine_right_covector_recovers_same_band_and_residue_without_mass_choice():
    rng=np.random.default_rng(618);ids=np.array([2,3,8,9,14,15])
    c=rng.normal(size=(3,24,6));t=rng.normal(size=(3,60,24));cr=c.transpose(0,2,1).copy();tr=t.transpose(0,2,1).copy()
    energy=rng.normal(size=(6,6))+1j*rng.normal(size=(6,6))
    args=dict(family_indices=ids,radius=.8,wall_connection=np.arange(20).reshape(5,4)*.01,
        H=np.array([.2j,.7]),electric_charge=.3,family=1)
    r=changing_family_mass_affine_covectors(c,t,cr,tr,charged_current_energy_first=energy,**args)
    mass=.2
    old=changing_family_normal_current_readout(c,t,cr,tr,matched_mass_action=mass,**args)
    J=old['charged_injection'];charged_energy=J.conj().T@energy@J
    residue=matched_kinetic_residue_contact(old['local_matched_positive_band'],charged_energy,
        matched_mass_action=mass,electric_charge=.3)
    covector=r['mass_affine_signed_soft_covectors']['right_symbol']
    np.testing.assert_allclose(mass*covector['mass_coefficient']+covector['constant_coefficient'],
        residue['residue_corrected_spin_functional'],rtol=2e-15,atol=2e-13)
    assert np.linalg.norm(r['first_Weyl_application']['first_Weyl_contact'])>0
    assert not r['action_mass_selected']
    assert r['physical_F2']is None
