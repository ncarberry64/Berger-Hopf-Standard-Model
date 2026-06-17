import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "theory" / "candidate_theorem_discharge_y0_coordinate_constraint.py"
RESULTS_PATH = ROOT / "theory" / "theorem_discharge_y0_coordinate_constraint_results.json"

def load_mod():
    spec = importlib.util.spec_from_file_location("y0coord", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

def load_results():
    return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

def test_results_schema_core_flags():
    data = load_results()
    assert data["official_predictions_changed"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["standard_model_fully_derived"] is False
    assert data["bhsm_replacement_claim_ready"] is False
    assert data["generic_y0_coordinates"] == ["alpha0", "beta0", "gamma0"]
    assert "PO-BH-32" in data["discharged_obligations"]
