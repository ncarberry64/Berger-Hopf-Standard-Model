"""Checks for the Gate-7 recentered-cone internal bordered response."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_RECENTERED_CONE_BORDERED_RHS_RESPONSE.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def test_complete_recentered_cone_response_is_certified() -> None:
    payload = _load(RESULT)
    rows = payload["rows"]
    assert payload["validation_passed"] is True
    assert payload["mesh"]["parent_cells"] == 3009
    assert payload["mesh"]["cells"] == 24072
    assert payload["mesh"]["projection_dimension"] == 101
    assert payload["mesh"]["base_response_refinement"] == 8
    assert payload["mesh"]["late_response_refinement"] == 8
    assert len(rows) == 24072
    assert all(row["selected_branch"] == 24 for row in rows)
    assert all(row["projection_dimension"] == 101 for row in rows)
    assert all(row["relative_bordered_operator_perturbation_upper"] < 1.0 for row in rows)
    assert all(math.isfinite(row["complete_bordered_response_2_norm_upper"]) for row in rows)
    assert all(row["center_internal_rhs_finite"] for row in rows)
    assert all(row["bordered_response_tube_finite"] for row in rows)


def test_each_parent_is_exactly_replaced_by_eight_ordered_children() -> None:
    payload = _load(RESULT)
    grouped: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for row in payload["rows"]:
        grouped[(int(row["seam"]), int(row["parent_local_index"]))].append(row)
    assert len(grouped) == 3009
    for children in grouped.values():
        children.sort(key=lambda row: int(row["child_within_parent"]))
        assert [int(row["child_within_parent"]) for row in children] == list(range(8))
        assert all(int(row["response_refinement_per_parent"]) == 8 for row in children)
        assert all(
            math.isclose(
                float(left["action_interval"][1]),
                float(right["action_interval"][0]),
                rel_tol=0.0,
                abs_tol=2.0e-15,
            )
            for left, right in zip(children, children[1:])
        )


def test_closed_system_source_ontology_and_claim_boundary() -> None:
    payload = _load(RESULT)
    validation = payload["validation"]
    assert payload["source_ontology"].startswith("EXTERNAL_CAUCHY_BIRTH_SOURCE_ZERO")
    assert validation["only_external_Cauchy_birth_source_zero_internal_rhs_retained"] is True
    assert validation["no_internal_child_contact_or_transport_response_zeroed"] is True
    assert validation["no_added_seam_force_or_double_counted_response"] is True
    assert validation["no_full_kinetic_Dirac_or_history_inverse_used"] is True
    assert payload["claim_boundary"]["recentered_cone_bordered_hard_response"] == (
        "CERTIFIED_FINITE"
    )
    assert payload["claim_boundary"]["recentered_cone_response_first_variation_tube"] == "OPEN"
    assert payload["claim_boundary"]["Gate7"] == "ACTIVE"
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_response_input_hashes_match_disk() -> None:
    payload = _load(RESULT)
    for relative, expected in payload["inputs"].items():
        assert _sha256(ROOT / relative) == expected

