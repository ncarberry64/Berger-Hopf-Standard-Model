"""Independent gauge, time-evolution and source controls; no prediction data."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'audits'), str(ROOT/'src'), str(ROOT)]

import numpy as np
from scipy.linalg import expm
from bhsm_collider_yukawa_noether_transfer import transfer_operators, excitation_transfer
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from bhsm.interface.muon_primal_electromagnetic_source import higgs_aligned_charge


def test_finite_gauge_covariance_with_both_mass_placements():
    h = np.array([[.7+.3j, -.4+.8j]])  # algebraic control, not a vacuum
    app = transfer_operators(h)
    for G, T in zip(app['gauge_generators'], app['Higgs_generators']):
        u, t = expm(.31*G), expm(.31*T)
        rotated = fixed_y_higgs_hamiltonian((t@h[0])[None])[0]
        assert np.max(abs(rotated-u@app['mass'][0]@u.conj().T)) < 3e-17


def test_mass_only_current_time_derivative_preserves_sign_and_nonzero_transfer():
    app = transfer_operators(np.array([[.7+.3j, -.4+.8j]]))
    psi = np.arange(1, 19)+1j*np.arange(18, 0, -1)
    psi = psi/np.linalg.norm(psi)
    M = app['mass'][0]
    dt = 1e-3
    future, past = expm(-1j*dt*M)@psi, expm(1j*dt*M)@psi
    numerical = np.array([(np.vdot(future, C@future)-np.vdot(past, C@past))/(2*dt)
                          for C in app['current_generators']])
    analytic = np.array([np.vdot(psi, T@psi) for T in app['mass_torque'][0]])
    assert np.max(abs(analytic)) > 1e-6
    assert np.max(abs(numerical-analytic)) < 1e-12


def test_excitation_scalar_source_has_complex_pairing_and_one_density():
    rng = np.random.default_rng(203)
    f = rng.normal(size=(3, 18, 4))+1j*rng.normal(size=(3, 18, 4))
    h = rng.normal(size=(3, 2))+1j*rng.normal(size=(3, 2))
    kw = dict(H=h, particle_modes=f[:, :, :2], antiparticle_modes=f[:, :, 2:],
              bilinear_expectation=np.diag([.5, .5, -.5, -.5]))
    a = excitation_transfer(**kw, canonical_spatial_density=np.array([.4, 1.3, 2.1]))
    b = excitation_transfer(**kw, canonical_spatial_density=np.array([.8, 2.6, 4.2]))
    assert np.max(abs(a['transfer_identity_residual'])) < 3e-16
    assert np.max(abs(b['lepton_gauge_current_transfer']-2*a['lepton_gauge_current_transfer'])) < 3e-16


def test_H_selected_EM_mass_torque_cancels_all_four_gauge_channels():
    h = np.array([[.7+.3j, -.4+.8j]])
    app = transfer_operators(h)
    em = higgs_aligned_charge(h[0], np.zeros(2, complex))
    combined = np.einsum('c,cij->ij', em['unit_Tr16_coefficients'], app['mass_torque'][0])
    # Individual HY transfer remains nonzero, while the full aligned EM cancels.
    assert np.max(abs(app['mass_torque'][0, 3])) > 1e-6
    assert np.max(abs(combined)) < 2e-17
