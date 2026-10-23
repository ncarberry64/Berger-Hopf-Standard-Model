"""Affected map transport reuses the original constraint geometry jets."""
from pathlib import Path
import json

import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_d5_event_constraint_twojet import event_constraint_twojet
from bhsm.interface.muon_d5_event_constraint_twojet_append import reorient_saved_constraint_twojet
from bhsm.interface.muon_d5_spatial_bundle_application import cross_matrix
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


@pytest.fixture(scope='module')
def actual():
    root = Path(__file__).resolve().parents[1]
    folder = root/'artifacts/muon_retained_response_20261018/inputs'
    metadata = json.loads((folder/'history_metadata.json').read_bytes())
    histories = []
    for side in ('incoming', 'outgoing'):
        rows = metadata['sides'][side]
        with np.load(folder/(side+'_history.npz')) as z:
            t = np.array([r['time'] for r in rows])
            x = np.array([z[r['label']+'_raw_fields'] for r in rows])
            xt = np.array([z[r['label']+'_raw_coordinate_time_derivative'] for r in rows])
        histories.append(recovered_export_history(root, side, t, x, xt)[0])
    raw = [h.value(0.)[0] for h in histories]
    p = histories[1].original_phase_operands
    geometry = np.array([raw[0][:100], raw[1][:100], p['initial_pair'][0, :100],
        p['reference_pair'][0, :100], p['reference_pair'][1, :100]])
    wall = np.array([(h.gauge_basis([WALL])[0]@r[100:180]).reshape(5, 4)
        for h, r in zip(histories, raw)])
    O = expm(cross_matrix([.2, -.4, .1]))
    R = expm(cross_matrix([-.3, .2, .5]))
    return geometry, wall, event_constraint_twojet(geometry, wall, O, R)


def test_saved_geometry_jets_transport_to_all_new_map_placements(actual):
    geometry, wall, cached = actual
    O = expm(cross_matrix([-.31, .07, .22]))
    R = expm(cross_matrix([.17, -.11, .29]))
    actual = reorient_saved_constraint_twojet(cached, O, R)
    independent = event_constraint_twojet(geometry, wall, O, R)
    for key in ('value', 'gradient', 'hessian'):
        np.testing.assert_allclose(actual[key], independent[key], rtol=2e-14, atol=3e-14)
    # No change to child/born/reference or radius jets, including all their
    # nonzero second placements, and no mutation of the historical cache.
    np.testing.assert_array_equal(actual['hessian'][0], cached['hessian'][0])
    np.testing.assert_array_equal(actual['hessian'][1:, 100:500, 100:500],
        cached['hessian'][1:, 100:500, 100:500])
    assert not np.array_equal(actual['base_rotation'], cached['base_rotation'])


def test_complete_saved_row_shapes_and_orthogonal_factors_are_required(actual):
    cached = actual[-1]
    bad = dict(cached, gradient=cached['gradient'][:, :-1])
    with pytest.raises(ValueError, match='complete cached13x546'):
        reorient_saved_constraint_twojet(bad, np.eye(3), np.eye(3))
    with pytest.raises(ValueError, match='orientation-preserving'):
        reorient_saved_constraint_twojet(cached, 2*np.eye(3), np.eye(3))
