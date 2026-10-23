"""Actual E1 event tangency and its distinct mechanical normal contacts."""
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.muon_complex_paired_normal_action import complex_proper_normal_trace
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_event_formation_constraints import (
    event_constraint_formation_application, proper_normal_coordinate_columns,
)


@pytest.fixture(scope='module')
def histories():
    root = Path(__file__).resolve().parents[1]
    folder = root/'artifacts/muon_retained_response_20261018/inputs'
    metadata = json.loads((folder/'history_metadata.json').read_bytes())
    result = []
    for side in ('incoming', 'outgoing'):
        with np.load(folder/(side+'_history.npz'), allow_pickle=False) as z:
            rows = metadata['sides'][side]
            times = np.array([row['time'] for row in rows])
            raw = np.array([z[row['label']+'_raw_fields'] for row in rows])
            rates = np.array([z[row['label']+'_raw_coordinate_time_derivative'] for row in rows])
        h, _ = recovered_export_history(root, side, times, raw, rates)
        result.append(h)
    return result


@pytest.fixture(scope='module')
def application(histories):
    return event_constraint_formation_application(*histories)


def test_actual_proper_normal_columns_are_reciprocal_to_original_graph_trace(histories):
    for history in histories:
        raw, rate = history.value(0.)
        P = history.original_phase_operands['resolved_phase_coordinate_lift']
        columns = proper_normal_coordinate_columns(raw, rate, P)
        B = columns['raw_normal_columns']
        a = columns['proper_graph_coefficient']
        at = columns['proper_graph_coefficient_time_first']
        trace = complex_proper_normal_trace(raw, P)['normal_chart_coefficient']
        assert abs(trace*a-1) < 4e-16
        assert B.shape == (268, 2)
        assert np.count_nonzero(B) == 3
        assert B[98, 0] == B[99, 1] == a
        assert B[99, 0] == at
        assert abs(at) > .01  # The moving proper graph's rate was not frozen.


def test_actual_two_pivot_source_solve_checks_every_invariant_row(application):
    a, report = application
    J = a['event_normal_coordinate_Jacobian']
    rows, columns = (a[k] for k in ('normal_displacement_pivot_rows',
                                  'normal_displacement_pivot_columns'))
    correction = a['provisional_normal_displacement_source_correction']
    before = a['supplied_Xi_event_constraint_load']
    after = a['corrected_supplied_Xi_event_constraint_rows']
    assert J.shape == (7, 4)
    assert report['normal_coordinate_Jacobian_rank'] == 2
    assert np.max(abs(before)) > .7
    assert np.max(abs(after[rows])) < 3e-17
    assert np.max(abs(after-(before+J[:, columns]@correction))) == 0
    assert np.max(abs(a['original_callback_source_reconstruction_rows'])) < 64*np.finfo(float).eps
    # The other original invariant rows remain a numerical nonpass.
    assert 2e-10 < np.max(abs(after)) < 1e-8
    assert np.max(abs(a['free_normal_time_derivative_original_rows'])) == 0


def test_event_tangency_does_not_select_formation_or_fermion_boundary_state(application):
    a, report = application
    assert a['provisional_raw_normal_source_correction'].shape == (2, 268)
    assert report['homogeneous_coordinates_per_time_node'] == 366
    assert not report['homogeneous_coordinates_assigned']
    assert not report['normal_amplitudes_assigned']
    assert not report['event_multipliers_assigned']
    assert not report['full_formation_Hessian_evaluated']
    assert not report['physical_admission']
    assert not report['complete_physical_derivative']
    assert report['normal_profile_normalization'] is None
    assert report['full_constraint_residual_after'] is None


def test_normal_column_application_rejects_a_different_phase_chart(histories):
    raw, rate = histories[0].value(0.)
    with pytest.raises(ValueError, match='phase252'):
        proper_normal_coordinate_columns(raw, rate, np.zeros((268, 251)))
