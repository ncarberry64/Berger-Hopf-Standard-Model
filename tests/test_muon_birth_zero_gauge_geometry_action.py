import numpy as np
import pytest

from bhsm.interface.muon_birth_zero_gauge_geometry_action import zero_gauge_geometry_action
from bhsm.interface.muon_birth_coupled_constraint_retraction import pointwise_assigned_action
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT, STATE_SOURCE, correction_representation


def fixture():
    with np.load(ROOT/STATE_SOURCE, allow_pickle=False) as f:
        x = f['state'][:98]
    rep = correction_representation(radial_points=12, radial_order=1, cap_points=12)
    fields = dict(gauge=np.zeros((12, 1, 5, 4)), gauge_tau=np.zeros((12, 1, 5, 4)),
        gauge_rho=np.zeros((12, 1, 5, 4)), gauge_angular=np.zeros((12, 1, 3, 5, 4)))
    args = dict(rho=rep['rho'], radial_quadrature=rep['radial_quadrature'], fields=fields,
        H_real=np.array([.1, .8, -.03, .04]), H_rate=np.array([.02, -.01, .03, -.02]),
        wall_gauge=np.zeros((5, 4)), lambda_H=rep['scalar_matching']['lambda_H'],
        nu_squared_action=4., cap_points=12, normal=.0001, normal_rate=.002)
    return x, args


def test_exact_cancelled_maxwell_geometry_matches_all_existing_action_columns():
    x, args = fixture()
    old = pointwise_assigned_action(x[:37], x[37:74], x[74:], **args)
    new = zero_gauge_geometry_action(x[:37], x[37:74], x[74:], **args)
    assert new['value'] == pytest.approx(old['value'], rel=2e-15)
    np.testing.assert_allclose(new['gradient'], old['gradient'], rtol=2e-14, atol=3e-14)
    np.testing.assert_allclose(new['hessian'], old['hessian'], rtol=3e-14, atol=2e-12)
    np.testing.assert_allclose(new['scalar_real_canonical_dual'], old['scalar_real_canonical_dual'], rtol=2e-14, atol=1e-16)
    np.testing.assert_array_equal(new['sectors']['independent_Maxwell']['hessian'], 0)
    assert not new['gauge_Euler_or_Hessian_zero_claim']
    # Actual mechanical spatial connection remains in the scalar action.
    assert abs(new['sectors']['Higgs_assigned']['value']) > 1e-3


def test_restricted_scalar_blocks_equal_the_literal_complex_polynomial():
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    from bhsm.interface.muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet
    x,args=fixture();new=zero_gauge_geometry_action(x[:37],x[37:74],x[74:],**args)
    weights=intrinsic_m4_weight_jet(12,x[:37],x[37:74],x[74:],source_value=args['normal'],source_rate=args['normal_rate'])
    V=np.zeros((1,4,8));V[0,:,:4]=np.eye(4)
    D=np.zeros((1,4,4,8));D[0,0,:,4:]=np.eye(4)
    scalar=material_intrinsic_higgs_gauge_action_jet(weights,
        scalar_coefficients=np.r_[args['H_real'],args['H_rate']],scalar_value_map=V,scalar_derivative_map=D,
        gauge_coefficients=np.zeros(20),gauge_trace_map=np.eye(20).reshape(1,5,4,20),
        angular_quadrature=np.ones(1),lambda_H=args['lambda_H'],nu_squared_action=args['nu_squared_action'])['action']
    factor=(2*np.pi**2)**2
    np.testing.assert_allclose(new['scalar_coefficient_gradient'],scalar.gradient[100:108]/factor,rtol=3e-14,atol=2e-16)
    np.testing.assert_allclose(new['scalar_coefficient_hessian'],scalar.hessian[100:108,100:108]/factor,rtol=3e-14,atol=2e-16)
    np.testing.assert_allclose(new['geometry_scalar_hessian'],scalar.hessian[:100,100:108]/factor,rtol=3e-14,atol=2e-14)


@pytest.mark.parametrize('key', ['gauge', 'gauge_tau', 'gauge_rho', 'gauge_angular'])
def test_reduction_rejects_every_nonzero_independent_field_jet(key):
    x, args = fixture(); args['fields'][key].flat[0] = 1e-30
    with pytest.raises(ValueError, match='zero '+key):
        zero_gauge_geometry_action(x[:37], x[37:74], x[74:], **args)


def test_reduction_rejects_nonzero_wall_trace_and_nonfinite_fields():
    x, args = fixture(); args['wall_gauge'][0, 0] = 1e-30
    with pytest.raises(ValueError, match='wall'):
        zero_gauge_geometry_action(x[:37], x[37:74], x[74:], **args)
    args['wall_gauge'][:] = 0; args['fields']['gauge_tau'].flat[0] = np.nan
    with pytest.raises(ValueError, match='gauge_tau'):
        zero_gauge_geometry_action(x[:37], x[37:74], x[74:], **args)
