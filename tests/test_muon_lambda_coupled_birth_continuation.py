from pathlib import Path
import json
import numpy as np
import pytest
from bhsm.interface.muon_lambda_coupled_birth_continuation import higgs_lambda_action_jet,load_lambda_coupled_birth
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('side',['incoming','outgoing'])
def test_literal_lambda_source_matches_original_full_action_parameter_application(side):
    # This independent retained application rebuilt the whole cap/Maxwell/H
    # action at three stiffness values, not this potential-only helper.
    path=ROOT/'artifacts/muon_local_lifetime_scalar_matching_20261011/run_1'/f'{side}_application.npz'
    with np.load(path,allow_pickle=False)as f:
        raw=f['raw_fields'];g=f['full_action_gradient_lambda_derivative'];h=f['full_action_hessian_lambda_derivative']
    a=higgs_lambda_action_jet(raw,nu_squared_action=4.)
    md=json.loads((ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1/result.json').read_bytes())
    P=generic_coordinate_lift(md['gauge_labels'])['lift']
    # Full-action subtraction retains binary cancellation from the much
    # larger cap terms; this comparison is a diagnostic, not an enclosure.
    np.testing.assert_allclose(P.T@a.gradient,g,atol=3e-12,rtol=1e-10)
    np.testing.assert_allclose(P.T@a.hessian@P,h,atol=3e-11,rtol=1e-9)
    assert np.linalg.norm(a.hessian[:100,260:264])>1e-4
    assert np.count_nonzero(a.gradient[100:260])==0
    assert np.count_nonzero(a.hessian[100:260])==0
    # The kinetic and gauge contacts remain in the base action.  Only
    # the potential derivative is gauge independent at held fields.
    assert np.count_nonzero(a.gradient[264:])==0


def test_real_action_source_rejects_complex_before_cast():
    with pytest.raises(ValueError):higgs_lambda_action_jet(np.zeros(268,complex),nu_squared_action=4.)


def test_field_and_geometric_cross_is_literal_derivative():
    with np.load(ROOT/'artifacts/muon_local_lifetime_scalar_matching_20261011/run_1/incoming_application.npz',allow_pickle=False)as f:x=f['raw_fields']
    a=higgs_lambda_action_jet(x,nu_squared_action=4.);d=np.zeros(268);d[260:264]=[.1,-.3,.2,.15]
    eps=1e-5
    p=higgs_lambda_action_jet(x+eps*d,nu_squared_action=4.);m=higgs_lambda_action_jet(x-eps*d,nu_squared_action=4.)
    np.testing.assert_allclose((p.gradient-m.gradient)/(2*eps),a.hessian@d,atol=2e-11,rtol=2e-9)


def test_actual_coupled_loader_retains_new_stiffness_and_changed_fields():
    path='artifacts/muon_lambda_coupled_birth_continuation_20261011/run_2'
    a=load_lambda_coupled_birth(path,side='outgoing',repository=ROOT)
    assert a['representation']['scalar_matching']['lambda_H']==a['receipt']['lambda_H']
    assert a['receipt']['lambda_H']!=a['receipt']['lambda_H_base']
    with np.load(ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1/application.npz',allow_pickle=False)as f:
        delta=a['arrays']['updated_raw_pair']-f['updated_raw_pair']
    assert np.linalg.norm(delta[:,:100])>0
    assert np.linalg.norm(delta[:,100:260])>0
    assert np.linalg.norm(delta[:,260:268])>0
    assert np.array_equal(a['coordinates']['lift']@a['master'],a['raw'])
    assert a['receipt']['scaled_residual']<2e-10
    assert not a['receipt']['physical_scalar_resonance_or_energy_unit_selected']
