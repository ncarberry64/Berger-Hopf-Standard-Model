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


def load_results():
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))


def test_schema_flags():
    data = load_results()
    assert data["official_predictions_changed"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["standard_model_fully_derived"] is False
    assert data["bhsm_replacement_claim_ready"] is False
    assert data["explicit_symbolic_gram_minor_layer_completed"] is True
    assert data["generation_feature_matrices_constructed"] is True
    assert data["symbolic_3x3_minor_candidates_enumerated"] is True
    assert "PO-BH-34" in data["discharged_obligations"]


def test_module_status_is_partial():
    mod = load_mod()
    assert mod.status().value == "PARTIAL"

