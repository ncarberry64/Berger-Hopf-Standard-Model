"""Focused tests of the new source projection, never physical mock states."""
import numpy as np
import pytest
from propagated_photon_charge import calculate,HERE,comm

@pytest.fixture(scope='module')
def result():return calculate()

def test_temporal_normal_pair_identity(result):
    _,r=result
    for name in ('all_normal_channel_insertion_identity','charge_insertion_commutes_normal_J','temporal_Gamma0_cancellation'):
        assert r['consistency_checks'][name]<2e-11
    assert r['normal_diagonal_sum_still_requires_both_sections']

def test_owned_charge_projector(result):
    a,r=result
    assert r['charged_rank18']==12 and r['neutral_rank18']==6
    assert np.linalg.norm(a['wall_charge18']@a['wall_charge18']+a['wall_charge18'])<2e-11
    assert r['consistency_checks']['wall_charge_from_original_H']<2e-11

def test_radial_covariant_transport_and_inherited_projection(result):
    a,r=result
    b=dict(np.load(HERE/'evidence/inputs.npz',allow_pickle=False))
    s=np.sqrt(16/3)*b['stabilizer_value']
    assert np.allclose(a['inherited_covector4'],b['inherited_transfer4x4'].T@s,rtol=0,atol=2e-14)
    assert r['consistency_checks']['covariant_transport_defect_identity']<2e-11
    assert r['inherited_flux_contraction'] is None

def test_covector_is_not_a_covariantly_constant_Ward_test(result):
    a,r=result
    eigen=np.linalg.eigvalsh(a['central_angular_test_Gram20x20'])
    assert np.max(abs(eigen-np.r_[np.full(4,10.),np.full(16,50.)]))<2e-11
    assert r['consistency_checks']['angular_Gram_direct_application']<2e-11
    assert not r['complete_matched_Ward_cancellation_proved']
    assert not r['physical_density_dependence_proved']

def test_new_derivatives_independent_difference(result):
    a,r=result
    assert max(r['finite_difference_checks'].values())<2e-11
    assert np.max(abs(a['photon_covector_gradient189x49x4'][:,:,3]))==0
    assert r['consistency_checks']['total_boundary_Higgs_range_motion']<2e-11

def test_consumes_v66_eight_sources(result):
    _,r=result
    assert r['consistency_checks']['v66_eight_source_dual_application']<1e-24
    assert r['consistency_checks']['v66_full_affine_dual_application']<2e-11

def test_scope_and_guard(result):
    _,r=result
    assert r['physical_guard']==2e-10 and r['temporal_baseline']==2**-9
    assert r['physical_a_mu'] is None and r['total_physical_uncertainty'] is None
    assert r['complete_bulk_current_contraction'] is None and r['complete_boundary_load_contraction'] is None
    assert not r['physical_reconnection_proved'] and not r['physical_event_domain_realized']
    assert not r['new_resolution'] and not r['new_quadrature']
