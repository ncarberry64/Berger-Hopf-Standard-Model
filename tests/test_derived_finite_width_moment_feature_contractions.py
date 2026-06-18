import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_finite_width_moment_feature_contractions_are_symbolic_only():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_finite_width_moment_feature_contractions.md").read_text()

    assert qj.finite_width_moment_feature_contraction() in text
    assert "No numerical moment contractions are computed" in text
    assert "FINITE_WIDTH_MOMENT_FEATURE_CONTRACTIONS_SCAFFOLD_DERIVED_CONDITIONAL" in text
