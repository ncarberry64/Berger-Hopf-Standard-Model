from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_action_candidate import build_action_density_candidate
from bhsm.interface.theorem_closure.cp_o_int_sprint_c_report import build_cp_o_int_field_action_report

ROOT = Path(__file__).resolve().parents[1]


def test_action_density_comes_from_blocked_symbolic_ledger():
    action = build_action_density_candidate(ROOT)
    assert action.expression == "G_raw exp(i delta_BH) O_int + h.c."
    assert action.status == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert action.is_artifact_backed is True
    assert action.is_placeholder is True
    assert action.variation_eom_defined is False


def test_symbolic_callable_is_not_production_callable():
    result = build_cp_o_int_field_action_report(repository=ROOT)
    assert result.callable_available is True
    assert result.symbolic_callable["production_callable"] is False
    assert result.production_eligible is False
    assert result.runtime_export_eligible is False
    assert "action-backed production theorem callable" in result.missing_objects
