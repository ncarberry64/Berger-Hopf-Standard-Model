from pathlib import Path

from bhsm.interface.formula_registry import default_formula_registry
from bhsm.interface.theorem_closure.registry_update import build_theorem_registry_update

ROOT = Path(__file__).resolve().parents[1]


def test_registry_proposal_applies_no_promotions_or_runtime_changes():
    proposal = build_theorem_registry_update(ROOT)
    rows = {row["entry_key"]: row for row in proposal["entries"]}
    assert proposal["promotions_allowed"] == []
    assert proposal["promotions_applied"] == []
    assert proposal["production_registry_mutated"] is False
    for key in ("charged_boundary_response_matrix", "neutral_operator_kernel_BH", "cp_holonomy_phase_attachment"):
        assert rows[key]["status_before"] == rows[key]["status_after"] == "OPEN_THEOREM_REQUIRED"
    for key in ("feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"):
        assert rows[key]["status_after"] == "DISABLED_UNTIL_RUNTIME_VALIDATED"


def test_formula_registry_reflects_exact_open_outcomes():
    rows = default_formula_registry(ROOT).entries
    assert rows["x_ch_production_vertex"].status == "OPEN_THEOREM_REQUIRED"
    assert rows["neutrino_physical_basis_scale"].status == "OPEN_THEOREM_REQUIRED"
    assert rows["cp_o_int_standalone_attachment"].status == "OPEN_THEOREM_REQUIRED"
    assert rows["cp_o_int_standalone_attachment"].theorem_status == "OPEN_MISSING_INTERACTION_ATTACHMENT"
