import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_feature_labels_exist_for_all_modes_with_two_ell_plus_one_counts():
    labels_by_mode = gy0.all_generic_y0_feature_labels()
    assert len(labels_by_mode) == 12
    for labels in labels_by_mode.values():
        first = labels[0]
        assert len(labels) == int(2 * first.ell) + 1


def test_local_feature_vector_contains_first_and_second_derivative_features():
    label = gy0.all_generic_y0_feature_labels()["cyclic_upper:2"][0]
    vector = gy0.local_feature_vector(label)
    assert label.expression in vector
    assert any("partial_beta[" in item for item in vector)
    assert any("partial_alpha partial_gamma" in item for item in vector)
    assert any("partial_beta partial_beta" in item for item in vector)
