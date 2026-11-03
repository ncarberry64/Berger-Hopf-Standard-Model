"""Focused verification; no chosen physical functions or finite harmonic cutoff."""
from fractions import Fraction
import numpy as np
import pytest
from weighted_current_regularities import calculate,exact_checks
@pytest.fixture(scope='module')
def result():return calculate()
def test_all_degree_certificate():
    _,cert,_=exact_checks()
    assert set(cert)=={'n+1','-n-2','n','-n-1'}
    for entry in cert.values():
        assert all(Fraction(c)>=0 for c in entry['coefficients_in_n_minus_nmin'])
        assert all(Fraction(c)>=0 for c in entry['angular_remainder_ratio_certificate'])
def test_weighted_product_constants():
    exact,_,_=exact_checks();assert all(Fraction(v)==0 for v in exact.values())
def test_old_graph_cannot_bound_product_by_scaling():
    _,_,d=exact_checks()
    assert Fraction(d['first_graph_squared'])==0 and Fraction(d['L2_squared'])>0
    assert Fraction(d['current_weighted_squared'])<0
def test_initializer_criterion_is_not_physical_admission(result):
    a,r=result
    assert r['maximum_numeric_defect']<2e-11
    assert r['whole_saved_cap_sufficient_criterion_excluded']==bool(np.any(a['full_relative_bound_sample2x49']>=1))
    assert r['numeric_checks']['complete_saved_spatial_body_recombination']<2e-11
    assert r['combined_eta_used_on_all_nodes'] and r['sigma_chart_failure_not_a_causal_obstruction']
    assert np.isfinite(a['complete_saved_spatial_V0_2x49x36x36']).all()
    assert not r['physical_columns_realized'] and not r['physical_event_graph_realized']
def test_independent_left_and_native_terms_stay_open(result):
    _,r=result
    assert not r['independent_left_graph_estimate_transferred']
    assert not r['strong_native_density_norm_is_required_by_physics']
    assert r['physical_native_remainder_norm'] is None and r['complete_matched_residual'] is None
def test_guard_and_no_campaign(result):
    _,r=result
    assert r['physical_guard']==2e-10 and r['method_tolerance']==2e-11
    assert r['temporal_baseline']==2**-9 and r['physical_a_mu'] is None
    assert not r['new_resolution'] and not r['new_quadrature'] and r['new_heat_integrals']==r['new_history_steps']==0
