from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"audits"))
"""Independent finite algebra tests; these fixtures are not BHSM pole data.

The explicitly soluble non-Hermitian pencil has two DISTINCT simple roots,
complex probe slopes, and independent analytic left/right frames. Tests do
not select any physical exterior, spin state, charge, or magnetic moment.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose
import pytest


_SOURCE = Path(__file__).resolve().parents[1]/"audits"/"bhsm_muon_split_pole_em_observable_20261015.py"
_SPEC = spec_from_file_location('independent_split_pole_em_consumer', _SOURCE)
em = module_from_spec(_SPEC)
_SPEC.loader.exec_module(em)


ENERGIES = np.array([2.1-.15j, 3.4-.25j])
SLOPES = np.array([.37+.08j, -.23-.11j])
P = np.array([[1+.2j, .3-.1j, .2], [.1j, 1.4, -.2+.1j], [.4, .15j, .9-.1j]])
Q = np.array([[1.2, -.2j, .3], [.25+.1j, .8+.2j, .15], [-.1, .4j, 1.1]])


def explicit_pencil(energy, magnetic=0):
    """Exact analytic reference, independent of the production formulas."""
    diagonal = np.array([energy-ENERGIES[0]-SLOPES[0]*magnetic,
                         energy-ENERGIES[1]-SLOPES[1]*magnetic,
                         1.8+.2j+(.17-.04j)*energy+(.12+.03j)*magnetic])
    return P @ np.diag(diagonal) @ Q


def pole_inputs(branch):
    e = np.eye(3, dtype=complex)[:, branch:branch+1]
    right = np.linalg.solve(Q, e)
    left = np.linalg.solve(P.T, e).T  # analytic transpose, not Hilbert adjoint
    return dict(gamma=explicit_pencil(ENERGIES[branch]),
                gamma_energy=P @ np.diag([1, 1, .17-.04j]) @ Q,
                probe_rows=np.array([P @ np.diag([-SLOPES[0], -SLOPES[1], .12+.03j]) @ Q]),
                right=right, left=left, pole_energy=ENERGIES[branch])


@pytest.mark.parametrize('branch', [0, 1])
def test_distinct_simple_poles_preserve_complex_energy_and_width_slopes(branch):
    a = pole_inputs(branch)
    r = em.simple_unsquared_pole_response(**a)
    # Reference slope comes directly from the exact root E_s(B)=E_s+v_s B.
    assert ENERGIES[0] != ENERGIES[1]
    assert SLOPES[branch].imag != 0
    assert_allclose(r['pole_probe_energy_first'], [SLOPES[branch]], atol=2e-14, rtol=2e-14)
    assert_allclose(r['pole_probe_mass_first'], [SLOPES[branch].real], atol=2e-14)
    assert_allclose(r['pole_probe_width_first'], [-2*SLOPES[branch].imag], atol=2e-14)
    assert_allclose(r['pole_width_action'], -2*ENERGIES[branch].imag, atol=2e-14)
    for name in ('original_right_pole_rows', 'original_left_pole_rows',
                 'full_bordered_inverse_rows', 'right_complement_rows', 'left_complement_rows'):
        assert_allclose(r[name], 0, atol=2e-14)
    assert r['same_energy_spin_degeneracy_required'] is False
    assert r['physical_pole_or_Pauli_admission_inferred'] is False


def test_literal_analytic_left_is_used_without_hidden_conjugation():
    a = pole_inputs(0)
    r = em.simple_unsquared_pole_response(**a)
    z = (a['left'] @ a['gamma_energy'] @ a['right']).item()
    reference = a['right'] @ a['left']/z
    assert np.linalg.norm(a['left']-a['right'].conj().T) > .1
    assert np.linalg.norm(a['left']-a['left'].conj()) > .1
    assert_allclose(r['pole_residue'], reference, atol=2e-14)
    # A conjugated row generally is NOT a left null row of this pencil.
    wrong_left = a['left'].conj()
    assert np.linalg.norm(wrong_left @ a['gamma']) > .1
    wrong_z = (wrong_left @ a['gamma_energy'] @ a['right']).item()
    wrong_residue = a['right'] @ wrong_left/wrong_z
    assert np.linalg.norm(r['pole_residue']-wrong_residue) > .1
    assert r['left_mode_conjugated'] is False


@pytest.mark.parametrize('branch', [0, 1])
def test_moving_nonorthogonal_boundary_coordinates_at_each_exact_pole(branch):
    a = pole_inputs(branch)
    original = em.simple_unsquared_pole_response(**a)
    A = np.array([[1.3+.1j, .4, -.1j], [.2j, .85, .3], [.1, -.15j, 1.1-.2j]])
    C = np.array([[.9, .25j, .3], [.2, 1.2+.1j, -.15], [-.1j, .1, 1.4]])
    AE = np.array([[.1j, .2, 0], [.1, -.1j, .05], [0, .15j, -.1]])
    CE = np.array([[.2, -.1j, .1], [0, .05, .08j], [-.12, .1j, 0]])
    AB = np.array([[0, .1, .05j], [-.1j, .2, 0], [.12, 0, -.15j]])
    CB = np.array([[.04, .1j, 0], [.05j, 0, .13], [-.07, .08, .02j]])
    assert np.linalg.norm(A.conj().T @ A-np.eye(3)) > .1
    assert np.linalg.norm(C.conj().T @ C-np.eye(3)) > .1
    G, GE, GB = a['gamma'], a['gamma_energy'], a['probe_rows'][0]
    # Full product rules for Gamma'=A(E,B) Gamma C(E,B), including contacts.
    changed = em.simple_unsquared_pole_response(
        A @ G @ C,
        AE @ G @ C+A @ GE @ C+A @ G @ CE,
        np.linalg.solve(C, a['right']),
        np.linalg.solve(A.T, a['left'].T).T,
        pole_energy=a['pole_energy'],
        probe_rows=np.array([AB @ G @ C+A @ GB @ C+A @ G @ CB]))
    assert_allclose(changed['pole_probe_energy_first'], [SLOPES[branch]], atol=3e-14)
    assert_allclose(changed['pole_kinetic_pairing'], original['pole_kinetic_pairing'], atol=3e-14)
    expected_residue = np.linalg.solve(C, original['pole_residue']) @ np.linalg.inv(A)
    assert_allclose(changed['pole_residue'], expected_residue, atol=3e-14)
    for name in ('original_right_pole_rows', 'original_left_pole_rows', 'full_bordered_inverse_rows'):
        assert_allclose(changed[name], 0, atol=3e-14)


def test_missing_probe_stays_absent_and_is_distinct_from_explicit_zero_probe():
    a = pole_inputs(0)
    del a['probe_rows']
    missing = em.simple_unsquared_pole_response(**a)
    assert missing['probe_supplied'] is False
    for key in ('pole_probe_energy_first', 'pole_probe_mass_first', 'pole_probe_width_first'):
        assert key not in missing
    zero = em.simple_unsquared_pole_response(**a, probe_rows=np.zeros((1, 3, 3), complex))
    assert zero['probe_supplied'] is True
    assert_allclose(zero['pole_probe_energy_first'], 0, atol=0)
    with pytest.raises(ValueError, match='probe rows need'):
        em.simple_unsquared_pole_response(**a, probe_rows=np.empty((0, 3, 3), complex))


def test_two_spin_responses_retain_common_and_nonzero_complex_spin_parts():
    plus = em.simple_unsquared_pole_response(**pole_inputs(0))['pole_probe_energy_first'][0]
    minus = em.simple_unsquared_pole_response(**pole_inputs(1))['pole_probe_energy_first'][0]
    r = em.split_spin_longitudinal_response(plus, minus, plus_spin=.5, minus_spin=-.5)
    difference = SLOPES[0]-SLOPES[1]
    assert_allclose(r['complex_moment_per_spin'], -difference, atol=3e-14)
    assert_allclose(r['spin_independent_energy_response'], SLOPES.mean(), atol=3e-14)
    assert_allclose(r['width_response_per_spin'], -2*difference.imag, atol=3e-14)
    assert_allclose([r['original_plus_response_row'], r['original_minus_response_row']], 0, atol=3e-14)
    assert r['gyromagnetic_or_F2_promotion_performed'] is False


def test_nonorthogonal_probe_conversion_keeps_complex_width_response():
    B = np.array([[1., .2, -.1], [.1, 1.3, .4], [-.2, .1, .9], [.4, -.3, .2]])
    gradient = np.array([.2+.04j, -.3+.12j, .17-.08j])
    probe_first = B @ gradient
    r = em.physical_magnetic_probe_conversion(probe_first, B)
    assert_allclose(r['energy_magnetic_first'], gradient, atol=3e-14)
    assert_allclose(r['complex_magnetic_moment'], -gradient, atol=3e-14)
    assert_allclose(r['width_magnetic_first'], -2*gradient.imag, atol=3e-14)
    assert_allclose(r['probe_conversion_original_rows'], 0, atol=3e-14)
    with pytest.raises(ValueError, match='three independent'):
        em.physical_magnetic_probe_conversion(probe_first, np.zeros_like(B))
