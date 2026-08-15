from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pytest

from bhsm.interface.aether_core_surface_trace_v15_11 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    compactified_core_compatibility,
    completion_payload,
    deterministic_json,
    evaluate_v15_10_selection,
    evaluate_v15_9_core_match,
    haar_endpoint_domain_payload,
    materialize,
    reciprocal_attachment_trace,
    surface_capacity_classification,
    weighted_haar_energy_lower_bound,
)


ROOT = Path(__file__).resolve().parents[1]


def test_reciprocal_attachment_selects_exact_compactified_trace() -> None:
    row = reciprocal_attachment_trace(0.25, 4.0)
    assert row["incidence_wall"] == 1.0
    assert row["dressed_wall"] == row["dressed_core"] == 2.0
    closure = compactified_core_compatibility()
    assert closure["core_compatible_zero_set"].startswith("upsilon|B=0")
    assert closure["regular_reconstructible_trace"] is False
    assert closure["geometric_consequence"] == "g5|B=0_as_a_covariant_two_tensor"


def test_reciprocal_trace_rejects_nonregular_support() -> None:
    with pytest.raises(ValueError, match="regular support"):
        reciprocal_attachment_trace(0.0, 1.0)


def test_sharp_weighted_haar_capacity_bound() -> None:
    bound = weighted_haar_energy_lower_bound(2.0, 1.0, 0.5, 3.0)
    assert bound == pytest.approx(4.0 * math.log(2.0) ** 2 / 6.0)
    assert math.isinf(weighted_haar_energy_lower_bound(1.0, 1.0, 0.0, 2.0))


def test_capacity_distinguishes_regular_surface_from_degenerate_escape() -> None:
    regular = surface_capacity_classification(2.0)
    assert regular["dirichlet_capacity"] == 0.5
    assert regular["positive_capacity"] is True
    assert regular["upsilon_zero_finite_Haar_energy"] is False
    degenerate = surface_capacity_classification(math.inf)
    assert degenerate["dirichlet_capacity"] == 0.0
    assert degenerate["upsilon_zero_finite_Haar_energy"] is None
    assert "without_an_ordinary" in degenerate["zero_capacity_interpretation"]


def test_core_endpoint_is_limit_point_not_a_passage_extension() -> None:
    payload = haar_endpoint_domain_payload()
    assert payload["infinite_endpoint_classification"] == "WEYL_LIMIT_POINT"
    assert payload["additional_self_adjoint_boundary_condition_at_core_endpoint"] is False
    assert payload["L2_Green_flux_at_infinity"] == 0
    assert payload["terminal_Dirichlet_data_creates_transfer_channel"] is False


def test_full_nonlinear_v15_9_branch_never_reaches_trace() -> None:
    payload = evaluate_v15_9_core_match((1.001, 1.01), modes=12)
    assert payload["branch"].startswith("full_nonlinear_v15_9")
    assert payload["constraint_spatially_constant_on_branch"] is True
    assert payload["dynamic_outer_layer_selected_by_core_constraint"] is False
    assert all(row["degree"] == pytest.approx(1.0, abs=2e-12) for row in payload["rows"])
    assert all(row["Euler_residual_inf"] < 2e-8 for row in payload["rows"])
    assert all(row["core_constraint_support_component"] == 1.0 for row in payload["rows"])
    assert all(not row["core_compatible_layer_exists"] for row in payload["rows"])


def test_core_match_does_not_select_v15_10_witnesses() -> None:
    payload = evaluate_v15_10_selection()
    assert payload["witness_labels"] == ["A", "B", "C"]
    assert payload["selector_jacobian_dM_d_alpha_r_gamma"] == [0, 0, 0]
    assert payload["surviving_physical_equivalence_classes"] == 3
    assert payload["response_nonuniqueness_resolved"] is False
    assert payload["F_alpha_zero_necessary_for_core_match"] is False
    assert payload["F_alpha_zero_sufficient_for_core_match"] is False


def test_completion_claim_boundary_and_terminal_obstruction() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["scientific_terminal_condition"].startswith("GENUINE_MATHEMATICAL")
    assert payload["response_and_passage"]["candidate_action_completion_adopted"] is False
    assert payload["response_and_passage"]["surface_passage_map_defined"] is False
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_PREGEOMETRIC_CORE_BOUNDARY")


def test_deterministic_materialization_and_committed_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.11"
    first = materialize(tmp_path / "a")
    second = materialize(tmp_path / "b")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    committed = ROOT / "artifacts" / first.name
    assert first.read_bytes() == committed.read_bytes()
