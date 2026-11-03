"""Targeted algebra/ordering/jet tests; no physical witness state or old campaign."""
import numpy as np
import pytest
from decimal import Decimal
from weak_photon_radial_reduction import calculate,exact_checks

@pytest.fixture(scope='module')
def result():return calculate()

def test_exact_ordering_and_all_mixed_placements():
    exact,placements=exact_checks()
    assert all(exact.values()) and len(placements)==9

def test_owned_coefficients_and_integral_derivatives(result):
    _,r=result
    assert r['maximum_check_defect']<2e-11

def test_response_defect_is_not_inferred_from_small_value(result):
    _,r=result
    assert r['first_order_mixed_radial_jet_defect_max']>1e-3
    assert r['first_order_radial_defect_max']<1e-20
    assert r['second_order_mixed_radial_jet_defect_max']<r['first_order_mixed_radial_jet_defect_max']*1e-8

def test_independent_higgs_and_central_directions_preserved(result):
    a,_=result
    assert a['corrected_local_gradient189x49x4'].shape==(189,49,4)
    assert np.count_nonzero(a['second_correction_radial_gradient16x49x4'][3::4])==0
    assert np.count_nonzero(a['second_correction_radial_hessian16x16x49x4'][3::4])==0
    assert np.all(a['ordered_second_transport49x4x4'][-1]==0)

def test_scope_and_unknown_complete_source_remain(result):
    _,r=result
    assert not r['angular_native_weak_term_eliminated']
    assert not r['boundary_native_weak_term_eliminated']
    assert r['physical_source_error_bound'] is None and r['physical_a_mu'] is None
    assert not r['physical_total_Y_evaluated'] and r['physical_guard']==2e-10

def test_analytic_polynomial_bound_preserves_cancellations(result):
    _,r=result;b=r['bounds']
    assert Decimal(b['connection_integral_upper'])<Decimal(b['coefficient_l1_connection_upper'])
    assert all(Decimal(b['radial_direction_integral_upper'][j])==0 for j in (3,7,11,15))
    assert Decimal(b['second_order_value_tail_upper'])>0
