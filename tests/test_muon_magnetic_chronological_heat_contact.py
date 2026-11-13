"""Independent exact selector/radius and interval target pairing tests."""
import numpy as np
import pytest
from bhsm.interface.muon_magnetic_chronological_heat_contact import (
    raw_mean_export_radii,exact_stored_mean_target_pair,
)


def test_future_raw_radius_uses_absolute_selector_not_incoming_rate_flip():
    P=np.array([[1,0,0],[0,-1,0],[0,0,1],[0,0,0]],float)
    r=np.arange(3*64,dtype=float).reshape(3,8,8)*1e-20
    a=raw_mean_export_radii(P,r)
    np.testing.assert_array_equal(a[:3],r);assert not np.any(a[3])
    with pytest.raises(ValueError):raw_mean_export_radii(np.ones((4,3)),r)


def test_exact_stored_pair_includes_mean_export_error_and_keeps_source_orders():
    k=np.array([.75,-2.,1.5]);m=np.arange(192,dtype=float).reshape(3,8,8)*.125
    r=np.ones_like(m)*2**-30 # Dyadic extremes are exactly represented here.
    a=exact_stored_mean_target_pair(k,m,r)
    for sign in (-1,1):
        extreme=np.einsum('i,iab->ab',k,m+sign*np.sign(k)[:,None,None]*r)
        assert np.all(a['lower']<=extreme) and np.all(a['upper']>=extreme)
    assert a['center'][0,1]!=a['center'][1,0] # no unrequested symmetrization.


def test_unknown_or_nonfinite_direction_cannot_be_zero_filled():
    for bad in (None,np.ones((2,8,8))*np.nan):
        with pytest.raises(ValueError):exact_stored_mean_target_pair([1,2],bad,np.ones((2,8,8)))
    with pytest.raises(ValueError):raw_mean_export_radii(np.eye(2),-np.ones((2,8,8)))
