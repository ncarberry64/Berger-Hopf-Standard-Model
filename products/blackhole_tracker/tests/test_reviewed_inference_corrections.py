"""Reviewed F1-F3 invariants; synthetic probes are not observational claims."""
from copy import deepcopy
import json

import numpy as np
import pytest

from bhtracker import fit, predict
from bhtracker.examples import make_example
from bhtracker.forward import LensEngine, GM_SUN, C, PC
from bhtracker.inference import ParameterMap, profile
from test_inference_contract import point_fixture


def test_reference_epoch_mass_and_reporting_covariance(point_fixture):
    raw, truth = point_fixture
    before = deepcopy(raw)
    baseline = fit(raw, starts=1, nuisance='none')
    base_cov = np.asarray(baseline['physical_parameter_uncertainty']['covariance'])
    base_track = np.asarray(baseline['center_track_mas'])
    for epoch, mass in [(2000.,7.), (2026.,.001), (2026.,100000.)]:
        changed=deepcopy(raw);changed['reference_epoch_yr']=epoch
        changed['analysis']['reference_mass_msun']=mass
        result=fit(changed,starts=1,nuisance='none')
        assert result['status']=='TRACKED' and result['chi2']<1e-12
        assert result['estimates']['mass_msun']==pytest.approx(10.,rel=1e-10)
        assert result['dataset_input']==changed
        np.testing.assert_allclose(result['center_track_mas'],base_track,atol=1e-9,rtol=1e-10)
        T=np.eye(len(base_cov));T[1,3]=T[2,4]=epoch-raw['reference_epoch_yr']
        np.testing.assert_allclose(result['physical_parameter_uncertainty']['covariance'],T@base_cov@T.T,rtol=2e-5,atol=1e-10)
        np.testing.assert_allclose(predict(changed,result['_internal']['parameters']),result['predictions'],rtol=1e-11,atol=1e-10)
        assert result['model']['parameter_basis']['optimization_epoch_yr']==baseline['model']['parameter_basis']['optimization_epoch_yr']
    assert raw==before


