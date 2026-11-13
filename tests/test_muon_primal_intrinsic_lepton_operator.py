"""Actual corrected primal fields and literal first-order Dirac contacts."""
import numpy as np
import pytest

from bhsm.interface.muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT,correction_representation
from bhsm.interface.muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_parent_maxwell_full_weak import M


@pytest.fixture(scope='module')
def primal():
    with np.load(ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/full_midpoint_outgoing_run_1/application.npz',allow_pickle=False) as f:
        raw=f['updated_midpoint_raw']
    rep=correction_representation(radial_points=24,cap_points=24,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    return raw,rep,primal_intrinsic_lepton_operator(raw,rep)


def test_same_actual_fields_and_normalized_operator_match_literal_owner(primal):
    raw,rep,a=primal
    assert np.linalg.norm(a['wall_trace'])>0
    generators=lepton_unit_trace_gauge_representation()['generators']
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    spatial=a['wall_trace'][2:]+M*(w['mechanical_connection_lambda'].value-1)
    Os=np.einsum('ac,cij->aij',spatial,generators)
    connection=np.r_[a['Omega_tau'][None],Os][None]
    literal=canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],spatial_derivative_map=np.zeros((1,3,18,18)),
        H=a['H'][None],R4=a['R4'],gauge_connection=connection)
    np.testing.assert_array_equal(a['W'],literal['spatial_mass_hamiltonian_map'][0])
    np.testing.assert_array_equal(a['H_can'],literal['hamiltonian_map'][0])
    np.testing.assert_allclose(a['H_can'],a['W']-1j*a['Omega_tau'],atol=0,rtol=0)
    assert np.linalg.norm(a['W']-a['W'].conj().T)<1e-13
    assert np.linalg.norm(a['Omega_tau']+a['Omega_tau'].conj().T)<1e-13
    np.testing.assert_array_equal(a['current_Gram'],np.eye(18))


@pytest.mark.parametrize('index',[0,74,98,99,104,126,220,223])
def test_geometry_normal_gauge_and_fixed_y_first_jets_by_independent_field_variation(primal,index):
    raw,rep,a=primal;step=2e-6
    plus=raw.copy();minus=raw.copy();plus[index]+=step;minus[index]-=step
    p=primal_intrinsic_lepton_operator(plus,rep);m=primal_intrinsic_lepton_operator(minus,rep)
    for key,jet in (('W','W_raw_first_jet'),('H_can','H_can_raw_first_jet'),('Omega_tau','Omega_tau_raw_first_jet')):
        numerical=(p[key]-m[key])/(2*step)
        np.testing.assert_allclose(numerical,a[jet][index],rtol=3e-6,atol=3e-9)
    numerical=(p['proper_time_Haar_measure']-m['proper_time_Haar_measure'])/(2*step)
    assert numerical==pytest.approx(a['proper_time_Haar_measure_first_jet'][index],rel=3e-6,abs=3e-8)


def test_no_covariance_domain_or_rate_zero_promotion(primal):
    raw,rep,a=primal
    assert a['W_raw_first_jet'].shape==(228,18,18)
    np.testing.assert_array_equal(a['W_raw_first_jet'][160:220],0)
    np.testing.assert_array_equal(a['W_raw_first_jet'][224:228],0)
    assert 'total coefficient-time derivatives' in a['zero_application_provenance']
    assert not a['complete_native_domain_or_LSZ_selected']
    assert not a['physical_Pauli_value']
    with pytest.raises(ValueError):primal_intrinsic_lepton_operator(None,rep)
