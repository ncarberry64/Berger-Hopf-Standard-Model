"""Action-source identities; synthetic examples are CONTROL_ONLY."""
from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_primal_electromagnetic_source import (
    higgs_aligned_charge,higgs_aligned_source,higgs_aligned_source_first_jets,
    retained_phase_source_inputs,electromagnetic_source_sample,matched_breit_pauli_projection,
)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def actual():
    folder='artifacts/muon_parent_gauge_geometry_correction_20261010/attached_phase_incoming_1steps_run_1'
    a=retained_phase_source_inputs(folder,repository=ROOT)
    a['angular']=retained_full_q_angular_space(ROOT)
    return a


def test_generic_H_selects_same_mass_neutral_line_without_axis_fit():
    # CONTROL_ONLY general complex doublet; no selected physical field.
    h=np.array([1+2j,3-1j]);hd=np.array([-.2+.1j,.4+.3j]);a=higgs_aligned_charge(h,hd)
    np.testing.assert_allclose(a['aligned_frame'].conj().T@a['aligned_frame'],np.eye(18),atol=3e-16)
    mass=fixed_y_higgs_hamiltonian(h[None])[0]
    np.testing.assert_allclose(a['charge']@mass,mass@a['charge'],atol=2e-18)
    np.testing.assert_allclose(a['H_projector']@h,h,atol=1e-15)
    assert a['generator_reconstruction_defect']<2e-15
    assert not a['global_charge_invariant_background_claimed']


def test_charge_frame_rate_is_literal_derivative():
    h=np.array([.3+.7j,1.1-.2j]);hd=np.array([.4-.1j,-.3+.2j]);a=higgs_aligned_charge(h,hd)
    eps=2e-6
    p=higgs_aligned_charge(h+eps*hd,hd);m=higgs_aligned_charge(h-eps*hd,hd)
    np.testing.assert_allclose((p['charge']-m['charge'])/(2*eps),a['charge_rate'],rtol=3e-10,atol=1e-10)
    np.testing.assert_allclose((p['aligned_frame']-m['aligned_frame'])/(2*eps),a['aligned_frame_rate'],rtol=3e-10,atol=1e-10)


@pytest.mark.parametrize('h,hd',[(np.zeros(2),np.zeros(2)),([1,0],[np.nan,0]),([1,2,3],[0,0])])
def test_missing_or_zero_H_not_assigned_axis(h,hd):
    with pytest.raises(ValueError):higgs_aligned_charge(h,hd)


def test_actual_EM_image_not_inherited_transported_Q8(actual):
    raw=actual['cell']['midpoint_raw'];h=raw[-8:-4];hd=raw[-4:]
    a=higgs_aligned_source(actual['angular'],h[:2]+1j*h[2:],hd[:2]+1j*hd[2:])
    np.testing.assert_allclose(a['source_Gram'],(16/3)*np.eye(8),atol=4e-15)
    assert a['old_source_span_relative_residual']==pytest.approx(.775044801572428,abs=3e-15)
    assert not a['old_transported_source_inverse_reused']
    assert not np.any(a['source'][:160])
    # The pure charge-direction field is in n1; old transported Q includes n3.
    ids=[i for i,l in enumerate(actual['angular']['harmonic_labels']) if l[0]==3]
    assert not np.any(a['source'].reshape(5,4,20,8)[:,:,ids])


def test_complete_source_and_rate_derivatives_include_Hdot_and_geometry(actual):
    # An actual reached geometry with a generic supplied H tests full dependence.
    x=actual['cell']['midpoint_raw'].copy();x[-8:]=[.3,1.1,.2,-.4,.1,-.2,.3,.05]
    a=higgs_aligned_source_first_jets(x,actual['angular'])
    direction=np.zeros(268);direction[[0,2,74,98,99]]=[.11,-.09,.03,.07,-.04]
    direction[-8:]=[.2,-.3,.1,.4,-.1,.2,.3,-.4]
    eps=1e-6
    plus=higgs_aligned_source_first_jets(x+eps*direction,actual['angular'])
    minus=higgs_aligned_source_first_jets(x-eps*direction,actual['angular'])
    for value,jet in [('connection_source','Q_first_jet'),('connection_source_rate','Qdot_first_jet')]:
        literal=(plus[value]-minus[value])/(2*eps)
        predicted=np.einsum('r,rAB->AB',direction,a[jet])
        np.testing.assert_allclose(literal,predicted,rtol=3e-8,atol=5e-10)
    assert np.linalg.norm(a['Qdot_first_jet'][-4:])>0
    assert not np.any(a['Q_first_jet'][100:260])


def test_actual_Clifford_projection_keeps_leakage_and_does_not_promote_F2(actual):
    a=electromagnetic_source_sample(actual['cell']['midpoint_raw'],actual['representation'],actual['angular'])
    p=a['Clifford_application']
    assert p['complete_Clifford_reconstruction_defect']<2e-12
    assert p['Clifford_tensor_projection_norm']<2e-13
    assert np.linalg.norm(p['charged_to_neutral_first_jet'])>0
    assert a['local_charge_evolution_commutator_norm']>2
    assert a['charge_alignment']['mass_charge_commutator_defect']<1e-28
    assert not p['primitive_tensor_zero_is_physical_Pauli_zero']
    assert not p['external_soft_derivative_evaluated']


def test_full_on_shell_Gordon_scalar_not_killed_by_offshell_tensor_test():
    # CONTROL_ONLY exact Gordon representative, no BHSM F2 assigned.
    mass=.7;q=np.array([.2,-.1,.3]);E=np.sqrt(mass**2+q@q/4)
    vertex=np.zeros((4,4,4),complex);vertex[0]=(E/mass)*np.eye(4)
    a=matched_breit_pauli_projection(vertex,mass,q)
    assert a['F1']==pytest.approx(1,abs=8e-16)
    assert a['F2']==pytest.approx(-1,abs=2e-15)
    assert a['relative_tensor_remainder']<2e-15
    assert a['mass_shell_residual']<4e-16


def test_matched_minimal_gamma_vertex_and_remainder():
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    a=matched_breit_pauli_projection(gamma,.6,np.array([.1,.2,-.3]))
    assert a['F1']==pytest.approx(1,abs=1e-15)
    assert abs(a['F2'])<2e-15
    modified=gamma.copy();modified[1]+=.2*np.eye(4)
    b=matched_breit_pauli_projection(modified,.6,np.array([.1,.2,-.3]))
    assert b['relative_tensor_remainder']>.01
    assert not b['native_Pauli_or_zero_transfer_limit_completed']


def test_soft_q_zero_is_not_rank_zero_result():
    gamma=retained_higgs_spin_charge_representation()['gamma_Dirac']
    with pytest.raises(ValueError):matched_breit_pauli_projection(gamma,.6,np.zeros(3))
