import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_internal_eigenfunction_mode_scaffold_labels_every_generation():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_internal_eigenfunction_mode_scaffold.md").read_text()

    for sector, modes in qj.generation_modes().items():
        assert f"## {sector}" in text
        for mode in modes:
            assert qj.symbolic_eigenfunction(mode) in text
            assert f"(q,j)=({mode.q},{mode.j})" in text
    assert "INTERNAL_EIGENFUNCTION_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL" in text
