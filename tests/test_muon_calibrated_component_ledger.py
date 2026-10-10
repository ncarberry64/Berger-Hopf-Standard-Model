import numpy as np
import pytest

from bhsm.interface.muon_calibrated_component_ledger import (
    shared_observable_uncertainty,leading_top_electromagnetic_vp,
)
from bhsm.interface.muon_calibrated_current_response import magnetic_moment_accounting


def test_common_input_cancellation_precedes_variance():
    result=shared_observable_uncertainty(a_subtotal=.001,mass_GeV=.1,
        component_gradients=[[2.,3.],[-2.,1.]],mass_gradient=[0.,0.],
        standard_uncertainties=[1.,.5],charge_sign=1)
    assert result['summed_a_gradient']==[0.,4.]
    assert result['input_standard_uncertainties'][0]==2.
    assert result['primitive_independence_is_only_illustrative']


def test_mass_and_anomaly_use_same_input_for_si_moment():
    # Select a tangent along which (1+a)/m is constant.  The moment
    # derivative must cancel rather than acquire two independent errors.
    a=.001;m=.1
    result=shared_observable_uncertainty(a_subtotal=a,mass_GeV=m,
        component_gradients=[[(1+a)/m]],mass_gradient=[1.],
        standard_uncertainties=[.001],charge_sign=-1)
    assert abs(result['output_gradient'][2][0]) < 1e-38
    assert result['accounting']['magnetic_moment_Sz_plus_hbar_over_2_J_per_T']<0


def test_correlated_common_primitive_covariance():
    result=shared_observable_uncertainty(a_subtotal=.001,mass_GeV=.1,
        component_gradients=[[2.,3.]],mass_gradient=[.01,-.02],
        standard_uncertainties=[1.,2.],charge_sign=1,
        primitive_covariance=[[1.,-2.],[-2.,4.]])
    assert result['input_standard_uncertainties'][0]==pytest.approx(4.)
    row=np.asarray(result['output_gradient'][2])
    assert result['input_standard_uncertainties'][2]==pytest.approx(abs(row[0]-2*row[1]))
    assert not result['primitive_independence_is_only_illustrative']


def test_bad_covariance_is_not_silently_independent():
    with pytest.raises(ValueError,match='positive-semidefinite'):
        shared_observable_uncertainty(a_subtotal=.001,mass_GeV=.1,
            component_gradients=[[1.,2.]],mass_gradient=[0.,0.],
            standard_uncertainties=[1.,1.],charge_sign=1,
            primitive_covariance=[[1.,2.],[2.,1.]])


def test_top_heavy_limit_and_exact_ratio_tangent():
    inputs=dict(alpha=1/137.035999206,muon_mass_GeV=.10565842526040435,
                top_pole_mass_GeV=171.1)
    r=leading_top_electromagnetic_vp(**inputs)
    assert 0<r['value']<=r['heavy_leading_upper']
    assert (r['heavy_leading_upper']-r['value'])/r['value']<1e-5
    h=1e-4
    plus=leading_top_electromagnetic_vp(**dict(inputs,top_pole_mass_GeV=171.1*np.exp(h)))
    minus=leading_top_electromagnetic_vp(**dict(inputs,top_pole_mass_GeV=171.1*np.exp(-h)))
    assert (plus['value']-minus['value'])/(2*h*171.1)==pytest.approx(r['derivative_top_mass'],rel=1e-7)
    assert not r['top_Higgs_Yukawa_assigned']
