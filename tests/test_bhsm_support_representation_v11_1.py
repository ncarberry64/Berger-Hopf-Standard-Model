from __future__ import annotations

import json

from bhsm.interface import cli
from bhsm.interface.completion import final_completion_gate_v11_1 as gate
from bhsm.interface.completion.haar_scale_normalization_v11_1 import haar_scale_payload
from bhsm.interface.completion.support_representation_category_v11_1 import (
    FUNCTOR_VERDICT,
    category_payload,
    functor_payload,
)
from bhsm.interface.completion.support_functor_equivalence_quotient_v11_1 import equivalence_payload
from bhsm.interface.recovery.historical_equivalence_audit import blocker_readiness_payload, recovery_payload
from bhsm.interface.completion.final_completion_gate_v11_1 import CURRENT_VERSION, EXACT_NEXT_OBJECT


def test_category_is_complete_but_has_no_action_owned_gd_lift() -> None:
    payload = category_payload()
    assert payload["validation_passed"]
    assert len(payload["objects"]) == 13
    assert len(payload["morphisms"]) >= 17
    assert all(row["action_defined_support_representation"] is None for row in payload["objects"])


def test_two_distinct_lifts_do_not_prejudge_physical_equivalence() -> None:
    payload = functor_payload()
    first, second = payload["candidate_action_limit_compatible_lifts"]
    assert payload["validation_passed"]
    assert payload["status"] == FUNCTOR_VERDICT
    assert payload["unique_functor"] is None
    assert payload["physical_equivalence_quotient_complete"] is False
    assert first["primitive_weights"] != second["primitive_weights"]
    assert first["parent_action_recovered_at_upsilon_one"]
    assert second["parent_action_recovered_at_upsilon_one"]


def test_equivalence_quotient_distinguishes_representation_from_physics() -> None:
    payload = equivalence_payload()
    assert payload["validation_passed"]
    assert payload["natural_isomorphism_test"]["monoidal_linear_natural_isomorphism_exists"] is False
    assert payload["field_redefinition_test"]["invertible_on_regular_domain"] is True
    assert payload["field_redefinition_test"]["invertible_at_core"] is False
    assert payload["physically_inequivalent_theories_proven"] is False
    assert payload["physically_equivalent_descriptions_proven"] is False
    assert payload["final_equivalence_classification"] == "NOT_YET_DECIDABLE_FROM_CURRENT_ACTION"


def test_historical_recovery_is_complete_before_blocker_is_emitted() -> None:
    recovery = recovery_payload()
    readiness = blocker_readiness_payload()
    assert recovery["validation_passed"]
    assert recovery["historical_routes_exhausted"]
    assert recovery["exact_current_object_recovered"] is False
    assert readiness["historical_recovery_complete"]
    assert readiness["blocker_may_be_emitted"]


def test_all_haar_normalization_routes_fail_closed() -> None:
    payload = haar_scale_payload()
    assert payload["validation_passed"]
    assert payload["lambda_D"] is None
    assert [row["route"][0] for row in payload["routes"]] == list("ABCDE")
    assert all(row["result"] not in {"DERIVED", "COMPLETE"} for row in payload["routes"])


def test_completion_gate_withholds_every_physical_output() -> None:
    payload = gate.completion_payload()
    assert payload["validation_passed"]
    assert payload["primary_verdict"] == FUNCTOR_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["Mark_I"] == "REACHED"
    assert payload["Mark_II"] == payload["Mark_III"] == payload["Mark_IV"] == "NOT_REACHED"
    assert payload["physical_outputs_promoted"] == []
    assert payload["frozen_predictions_changed"] is False


def test_materialization_is_deterministic_and_canonical_gate_is_current(tmp_path) -> None:
    first = gate.materialize(tmp_path)
    bytes_first = {path.name: path.read_bytes() for path in first}
    second = gate.materialize(tmp_path)
    assert bytes_first == {path.name: path.read_bytes() for path in second}
    assert len(first) == 19
    canonical = json.loads((tmp_path / "artifacts" / "BHSM_1_0_completion_gate.json").read_text())
    assert canonical["version"] == CURRENT_VERSION
    assert canonical["current_verdict"] == FUNCTOR_VERDICT


def test_all_v11_1_cli_commands_are_registered_and_emit_json(capsys) -> None:
    for command in gate.COMMAND_SECTIONS:
        assert cli.main([command, "--format", "json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["version"] == CURRENT_VERSION
        assert payload["primary_verdict"] == FUNCTOR_VERDICT


def test_recovery_cli_commands_fail_closed_and_are_machine_readable(capsys) -> None:
    for command in ("historical-recovery-status", "historical-object-search", "historical-equivalence-audit", "blocker-readiness-status"):
        assert cli.main([command, "--object", "support representation functor", "--format", "json"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload
    readiness = blocker_readiness_payload()
    assert readiness["blocker_may_be_emitted"] is readiness["historical_recovery_complete"]
