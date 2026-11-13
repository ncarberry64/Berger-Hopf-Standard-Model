"""Independent normalization and original field-variation applications."""
from pathlib import Path
import numpy as np

from scripts.evaluate_muon_provisional_preparation import (
    ROOT, SOURCE, hamiltonian, pair_action_cotangent,
)
from bhsm.interface.muon_stationary_native_reference_load import field_pullback
from bhsm.interface.muon_provisional_packet_gauss import sign_projected_constant_sections
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation


def operands():
    with np.load(ROOT/SOURCE, allow_pickle=False) as z:
        x = z['input_iterate151'].copy()
    pull = field_pullback(x)
    t = pull['value']
    sections = sign_projected_constant_sections(hamiltonian(t), t[18:20]+1j*t[20:22])
    return x, pull, sections


def test_common_cap_rescaling_cancels_volume_and_radius_in_original_source():
    _, pull, sections = operands()
    R, N = pull['value'][:2]
    volume = 2*np.pi**2
    U, V = sections['particle_modes'][0], sections['antiparticle_modes'][0]
    rawU, rawV = volume*R**-1.5*U, volume*R**-1.5*V
    G = lepton_unit_trace_gauge_representation()['generators']
    # Original raw action /V², spatial R³, and temporal dH/dAt=-iG/N.
    raw_source = .5*np.array([N*R**3/volume**2*(
        np.trace(rawU.conj().T@(1j*g/N)@rawU)
        -np.trace(rawV.conj().T@(1j*g/N)@rawV)) for g in G])
    canonical = .5*np.array([np.trace(U.conj().T@(1j*g)@U)
        -np.trace(V.conj().T@(1j*g)@V) for g in G])
    np.testing.assert_allclose(raw_source, canonical, atol=2e-17)


def test_original_pair_cotangent_matches_fixed_section_action_difference():
    x, pull, sections = operands()
    gradient, D, _ = pair_action_cotangent(pull['value'], pull['gradient'], sections)
    direction = np.random.default_rng(71).normal(size=151)/20
    direction[150] = 0.  # calibration remains an independent equation
    def action(z):
        t = field_pullback(z)['value']
        return -float(np.trace(D@(t[1]*hamiltonian(t))).real)
    step = 2e-6
    difference = (action(x+step*direction)-action(x-step*direction))/(2*step)
    np.testing.assert_allclose(difference, gradient@direction, atol=2e-9, rtol=2e-8)
    G = lepton_unit_trace_gauge_representation()['generators']
    direct = np.einsum('ab,cba->c',D,1j*G).real
    np.testing.assert_allclose(gradient[122:126], direct, atol=3e-16)


def test_current_snapshot_trial_retains_both_sign_spin_columns():
    _, _, sections = operands()
    assert np.min(sections['projected_seed_Gram_eigenvalues']) > .2
    np.testing.assert_allclose(sections['complete_Haar_Cauchy_Gram'],np.eye(4),atol=3e-15)
    assert sections['physical_admission'] is False
