"""Actual source algebra/guards; finite perturbations are CONTROL_ONLY tests."""
import numpy as np
import pytest

from bhsm.interface.muon_primal_electromagnetic_source import retained_phase_source_inputs
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_electromagnetic_soft_magnetic_source import (
    local_magnetic_wavefunctions,uniform_magnetic_source_first_jets,
    magnetic_point_jet,magnetic_turn_on_profile,magnetic_source_sample,
)
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_basis_values,real_scalar_basis_transform,real_scalar_basis_labels
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_current_source_motion_cubic import current_face_source_jets


@pytest.fixture(scope='module')
def actual():
    b=retained_phase_source_inputs('artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_incoming_1steps_run_1')
    return b['cell']['midpoint_raw'],b['representation'],retained_full_q_angular_space()


def test_normal_coordinates_have_positive_identity_derivative(actual):
    _,_,angular=actual
    result=local_magnetic_wavefunctions(angular)
    labels=real_scalar_basis_labels(3);odd=[i for i,l in enumerate(labels) if l[0] in (1,3)]
    value=(scalar_basis_values(np.eye(2,dtype=complex)[None],3)@real_scalar_basis_transform(3))[0,odd].real
    coefficient=result['quaternion_coefficients']
    np.testing.assert_allclose(value@coefficient,0,atol=3e-16)
    np.testing.assert_allclose(np.einsum('h,ahk,kj->aj',value,angular['derivative_matrices'],coefficient),np.eye(3),atol=5e-15)
    assert result['angular_reconstruction_maximum']<1e-13
    assert not np.any(result['wavefunctions'][:,:,3:])


def test_actual_covariant_magnetic_jet_sign_and_normalization(actual):
    raw,rep,angular=actual;e=.302822
    s=uniform_magnetic_source_first_jets(raw,angular,electric_charge=e)
    w=current_face_source_jets(raw[:100])['intrinsic_weights']
    wall=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180])
    wall[2:]+=M*(w['mechanical_connection_lambda'].value-1)
    result=magnetic_point_jet(s,angular,wall[2:])
    assert result['potential_zero_defect']<2e-15
    assert result['magnetic_curvature_defect']<1e-13
    # Positive B3 means F12 positive, not the negative r-cross-B convention.
    np.testing.assert_allclose(result['full_curvature_at_point'][0,1,:,2],e*s['R4']**2*s['charge_alignment']['unit_Tr16_coefficients'],rtol=4e-14,atol=3e-15)
    assert np.linalg.norm(wall[2:,:3])>1
    assert np.linalg.norm(result['mechanical_commutator_contact'])<1e-14
    assert s['old_coexact_relative_remainder']>.9
    assert s['active_source_indices']==[0,1,2]
    assert not np.any(s['Q'][:,3:]) and not np.any(s['Qdot'][:,3:])


def test_exact_source_rate_and_jets_with_higgs_and_radius_motion(actual):
    raw,_,angular=actual
    # CONTROL_ONLY generic scalar direction tests normalized-axis Hessian.
    x=raw.copy();x[-8:]=[.7,-.9,.3,.2,.13,.2,-.1,.04]
    d=np.zeros(268);d[[0,14,40,75,98,99,-8,-6,-4,-1]]=[.1,-.04,.03,.01,.02,.07,.1,-.09,.04,.05]
    a=uniform_magnetic_source_first_jets(x,angular,electric_charge=.3)
    h=2e-6;p=uniform_magnetic_source_first_jets(x+h*d,angular,electric_charge=.3);m=uniform_magnetic_source_first_jets(x-h*d,angular,electric_charge=.3)
    for key,jet in (('Q','Q_first_jet'),('Qdot','Qdot_first_jet')):
        fd=(p[key]-m[key])/(2*h);exact=np.einsum('r,rha->ha',d,a[jet])
        np.testing.assert_allclose(fd,exact,rtol=3e-7,atol=2e-9)


def test_electric_charge_inserted_once(actual):
    x,_,angular=actual
    a=uniform_magnetic_source_first_jets(x,angular,electric_charge=.2)
    b=uniform_magnetic_source_first_jets(x,angular,electric_charge=.4)
    for key in ('Q','Qdot','Q_first_jet','Qdot_first_jet'):
        np.testing.assert_array_equal(b[key],2*a[key])
    assert a['canonical_current']=='chi_hat=R4^(3/2)psi/(2pi²); unit current Gram'


def test_turn_on_is_compatible_and_active_at_midpoint():
    D=.25
    assert magnetic_turn_on_profile(0,D)==(0.,0.,0.)
    assert magnetic_turn_on_profile(.5,D)==(1.,0.,0.)
    assert magnetic_turn_on_profile(D,D)==(1.,0.,0.)
    for t in (.04,.1,.2):
        h=1e-6;g,gd,gdd=magnetic_turn_on_profile(t,D)
        np.testing.assert_allclose((magnetic_turn_on_profile(t+h,D)[0]-magnetic_turn_on_profile(t-h,D)[0])/(2*h),gd,rtol=2e-9)
        np.testing.assert_allclose((magnetic_turn_on_profile(t+h,D)[1]-magnetic_turn_on_profile(t-h,D)[1])/(2*h),gdd,rtol=3e-9)
        assert 0<g<1
    with pytest.raises(ValueError):magnetic_turn_on_profile(1,0)


def test_no_fallback_field_or_claimed_soft_vertex(actual):
    x,rep,angular=actual
    with pytest.raises(ValueError):uniform_magnetic_source_first_jets(x,angular,electric_charge=0)
    z=x.copy();z[-8:-4]=0
    with pytest.raises(ValueError):uniform_magnetic_source_first_jets(z,angular,electric_charge=.3)
    s=magnetic_source_sample(x,rep,angular,electric_charge=.3)
    assert not s['Fourier_soft_limit_or_native_Pauli_completed']
    assert not s['Clifford_application']['primitive_tensor_zero_is_physical_Pauli_zero']


def test_outgoing_independent_turn_on_rejected():
    from scripts.evaluate_muon_electromagnetic_soft_magnetic_source import materialize
    with pytest.raises(ValueError,match='outgoing requires the actual sourced birth reset'):
        materialize('artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_outgoing_1steps_run_1','unused-output-that-must-not-be-created')
