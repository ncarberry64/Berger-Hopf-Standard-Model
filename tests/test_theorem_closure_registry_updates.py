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
    expected = {
        "charged_boundary_response_matrix": "CONDITIONAL_THEOREM",
        "neutral_operator_kernel_BH": "CONDITIONAL_THEOREM",
        "cp_holonomy_phase_attachment": "ARTIFACT_BACKED_CONSTRAINT",
    }
    for key, status in expected.items():
        assert rows[key]["status_before"] == rows[key]["status_after"] == status
    for key in ("feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"):
        assert rows[key]["status_after"] == "DISABLED_UNTIL_RUNTIME_VALIDATED"


def test_formula_registry_reflects_ontology_aware_outcomes():
    rows = default_formula_registry(ROOT).entries
    assert rows["x_ch_production_vertex"].status == "RETIRED_TARGET"
    assert rows["neutrino_physical_basis_scale"].status == "AVAILABLE_AUTHOR_SUPPLIED_CONDITIONAL"
    assert rows["neutrino_physical_basis_scale"].theorem_status == "CONDITIONAL_PROPAGATION_THEOREM"
    assert rows["cp_o_int_standalone_attachment"].status == "RETIRED_TARGET"
    assert rows["cp_o_int_standalone_attachment"].theorem_status == "RETIRED_TARGET"
