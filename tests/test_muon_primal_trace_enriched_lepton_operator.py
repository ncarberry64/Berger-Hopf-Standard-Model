import numpy as np
import pytest
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
from bhsm.interface.muon_birth_coupled_primal_midpoint import endpoint_raw_from_assigned_application
from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_representation
from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps


@pytest.fixture(scope='module')
def actual_representation():
    folder=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/two_arm_scalar_run_1'
    pair=np.array([endpoint_raw_from_assigned_application(folder,s)[0] for s in ('incoming','outgoing')])
    return pair,trace_enriched_representation(pair,radial_points=48,cap_points=48)


def test_exact_full_wall_action_has_no_radial_projection_loss(actual_representation):
    pair,rep=actual_representation
    raw=np.zeros(268);raw[:100]=pair[0,:100];raw[-8:]=pair[0,-8:]
    # Exercise every active independent component and the actual new source
    # image. This numerical control changes no physical state selection.
    raw[100:180]=.004*np.sin(np.arange(80)+.3)
    result=primal_trace_enriched_lepton_operator(raw,rep)
    assert result['wall_action_rank']==20
    assert result['complete_trace_reconstruction_defect']==0
    weight=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
    tr=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:180])
    gen=lepton_unit_trace_gauge_representation()['generators']
    connection=np.concatenate(((np.einsum('c,cij->ij',tr[0],gen)/weight['induced_lapse'].value)[None],
        np.einsum('ac,cij->aij',tr[2:]+M*(weight['mechanical_connection_lambda'].value-1),gen)))[None]
    H=(raw[260:262]+1j*raw[262:264])[None]
    literal=canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],spatial_derivative_map=np.zeros((1,3,18,18)),
        H=H,R4=weight['R4'].value,gauge_connection=connection)
    np.testing.assert_allclose(result['W'],literal['spatial_mass_hamiltonian_map'][0],rtol=0,atol=2e-15)
    np.testing.assert_allclose(result['H_can'],literal['hamiltonian_map'][0],rtol=0,atol=2e-15)


@pytest.mark.parametrize('coordinate',[0,74,98,99,100,164,167,260,263])
def test_enriched_first_jets_against_literal_operator_variation(actual_representation,coordinate):
    pair,rep=actual_representation
    raw=np.zeros(268);raw[:100]=pair[1,:100];raw[-8:]=pair[1,-8:]
    raw[100:180]=.004*np.cos(np.arange(80)+.3)
    result=primal_trace_enriched_lepton_operator(raw,rep)
    eps=2e-6;a=raw.copy();b=raw.copy();a[coordinate]+=eps;b[coordinate]-=eps
    plus=primal_trace_enriched_lepton_operator(a,rep);minus=primal_trace_enriched_lepton_operator(b,rep)
    np.testing.assert_allclose(result['H_can_raw_first_jet'][coordinate],(plus['H_can']-minus['H_can'])/(2*eps),rtol=3e-7,atol=2e-9)
    np.testing.assert_allclose(result['proper_time_Haar_measure_first_jet'][coordinate],
        (plus['proper_time_Haar_measure']-minus['proper_time_Haar_measure'])/(2*eps),rtol=3e-7,atol=2e-9)
