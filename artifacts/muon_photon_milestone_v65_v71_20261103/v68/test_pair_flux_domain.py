"""Focused checks of new finite-pair enclosure and exact source-domain identity."""
import numpy as np
import pytest
from fractions import Fraction
from pair_flux_domain import calculate,exact_identities,HERE
@pytest.fixture(scope='module')
def result():return calculate()
def test_recovered_pair_bound_uses_signed_relative_weights(result):
    a,r=result
    assert np.array_equal(a['signed_pair_current4'],np.diag([.5,.5,-.5,-.5]))
    assert r['signed_pair_trace_norm']==2
    assert r['adopted_pair_sha256']=='20db0b3b1a5cb09be1979b0fb24027bbb70f713d4001bd8c50e9807137a136d3'
def test_complete_haar_harmonic_enclosure(result):
    a,r=result
    assert np.allclose(a['conditional_moment_bounds3']**2,[16,64,80],rtol=0,atol=2e-14)
    assert r['unitary_complete_Cauchy_condition_required']
    assert not r['independent_left_response_bounded']
def test_covariant_Hardy_exact_identity():
    assert all(Fraction(x)==0 for x in exact_identities().values())
def test_owned_velocity_load_has_regular_pole_power(result):
    _,r=result
    assert r['known_v66_forcing_pole_order']>1.5
    assert r['known_v66_flux_pole_order']>2.5
    assert r['known_v66_weighted_source_integrability_exponent']>-1
def test_weighted_source_application_separate_component_contraction(result):
    a,r=result
    b=dict(np.load(HERE/'evidence/inputs.npz',allow_pickle=False))
    K=b['known_canonical_Gauss_load49x4x20x4x8'][:-1]
    direct=np.zeros((4,8))
    for j,w in enumerate(b['radial_weights']):
        direct+=w*np.sum(K[j]**2,axis=(0,1))/b['radial_nodes49'][j]**4
    assert np.max(abs(direct-a['known_forcing_weighted_norm2_4x8']))<2e-11
    assert np.all(a['known_forcing_weighted_norm2_4x8']>=0)
def test_no_physical_values_or_ports_filled(result):
    _,r=result
    for k in ('complete_matched_source_weighted_norm','physical_kappa_minus','physical_entering_port_flux','physical_a_mu','total_physical_uncertainty'):
        assert r[k] is None
    assert not r['physical_density_realized'] and not r['physical_retained_released_load_realized']
    assert r['physical_guard']==2e-10 and r['method_tolerance']==2e-11
    assert r['temporal_baseline']==2**-9 and not r['new_resolution'] and not r['new_quadrature']
