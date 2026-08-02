from __future__ import annotations

import hashlib
import json
from math import isclose

from sympy import Matrix, Rational

from bhsm.interface import cli
from bhsm.interface.completion.attachment_boundary_core_domain_v11_3 import boundary_payload, core_payload, on_constraint_terms
from bhsm.interface.completion.attachment_character_derivation_v11_3 import W_CORE, W_WALL, character_payload, constraint_matrix_payload, total_weight
from bhsm.interface.completion.attachment_exchange_current_v11_3 import current_payload, transfer_vectors
from bhsm.interface.completion.attachment_incidence_ledger_v11_3 import BASE_MAIN_SHA, BASE_TREE_SHA, ledger_payload
from bhsm.interface.completion.mark_ii_gate_v11_3 import ARTIFACT_FILES, COMMAND_SECTIONS, MARK_STATUS, completion_payload, materialize
from bhsm.interface.completion.reciprocal_attachment_action_v11_3 import EXACT_NEXT_OBJECT, PRIMARY_VERDICT, attachment_density, mismatch, qd_source
from bhsm.interface.completion.three_mode_action_v11_3 import constraint_jacobian, kinetic_matrix, tangent_basis, three_mode_payload


def test_exact_baseline_and_compatibility_action_recovery() -> None:
    assert BASE_MAIN_SHA == "1aa1ebf1c924e494c903e794aaed5f0d7d42e173"
    assert BASE_TREE_SHA == "8975c13c1993dcca1e88a73d28e613b22704ac6d"
    payload = ledger_payload()
    assert payload["validation_passed"]
    assert payload["selected_core_incidence"] == "Q_H(G8)"
    assert payload["selected_wall_incidence"] == "id_5(g5)"
    assert payload["normalization"] == 1
    assert payload["new_objects"] == []


def test_reciprocal_half_characters_and_neutral_density() -> None:
    assert W_CORE == Rational(-1, 2)
    assert W_WALL == Rational(1, 2)
    assert abs(W_CORE - W_WALL) == 1
    assert total_weight(Rational(1, 2), W_CORE) == 0
    assert total_weight(Rational(-1, 2), W_WALL) == 0
    payload = character_payload()
    assert payload["characters"]["h_enc"] == "0"
    assert payload["attachment_subsystem"]["rank"] == 5
    assert payload["attachment_subsystem"]["nullity"] == 0


def test_frozen_limit_multiplier_variation_and_qd_sign() -> None:
    assert mismatch(1.0, 3.0, 5.0) == 2.0
    assert attachment_density(1.0, 3.0, 5.0, 7.0) == 14.0
    assert mismatch(0.25, 4.0, 1.0) == 0.0
    assert isclose(qd_source(1.0, 2.0, 2.0, 3.0, 5.0), -1.2)


def test_algebraic_attachment_has_exact_zero_A_terms_and_closes_stress_transfer() -> None:
    payload = current_payload()
    assert payload["linear_A_D_term"] == 0
    assert payload["quadratic_A_D_term"] == 0
    assert payload["normal_momentum_shift"] == 0
    assert payload["new_boundary_flux"] == 0
    qc, qw, qd = transfer_vectors(4.0, -1.0)
    assert qc + qw + qd == 0
    assert payload["validation_passed"]


def test_boundary_differentiability_and_core_asymptotic_finiteness() -> None:
    boundary = boundary_payload()
    core = core_payload()
    assert boundary["bulk_variation_boundary_term"] == 0
    assert boundary["presymplectic_potential_attachment"] == 0
    left, right = on_constraint_terms(1e-12, 2.0)
    assert left == right and left < 1e-5
    assert core["finite_action"] and core["finite_symplectic_flux"]
    assert core["wall_suppression"].endswith("->0")
    assert "separate" in core["core_entry"]


def test_expanded_character_matrix_rank_nullity_and_weight_propagation() -> None:
    payload = constraint_matrix_payload()
    assert payload["rank"] == 11
    assert payload["nullity"] == 8
    assert "w_C" in payload["pivot_columns"]
    assert "w_W" in payload["pivot_columns"]
    assert payload["physical_character_directions"] == []
    rows = character_payload()["primitive_field_propagation"]
    assert all(row["linear_A_D_coupling"] == row["quadratic_A_D_coupling"] == 0 for row in rows)
    assert all(row["support_weight"] == 0 for row in rows)


def test_three_mode_kinetic_operator_and_conditional_Hessian() -> None:
    B = constraint_jacobian()
    N = tangent_basis()
    K = kinetic_matrix()
    assert B == Matrix([[-1, 1, 1]])
    assert B * N == Matrix.zeros(1, 2)
    assert K.rank() == 3
    payload = three_mode_payload()
    assert payload["reduced_kinetic_matrix"] == [[2, 1], [1, 2]]
    assert payload["reduced_kinetic_eigenvalues"] == [1, 3]
    assert payload["physical_mode_count"] == 2
    assert payload["three_physical_slots_collapsed"] is False
    assert payload["stability_status"].startswith("CONDITIONAL")


def test_mark_ii_is_conditional_on_one_exact_operator_block() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["mark_ii_status"] == MARK_STATUS == "BHSM_MARK_II_REACHED_CONDITIONALLY"
    assert payload["conditions_open"] == ["physical_three_mode_kinetic_Hessian_operator"]
    assert payload["physical_outputs_promoted"] == []
    assert payload["frozen_predictions_changed"] is False


def test_deterministic_materialization_and_required_artifacts(tmp_path) -> None:
    first_paths = materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert len(ARTIFACT_FILES) == 10
    assert set(ARTIFACT_FILES.values()) <= first.keys()
    assert len(first) == 11  # ten v11.3 artifacts plus the canonical gate
    assert {name: hashlib.sha256(data).hexdigest() for name, data in first.items()} == {name: hashlib.sha256(data).hexdigest() for name, data in second.items()}


def test_cli_json_markdown_and_historical_compatibility(capsys) -> None:
    for command in COMMAND_SECTIONS:
        assert cli.main([command, "--format", "json"]) == 0
        assert json.loads(capsys.readouterr().out)["version"] == "v11.3"
        assert cli.main([command, "--format", "markdown"]) == 0
        assert PRIMARY_VERDICT in capsys.readouterr().out
    assert cli.main(["physical-completion-status-v11-2", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["version"] == "v11.2"
    assert cli.main(["physical-completion-status-v11-1", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["version"] == "v11.1"
