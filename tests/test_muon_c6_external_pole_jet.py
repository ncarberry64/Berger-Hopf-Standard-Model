from pathlib import Path
import numpy as np
from bhsm.interface.muon_c6_external_pole_jet import external_c6_pole_application
ROOT=Path(__file__).resolve().parents[1]


def actual():
    with np.load(ROOT/'artifacts/muon_changing_zero_energy_moments_20261011/run_1/application.npz',allow_pickle=False)as a:
        z=a['incoming_family_1_value'].copy();d=a['incoming_family_1_energy_first'].copy()
    with np.load(ROOT/'artifacts/muon_coupled_lambda_local_matching_20261011/run_2/application.npz',allow_pickle=False)as a:
        h=a['original_incoming_raw_fields'][260:264]
    return h[:2]+1j*h[2:],z,d


def test_actual_full_neutral_return_matches_the_full_C6_inverse():
    h,z,d=actual();a=external_c6_pole_application(h,z,d,family=1,matched_mass_action=.002145068448715311)
    assert np.linalg.norm(a['full_C6_to_charged_inverse_identity_residual'])<1e-8
    assert np.linalg.norm(a['neutral_Schur_return'])>0
    assert not a['interacting_pole_or_LSZ_certified']


def test_neutral_return_frequency_jet_agrees_with_literal_energy_variation():
    h,z,d=actual();m=.002145068448715311;step=1e-7
    app=lambda E:external_c6_pole_application(h,z,d,family=1,matched_mass_action=E)
    a=app(m);finite=(app(m+step)['charged_effective_inverse_symbol']-app(m-step)['charged_effective_inverse_symbol'])/(2*step)
    assert np.linalg.norm(finite-a['charged_effective_energy_derivative'])<2e-9


def test_scalar_mass_load_does_not_discard_the_complex_pole_remainder():
    h,z,d=actual();a=external_c6_pole_application(h,z,d,family=1,matched_mass_action=.002145068448715311)
    p=a['matched_positive_band_inverse'];load=a['isotropic_mass_matching_load'];r=a['surviving_positive_band_pole_matrix']
    assert np.array_equal(load*np.eye(2)+r,p)
    assert np.linalg.norm(r)>0 and np.any(p.imag!=0)
