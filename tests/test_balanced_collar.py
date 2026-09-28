"""Test coupled-chart coefficient cancellation against explicit normal algebra."""
from pathlib import Path
import sys
from contextlib import nullcontext
from types import SimpleNamespace
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
import certify_n12_balanced_collar_normal as balanced
from certify_n12_collar_normal_graph import jacobian
from bhsm.interface.shared_action_taylor import TaylorDomain


def test_streamed_jacobian_combines_shared_action_and_normal_coefficients(monkeypatch):
    ctx.prec = 128
    d = TaylorDomain([(0, 1, 'interval'), (1, 2, 'box')], 2)
    n = [d.affine(arb(i+1)/256, [arb(i % 3-1)/1024, arb(i % 5-2)/2048]) for i in range(124)]
    # H includes the same lambda dependence; H-lambda I must cancel it
    # before any support, including the curve parameter.
    H = [[n[61]+(i+1) if i == j else d.affine(arb(i-j)/65536)
          for j in range(61)] for i in range(61)]
    def contraction(y, legs, maps):
        j = next(i-37 for i in range(37, 98) if legs[1][i] == 1)
        return sum((legs[0][37+k]*H[k][j] for k in range(61)), 0)
    A = SimpleNamespace(_contracted_action=contraction)
    monkeypatch.setattr(balanced, 'input_linear_taylor_action', lambda a: nullcontext())
    radii = [arb(i % 4+1)/16 for i in range(124)]
    R = arb_mat([[arb(i == j)+arb((i+1) % 124 == j)/8 for j in range(124)] for i in range(124)])
    scaled = arb_mat(124, 124, [R[i, j]/radii[i] for i in range(124) for j in range(124)])
    result = balanced.stream_jacobian(A, [d.affine(0)]*98, n, radii, scaled, [])
    curves = arb(0)
    I = arb_mat([[arb(i == j) for j in range(124)] for i in range(124)])
    for parameter in (-1, 0, 1):
        get = lambda v: v.c if parameter == -1 else v.a[0, parameter]
        J = jacobian(arb_mat([[get(v) for v in row] for row in H]), [get(v) for v in n])
        raw = scaled*J
        expected = (I if parameter == -1 else arb_mat(124, 124))-arb_mat(124, 124,
            [raw[i, j]*radii[j] for i in range(124) for j in range(124)])
        if parameter < 1:
            got = result['jacobian_constant' if parameter == -1 else 'jacobian_theta']
            assert all(v.contains(0) for v in (got-expected).entries())
        else:
            curves = sum((abs(v).upper()**2 for v in expected.entries()), arb(0)).sqrt()
    tails = result['jacobian_tail_bounds']
    assert tails[0, 0].overlaps(curves)
    assert tails[0, 1] == 0 and tails[0, 2] == 0


def test_balanced_proposal_retains_signed_frozen_jet_and_is_not_certificate():
    import json
    import numpy as np
    from checkpoint_n12_gate7_66d_tangent_binding import digest, restore
    ctx.prec = 512
    base = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928'
    report = json.loads((base/'balanced45_proposal1/report.json').read_bytes())
    assert digest(base/'balanced45_proposal1/arrays.npz') == report['arrays_SHA256']
    assert not report['uniform_domain_certified']
    assert not report['actual_flow_tube_included']
    with np.load(base/'balanced45_proposal1/arrays.npz') as z:
        J, A, rho, b = [restore(z, k) for k in ('point_rate_jacobian', 'point_absolute_majorant',
            'curve_action_radii', 'point_curvature_forcing')]
        h = restore(z, 'step')[0, 0]
        residual = rho-4*h*A*rho-4*b
        assert all(abs(v).upper() < arb('1e-130') for v in residual.entries())
        assert all(v>0 for v in rho.entries())
        assert any(v<0 for v in J.entries())
        # Rehydrating rational ball data may widen J by an outward rounding
        # ulp. Compare the stored magnitude with that enclosure, not a second
        # newly rounded endpoint treated as an exact scalar.
        assert all(A[i, j].overlaps(abs(J[i, j])) for i in range(98) for j in range(98))


def test_prepared_numerator_adjoint_matches_owned_algebraic_derivative():
    from certify_n12_balanced_collar_flow import numerator_adjoint
    ctx.prec = 128
    center = [arb(i+1)/128 for i in range(124)]
    s0 = arb(-1)/1024
    rw = [arb(i+1)/64 for i in range(61)]
    J0 = arb_mat([[arb(i == j)*(i+1) for j in range(124)] for i in range(124)])
    rho = [arb(1)/256]*98
    beta, replay = numerator_adjoint(center, s0, rw, J0, [0, 37, 97], rho)
    assert all(abs(v).upper() < arb('1e-32') for v in replay.entries())
    # beta is deliberately rounded to a point; its stored residual must be
    # included when checking equality with the exact output derivative.
    derivative = beta*J0+replay
    assert all(v == 0 for v in [derivative[0, j] for j in range(124)])
    for row, k in ((1, 0), (2, 60)):
        assert derivative[row, k].overlaps(rw[k]*center[123]/rho[37+k])
        assert derivative[row, 62+k].overlaps(rw[k]*s0/rho[37+k])
        assert derivative[row, 123].overlaps(rw[k]*center[k]/rho[37+k])


def test_balanced_uniform_normal_certificate_does_not_promote_flow():
    import json
    import numpy as np
    from checkpoint_n12_gate7_66d_tangent_binding import restore, digest
    ctx.prec = 512
    folder = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928/balanced45_normal1'
    report = json.loads((folder/'report.json').read_bytes())
    assert digest(folder/'arrays.npz') == report['arrays_SHA256']
    with np.load(folder/'arrays.npz') as z:
        YZ = restore(z, 'YZ')
        assert sum(YZ.entries(), arb(0)) < 1
        assert restore(z, 'posterior')[0, 0] < 1
        assert restore(z, 'anchor_distance')[0, 0] < 1
        assert restore(z, 'orientation')[0, 0] > 0
        assert restore(z, 'step')[0, 0] == arb(2)**-45
        initial, final = [restore(z, k) for k in ('initial_normal_radii', 'normal_radii')]
        assert all(v.contains(0) for v in (final-report['radius_factor']*initial).entries())
    assert report['normal_graph_certified']
    assert not report['actual_flow_tube_included']
    assert not report['first_variation_transported']
    assert not report['prefix_overlap_certified']
    assert not report['Gate7_closed'] and not report['FULL_BHSM_COMPLETE']
