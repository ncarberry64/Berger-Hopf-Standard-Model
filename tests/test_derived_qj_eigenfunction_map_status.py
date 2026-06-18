import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_qj_eigenfunction_map_status_keeps_explicit_map_open():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_qj_eigenfunction_map_status.md").read_text()
    payload = json.loads((ROOT / "theory" / "theorem_discharge_qj_eigenfunction_map_results.json").read_text())

    assert "| explicit Berger/BHSM eigenfunction map | `OPEN` |" in text
    assert "| internal feature independence | `OPEN` |" in text
    assert "| finite-width rank three | `False` |" in text
    assert payload["explicit_qj_eigenfunction_map_derived"] is False
    assert payload["internal_feature_independence_derived"] is False
    assert "QJ_TO_BERGER_EIGENFUNCTION_MAP_REMAINS_OPEN" in payload["verdict_labels"]
