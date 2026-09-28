"""Directional and implicit-response witnesses, never physical input seeds."""
import numpy as np
import pytest
import hashlib
import json
from pathlib import Path
from flint import arb, arb_mat, ctx
from bhsm.interface.current_incoming_formation_family import (
    coefficient_first, local_internal_system, descriptor_clock_first,
    zero_descriptor_clock_germ,
)


@pytest.fixture(autouse=True)
def precision():
    old = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = old


def test_coefficient_directions_against_independent_centered_samples():
    rng = np.random.default_rng(143)
    y = [arb(float(v)) for v in rng.normal(size=98)/30]
    u = [arb(float(v)) for v in rng.normal(size=98)/10]
    _, derivatives = coefficient_first(y, arb_mat(98, 1, u))
    errors = []
    for exponent in (14, 15):
        step = arb(2)**-exponent
        plus, _ = coefficient_first([v+step*d for v, d in zip(y, u)], arb_mat(98, 1))
        minus, _ = coefficient_first([v-step*d for v, d in zip(y, u)], arb_mat(98, 1))
        errors.append({k: float(abs((plus[k]-minus[k])/(2*step)-derivatives[k][0, 0]).upper())
                       for k in derivatives})
    for name in derivatives:
        assert errors[1][name] < 1e-8
        if errors[0][name] > 1e-50:
            assert errors[1][name] < .251*errors[0][name]


def test_fixed_endpoint_radius_does_not_freeze_lapse_or_radius_rate():
    y = [arb(0)]*98
    y[37] = arb('0.2')
    u = arb_mat(98, 2)
    u[74, 0] = 1
    u[37, 1] = 1
    values, first = coefficient_first(y, u)
    assert all(v.is_zero() for v in first['log_radius'].entries())
    assert all(v.is_zero() for v in first['unit_scalar_gauge_potential'].entries())
    assert first['log_lapse'][0, 0] == -1
    assert first['proper_log_radius_rate'][0, 0].contains(arb('0.2'))
    assert first['proper_log_radius_rate'][0, 1] == 1
    assert first['zeta_proper_density'][0, 0].is_zero()
    assert not first['zeta_coordinate_density'][0, 0].contains(0)
    # Original attached-action rounding is part of provenance.
    assert (values['zeta_proper_density']/values['unit_Weyl_superpotential']).contains(-arb(float(59/30)))


def _solve_witness(x):
    H = np.array([[1+0.3*x, 0.4*x], [0.4*x, 3-0.1*x]])
    rhs = np.array([2+x, -0.5+0.2*x])
    eigenvalues, vectors = np.linalg.eigh(H)
    p = vectors[:, 0]
    if p[0] < 0:
        p = -p
    lam = eigenvalues[0]
    K = np.block([[H-lam*np.eye(2), p[:, None]], [p[None, :], np.zeros((1, 1))]])
    hb = np.linalg.solve(K, np.r_[rhs, 0])
    return H, rhs, p, lam, K, hb


def test_shared_internal_first_matches_finite_difference_and_adjoint():
    H, rhs, p, lam, K, hb = _solve_witness(0)
    Hp = np.array([[.3, .4], [.4, -.1]])
    rp = np.array([1, .2])
    lp = p@Hp@p
    dp = np.linalg.solve(K, np.r_[-Hp@p+lp*p, 0])
    right = np.r_[rp-Hp@hb[:2]+lp*hb[:2]-hb[2]*dp[:2], -dp[:2]@hb[:2]]
    dhb = np.linalg.solve(K, right)
    toarb = lambda a: np.array([arb(float(v)) for v in np.asarray(a).flat], dtype=object).reshape(np.shape(a))
    shared = dict(H=toarb(H), rhs=toarb(rhs), psi=toarb(p), eigenvalue=arb(float(lam)),
                  hard=toarb(hb[:2]), bpsi=arb(float(hb[2])),
                  H_first_on_psi=toarb((Hp@p)[:, None]),
                  H_first_on_hard=toarb((Hp@hb[:2])[:, None]),
                  dpsi=toarb(dp[:, None]), deigenvalue=toarb([lp]),
                  dhard_b=toarb(dhb[:, None]), hard_first_rhs=toarb(right[:, None]))
    result = local_internal_system(shared)
    for key in ('residual', 'first_replay', 'b_forward_adjoint_replay', 'b_adjoint_replay'):
        assert max(float(abs(v).upper()) for v in result[key].entries()) < 1e-14
    step = 1e-5
    plus, minus = _solve_witness(step), _solve_witness(-step)
    packed = lambda v: np.r_[v[2], v[3], v[5]]
    secant = (packed(plus)-packed(minus))/(2*step)
    computed = np.array([float(v.mid()) for v in result['internal_first'].entries()])
    np.testing.assert_allclose(computed, secant, rtol=1e-8, atol=1e-10)


