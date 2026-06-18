import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_qj_to_internal_eigenfunction_map_scaffold_and_ledgers():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_qj_to_internal_eigenfunction_map.md").read_text()
    modes = qj.generation_modes()

    assert qj.qj_to_eigenfunction_map() == "E:(q,j)->psi_qj(y)"
    assert qj.qj_to_eigenfunction_map_status() == "SCAFFOLD_DERIVED_CONDITIONAL"
    assert set(modes) == {"reference_charged", "reference_neutral", "cyclic_upper", "cyclic_lower"}
    assert all(len(sector_modes) == 3 for sector_modes in modes.values())
    assert "psi_q6_j0(y)" in text
    assert "psi_q4_j2(y)" in text
    assert "does not derive explicit Berger/BHSM eigenfunction formulas" in text
