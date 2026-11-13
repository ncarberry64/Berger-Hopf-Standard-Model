"""Tests of the actual replacement term and its common coupled chart."""
from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_coupled_reference_replacement import (
    coupled_seed,assemble_known_coupled,reference_subtraction,GEOMETRY_IDS,
    GAUGE,HIGGS,LOG_UNIT,MULTIPLIER_ROWS,
    coupled_known_subtotal_trial,EULER_ROWS,
)
from bhsm.interface.muon_moving_geometric_action import moving_cap_action_jet

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def saved():
    p=ROOT/'artifacts/muon_adopted_incoming_reference_20261018/run_5/reference_application.npz'
    with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}


@pytest.fixture(scope='module')
def application(saved):
    x=coupled_seed(saved)
    arguments=dict(rho=saved['radial_points48'],radial_weights=saved['radial_weights48'],cap_points=32)
    result=assemble_known_coupled(x,**arguments,saved=saved,seed=x)
    return x,arguments,result


def test_exact_original_zeta_removal_not_an_unknown_fitted_load(saved):
    raw=saved['incoming_seed_raw268'].copy();raw[37:74]=0.;raw[99]=0.
    counter=reference_subtraction(raw[:100])
    original=moving_cap_action_jet(12,raw[:37],raw[37:74],raw[74:98],
        points=16,source_value=raw[98],source_rate=0.)['retained_local_Casimir']
    assert counter.value>2
    np.testing.assert_allclose(counter.value,-original.value,atol=2e-14)
    np.testing.assert_allclose(counter.gradient,-original.gradient,atol=2e-13)
    np.testing.assert_allclose(counter.hessian,-original.hessian,atol=2e-12)
    assert np.max(abs(counter.gradient[74:98]))>2


def test_cached52_and_original_multiplier_identity_are_preserved(saved,application):
    _,_,a=application
    np.testing.assert_array_equal(a['original_gradient'][GAUGE],saved['final_weak_field_rows84'])
    np.testing.assert_array_equal(a['original_hessian'][GAUGE,GAUGE],saved['final_weak_field_Hessian84'])
    np.testing.assert_allclose(a['original_gradient'][MULTIPLIER_ROWS],
        saved['multiplier_at_classical_unit_no_area24'],atol=2e-12)
    np.testing.assert_array_equal(a['subtraction_gradient'][GAUGE],0.)
    np.testing.assert_array_equal(a['subtraction_gradient'][HIGGS],0.)
    assert a['subtraction_gradient'][LOG_UNIT]==0.


def test_joint_geometry_gauge_Higgs_unit_jacobian_is_actual_derivative(application):
    x,args,a=application
    direction=np.zeros(151)
    direction[[0,11,37,61,122,128,147,150]]=[.21,-.08,.13,-.17,.11,-.09,.19,-.12]
    eps=2e-6
    plus=assemble_known_coupled(x+eps*direction,**args)
    minus=assemble_known_coupled(x-eps*direction,**args)
    finite=(plus['known_gradient']-minus['known_gradient'])/(2*eps)
    exact=a['known_hessian']@direction
    np.testing.assert_allclose(finite,exact,rtol=8e-7,atol=8e-7)
    # The load derivative must not be frozen out of the geometry Jacobian.
    assert np.linalg.norm(a['subtraction_hessian']@direction)>1
    assert abs(exact[LOG_UNIT])>1e-5


def test_unit_equation_is_kept_separate_and_gamma_cannot_cancel(application):
    _,_,a=application
    assert a['known_gradient'].shape==(151,)
    assert a['known_hessian'].shape==(151,151)
    assert np.count_nonzero(a['unit_known_gradient'])==1
    np.testing.assert_allclose(a['unit_known_gradient'][LOG_UNIT],2*a['required_cF'])
    c=a['known_gradient'][MULTIPLIER_ROWS]
    area=a['area_gradient_per_gamma'][MULTIPLIER_ROWS]
    remaining=c-area*np.dot(area,c)/np.dot(area,area)
    assert np.max(abs(remaining))>27.65
    assert abs(a['known_hessian'][147,LOG_UNIT])>1e-4


def test_counterterm_hessian_includes_normal_and_multiplier_motion(saved):
    raw=saved['incoming_seed_raw268'][:100].copy();raw[37:74]=0.;raw[99]=0.
    base=reference_subtraction(raw)
    d=np.zeros(100);d[98]=.3;d[74]=.2;d[0]=-.1
    eps=1e-6
    numerical=(reference_subtraction(raw+eps*d).gradient-reference_subtraction(raw-eps*d).gradient)/(2*eps)
    np.testing.assert_allclose(numerical,base.hessian@d,rtol=2e-8,atol=2e-8)


def test_actual_coupled_trial_reduces_original_known_rows_without_refining52(saved,application):
    x,args,a=application
    result=coupled_known_subtotal_trial(x,a,saved,evaluate=lambda z:assemble_known_coupled(z,**args))
    assert result['accepted']
    assert result['Schur98x99'].shape==(98,99)
    assert result['reduced_rows98'].shape==(98,)
    assert LOG_UNIT not in result['reduced_rows98']
    assert LOG_UNIT in result['reduced_columns99']
    assert np.max(abs(result['after']['known_gradient'][EULER_ROWS]))<np.max(abs(a['known_gradient'][EULER_ROWS]))
    assert abs(result['actual_step'][LOG_UNIT])>1e-5
    assert np.linalg.norm(result['actual_step'][HIGGS])>1e-3
    assert not result['physical_correction_admitted']
    # The new background no longer inherits the old52 residual admission.
    assert np.max(abs(result['after']['known_gradient'][result['active52']]))>2e-10


def test_new_native_field_jacobian_cannot_reuse_old_classical_inverse(saved,application):
    x,args,a=application
    changed=dict(a,known_hessian=a['known_hessian'].copy())
    index=62+saved['active_interior_rows52'][0]
    changed['known_hessian'][index,index]+=1.
    with pytest.raises(ValueError,match='saved52 inverse'):
        coupled_known_subtotal_trial(x,changed,saved,evaluate=lambda z:assemble_known_coupled(z,**args))
