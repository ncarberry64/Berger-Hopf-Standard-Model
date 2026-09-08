"""Symbolic and independent matrix checks of the scoped observable test."""
import hashlib

import numpy as np
import pytest
import sympy as sp

from bhsm.interface.ae31_c2_state_observable_audit import (
    CHARGE, CONJUGATION, REFERENCE, affine_response_screen, algebraic_controls,
    direct_affine_difference, phase_covariance,
)
from scripts.materialize_ae31_c2_state_observable_audit import TARGET, build_payload, main


def test_symbolic_complex_frame_is_pure_self_dual_and_charge_preserving():
    theta, phase = sp.symbols("theta phase", real=True)
    c, z = sp.cos(theta), sp.sin(theta)*sp.exp(sp.I*phase)
    frame = sp.Matrix([[c, 0], [0, c], [0, -z], [z, 0]])
    p = frame*frame.adjoint()
    gamma = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]])
    q = sp.diag(1, -1, -1, 1)
    assert sp.simplify(frame.adjoint()*frame-sp.eye(2)) == sp.zeros(2)
    assert sp.simplify(p+gamma*sp.conjugate(p)*gamma-sp.eye(4)) == sp.zeros(4)
    assert sp.simplify(p*q-q*p) == sp.zeros(4)
    assert sp.simplify(p*p-p) == sp.zeros(4)


def test_symbolic_general_hermitian_trace_formula():
    theta, phase = sp.symbols("theta phase", real=True)
    diagonal = sp.symbols("d0:4", real=True)
    real = sp.symbols("r0:6", real=True)
    imaginary = sp.symbols("j0:6", real=True)
    bmat = sp.diag(*diagonal)
    for k, (i, j) in enumerate(( (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3) )):
        bmat[i, j] = real[k]+sp.I*imaginary[k]
        bmat[j, i] = real[k]-sp.I*imaginary[k]
    c, z = sp.cos(theta), sp.sin(theta)*sp.exp(sp.I*phase)
    frame = sp.Matrix([[c, 0], [0, c], [0, -z], [z, 0]])
    a = diagonal[2]+diagonal[3]-diagonal[0]-diagonal[1]
    b = bmat[0, 3]-bmat[1, 2]
    expected = a*sp.sin(theta)**2 + sp.sin(2*theta)*sp.re(sp.exp(sp.I*phase)*b)
    actual = sp.trace(bmat*(frame*frame.adjoint()-sp.diag(1, 1, 0, 0)))
    assert sp.simplify(sp.expand_complex(actual-expected)) == 0


@pytest.mark.parametrize("theta,phase", [(0, .6), (.37, .61), (np.pi/2, 1.9), (.9, -2.1)])
def test_numeric_covariance_constraints(theta, phase):
    c = phase_covariance(theta, phase)
    assert np.linalg.norm(c@c-c) < 2e-15
    assert np.linalg.norm(c+CONJUGATION@c.conj()@CONJUGATION-np.eye(4)) < 2e-15
    assert np.linalg.norm(c@CHARGE-CHARGE@c) < 2e-15
    assert np.linalg.eigvalsh(c).min() > -2e-15
    assert np.linalg.eigvalsh(c).max() < 1+2e-15


def test_phase_zero_can_hide_an_entire_sensitive_quadrature():
    b = algebraic_controls()["imaginary_mixed_response"]
    for theta in (.1, .3, .7, 1.2):
        assert direct_affine_difference(b, theta, 0) == 0
    assert direct_affine_difference(b, np.pi/4, np.pi/2) == pytest.approx(-1)
    assert affine_response_screen(b)["affine_difference_range"] == [-1, 1]


def test_range_endpoints_are_attained_and_match_independent_eigenproblem():
    bmat = np.diag([1., 3., -2., 5.]).astype(complex)
    bmat[0, 3], bmat[3, 0] = 2+3j, 2-3j
    bmat[1, 2], bmat[2, 1] = -1+1j, -1-1j
    report = affine_response_screen(bmat)
    b = complex(report["b_real"], report["b_imag"])
    h = np.asarray([[0, b], [b.conjugate(), report["a"]]])
    eigenvalues, vectors = np.linalg.eigh(h)
    assert report["affine_difference_range"] == pytest.approx(eigenvalues)
    for index in (0, 1):
        v = vectors[:, index]
        theta = np.arctan2(abs(v[1]), abs(v[0]))
        phase = np.angle(v[1])-np.angle(v[0])
        assert direct_affine_difference(bmat, theta, phase) == pytest.approx(eigenvalues[index])


def test_state_nonuniqueness_does_not_force_every_observable_to_vary():
    for name in ("identity", "charge"):
        assert affine_response_screen(algebraic_controls()[name])["floating_coefficients_exactly_zero"]
    assert not affine_response_screen(REFERENCE)["floating_coefficients_exactly_zero"]


def test_zero_first_derivative_does_not_establish_finite_invariance():
    screen = affine_response_screen(REFERENCE)
    assert screen["maximum_reference_tangent_response"] == 0
    assert screen["affine_range_diameter"] == 2


def test_nonlinear_functional_cannot_be_replaced_by_its_frozen_gradient():
    c = phase_covariance(.47, .93)
    assert np.trace(c@c).real == pytest.approx(2)
    assert direct_affine_difference(2*REFERENCE, .47, .93) < -.1


def test_reset_conjugation_preserves_a_response_when_both_operators_are_transported():
    # A general complex unitary checks coordinate invariance; no new physical reset.
    rng = np.random.default_rng(741)
    u, _ = np.linalg.qr(rng.normal(size=(4, 4))+1j*rng.normal(size=(4, 4)))
    b = algebraic_controls()["imaginary_mixed_response"]
    delta = phase_covariance(.31, .78)-REFERENCE
    assert np.trace((u@b@u.conj().T)@(u@delta@u.conj().T)) == pytest.approx(np.trace(b@delta))


@pytest.mark.parametrize("bad", [np.eye(3), np.full((4, 4), np.nan), np.eye(4)+np.triu(np.ones((4, 4)), 1)])
def test_invalid_response_matrix_is_rejected(bad):
    with pytest.raises(ValueError):
        affine_response_screen(bad)


def test_nonfinite_phase_is_rejected():
    with pytest.raises(ValueError):
        phase_covariance(.3, float("nan"))


def test_report_promotes_no_physical_state_or_lepton_prediction():
    report = build_payload()
    assert report["validation_passed"]
    assert not report["controls_are_physical_operators"]
    assert not report["lepton_target"]["covariance_response_operator_available"]
    assert not report["claim_boundary"]["physical_lepton_dressing_invariant_state_independent"]
    assert not report["FULL_BHSM_COMPLETE"]


def test_free_retarded_control_does_not_select_the_time_ordered_state():
    control = build_payload()["quadratic_causal_control"]
    assert control["retarded_state_difference_norm"] < 2e-15
    assert control["time_ordered_state_difference_norm"] == pytest.approx(2*np.sin(.37))
    assert not control["control_energies_are_BHSM_masses"]
    assert not control["interacting_or_composite_response_independence_inferred"]


def test_twice_materialization_preserves_tracked_report(tmp_path):
    original = TARGET.read_bytes() if TARGET.exists() else None
    output = tmp_path / "audit.json"
    main(["--output", str(output)])
    first = hashlib.sha256(output.read_bytes()).digest()
    main(["--output", str(output)])
    assert hashlib.sha256(output.read_bytes()).digest() == first
    assert (TARGET.read_bytes() if TARGET.exists() else None) == original
