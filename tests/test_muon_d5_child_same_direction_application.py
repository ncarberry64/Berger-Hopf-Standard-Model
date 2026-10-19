"""Independent kinematic and cached-chart/source recovery checks."""
import numpy as np

from bhsm.interface.muon_d5_child_same_direction_application import (
    ChildNormalCorrectionHistory,recover_cached_original_coefficients,
    additional_cached_chart_source,
)
from bhsm.interface.muon_d5_fitted_birth_domain import SigmaNormalBirthDomain,fitted_d5_coefficients


def test_child_correction_keeps_free_rate_distinct_and_preserves_kinematics(monkeypatch):
    import bhsm.interface.muon_d5_child_same_direction_application as module
    class History:
        times=np.array([0.,1.])
        original_phase_operands={'resolved_phase_coordinate_lift':np.zeros((268,252))}
        original_radial_representation={}
        def value(self,t):
            x=np.zeros(268,complex);rate=x.copy();x[98]=.2+.3*t;x[99]=.3;rate[98]=.3
            return x,rate
    def shape(raw,P):
        grad=np.zeros(100,complex);grad[98]=2*raw[98]
        H=np.zeros((100,100),complex);H[98,98]=2
        return dict(value=1+raw[98]**2,raw_gradient=grad,raw_hessian=H)
    monkeypatch.setattr(module,'proper_normal_shape_coefficient',shape)
    history=History();displacement=ChildNormalCorrectionHistory(history,17.98966013686085)
    free=ChildNormalCorrectionHistory(history,17.98966013686085,free_rate_column=True)
    assert free.source(0.)[0][98]==0
    assert free.source(0.)[0][99]==1.04
    assert abs(displacement.source(0.)[0][98])>18
    for correction in (displacement,free):
        t=.27;step=1e-6;b,bt=correction.source(t)
        np.testing.assert_allclose((correction.source(t+step)[0]-correction.source(t-step)[0])/2/step,bt,atol=2e-9)
        np.testing.assert_allclose(bt[98],b[99],atol=0,rtol=0)
        np.testing.assert_array_equal(correction.value(t)[0],history.value(t)[0])


def test_cached_original_time_jet_is_recovered_without_reinterpreting_source():
    rng=np.random.default_rng(182)
    values=tuple(rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)) for _ in range(3))
    times=tuple(rng.normal(size=(4,4))*.3 for _ in range(3))
    radials=tuple(rng.normal(size=(4,4))*.2 for _ in range(3))
    J=np.array([[1.1,.12],[-.03,-.9]]);X=np.linalg.inv(J);Jj=np.array([[.1,-.04],[.07,.09]])
    xj=np.array([.13,-.17]);chart=dict(forward_jacobian=J,inverse_jacobian=X,forward_jacobian_source=Jj)
    source=tuple(a*(1+xj[0])+b*xj[1] for a,b in zip(times,radials))
    app=fitted_d5_coefficients(*values,chart,source=source);prefix='child_plus_particle_'
    cached=dict(child_fitted_forward_jacobian=J,child_fitted_inverse_jacobian=X,
        child_fitted_forward_jacobian_source=Jj,original_child_coordinates_source=xj)
    for key,a in app.items():cached[prefix+key+'64']=a
    for key,a in zip(('time','radial','body'),radials):cached[prefix+key+'_original_radial64']=a
    actual,dt,dr=recover_cached_original_coefficients(cached,prefix)
    for got,expected in zip((*actual,*dt,*dr),(*values,*times,*radials)):
        np.testing.assert_allclose(got,expected,atol=8e-16)


def test_new_normal_chart_source_reuses_cached_value_and_moves_child_once(monkeypatch):
    import bhsm.interface.muon_d5_child_same_direction_application as module
    class History:times=np.array([0.,1.])
    a,b,d=.17,.8,1.06;theta,s=.021,.027;delta=np.array([.4,-.13])
    def normal(t,r):
        return dict(value=np.array([a+b*t,d]),time=np.array([b,0.]),radial=np.zeros(2),source=np.zeros(2))
    old=SigmaNormalBirthDomain(History(),normal_jet=normal).point(theta,s,source=True)
    cached=dict(fitted_coordinates=np.array([theta,s]),child_birth=np.array([old['birth']['wall_label'],old['birth']['slope'],0.,0.]),
        child_birth_radius=np.array(old['birth']['birth_rho']),original_child_coordinates=old['original_point'],
        child_fitted_forward_jacobian=old['forward_jacobian'],child_fitted_inverse_jacobian=old['inverse_jacobian'])
    def new_domain(history):
        def value(t,r):return dict(value=np.array([a+b*t,d]),time=np.array([b,0.]),radial=np.zeros(2),source=delta)
        return SigmaNormalBirthDomain(History(),normal_jet=value)
    monkeypatch.setattr(module,'SigmaNormalBirthDomain',new_domain)
    chart,report,_=additional_cached_chart_source(History(),cached)
    np.testing.assert_allclose(chart['original_point_source'],[0.,-s*delta[1]],atol=4e-14)
    np.testing.assert_allclose(chart['birth_source'],[delta[0]*np.expm1(b*s)/b,delta[0]*np.exp(b*s)],atol=3e-12)
    np.testing.assert_array_equal(chart['original_point'],cached['original_child_coordinates'])
    assert report['finite_birth_root_repeated'] is False
    assert report['cached_point_Newton_repeated'] is False
    assert report['minimum_evaluated_child_time']==0
    assert report['original_point_source_constraint_max']<1e-16
    assert report['coordinate_inverse_source_max']<1e-16
