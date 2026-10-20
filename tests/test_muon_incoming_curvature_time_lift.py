import numpy as np

from bhsm.interface.muon_incoming_curvature_time_lift import (
    stationary_curvature_rows,execute_pointwise_time_lift,
    execute_covariant_electron_comparison,
)
from bhsm.interface.muon_incoming_comparison_time_lift import execute_stationary_time_lift


def comparison_control():
    t=np.zeros(22);t[:2]=[.9,1.2];t[2:6]=[.03,-.01,.02,.04]
    t[6:18]=np.c_[np.diag([-.8,-1.1,-.9]),[.02,.03,-.01]].ravel()
    t[18:22]=[.1,.7,.05,-.03]
    return t


def test_pointwise_curvature_proof_distinguishes_nonconstant_compensators():
    t=comparison_control();a=execute_pointwise_time_lift(t,np.eye(22))
    assert a['pointwise_time_gauge_rank']==4
    np.testing.assert_array_equal(a['pointwise_gauge_compensator'],0)
    np.testing.assert_array_equal(a['pointwise_original_integrability_source_rows'],0)
    # Flat right-Maurer connection: pure gauge can transport a nonconstant
    # stabilizer. The constant-class matrix spuriously appears full rank.
    t[2:18]=0;t[6:18]=np.c_[-np.sqrt(8)*np.eye(3),np.zeros(3)].ravel()
    assert execute_stationary_time_lift(t)['represented_time_gauge_lift_rank']==4
    b=execute_pointwise_time_lift(t,np.eye(22))
    assert b['pointwise_time_gauge_rank']==3
    assert b['pointwise_remaining_gauge_generators'].shape==(4,1)
    np.testing.assert_allclose(b['original_curvature'],0,atol=2e-15)


def test_curvature_source_retains_Maurer_and_proper_frame_derivatives():
    t=comparison_control();a=stationary_curvature_rows(t,np.eye(22))
    d=np.linspace(-.17,.21,22);eps=1e-5
    p=stationary_curvature_rows(t+eps*d,np.eye(22))
    m=stationary_curvature_rows(t-eps*d,np.eye(22))
    for key in ('original_curvature','original_integrability_matrix'):
        actual=np.einsum('k,k...->...',d,a[key+'_source'])
        np.testing.assert_allclose(actual,(p[key]-m[key])/(2*eps),atol=2e-10,rtol=3e-8)
    # A central constant right-body one-form has nonzero exterior dA.
    central=t.copy();central[2:18]=0;central[9]=.3
    F=stationary_curvature_rows(central,np.eye(22))['original_curvature']
    assert np.max(abs(F[3:]))>.09


def test_original_charge_contact_has_both_covariant_terms_and_source():
    t=comparison_control();a=execute_covariant_electron_comparison(t,np.eye(22))
    for key in ('covariant_Higgs_charge_rate_identity_rows',
            'original_charge_clock_forms_identity_rows',
            'original_charge_clock_forms_source_identity_rows'):
        np.testing.assert_allclose(a[key],0,atol=3e-15)
    assert np.max(abs(a['original_covariant_charge_stationarity_rows']))>.1
    d=np.linspace(-.13,.21,22);eps=1e-5
    p=execute_covariant_electron_comparison(t+eps*d,np.eye(22))
    m=execute_covariant_electron_comparison(t-eps*d,np.eye(22))
    actual=np.einsum('k,kab->ab',d,a['original_covariant_charge_stationarity_source_rows'])
    np.testing.assert_allclose(actual,(p['original_covariant_charge_stationarity_rows']
        -m['original_covariant_charge_stationarity_rows'])/(2*eps),atol=3e-10,rtol=3e-8)
