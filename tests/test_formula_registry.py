import json
from pathlib import Path

from bhsm.interface.formula_registry import default_formula_registry, evaluate_formula

ROOT = Path(__file__).resolve().parents[1]


def test_formula_registry_separates_artifacts_defaults_and_theorem_blockers():
    registry = default_formula_registry(ROOT)
    rows = registry.entries
    for key in ("ckm_matrix_from_artifact", "pmns_matrix_from_artifact", "cp_phase_from_artifact", "boundary_constants_from_artifact", "mass_ratios_from_artifact"):
        assert rows[key].status == "AVAILABLE_ARTIFACT_BACKED"
    for key in ("hyperspherical_default_metric", "hyperspherical_default_tension"):
        assert rows[key].status == "AVAILABLE_INTERFACE_DEFAULT"
        assert "default" in rows[key].claim_boundary.lower()
    for key in ("x_ch_production_vertex", "neutrino_physical_basis_scale", "cp_o_int_standalone_attachment"):
        assert rows[key].status == "OPEN_THEOREM_REQUIRED"
        assert evaluate_formula(key, ROOT).evaluation_status == "CALLABLE_NOT_AVAILABLE"


def test_formula_registry_artifact_exists_and_parses():
    payload = json.loads((ROOT / "artifacts/BHSM_formula_registry_v0_3.json").read_text(encoding="utf-8"))
    assert payload["available_artifact_backed"]
    assert payload["open_theorem_required"]
