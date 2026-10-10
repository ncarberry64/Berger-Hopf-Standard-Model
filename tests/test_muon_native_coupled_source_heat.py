"""Actual same-source H80 mass applications, with genuine mixed term open."""
import numpy as np
import pytest
from bhsm.interface.muon_native_coupled_source_heat import (
    retained_corrected_scalar_photon_response,corrected_response_source_vertices,
    corrected_first_response_heat_core,corrected_first_response_heat_application,
)
from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
from bhsm.interface.muon_parent_retarded_hypercharge import compact_trace_pulse


@pytest.fixture(scope='module')
def response():return retained_corrected_scalar_photon_response()


def test_actual_h80_and_rates_bind_exact_order_and_same_pulse(response):
    index=64;u=response['times'][index];t=u+response['time_shift']
    data=corrected_response_source_vertices(response,t)
    raw=response['H80'][index].reshape(4,20,8).transpose(2,1,0)
    rates=response['H80_rate'][index].reshape(4,20,8).transpose(2,1,0)
    expected=np.stack((raw[:,:,0]+1j*raw[:,:,2],raw[:,:,1]+1j*raw[:,:,3]),axis=-1)
    expected_rate=np.stack((rates[:,:,0]+1j*rates[:,:,2],rates[:,:,1]+1j*rates[:,:,3]),axis=-1)
    np.testing.assert_allclose(data['complex_H_response'],expected,rtol=1e-14,atol=1e-22)
    np.testing.assert_allclose(data['complex_H_response_rate'],expected_rate,rtol=1e-14,atol=1e-18)
    mass=fixed_y_higgs_hamiltonian(expected.reshape(160,2)).reshape(8,20,18,18)
    np.testing.assert_allclose(data['fixed_Y_mass_vertex'],mass,rtol=1e-14,atol=1e-22)
    np.testing.assert_allclose(mass,mass.conj().transpose(0,1,3,2),atol=0)
    assert np.linalg.norm(mass)>0
    pulse=compact_trace_pulse(u,response['duration'])[0]
    assert data['pulse']==pytest.approx(pulse,abs=1e-15)
    assert not data['extra_e_Tb_or_family_factor_applied']


def test_actual_retarded_h_response_survives_source_pulse(response):
    t=-.0002;data=corrected_response_source_vertices(response,t)
    assert data['pulse']==0
    np.testing.assert_array_equal(data['raw_gauge_unit_radius_vertex'],0)
    assert np.linalg.norm(data['fixed_Y_mass_vertex'])>0
    # An independently chosen fixed H profile would not reproduce this tail.
    assert data['genuine_mixed_mass_vertex'] is None


@pytest.fixture(scope='module')
def core(response):
    return corrected_first_response_heat_core(response,time_nodes=np.linspace(-.001,0,5),quadrature_order=4)


def test_fixed_y_scalar_first_response_reaches_all_complement_modes(core):
    for f in core['families'].values():
        assert np.min(f['n0_eigenvalues'])>0
        assert np.linalg.norm(f['first_response_contact_spectral_diagonal']['scalar'])>0
        for n,s in f['intermediate_shells'].items():
            assert s['first_jet_n0']['scalar'].shape[1]=={'1':72,'3':288}[n]
            assert np.linalg.norm(s['first_jet_n0']['scalar'])>0
            assert s['all_complementary_eigenmodes_retained']
    assert core['actual_H_response_included']
    assert core['mixed_factor_jet_from_actual_mean_H_second_response'] is None
    assert not core['remaining_geometric_and_domain_first_response_included']


def test_scalar_and_interference_are_explicit_small_components_not_total_subtraction(core):
    c=1/core['families']['1']['n0_eigenvalues'][0]
    application=corrected_first_response_heat_application(core,c,integrate_cutoff=True)
    for f in application['families'].values():
        parts=f['components']
        np.testing.assert_allclose(f['reached_first_response_pair_sum'],
            sum(p['reached_first_response_pair'] for p in parts.values()),atol=0)
        assert np.linalg.norm(parts['scalar']['source_square_contact'])>0
        assert np.linalg.norm(parts['scalar']['ordered_two_insertion'])>0
        assert np.linalg.norm(parts['interference']['reached_first_response_pair'])>0
        assert f['genuine_mixed_scalar_mean_contact'] is None
        assert f['complete_total_source_pair_heat'] is None
    assert application['genuine_mixed_response_not_assigned_affine_zero']
    assert not application['physical_cutoff_or_complete_native_Pauli_selected']


def test_reached_time_and_parameter_guard(response,core):
    with pytest.raises(ValueError,match='extrapolate'):
        corrected_response_source_vertices(response,.0001)
    with pytest.raises(ValueError,match='positive'):
        corrected_first_response_heat_application(core,0)
    with pytest.raises(ValueError,match='explicit real'):
        corrected_first_response_heat_core(response,time_nodes=np.linspace(-.001,0,5)+1j,quadrature_order=4)
