from __future__ import annotations

import json

from bhsm.interface import cli
from bhsm.interface.completion import final_completion_gate_v11_2 as gate
from bhsm.interface.completion.complete_local_supported_action_v11_2 import (
    EXACT_NEXT_OBJECT,
    PRIMARY_VERDICT,
    action_payload,
)
from bhsm.interface.completion.historical_recovery_complete_supported_action_v11_2 import recovery_payload
from bhsm.interface.completion.support_covariant_derivative_v11_2 import (
    covariant_derivative_component,
    derivative_payload,
    transformed_derivative_component,
)
from bhsm.interface.current_program_status import CURRENT_VERSION


def test_historical_recovery_is_exhaustive_and_classifies_closest_branches() -> None:
    payload = recovery_payload()
    assert payload["validation_passed"]
    assert payload["historical_routes_exhausted"]
    assert payload["exact_object_recovered"] is False
    assert {row["commit"] for row in payload["candidates"]} >= {"837d806", "27a9dee", "820198f", "75894b9"}
    assert payload["status"] == PRIMARY_VERDICT


def test_composite_connection_covariance_is_exact() -> None:
    base = covariant_derivative_component(2.0, 3.0, 2.0, 0.4)
    transformed = transformed_derivative_component(2.0, 3.0, 2.0, 0.4, 1.7, -0.2)
    assert abs(transformed - 1.7**2 * base) < 1e-12
    payload = derivative_payload()
    assert payload["validation_passed"]
    assert payload["connection_is_independent_field"] is False
    assert payload["primitive_field_weights"] is None
    assert payload["laws"]["curvature"].startswith("F_D=dA_D")


def test_tensor_dual_contraction_metric_and_density_laws_are_explicit() -> None:
    laws = derivative_payload()["laws"]
    for key in ("tensor", "dual", "contraction", "metric", "density"):
        assert laws[key]
    assert "iff w_G=0" in laws["metric"]


def test_boundary_fiber_reduction_and_frozen_compatibility_are_conditional_not_fabricated() -> None:
    laws = derivative_payload()["laws"]
    assert "equivariant" in laws["boundary_pullback"]
    assert "assigned fiber-measure character" in laws["fiber_integration"]
    assert laws["frozen_limit"].endswith("D^(w)=nabla")


def test_complete_action_ledger_exposes_first_missing_coupling() -> None:
    payload = action_payload()
    assert payload["validation_passed"]
    assert payload["complete_local_action"] is None
    assert payload["support_kinetic_term"]
    assert "-A_D,A J_D^A" in payload["first_missing_action_owned_term"]
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert all(row["primitive_support_character"] is None for row in payload["term_ledger"])


def test_completion_gate_fail_closes_every_mark_ii_dependent_output() -> None:
    payload = gate.completion_payload()
    assert payload["validation_passed"]
    assert payload["Mark_I"] == "REACHED"
    assert payload["Mark_II"] == payload["Mark_III"] == payload["Mark_IV"] == "NOT_REACHED"
    assert payload["physical_outputs_promoted"] == []
    assert payload["core_transfer_operator"]["transfer_operator"] is None
    assert payload["three_mode_physical_action"]["hessian"] is None
    assert payload["frozen_predictions_changed"] is False


def test_materialization_is_byte_deterministic(tmp_path) -> None:
    first = gate.materialize(tmp_path)
    first_bytes = {path.name: path.read_bytes() for path in first}
    second = gate.materialize(tmp_path)
    assert first_bytes == {path.name: path.read_bytes() for path in second}
    assert len(first) == 29
    canonical = json.loads((tmp_path / "artifacts" / "BHSM_1_0_completion_gate.json").read_text())
    assert canonical["version"] == "v11.2"
    assert CURRENT_VERSION == "v11.3"
    assert canonical["current_verdict"] == PRIMARY_VERDICT


def test_all_v11_2_commands_emit_current_json(capsys) -> None:
    for command in gate.COMMAND_SECTIONS:
        assert cli.main([command, "--format", "json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["version"] == "v11.2"
        assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert cli.main(["historical-recovery-status", "--object", "complete local supported action", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["artifact"].endswith("v11_2")