def test_no_numerical_position_boxes_and_compact_physical_basis(point_fixture):
    raw,truth=point_fixture
    raw=deepcopy(raw);raw['analysis']['compact_quad_reference_mass_msun']=7.
    a=LensEngine(raw,reference_mass=7.);ma=ParameterMap(a,'full')
    changed=deepcopy(raw);changed['analysis']['reference_mass_msun']=700.
    b=LensEngine(changed,reference_mass=700.);mb=ParameterMap(b,'full')
    assert np.isinf(ma.lower[[1,2,-1,-2]]).all()
    p=deepcopy(truth);p['compact_quad']=[.0001,-.00007]
    q=deepcopy(p);q['compact_quad']=(np.asarray(p['compact_quad'])*(7/700)**2).tolist()
    xa,xb=ma.encode(p),mb.encode(q)
    np.testing.assert_allclose(xa,xb,rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(ma.lower,mb.lower,rtol=0,atol=0)
    np.testing.assert_allclose(ma.upper,mb.upper,rtol=0,atol=0)
    np.testing.assert_allclose(a.calculate(ma.decode(xa))[0],b.calculate(mb.decode(xb))[0],rtol=1e-10,atol=1e-10)
    # Full nuisance fitting preserves the same physical compact prior.
    first=fit(raw,starts=1,nuisance='full',initial=p)
    second=fit(changed,starts=1,nuisance='full',initial=q)
    np.testing.assert_allclose(first['predictions'],second['predictions'],rtol=1e-7,atol=3e-6)
    assert abs(first['chi2']-second['chi2'])<1e-5


def test_default_worldtube_and_alignment_domain_are_reference_independent():
    raw,truth=make_example('nearby_motion',noise=False)
    raw['analysis'].pop('r0_pc')
    engines=[LensEngine(raw,reference_mass=mass) for mass in [.001,1e5,1e9]]
    assert len({e.r0 for e in engines})==1
    predictions=[e.calculate(truth)[0] for e in engines]
    np.testing.assert_allclose(predictions[0],predictions[1],rtol=1e-10,atol=1e-10)
    np.testing.assert_allclose(predictions[1],predictions[2],rtol=1e-10,atol=1e-10)


def test_unidentified_motion_and_distant_reporting_epoch_do_not_create_precision():
    raw,truth=make_example('nearby_motion',noise=False)
    raw['epochs_yr']=[2020.]*len(raw['epochs_yr'])
    raw['observations']=predict(raw,truth).tolist()
    alternative=deepcopy(truth);alternative['proper_motion_mas_yr']=[-.125,.075]
    np.testing.assert_array_equal(predict(raw,truth),predict(raw,alternative))
    baseline=fit(raw,starts=1,nuisance='none')
    raw['reference_epoch_yr']=2000.
    distant=fit(raw,starts=1,nuisance='none')
    for r in [baseline,distant]:
        assert r['proper_motion_covariance'] is None
        assert r['uncertainty']['proper_motion_mas_yr']==[None,None]
        assert r['motion_snr'] is None
        assert r['status']=='PARTIALLY_IDENTIFIED'
        assert all(r['physical_parameter_uncertainty']['unidentified'][3:5])
        assert np.isfinite(np.asarray(r['center_track_sigma_mas'],dtype=float)).all()
        json.dumps(r,allow_nan=False)
    assert distant['uncertainty']['center_mas']==[None,None]
    assert not any(baseline['physical_parameter_uncertainty']['unidentified'][1:3])
    raw['reference_epoch_yr']=2020.+1e-5
    nearby_reporting=fit(raw,starts=1,nuisance='none')
    assert nearby_reporting['uncertainty']['center_mas']==[None,None]


def test_weak_but_identifiable_motion_retains_finite_covariance():
    raw,_=make_example('cosmological_short_track',noise=False)
    result=fit(raw,starts=1,nuisance='none')
    assert result['motion_snr'] is not None and result['motion_snr']<5
    cov=np.asarray(result['proper_motion_covariance'])
    assert cov.shape==(2,2) and np.isfinite(cov).all()
    assert np.linalg.eigvalsh(cov).min()>0
    assert all(x is not None for x in result['uncertainty']['proper_motion_mas_yr'])


def test_constrained_profile_recovers_admissible_nuisance_at_invalid_free_optimum():
    raw,truth=make_example('nearby_motion',noise=False)
    _,branch=LensEngine(raw).calculate(truth,admit=False)
    raw['analysis']['weak_metric_cap']=float(GM_SUN*truth['mass_msun']/(C*C*PC)/np.min(branch['impact_pc'])*1.00001)
    result=fit(raw,starts=1,nuisance='none');curve=profile(raw,result,points=7)
    invalid_free=[p for p in curve['points'] if not p['unconstrained_admitted']]
    assert len(invalid_free)>=3
    for point in invalid_free:
        assert point['constrained_nuisance_search']
        assert point['admitted'] and point['physical_interval_eligible']
        assert point['solution_status']=='ADMITTED_BOUNDARY'
        assert point['chi2']>point['unconstrained_chi2']
        LensEngine(raw).calculate(point['parameters'],admit=True)
        assert min(point['admission_margins'].values())>=0
    assert curve['reference_admitted'] and curve['reference_chi2']<1e-12


def test_conditional_r1_profile_physical_limit_is_unresolved_not_false_crossing():
    raw,truth=make_example('nearby_motion',noise=False)
    raw['observations']=LensEngine(raw,'r1').calculate(truth)[0].tolist()
    from bhtracker.physics_admission import assess_physics
    base=LensEngine(raw,'r1');_,branch=base.calculate(truth)
    admission=assess_physics(base.physics_config,truth,branch['impact_pc'])
    raw['analysis']['weak_metric_cap']=admission['scales']['weak_metric_bound_at_worldtube']*1.00001
    result=fit(raw,family='r1',starts=1,nuisance='none')
    curve=profile(raw,result,points=7)
    unresolved=[p for p in curve['points'] if not p['admitted']]
    assert unresolved
    for point in curve['points']:
        if point['admitted']:
            LensEngine(raw,'r1').calculate(point['parameters'],admit=True)
        else:
            assert point['constrained_nuisance_search']
            assert point['solution_status']=='PHYSICAL_DOMAIN_UNRESOLVED'
            assert point['chi2'] is None and point['delta_chi2'] is None
            assert not point['physical_interval_eligible']
            assert not point['physical_feasibility_proven_impossible']


def test_legacy_profile_internal_state_requires_explicit_refit():
    raw,_=make_example('nearby_motion',noise=False)
    result=fit(raw,starts=1,nuisance='none')
    result['model'].pop('parameter_basis')
    with pytest.raises(ValueError,match='legacy or incompatible internal parameter basis'):
        profile(raw,result,points=7)

def test_reporting_covariance_resolution_across_independent_derivative_steps():
    """Numerical covariance tolerance, separate from physical fit/admission gates."""
    from bhtracker import load_dataset
    from bhtracker.inference import _local_covariance
    raw,_=make_example('nearby_motion')
    result=fit(raw,starts=2)
    d=load_dataset(raw);e=LensEngine(d,reference_mass=result['model']['reference_mass_msun'])
    mapping=ParameterMap(e,'shear');x=np.asarray(result['_internal']['x'])
    transform=mapping.reporting_jacobian(x)
    def residual(y):return d.whiten((e.calculate(mapping.decode(y),admit=False)[0]-d.observations).ravel())
    for step in [1e-6,2e-6,4e-6,8e-6]:
        # Explicit central differences, independent of least_squares' derivative.
        steps=step*np.maximum(1.,abs(x));directions=np.eye(len(x))
        jac=np.column_stack([(residual(x+directions[i]*h)-residual(x-directions[i]*h))/(2*h)
                             for i,h in enumerate(steps)])
        cov,_,_,rank=_local_covariance(jac)
        physical=transform@cov@transform.T
        assert rank==result['rank']
        assert np.sqrt(physical[0,0])==pytest.approx(result['uncertainty']['mass_msun'],rel=1e-9)
        np.testing.assert_allclose(physical[3:5,3:5],result['proper_motion_covariance'],rtol=1e-9,atol=1e-18)
