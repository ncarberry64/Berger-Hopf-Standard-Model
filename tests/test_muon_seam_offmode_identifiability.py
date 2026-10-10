"""New witness checks only; no prior producer or scientific check replay."""
from fractions import Fraction
from pathlib import Path
import importlib.util
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('offmode',
    ROOT/'scripts/replay_muon_seam_offmode_identifiability.py')
REPLAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


@pytest.fixture(scope='module')
def computed():
    # One focused inexpensive new calculation shared by all checks.
    return REPLAY.calculate(ROOT)


def test_transported_fundamental_higgs_matches_actual_saved_adjoint(computed):
    match = computed[5]
    assert max(match.values()) < 8e-15


def test_actual_projected_offmode_kernel_is_nonzero_with_exact_nodal_scope(computed):
    radial, actions = computed[3], computed[6]
    exact = Fraction(int(radial['exact_eta_numerator']), int(radial['exact_eta_denominator']))
    lo, hi = (Fraction.from_float(float(x)) for x in radial['eta_interval'])
    assert 0 < lo <= exact <= hi
    assert float(hi-lo) <= np.spacing(radial['eta'])
    assert actions['unit_higgs_projected_source_norm'] > 2
    # A nonzero full coordinate-column map does not establish sensitivity
    # of the particular original load. Preserve this meaningful limitation.
    coordinates = computed[1]['cut']['source_coordinates']
    original = np.sqrt(sum(np.linalg.norm(x.reshape(-1, 12)@coordinates)**2
                           for x in actions['forward_h'].values()))
    assert original < 1e-14


def test_reverse_action_uses_dirac_bar_and_geometric_volume_pairing(computed):
    actions = computed[6]
    assert set(actions['e45']) == {0, 2, 4}
    assert set(actions['reverse']) == {1, 3, 5}
    assert np.linalg.norm(actions['forward_pair']) > .1
    assert actions['reverse_bar_pairing_residual'] < 1e-14
    # This compares the computed reverse against the independently paired
    # forward on all twelve directions, not an isolated Euclidean adjoint.
    assert np.allclose(actions['forward_pair'].conj().T,
                       actions['reverse_pair'], rtol=0, atol=1e-14)


def test_evaluated_reverse_is_distributed_not_a_boundary_cotangent(computed):
    d, radial, actions = computed[1], computed[3], computed[6]
    # The cached source columns have zero geometric material trace. Their
    # NEW K_L action is nevertheless nonzero, so this witness cannot be
    # represented as T*gamma_trace. Its reverse is a volume Euler term.
    assert np.count_nonzero(d['wall']['material_source_trace']) == 0
    assert actions['unit_higgs_projected_source_norm'] > 2
    assert np.linalg.norm(actions['forward_pair']) > .1
    assert np.count_nonzero(radial['chi'][d['point']['p'] == 0]) > 0
