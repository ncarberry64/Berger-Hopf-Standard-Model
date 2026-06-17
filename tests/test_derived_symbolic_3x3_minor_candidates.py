import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "theory" / "candidate_theorem_discharge_explicit_symbolic_gram_minor.py"
RESULTS_PATH = ROOT / "theory" / "theorem_discharge_explicit_symbolic_gram_minor_results.json"


def load_mod():
    spec = importlib.util.spec_from_file_location("explicit_minor", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_minor_candidates_exist_for_each_sector():
    mod = load_mod()
    candidates = mod.all_symbolic_minor_candidates()
    assert set(candidates) == set(mod.generation_modes())
    for sector, sector_candidates in candidates.items():
        assert sector_candidates
        first = sector_candidates[0]
        assert first["sector"] == sector
        assert len(first["row_indexes"]) == 3
        assert first["entries_tied_to_wigner_labels"] is True
        assert first["nonzero_proven"] is False


def test_json_records_minor_candidates_layer():
    data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    assert data["symbolic_3x3_minor_candidates_enumerated"] is True
    assert "SYMBOLIC_3X3_MINOR_CANDIDATES_ENUMERATED" in data["verdict_labels"]

