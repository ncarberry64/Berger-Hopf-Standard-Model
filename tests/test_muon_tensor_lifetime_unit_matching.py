from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_tensor_lifetime_unit_matching import temporal_tensor_lifetime_match

ROOT=Path(__file__).resolve().parents[1]
ARGS=dict(muon_mass_GeV=.10565842526040435,electron_mass_GeV=.000510998950905377,
    lifetime_seconds=2.1969803e-6,hbar_GeV_seconds=6.582119569509066e-25)


def actual():
    with np.load(ROOT/'artifacts/muon_coupled_lambda_local_matching_20261011/run_2/application.npz',allow_pickle=False)as a:
        C=a['changed_outgoing_current_full_charged_current_tensor'].copy()
        P=a['changed_outgoing_series_temporal_current_coefficients'].copy()
        return C,P


def test_complete_actual_temporal_tensor_closes_the_lifetime_equation():
    C,P=actual();a=temporal_tensor_lifetime_match(C,P,**ARGS)
    assert abs(a['normalized_matching_residual'])<1e-12
    assert a['full_nonVA_tensor_used'] and not a['physical_unit_selected']
    assert a['conditional_E_kappa_GeV']<a['static_matching_seed_GeV']
    assert abs(a['temporal_rate_log_energy_elasticity'])>1e-8
    assert abs(a['elasticity_step_halving_difference'])<1e-8


def test_static_action_has_exact_quarter_power_radiative_response():
    C,_=actual();P=C[None]
    base=temporal_tensor_lifetime_match(C,P,**ARGS)
    shifted=temporal_tensor_lifetime_match(C,P,inclusive_radiative_fraction=.01,**ARGS)
    assert abs(shifted['conditional_E_kappa_GeV']/base['conditional_E_kappa_GeV']-(1.01)**.25)<1e-12
    assert abs(base['conditional_log_E_derivative_log_lifetime']-.25)<1e-11
    assert abs(shifted['conditional_log_mass_derivative_radiative_fraction']+1/(4*1.01))<1e-11


def test_rejects_complex_metrology_before_real_conversion():
    C,P=actual()
    with pytest.raises(ValueError,match='explicit real'):
        temporal_tensor_lifetime_match(C,P,**(ARGS|{'lifetime_seconds':2.1969803e-6+1j}))
