"""Independent finite birth-level and original-operator pullback checks."""
import numpy as np
import pytest

from bhsm.interface.muon_d5_fitted_birth_domain import (
    SigmaNormalBirthDomain, fitted_d5_coefficients, pullback_value_first,
)
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


class _History:
    times=np.array([0.,1.])


def _normal(a=.17,b=.8,d=1.06, source=True):
    def callback(t,r):
        out=dict(value=np.array([a+b*t,d]),time=np.array([b,0.]),radial=np.zeros(2))
        if source:out['source']=np.array([1.,0.])
        return out
    return callback


def test_finite_birth_curve_is_original_level_inverse_not_quadratic_jet():
    a,b,d=.17,.8,1.06
    domain=SigmaNormalBirthDomain(_History(),normal_jet=_normal(a,b,d))
    for s in (.003,.017,.039):
        birth=domain.birth(s,source=True)
        expected=a*np.expm1(b*s)/b
        assert abs(birth['wall_label']-expected)<3e-15
        assert abs(birth['slope']-a*np.exp(b*s))<2e-14
        assert abs(birth['source']-np.expm1(b*s)/b)<3e-14
        assert abs(birth['slope_source']-np.exp(b*s))<3e-13
        assert abs(birth['birth_rho']-(WALL-d*s))<2e-15
        # The exact finite curve differs measurably from its local two-jet.
        assert abs(expected-a*s-a*b*s*s/2)>1e-10
        assert abs(birth['normal_length_residual'])<3e-15
        check=domain.verify_birth(s)
        assert abs(check['normal_length_residual'])<3e-13
        assert abs(check['birth_radius_residual'])<3e-14
        assert check['original_radial_rows']<2e-9
        assert check['original_length_rows']<2e-9
    assert domain.minimum_evaluated_time==0
    assert domain.maximum_evaluated_time>0


def test_fitted_chart_and_source_keep_complete_chain_rule():
    a,b,d=.17,.8,1.06;s=.031;theta=.023
    domain=SigmaNormalBirthDomain(_History(),normal_jet=_normal(a,b,d))
    chart=domain.point(theta,s,source=True)
    original=np.array([theta*np.exp(-b*s),WALL-d*s])
    expected=np.array([[np.exp(-b*s),-b*original[0]],[0.,-d]])
    np.testing.assert_allclose(chart['original_point'],original,atol=3e-15)
    np.testing.assert_allclose(chart['inverse_jacobian'],expected,atol=3e-14)
    np.testing.assert_allclose(chart['original_point_source'],0,atol=3e-14)
    np.testing.assert_allclose(chart['inverse_jacobian_source'],0,atol=3e-12)
    assert np.max(abs(chart['coordinate_inverse_residual']))<3e-16
    # A finite original field is differentiated independently before and
    # after the coordinate pullback. This is not a derivative of a matrix
    # identity copied from the implementation.
    t,r=original
    v=np.array([np.exp(t)+r*r,t*r])
    first=np.array([[np.exp(t),r],[2*r,t]])
    pulled=pullback_value_first(v,first,chart,source=np.array([.3,-.2]),
        original_second=np.array([[[np.exp(t),0.],[0.,1.]],[[0.,1.],[2.,0.]]]),
        source_first=np.zeros((2,2)))
    h=1e-6
    def field(th,ss):
        tt=th*np.exp(-b*ss);rr=WALL-d*ss
        return np.array([np.exp(tt)+rr*rr,tt*rr])
    numerical=np.array([(field(theta+h,s)-field(theta-h,s))/(2*h),
        (field(theta,s+h)-field(theta,s-h))/(2*h)])
    np.testing.assert_allclose(pulled['first'],numerical,atol=2e-10)
    np.testing.assert_allclose(pulled['source'],[.3,-.2],atol=3e-14)
    np.testing.assert_allclose(pulled['first_source'],0,atol=3e-12)
    assert abs(pulled['volume_jacobian']-d*np.exp(-b*s))<3e-14


