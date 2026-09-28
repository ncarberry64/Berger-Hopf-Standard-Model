"""Check the actual normal-residual identity and time-integrated support."""
from pathlib import Path
import sys
from types import SimpleNamespace
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from reduce_n12_collar_flow_descriptor import normal_contraction, integral_bound
from bhsm.interface.shared_action_taylor import TaylorDomain


def test_material_parameters_are_not_integrated_as_known_time_coordinate():
    ctx.prec = 128
    d = TaylorDomain([(0, 1, 'interval'), (1, 3, 'box'), (3, 5, 'euclidean')], 5)
    f = d.affine(2, [4, -3, 2, 3, 4], 1)
    # Only theta=t/h gets the factor 1/2. The Euclidean pair has support 5.
    assert integral_bound(f, arb(1)/8) == arb(15)/8


def test_projected_normal_action_matches_complete_equations():
    ctx.prec = 128
    d = TaylorDomain([(0, 1, 'interval')], 1)
    y = [d.affine(arb(i+1)/128, [arb(i % 3-1)/1024]) for i in range(98)]
    n = [d.affine(arb(i-20)/256, [arb(i % 5-2)/2048]) for i in range(124)]
    weights = [arb(1)]*98
    beta = [arb(i % 7-3)/32 for i in range(124)]
    H = arb_mat([[arb(i == j)*(i+1)/128 for j in range(98)] for i in range(98)])
    H[0, 37] = H[37, 0] = arb(1)/4
    def matvec(v):
        return [sum((H[i, j]*v[j] for j in range(98)), 0) for i in range(98)]
    def action(state, legs, maps):
        right = state if len(legs) == 1 else legs[1]
        return sum((a*b for a, b in zip(legs[0], matvec(right), strict=True)), 0)
    A = SimpleNamespace(metric_data=lambda: ([1]*37, [1]*61, None, None), _contracted_action=action)
    projected = normal_contraction(A, y, n, weights, beta, [])
    psi, lam, hard, b = n[:61], n[61], n[62:123], n[123]
    gradient = matvec(y)
    rhs = [(gradient[i] if i < 37 else d.affine(0))
           -sum((H[37+i, j]*y[37+j] for j in range(37)), 0) for i in range(61)]
    Hp = [sum((H[37+i, 37+j]*psi[j] for j in range(61)), 0) for i in range(61)]
    Hh = [sum((H[37+i, 37+j]*hard[j] for j in range(61)), 0) for i in range(61)]
    F = [Hp[i]-lam*psi[i] for i in range(61)]
    F += [(sum((v*v for v in psi), 0)-1)/2]
    F += [Hh[i]-lam*hard[i]+b*psi[i]-rhs[i] for i in range(61)]
    F += [sum((p*h for p, h in zip(psi, hard, strict=True)), 0)]
    explicit = sum((a*v for a, v in zip(beta, F, strict=True)), 0)
    assert (projected.c-explicit.c).contains(0)
    assert (projected.a[0, 0]-explicit.a[0, 0]).contains(0)


def test_residual_subtraction_preserves_solution_without_exact_adjoint():
    ctx.prec = 128
    # n^2=p, output n. Any fixed beta is an identity on F=0.
    for p in (arb(1), arb(4), arb(9)):
        n = p.sqrt()
        for beta in (arb(0), arb(1)/3, arb(8)):
            assert (n-beta*(n*n-p)-n).contains(0)


def test_time_restriction_is_not_radius_or_tolerance_relaxation():
    from certify_n12_collar_partial_step import restricted_ratios
    ctx.prec = 128
    f = arb(15)/16
    A, B = arb(1)/4, arb(3)/2
    old = A+B/2
    actual_short_bound = f*A+f*f*B/2
    assert actual_short_bound <= restricted_ratios([old], f)[0]
    assert restricted_ratios([arb(67)/64], f)[0] < 1
    assert restricted_ratios([arb(67)/64], arb(1))[0] > 1


def test_partial_flow_certificate_preserves_open_prefix_and_operator_obligations():
    import json
    import numpy as np
    from checkpoint_n12_gate7_66d_tangent_binding import restore, digest
    ctx.prec = 512
    folder = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928/flow55_partial1'
    record = json.loads((folder/'report.json').read_bytes())
    assert digest(folder/'arrays.npz') == record['arrays_SHA256']
    with np.load(folder/'arrays.npz') as z:
        h, old = restore(z, 'step')[0, 0], restore(z, 'old_step')[0, 0]
        assert h == arb(15)*old/16
        assert all(v<1 for v in restore(z, 'first_exit_ratios').entries())
        assert restore(z, 'initial_action')[98, 0] < 0
        assert (restore(z, 'endpoint_action')[98, 0]-restore(z, 'initial_action')[98, 0]-h).contains(0)
    assert record['actual_flow_tube_included']
    assert not record['prefix_overlap_certified']
    assert not record['first_variation_transported']
    assert not record['positive_operator_history_certified']
    assert not record['tolerances_changed'] and not record['physical_radii_changed']
    assert not record['Gate7_closed'] and not record['FULL_BHSM_COMPLETE']


def test_curve_normal_lift_replays_and_stays_in_existing_normal_ball():
    import json
    import numpy as np
    from checkpoint_n12_gate7_66d_tangent_binding import restore, digest
    from bind_n12_collar_curve_normal_response import box_image_bound
    ctx.prec = 512
    folder = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928/flow55_curve_normal1'
    record = json.loads((folder/'report.json').read_bytes())
    assert digest(folder/'arrays.npz') == record['arrays_SHA256']
    with np.load(folder/'arrays.npz') as z:
        P, T, X = [restore(z, k) for k in (
            'source_preconditioned_normal', 'curve_normal_response_scaled', 'source_partial_scaled')]
        assert all(v.contains(0) for v in (P*T+X).entries())
        assert box_image_bound(T) < 1
        assert sum(restore(z, 'old_normal_YZ').entries(), arb(0)) < 1
        assert restore(z, 'new_normal_posterior')[0, 0] < arb(1)/8192
    assert record['reused_uniform_normal_jacobian_bound']


def test_shared_endpoint_remains_inside_the_certified_curve_corridor():
    import json
    import numpy as np
    from checkpoint_n12_gate7_66d_tangent_binding import restore
    from bhsm.interface.shared_parameter_residual import linear_support
    ctx.prec = 512
    base = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928'
    record = json.loads((base/'flow55_endpoint1/report.json').read_bytes())
    with np.load(base/'flow55_endpoint1/arrays.npz') as e, np.load(base/'flow55_partial1/arrays.npz') as p, np.load(base/'directional1/arrays.npz') as j:
        c, a, r = [restore(e, k) for k in ('endpoint_constant', 'endpoint_affine', 'endpoint_remainder')]
        initial = restore(p, 'initial_action')
        h = restore(p, 'step')[0, 0]
        U = restore(j, 'fixed_s_direction')
        rho = restore(p, 'curve_action_radii')
        for i in range(98):
            bound = (abs(c[i, 0]-initial[i, 0]-h*U[i, 0]).upper()
                     +linear_support([a[i, k] for k in range(222)], record['groups'])+r[i, 0])
            assert bound < rho[i, 0]
        assert all(v.contains(0) for v in restore(e, 'rate_first_coefficient_replay').entries())
    assert record['physical_input_count_added'] == 0
    assert not record['first_variation_transported']
