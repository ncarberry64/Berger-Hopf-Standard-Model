"""Charge continuity consumes the actual Gauss and causal operator jets."""
from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_comparison_charge_balance import consume_charge_balance
from bhsm.interface.muon_incoming_comparison_time_lift import (
    causal_comparison_coefficients, sector_projector_source,
)
from bhsm.interface.muon_prepared_weak_gauss_dressing import charge_test_twojet


def case(theta, gradient, hessian):
    h = causal_comparison_coefficients(theta, gradient)
    C = np.eye(18)[:, [4,5,10,11,16,17]]
    sector = sector_projector_source(C.T@h['H']@C,
        np.einsum('ai,kab,bj->kij', C,h['H_source'],C))
    comparison = dict(h, input_iterate151=np.arange(151.), input_theta22=theta,
        input_theta_gradient22x151=gradient, electron_family_lift=C,
        electron_positive=sector['positive'],electron_negative=sector['negative'],
        electron_positive_source=sector['positive_source'])
    raw=charge_test_twojet(theta,gradient,hessian)
    gauss=dict(input_iterate151=np.arange(151.),actual_theta22=theta,
        actual_theta_gradient22x151=gradient)
    for k,v in raw.items():
        if isinstance(v,dict):
            for n,a in v.items():gauss[k+'_'+n]=a
        elif isinstance(v,np.ndarray):gauss[k]=v
    return comparison,gauss


@pytest.fixture(scope='module')
def actual():
    p=Path(__file__).resolve().parents[1]/'artifacts/muon_stationary_native_reference_load_20261019/run_5/native_reference_load.npz'
    with np.load(p,allow_pickle=False) as z:
        return tuple(z[k].copy() for k in ('actual_theta','actual_theta_gradient','actual_theta_hessian'))


def test_original_continuity_and_complete_source_match(actual):
    c,g=case(*actual);a=consume_charge_balance(c,g)
    assert np.max(abs(a['original_charge_balance_rows']))<2e-14
    assert np.max(abs(a['original_charge_balance_source_rows']))<2e-14
    assert np.max(abs(a['charge_exchange']))>1.
    assert np.max(abs(a['electron_pair_charge_exchange']))>0
    assert a['physical_d_in'] is None and not a['state_contracted']
    bad=dict(g,actual_theta22=g['actual_theta22']+np.eye(22)[0]*1e-6)
    with pytest.raises(ValueError,match='identities differ'):
        consume_charge_balance(c,bad)


def test_new_exchange_and_pair_source_against_original_field_variations(actual):
    theta,gradient,hessian=actual;c,g=case(*actual);a=consume_charge_balance(c,g)
    # Mixed radius, lapse, Higgs-axis and spatial/temporal gauge directions;
    # compare an independently reevaluated original operator, not its RHS.
    for direction in (0,62,146,147,148,149):
        v=gradient[:,direction];eps=2e-6
        results=[]
        for sign in (-1,1):
            t=theta+sign*eps*v
            cc,gg=case(t,np.zeros_like(gradient),np.zeros_like(hessian))
            results.append(consume_charge_balance(cc,gg))
        for value,source in (('charge_exchange','charge_exchange_source'),
            ('electron_pair_charge_exchange','electron_pair_charge_exchange_source')):
            finite=(results[1][value]-results[0][value])/(2*eps)
            np.testing.assert_allclose(finite,a[source][direction],atol=3e-9,rtol=3e-7)