def test_original_d5_in_fitted_chart_retains_birth_shear_and_source():
    domain=SigmaNormalBirthDomain(_History(),normal_jet=_normal())
    chart=domain.point(.021,.027,source=True)
    rng=np.random.default_rng(19465)
    T,R,A=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)) for _ in range(3))
    Tj,Rj,Aj=(rng.normal(size=(3,3)) for _ in range(3))
    app=fitted_d5_coefficients(T,R,A,chart,source=(Tj,Rj,Aj))
    # Independent direct original derivatives of a two-coordinate field.
    t,r=chart['original_point'];V=np.array([np.exp(t),r*r,t*r],complex)
    original_first=np.array([[np.exp(t),0.,r],[0.,2*r,t]])
    fitted_first=chart['inverse_jacobian'].T@original_first
    old=T@original_first[0]+R@original_first[1]+A@V
    new=app['time']@fitted_first[0]+app['normal']@fitted_first[1]+app['body']@V
    np.testing.assert_allclose(new,old,atol=2e-15)
    # Source consists of BOTH coefficient and domain contacts.
    np.testing.assert_allclose(app['time_source'],Tj*chart['forward_jacobian'][0,0]
        +Rj*chart['forward_jacobian'][0,1],atol=3e-12)
    assert abs(chart['birth']['slope'])>.17


def test_future_domain_and_unassigned_source_are_guarded():
    domain=SigmaNormalBirthDomain(_History(),normal_jet=_normal(source=False))
    with pytest.raises(ValueError,match='vartheta'):
        domain.point(-1e-12,.01)
    with pytest.raises(ValueError,match='unknown normal source'):
        domain.birth(.01,source=True)
    with pytest.raises(ValueError,match='outside actual child domain'):
        domain._normal(-1e-20,WALL)
    with pytest.raises(ValueError,match='future child'):
        class _Past:times=np.array([-1.,0.])
        SigmaNormalBirthDomain(_Past())


def test_zero_depth_is_actual_birth_face_not_a_missing_root():
    domain=SigmaNormalBirthDomain(_History(),normal_jet=_normal())
    b=domain.birth(0.,source=True)
    assert b['wall_label']==0 and b['birth_rho']==WALL and b['source']==0
    p=domain.point(.02,0.,source=True)
    np.testing.assert_allclose(p['original_point'],[.02,WALL],atol=1e-18)


def test_variable_normal_source_jacobian_matches_independent_source_solutions():
    def normal(eps):
        def value(t,r):
            return dict(value=np.array([.14+eps+.7*t+.04*r,1.04+.2*eps+.3*t]),
                time=np.array([.7,.3]),radial=np.array([.04,0.]),source=np.array([1.,.2]))
        return value
    theta,s=.021,.027;step=2e-5
    center=SigmaNormalBirthDomain(_History(),normal_jet=normal(0)).point(theta,s,source=True)
    plus=SigmaNormalBirthDomain(_History(),normal_jet=normal(step)).point(theta,s)
    minus=SigmaNormalBirthDomain(_History(),normal_jet=normal(-step)).point(theta,s)
    np.testing.assert_allclose(center['birth']['source'],
        (plus['birth']['wall_label']-minus['birth']['wall_label'])/(2*step),atol=2e-10)
    np.testing.assert_allclose(center['birth']['slope_source'],
        (plus['birth']['slope']-minus['birth']['slope'])/(2*step),atol=2e-9)
    np.testing.assert_allclose(center['original_point_source'],
        (plus['original_point']-minus['original_point'])/(2*step),atol=2e-10)
    np.testing.assert_allclose(center['inverse_jacobian_source'],
        (plus['inverse_jacobian']-minus['inverse_jacobian'])/(2*step),atol=2e-9)


def test_tiny_finite_domain_preserves_radius_float_floor_without_physical_admission():
    # Actual application failure: an order-one radius cannot represent a
    # sub-ulp correction even when the two endpoint equations are correct.
    b,d=.8,1.06;theta,s=2e-6,5.581655955689221e-8
    domain=SigmaNormalBirthDomain(_History(),normal_jet=_normal(.17,b,d))
    chart=domain.point(theta,s,source=True)
    np.testing.assert_allclose(chart['original_point'],
        [theta*np.exp(-b*s),WALL-d*s],atol=4*np.spacing(WALL),rtol=0)
    assert abs(chart['wall_label_residual'])<=max(1e-18,chart['radial_float_wall_clock_floor'])
    assert abs(chart['actual_normal_length_residual'])<4*np.finfo(float).eps*WALL
    assert chart['radial_float_wall_clock_floor']>0