def test_proper_clock_keeps_lapse_and_negative_orientation_visible():
    # A negative selected descriptor at an approximate event cannot be
    # silently clamped to zero or converted into a positive duration.
    clock, first = descriptor_clock_first(lapse=2, log_lapse_first=arb_mat([[3]]),
        descriptor=-1, descriptor_first=arb_mat([[5]]), delta=-4, delta_first=arb_mat([[7]]))
    assert clock == arb('-0.5')
    assert first[0, 0] == arb('0.125')
    with pytest.raises(ValueError):
        descriptor_clock_first(lapse=2, log_lapse_first=arb_mat([[0]]),
            descriptor=0, descriptor_first=arb_mat([[0]]), delta=arb('0 +/- 1'), delta_first=arb_mat([[0]]))


def test_duration_germ_signed_cancellation_and_eigenline_orientation():
    kwargs = dict(lapse=2, log_lapse_first=arb_mat([[3]]),
                  cpsi=-2, bpsi=4, cpsi_first=arb_mat([[-2]]), bpsi_first=arb_mat([[8]]))
    a, da = zero_descriptor_clock_germ(**kwargs)
    assert a == arb('0.125')
    assert da[0, 0].is_zero()  # signed response cancels, norms would not
    kwargs.update(cpsi=2, bpsi=-4, cpsi_first=arb_mat([[2]]), bpsi_first=arb_mat([[-8]]))
    flipped_a, flipped_da = zero_descriptor_clock_germ(**kwargs)
    assert flipped_a == a and flipped_da == da


def test_full_family_is_not_inferred_from_local_response():
    with pytest.raises(KeyError):
        local_internal_system({})
    with pytest.raises(ValueError):
        coefficient_first([arb(0)]*98, arb_mat(73, 66))


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT/'artifacts/flagship_integration/current_incoming_response_20260928'


def test_current_response_reproduction_and_source_binding():
    for filename in ('arrays.npz', 'report.json'):
        assert (PACKET/'run2'/filename).read_bytes() == (PACKET/'run3'/filename).read_bytes()
    report = json.loads((PACKET/'run2/report.json').read_bytes())
    assert not report['complete'] and not report['root_solve_attempted']
    assert report['local_internal_first_shape'] == [124, 66]
    assert report['eigenpair_proof']['validation_passed']
    assert report['eigenpair_proof']['selected_zero_based_index_verified'] == 23
    assert report['ten_local_action_sector_producer_calls'] == 0
    assert not report['descriptor_consistency']['positive_incoming_clock']
    for path, expected in report['source_SHA256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest().upper() == expected
    assert hashlib.sha256((PACKET/'run2/arrays.npz').read_bytes()).hexdigest().upper() == report['arrays_SHA256']


def test_current_secants_repeat_and_converge():
    for filename in ('arrays.npz', 'report.json'):
        assert (PACKET/'secants2'/filename).read_bytes() == (PACKET/'secants3'/filename).read_bytes()
    report = json.loads((PACKET/'secants2/report.json').read_bytes())
    assert not report['physical_reduced_action_checked']
    for name in ('local_internal', 'duration_coefficient', 'radius_history_coefficient'):
        errors = [record['errors'][name]['relative_upper'] for record in report['records']]
        assert errors[1] < .251*errors[0]
        assert errors[1] < 2e-12
    for path, expected in report['source_SHA256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest().upper() == expected


def test_sufficient_state_ledger_preserves_missing_full_family():
    report = json.loads((PACKET/'FORMATION_SUFFICIENT_STATE_LEDGER.json').read_bytes())
    assert report['q66'] is report['H66'] is report['B66x73'] is None
    assert report['independent_input_count_after_assembly'] is None
    assert not report['globally_minimal'] and not report['complete_common_incoming_family']
    witness = report['endpoint_compression_witness']
    assert witness['endpoint_log_lapse_and_proper_rate_replay']['approximate_upper'] < 2e-58
    assert arb(witness['formal_duration_coefficient_response']['lower']) > 0
    assert len(witness['unit_direction_66']) == 66
    for path, expected in report['source_SHA256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest().upper() == expected
