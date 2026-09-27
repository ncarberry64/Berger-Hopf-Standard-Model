"""Native row/sign binding and the exact joint-operator dependency."""
import json
from pathlib import Path
import sys
import pytest
from flint import arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.native_seven_outputs import native_row_indices, native_seven_residual, event_boundary_outputs
from certify_n12_gate7_coupled_center_neighborhood import load
from bind_n12_gate7_seven_physical_outputs import digest

OUT=ROOT/'artifacts/flagship_integration/gate7_seven_outputs_20260927'


def report():
    return json.loads((OUT/'report.json').read_bytes())


def same_balls(a,b):
    return (a.nrows(),a.ncols())==(b.nrows(),b.ncols()) and all(
        x.mid()==y.mid() and x.rad()==y.rad() for x,y in zip(a.entries(),b.entries()))


def test_actual_owner_row_selection():
    d=report()['output_definition']
    assert native_row_indices(12)==(0,1,2,28,29,30,31)
    assert d['original_child_rows']==32 and d['original_constraint_rows']==25
    assert d['zero_based_native_indices']==list(native_row_indices(12))
    owner=report()['source_definitions'][0]['functions']['_child_rows_at_order']['text']
    assert 'momentum - event_momentum' in owner
    assert 'flux = child_flux - (-momentum_rate + force - event_flux)' in owner


def test_event_orientation_on_actual_frozen_native_jet():
    # Partial derivative holding child arguments fixed, not a physical child
    # chart or a surrogate output seed. Only the stored event jet is used.
    ctx.prec=512
    a=load(ROOT/'artifacts/flagship_integration/gate7_launch_response_20260927/arrays.npz')['response_7x73']
    trace=arb_mat(a[:3].tolist());momentum=arb_mat(a[3:5].tolist());flux=arb_mat(a[5:].tolist())
    z3=arb_mat(3,73);z2=arb_mat(2,73)
    got=native_seven_residual(child_trace=z3,event_trace=trace,
        child_momentum=z2,event_momentum=momentum,child_conormal=z2,
        child_momentum_rate=z2,child_force=z2,event_conormal=flux)
    expected=arb_mat((-trace).tolist()+(-momentum).tolist()+flux.tolist())
    assert same_balls(got,expected)
    assert same_balls(event_boundary_outputs(event_trace=trace,event_momentum=momentum,event_conormal=flux),arb_mat(a.tolist()))


def test_output_assembler_requires_correct_physical_shapes():
    with pytest.raises(ValueError):
        native_seven_residual(child_trace=arb_mat(2,1),event_trace=arb_mat(3,1),
            child_momentum=arb_mat(2,1),event_momentum=arb_mat(2,1),child_conormal=arb_mat(2,1),
            child_momentum_rate=arb_mat(2,1),child_force=arb_mat(2,1),event_conormal=arb_mat(2,1))
    with pytest.raises(ValueError):native_row_indices(1)


def test_exact_missing_owner_is_numerical_realization_not_new_law():
    d=report();m=d['exact_missing_owner']
    assert d['status'].startswith('OUTCOME_C_')
    assert m['no_new_environment_law']
    assert m['evidence']['actual_complete_joint_operator_value']=='ACTUALLY_MISSING'
    assert m['evidence']['actual_complete_joint_operator_first_jet']=='ACTUALLY_MISSING'
    assert d['boundary_of_available_evidence']['z_minus_one']['complete_heat_spectral_family']=='OPEN'


def test_outcome_c_does_not_manufacture_complete_response():
    d=report()
    for k in ('complete_response','delta_history','rank_complete','rank_delta',
              'rowwise_correction_norms','largest_entry_and_location','seven_adjoint_residuals'):
        assert d[k] is None
    assert not d['promoted'] and not d['Gate7_closed'] and not d['FULL_BHSM_COMPLETE']
    assert not d['producers_run'] and not d['historical_test_covectors_run']
    assert not d['tolerances_changed']


def test_source_and_frozen_packet_binding():
    d=report()
    for item in d['source_definitions']+list(d['packet_binding'].values()):
        assert digest(ROOT/item['path'])==item['SHA256']
    for p,h in d['code_SHA256'].items():assert digest(ROOT/p)==h


def test_repeated_report_is_identical():
    receipt=json.loads((OUT/'reproduction.json').read_bytes())
    assert receipt['byte_identical']
    assert digest(OUT/'report.json')==receipt['report_SHA256']
