"""Independent Eulerian/reference pullback and shape-contact checks."""
import math

import numpy as np
import pytest

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_intrinsic_higgs_gauge_action import intrinsic_higgs_gauge_action_jet
from bhsm.interface.muon_material_higgs_gauge_action import material_intrinsic_higgs_gauge_action_jet


def data():
    return dict(scalar_coefficients=np.array([.1,.4,-.2,.3]),
        scalar_value_map=np.eye(4)[None],scalar_derivative_map=np.zeros((1,4,4,4)),
        gauge_coefficients=np.arange(20,dtype=float)/30-.2,
        gauge_trace_map=np.eye(20).reshape(1,5,4,20),
        angular_quadrature=np.ones(1),lambda_H=.13,nu_squared_action=.3)


def weights(x=0.,rate=.17):
    coordinate=Jet.affine(x,np.ones(1))
    return dict(wT=2*coordinate.exp(),wS=3*(-coordinate).exp(),wV=4*(2*coordinate).exp(),
        mechanical_connection_lambda=.7+.2*coordinate,wall_rate=rate+coordinate)


def eulerian_value(x,reference,rate=.17):
    # Independently convert the one-form. J is allowed to move with x;
    # rho_phys_dot=2*rate and only the physical radial component advects.
    J=math.exp(.4*x)
    g=reference['gauge_coefficients'].reshape(5,4).copy()
    g[1]/=J
    g[0]-=2*(rate+x)*g[1]
    d=dict(reference,gauge_coefficients=g.ravel())
    return intrinsic_higgs_gauge_action_jet(weights(x,rate),**d)['action'].value


@pytest.mark.parametrize('rate',[-.2,0.,.17])
def test_material_action_matches_independent_eulerian_coordinate_conversion(rate):
    d=data()
    result=material_intrinsic_higgs_gauge_action_jet(weights(.03,rate),**d)
    assert result['action'].value==pytest.approx(eulerian_value(.03,d,rate),rel=3e-15)
    assert result['physical_wall_rate'].value==pytest.approx(rate+.03)
    assert not result['physical_wall_velocity_set_to_zero']
    assert result['material_pullback_motion_count']==1


def test_normal_first_second_and_mixed_derivatives_keep_geometric_motion_once():
    d=data();actual=material_intrinsic_higgs_gauge_action_jet(weights(),**d)['action']
    h=2e-4
    f0=eulerian_value(0.,d)
    fp,fm=(eulerian_value(sign*h,d) for sign in (1,-1))
    assert (fp-fm)/(2*h)==pytest.approx(actual.gradient[0],rel=4e-8)
    assert (fp-2*f0+fm)/h**2==pytest.approx(actual.hessian[0,0],rel=2e-7)
    # Shape/scalar and shape/gauge mixed derivatives of the literal action.
    direction=np.arange(24,dtype=float)/25-.4
    def tangent(x):
        step=1e-5
        plus=dict(d,scalar_coefficients=d['scalar_coefficients']+step*direction[:4],
                    gauge_coefficients=d['gauge_coefficients']+step*direction[4:])
        minus=dict(d,scalar_coefficients=d['scalar_coefficients']-step*direction[:4],
                     gauge_coefficients=d['gauge_coefficients']-step*direction[4:])
        return (eulerian_value(x,plus)-eulerian_value(x,minus))/(2*step)
    assert (tangent(h)-tangent(-h))/(2*h)==pytest.approx(actual.hessian[0,1:]@direction,
                                                                   rel=3e-6,abs=1e-5)


def test_reference_Ar_is_not_a_second_independent_temporal_wall_trace():
    d=data();material=material_intrinsic_higgs_gauge_action_jet(weights(),**d)['action']
    physical=intrinsic_higgs_gauge_action_jet(weights(),**d)['action']
    # The field Ar_ref remains in the parent action, but does not provide
    # an extra intrinsic temporal covariant derivative at a fixed reference wall.
    np.testing.assert_array_equal(material.gradient[9:13],0)
    np.testing.assert_array_equal(material.hessian[9:13],0)
    assert np.linalg.norm(physical.gradient[9:13])>1e-3
    assert np.linalg.norm(material.hessian[0,1:5])>1.
