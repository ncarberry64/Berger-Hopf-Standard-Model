from pathlib import Path
import json
import numpy as np

from bhsm.interface.muon_normal_current_contraction_maps import (
    normal_current_contraction_maps, tensor_covector_application,
    dyadic_two_green_contraction, dyadic_three_green_contraction,
)
from bhsm.interface.muon_changing_normal_current_readout import changing_family_current_inverse_covectors
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase, profile_preserving_lepton_sample
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_wall_reference

ROOT = Path(__file__).resolve().parents[1]


def actual_arguments():
    phase = load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1')
    sample = profile_preserving_lepton_sample(phase, 0.)
    raw, operator = sample['sample']['raw_fields'], sample['operator']
    wall = corrected_wall_reference(raw, phase['representation'], coordinate_time=0.)['background_values'][0]
    inputs = json.loads((ROOT / 'artifacts/muon_calibrated_pauli_20261009/inputs.json').read_bytes())
    return dict(family_indices=np.array([2, 3, 8, 9, 14, 15]), family=1,
        radius=operator['R4'], wall_connection=wall, H=operator['H'],
        electric_charge=np.sqrt(4*np.pi*inputs['alpha_consumer']['value']))


def test_maps_match_complete_owned_joined_action_block_and_both_weyl_contacts():
    args = actual_arguments()
    maps = normal_current_contraction_maps(**args)
    path = ROOT / 'artifacts/muon_joined_common_y_current_20261011/run_1/joined_16.npz'
    with np.load(path, allow_pickle=False) as a:
        C, T = a['paired_constant_forward'], a['paired_momentum_forward']
        expected = changing_family_current_inverse_covectors(C, T,
            a['paired_constant_reverse'], a['paired_momentum_reverse'], **args)
    actual = tensor_covector_application(C, T, maps)
    for symbol in ('right_symbol', 'first_Weyl_symbol'):
        for key in ('mass_coefficient', 'FW_constant_coefficient'):
            np.testing.assert_allclose(actual[symbol][key],
                expected['mass_affine_signed_soft_covectors'][symbol][key], rtol=2e-10, atol=1e-40)


def test_dyadic_streaming_preserves_literal_nonhermitian_left_and_ordered_rectangular_insertions():
    maps = normal_current_contraction_maps(**actual_arguments())
    bundle = maps['Weyl_FW_T'][1]
    rng = np.random.default_rng(619)
    L = rng.normal(size=(60, 4, 5)) + 1j*rng.normal(size=(60, 4, 5))
    R = rng.normal(size=(4, 24, 5)) + 1j*rng.normal(size=(4, 24, 5))
    K = rng.normal(size=(4, 5))
    full = np.einsum('ofb,fib,fb->oi', L, R, K)
    expected = np.einsum('oi,oi->', bundle['tensor_weight'], full)
    np.testing.assert_allclose(dyadic_two_green_contraction(L, R, K, bundle),
        expected, rtol=3e-14, atol=2e-12)
    Rt = rng.normal(size=(3, 24, 5)) + 1j*rng.normal(size=(3, 24, 5))
    D = rng.normal(size=(3, 4, 3)) + 1j*rng.normal(size=(3, 4, 3))
    K3 = rng.normal(size=(4, 3, 5))
    full3 = np.einsum('otb,Ats,sib,tsb->Aoi', L, D, Rt, K3)
    expected3 = np.einsum('oi,Aoi->A', bundle['tensor_weight'], full3)
    np.testing.assert_allclose(dyadic_three_green_contraction(L, Rt, D, K3, bundle),
        expected3, rtol=3e-14, atol=3e-12)


def test_energy_residue_weight_keeps_complex_trace_and_counts_it_once():
    maps = normal_current_contraction_maps(**actual_arguments())
    rng = np.random.default_rng(103)
    E = rng.normal(size=(6, 6)) + 1j*rng.normal(size=(6, 6))
    J = maps['charged_injection']
    Z = (J.conj().T @ E @ J)[:2, :2]
    answer = tensor_covector_application(np.zeros((3, 24, 6)), np.zeros((3, 60, 24)),
        maps, energy_first=E)
    for row in answer.values():
        np.testing.assert_allclose(row['kinetic_residue_constant_coefficient'],
            np.trace(Z)*np.eye(3)/2, rtol=3e-15, atol=2e-15)
