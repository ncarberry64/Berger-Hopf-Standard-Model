import numpy as np
import pytest
from photon_native_seam import calculate
@pytest.fixture(scope='module')
def result():return calculate()
def test_original_Green_row_and_same_background(result):
    _,r=result
    assert r['maximum_check_defect']<2e-11
def test_photon_scalar_cancellation_keeps_readout_jets(result):
    a,_=result
    for k in ('scalar_seam_channels2x18x18','scalar_first_H_jets2x4x18x18','scalar_mixed_H_jets2x4x4x18x18'):
        assert np.max(abs(a[k]))<2e-11
def test_angular_connection_is_not_eliminated(result):
    a,r=result
    assert max(r['summed_angular_operator_norms'])>1e-6
    assert np.max(abs(a['angular_gradient22x2x3x18x18'][18:22]))>1e-6
def test_independent_channels_and_local_chain_retained(result):
    a,r=result
    assert a['angular_full_gradient189x2x3x18x18'].shape==(189,2,3,18,18)
    assert not r['normal_monomials_assigned'] and not r['independent_left_assigned']
def test_complete_physical_application_not_inferred(result):
    _,r=result
    assert not r['relative_kernel_evaluated'] and not r['entering_pole_event_work_evaluated']
    assert r['physical_a_mu'] is None and r['physical_guard']==2e-10
