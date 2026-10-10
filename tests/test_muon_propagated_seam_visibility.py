"""New cache-only propagated diagnostic controls, without old tests."""
from pathlib import Path
import importlib.util
import numpy as np
import pytest
from flint import arb, acb, acb_mat

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('visibility', ROOT/'scripts/replay_muon_propagated_seam_visibility.py')
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


@pytest.fixture(scope='module')
def computed():
    return REPLAY.calculate(ROOT)


def test_actual_accepted_trace_and_same_affine_source_are_used(computed):
    d, r, numeric = computed[1], computed[2], computed[5]
    assert numeric['frame_coordinate_residual'] == 0
    assert numeric['node2_distance_from_earlier_tail_entrance'] > .008
    assert numeric['node3_distance_from_earlier_tail_solution'] > .008
    assert np.linalg.norm(d['tail']['backsubstitution_y'][0]) > 0
    assert r['node2_export_error_upper'] < 1e-16
    assert r['local_pivot_correction_norm_upper'] < 1e-14


def test_existing_witness_cancels_W_before_application(computed):
    from bhsm.interface.muon_propagated_seam_visibility import existing_witness_actions, matrix, center
    d, r, actions = computed[1:4]
    altered = dict(r, a3=matrix(np.full(12, 1e30)))
    changed = existing_witness_actions(d['witness'], altered)
    for key in ('left', 'higgs'):
        for n in actions[key]:
            assert np.array_equal(center(actions[key][n]), center(changed[key][n]))
    assert actions['higgs_norm'].lower() > 3e-9
    assert actions['higgs_norm'].upper() < 4e-9


def test_small_visibility_does_not_establish_an_invariant_subspace(computed):
    chiral = computed[4]
    assert chiral['actual_array_intertwining_residual'] < 2e-14
    assert chiral['recurrence_right_to_left_norm'] > 1e-5
    assert chiral['point_moment_chirality_form_defects']['A'] > 100
    assert chiral['point_moment_chirality_form_defects']['B'] > 1
    assert not chiral['invariant_right_subspace_established']


def test_norm_enclosure_handles_zero_crossing_component_balls():
    from bhsm.interface.muon_propagated_seam_visibility import norm
    z = acb(arb('0', '1e-80'), arb('0', '1e-80'))
    bound = norm(acb_mat([[z], [0]]))
    assert bound.is_finite()
    assert bound.upper() > 0
    assert float(bound.upper()) < 2e-80
