import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_local_feature_vector_has_value_gradient_and_hessian_for_each_weight():
    label = mm.multiplet_ledgers()["cyclic_lower"][2]
    features = mm.local_feature_vector(label)
    assert len(features) == 3 * len(label.m_values)
    assert any(feature.startswith("partial_a ") for feature in features)
    assert any(feature.startswith("partial_a partial_b ") for feature in features)
