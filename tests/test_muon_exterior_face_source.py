"""New operator/source controls, separate from an exterior or Pauli solve."""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT/'artifacts/muon_exterior_face_source_20261002/replay_reference'


def test_conditional_curvature_has_charged_complement():
    with np.load(REF/'continued_source_and_angular_coefficients.npz') as z:
        # Independent representation result: four weak doublets, e=-i sigma;
        # only the first two generators fail to commute with Q=T3+Y.
        np.testing.assert_allclose(z['commutator_Gram'], np.diag([8,8,0]), atol=2e-14)
        # spin1 x spin1/2 -> spin3/2: the e3 polarization norm is 0 or2/3.
        # Consequently C_Q=(3/2)(I+G_e3) has these exact eigenvalues.
        np.testing.assert_allclose(np.linalg.eigvalsh(z['QQ_connection']),
                                   [1.5]*4+[2.5]*4, atol=2e-14)
        assert np.linalg.norm(z['frontier_charge_complement']) > 0
        np.testing.assert_allclose(z['QQ_cross'], 0, atol=2e-14)


def test_full_curvature_action_matches_same_source_compression():
    data=json.loads((REF/'result.json').read_text())
    with np.load(REF/'continued_source_and_angular_coefficients.npz') as z:
        Tb=data['frontier_source']['T_b']
        qnorm=16/3
        # Full output contraction includes the T1/T2 pieces. Squaring a
        # Q-only compression would omit precisely this positive QQ term.
        full=z['frontier_curvature_Gram']/(Tb*Tb*qnorm)
        np.testing.assert_allclose(full,z['QQ_covariant_angular_matrix'][0,-1],
                                   rtol=3e-15,atol=3e-14)
        assert np.ptp(np.linalg.eigvalsh(full)) > 0.01


def test_frontier_is_a_cut_with_nonzero_source_frame_derivative():
    data=json.loads((REF/'result.json').read_text())
    lo,hi=data['frontier_H_reused_certified_interval']
    assert 0 < lo <= data['frontier_source']['H'] <= hi
    assert data['frozen_parent_H_at_frontier']==0
    assert data['frontier_source']['T_b_prime'] < 0
    assert data['frontier_source']['temporal_known_moving_frame_term'] < 0
    assert data['orientations']['past_core_outward']==-data['orientations']['past_prefix_outward']
    assert data['actual_execution']['exterior_source_response_directions']==0
    assert data['physical_a_mu'] is None and data['exterior_affine_return'] is None
    assert data['source_frame_matching']['actual_parent_angular_coefficient'] is None
    assert data['actual_execution']['action_derived_parent_angular_source_directions']==0


def test_newer_local_history_has_identical_consumed_face_fields():
    base=REF.parent
    refs=json.loads((base/'input_refs.json').read_text())
    with np.load(ROOT/refs['inputs']['center']['repository_path']) as current:
        with np.load(REF/'continued_source_and_angular_coefficients.npz') as saved:
            np.testing.assert_array_equal(current['centers'][0],saved['core_initial_state'])
        assert current['signed_descriptors'][-1]==0
        assert current['centers'].shape==(2,98)
    proof=json.loads((base/'current_history_reconciliation.json').read_text())
    assert proof['entire_center_arrays_identical'] is False
    assert proof['numerical_rerun'] is False
