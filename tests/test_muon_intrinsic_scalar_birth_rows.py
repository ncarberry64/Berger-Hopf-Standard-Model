"""Action-boundary controls; their represented worldvolume is not physical E1."""
import numpy as np
import pytest

from bhsm.interface.muon_intrinsic_scalar_birth_rows import (
    scalar_birth_action_rows, scalar_birth_action_jacobian,
)
from bhsm.interface.muon_intrinsic_worldvolume_scalar_transport import unit_s3_material_frame
from test_muon_intrinsic_worldvolume_scalar_transport import (
    POINTS, coupled_control, solve, basis, density,
)


def control():
    c, hp, hc = coupled_control()
    c = np.concatenate((c, np.linspace(-.7, .2, 20), np.linspace(.3, -.1, 20)))
    hp, hc = (np.pad(M, ((0, 0), (0, 40))) for M in (hp, hc))
    pp = np.zeros((20, 85)); pc = pp.copy()
    pp[:, 45:65] = np.eye(20); pc[:, 65:85] = np.eye(20)
    return c, hp, hc, pp, pc


def varied_density(side, q, c, v):
    data = density(side, q, c, v)
    scale = .4 if side == 'child' else .2
    factor = 1+scale*c[0]*q[:, 0]
    mu = data['density']
    data['density'] = mu*factor
    data['density_spatial_derivatives'] = scale*c[0]*mu[:, None]*unit_s3_material_frame(q)[:, 0]
    data['density_variation'] = (data['density_variation']*factor
        if v is None else data['density_variation']*factor+mu*scale*v[0]*q[:, 0])
    return data


def rows(c, v=None, *, nonlinear=False, varying_density=False, moving_quadrature=False):
    _, hp, hc, pp, pc = control()
    quad = np.full(8, .125)
    dq = None
    if moving_quadrature:
        shape = np.linspace(-.4, .5, 8)
        quad *= 1+.03*c[1]*shape
        if v is not None:
            dq = np.full(8, .125)*.03*v[1]*shape
    return scalar_birth_action_rows(
        transport=solve(c, v, nonlinear), parent_birth_points=POINTS,
        birth_parent_time=1., birth_child_time=1., quadrature=quad,
        basis_evaluator=basis, density_evaluator=varied_density if varying_density else density,
        parent_coefficient_map=hp, child_coefficient_map=hc,
        parent_momentum_coefficient_map=pp, child_momentum_coefficient_map=pc,
        parent_birth_points_variation=None if v is None else np.zeros_like(POINTS),
        delta_quadrature=dq)


def test_canonical_momentum_density_is_paired_once_not_weighted_by_gram_again():
    c, _, _, pp, pc = control()
    a = rows(c)
    np.testing.assert_allclose(a['parent_momentum_dual'], 2*(pp@c), atol=2e-11)
    np.testing.assert_allclose(a['child_momentum_dual'], 2*(pc@c), atol=2e-11)
    np.testing.assert_allclose(a['child_momentum_riesz'], np.exp(-3*c[4])*(pc@c), atol=2e-11)
    app = a['transport_application']
    np.testing.assert_allclose(a['momentum_residual'],
        app['parent_pairing']@(a['parent_momentum_riesz']
            -app['dual_trace_return']@a['child_momentum_riesz']), atol=3e-11)
    assert a['direct_fixed_geometry_surface_H_cotangent'] == 0
    assert not a['physical_primal_claim']


def test_boundary_rows_cancel_on_the_matched_control_graph_with_opposite_endpoint_signs():
    c, hp, _, _, pc = control()
    T = rows(c)['transport_application']['trace_transport']
    c[25:45] = T@(hp@c)
    c[45:65] = T.T@(pc@c)
    a = rows(c)
    np.testing.assert_allclose(a['trace_residual'], 0, atol=2e-11)
    np.testing.assert_allclose(a['momentum_residual'], 0, atol=2e-11)
    # Flipping the child endpoint sign would give an unmistakable nonzero row.
    assert np.linalg.norm(a['parent_momentum_dual']+a['exact_child_momentum_return']) > .1


def test_unrepresented_transport_image_and_its_momentum_contact_are_not_dropped():
    c, _, _, _, _ = control()
    a = rows(c, nonlinear=True, varying_density=True)
    app = a['transport_application']
    assert app['image_projection_weighted_norm'] > .01
    assert np.linalg.norm(a['unrepresented_momentum_return']) > 1e-5
    exact = 2*np.einsum('pid,pi,p->d', app['scalar_transport_image'].conj(),
        a['canonical_child_density'], .125*solve(c, nonlinear=True)['haar_jacobian'][-1]).real
    np.testing.assert_allclose(a['exact_child_momentum_return'], exact, atol=2e-11)
    np.testing.assert_allclose(a['momentum_residual'],
        a['projected_momentum_residual']-a['unrepresented_momentum_return'], atol=2e-12)
    assert not a['finite_image_invariance_claim']
    assert a['residual'].shape[0] == 2*app['trace_residual'].size+len(a['momentum_residual'])


@pytest.mark.parametrize('nonlinear', [False, True])
def test_same_vector_tangent_includes_density_map_basis_bundle_momentum_and_domain_motion(nonlinear):
    c, _, _, _, _ = control()
    v = np.linspace(-.17, .23, len(c)); eps = 2e-6
    kwargs = dict(nonlinear=nonlinear, varying_density=True, moving_quadrature=True)
    a = rows(c, v, **kwargs)
    plus, minus = rows(c+eps*v, **kwargs), rows(c-eps*v, **kwargs)
    for key in ('trace_residual', 'trace_coefficient_residual', 'parent_momentum_dual',
                'child_momentum_dual', 'parent_momentum_riesz', 'child_momentum_riesz',
                'exact_child_momentum_return', 'projected_child_momentum_return',
                'unrepresented_momentum_return', 'momentum_residual', 'residual'):
        np.testing.assert_allclose(a[key+'_variation'], (plus[key]-minus[key])/(2*eps),
                                   rtol=8e-7, atol=8e-8, err_msg=key)


def test_jacobian_assembles_the_actual_boundary_producer_columns():
    base, _, _, _, _ = control()
    # A fixed affine computational subspace, not a physical state/trace.
    lift = np.zeros((len(base), 5))
    lift[[0, 3, 7, 49, 68], np.arange(5)] = 1
    x = np.array([.01, -.02, .03, -.04, .05])
    def application(z, direction):
        return rows(base+lift@z, None if direction is None else lift@direction,
                    nonlinear=True, varying_density=True, moving_quadrature=True)
    a = scalar_birth_action_jacobian(x, application)
    direction = np.array([.2, -.1, .3, .4, -.2]); eps = 2e-6
    fd = (application(x+eps*direction, None)['residual']
          -application(x-eps*direction, None)['residual'])/(2*eps)
    np.testing.assert_allclose(a['jacobian']@direction, fd, atol=8e-8, rtol=8e-7)
    assert not a['square_system_claim']


def test_momentum_maps_must_extract_the_one_transport_vector():
    c, hp, hc, _, pc = control()
    with pytest.raises(ValueError, match='same coefficient vector'):
        scalar_birth_action_rows(
            transport=solve(c), parent_birth_points=POINTS,
            birth_parent_time=1., birth_child_time=1., quadrature=np.full(8, .125),
            basis_evaluator=basis, density_evaluator=density,
            parent_coefficient_map=hp, child_coefficient_map=hc,
            parent_momentum_coefficient_map=np.zeros((20, 84)),
            child_momentum_coefficient_map=pc)
