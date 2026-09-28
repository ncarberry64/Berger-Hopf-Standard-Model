"""Check the coupled normal proof independently of trajectory claims."""
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from certify_n12_collar_normal_graph import jacobian, correlated_jacobian, refine_normal_radius
from contract_n12_collar_shared_speed import normal_center, owner
from bhsm.interface.shared_action_taylor import TaylorDomain


@pytest.fixture(autouse=True)
def precision():
    old = ctx.prec
    ctx.prec = 128
    yield
    ctx.prec = old


def test_normal_block_layout_recovers_center_without_eigensolve():
    H = arb_mat([[arb(i == j)*(i+2) for j in range(61)] for i in range(61)])
    n = [arb(i+1)/100 for i in range(61)]+[arb('0.03')]
    n += [arb(i-20)/71 for i in range(61)]+[arb('0.07')]
    J = jacobian(H, n)
    assert all(a.contains(b) and b.contains(a) for a, b in zip(normal_center(J, n[61]), n, strict=True))
    J[80, 18] += 1
    with pytest.raises(ValueError, match='b block'):
        normal_center(J, n[61])


def test_correlated_jacobian_matches_polynomial_normal_system():
    # Analytic action has Hzz=(2+y0+y0^2)I. This exercises simultaneous
    # Hessian, eigenvalue, normalization and hard-response derivatives.
    real = owner.action
    def contracted(y, legs, maps):
        left, right = legs
        return (2+y[0]+y[0]*y[0])*sum((left[i]*right[i] for i in range(37, 98)), 0)
    A = SimpleNamespace(_a=real._a, Mixed=real.Mixed,
        _local_variables=real._local_variables, _contracted_action=contracted,
        LOCAL=1000)
    d = TaylorDomain([(0, 1, 'interval')], 1)
    y = [d.affine(arb(1)/10, [arb(1)/100])]+[d.affine(0)]*97
    n = [d.affine(arb(i == 0), [arb(i == 1)/100]) for i in range(61)]
    n += [d.affine(arb(1)/20, [arb(1)/100])]
    n += [d.affine(arb(i == 2)/10, [arb(i == 3)/100]) for i in range(61)]
    n += [d.affine(arb(1)/10, [arb(1)/100])]
    I = arb_mat([[arb(i == j) for j in range(124)] for i in range(124)])
    Z, data = correlated_jacobian(A, y, n, [arb(1)]*124, I, [])
    tail = sum(data['jacobian_tail_bounds'].entries(), arb(0))
    for theta in (arb(-1)/2, arb(0), arb(1)/2):
        state = y[0].c+y[0].a[0, 0]*theta
        H = arb_mat([[arb(i == j)*(2+state+state*state) for j in range(61)] for i in range(61)])
        actual = I-jacobian(H, [v.c+v.a[0, 0]*theta for v in n])
        approx = data['jacobian_constant']+data['jacobian_linear']*theta
        remainder = sum((abs(v).upper()**2 for v in (actual-approx).entries()), arb(0)).sqrt()
        assert remainder.upper() <= tail
        assert Z > 0


def test_radius_rescaling_changes_only_normal_correction_part():
    C, L = arb_mat([[arb(1)/64]]), arb_mat([[arb(1)/32]])
    g, Y, Z, attempts = refine_normal_radius(arb(9), C, L, arb(1)/1024, arb(1)/512)
    assert g == 16 and Y == arb(9)/16
    assert Z == arb(66)/1024
    assert Y+Z < 1
    assert attempts[-1]['factor'] == 16


def test_missing_normal_graph_is_not_inferred_from_positive_predictor_speed():
    import json
    base = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928'
    # The original point jet is frozen and must remain a point-only packet.
    r = json.loads((base/'directional1/report.json').read_bytes())
    assert r['point_jet_only'] and not r['prefix_overlap_certified']
    assert r['uniform_correlated_remainder'] is None


def test_saved_uniform_normal_certificate_and_speed_are_replayable():
    import json
    import numpy as np
    from checkpoint_n12_gate7_66d_tangent_binding import restore, digest
    from bhsm.interface.input_linear_taylor import matrix_norm_bound, vector_norm
    ctx.prec = 512
    folder = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928/normal45_final1'
    record = json.loads((folder/'report.json').read_bytes())
    assert digest(folder/'arrays.npz') == record['arrays_SHA256']
    with np.load(folder/'arrays.npz') as z:
        Y = (vector_norm(restore(z, 'residual_constant').entries())
             +vector_norm(restore(z, 'residual_linear').entries())
             +restore(z, 'residual_remainder')[0, 0])
        Z = (matrix_norm_bound(restore(z, 'jacobian_constant'))
             +matrix_norm_bound(restore(z, 'jacobian_linear'))
             +sum(restore(z, 'jacobian_tail_bounds').entries(), arb(0)))
        assert Y+Z < 1
        speed = restore(z, 'enclosed_speed')
        assert speed[0, 0]-abs(speed[0, 1]).upper()-speed[0, 2] > 0
        assert restore(z, 'positive_reference_overlap')[0, 0] > 0
        assert restore(z, 'anchor_scaled_distance')[0, 0] < 1
    assert record['actual_normal_graph_included']
    assert record['selected_zero_based_index'] == 24
    assert not record['actual_flow_tube_included']
    assert not record['prefix_overlap_certified']
    assert record['prefix_cells_rebuilt'] == 0
