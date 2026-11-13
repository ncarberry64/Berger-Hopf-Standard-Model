import numpy as np
import pytest
from bhsm.interface.muon_chronological_native_return import enclosed_chronological_magnetic_return


def test_chronological_mean_interval_is_carried_to_signed_boundary_return_once():
    bare=np.zeros((8,8));bare[:3,:3]=np.diag([2.,-3.,4.])
    direct=np.zeros((8,8),complex);direct[:3,:3]=np.diag([1e-12,2e-12,3e-12])
    mean=np.zeros((8,8));mean[:3,:3]=np.diag([4e-12,-2e-12,1e-12])
    radius=np.zeros((8,8));radius[:3,:3]=1e-15
    a=enclosed_chronological_magnetic_return(bare,direct,mean-radius,mean+radius)
    for k in (0,1,2):
        native=.5*(direct[k,k].real+mean[k,k])
        expected=-native/(bare[k,k]*(bare[k,k]+native))
        assert a['stable_native_return_real_lower'][k,k]<=expected<=a['stable_native_return_real_upper'][k,k]
    assert a['statistics_applied_once']
    assert not a['source_return_promoted_to_quantum_propagator']
    assert a['interval_inverse_residual_upper']<1e-13
    active=enclosed_chronological_magnetic_return(bare,direct[:3,:3],
        (mean-radius)[:3,:3],(mean+radius)[:3,:3])
    np.testing.assert_array_equal(active['stable_native_return'],a['stable_native_return'])


def test_absent_axes_and_unordered_mean_intervals_are_rejected():
    bare=np.zeros((8,8));bare[:3,:3]=np.eye(3)
    direct=np.zeros((8,8),complex);lower=np.zeros((8,8));upper=lower.copy()
    lower[0,0]=1.
    with pytest.raises(ValueError):enclosed_chronological_magnetic_return(bare,direct,lower,upper)
    lower[:]=0;direct[3,3]=1.
    with pytest.raises(ValueError):enclosed_chronological_magnetic_return(bare,direct,lower,upper)
