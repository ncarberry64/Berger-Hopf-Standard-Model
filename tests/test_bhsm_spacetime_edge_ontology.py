"""Regression guards for the BHSM spacetime-edge ontology separation."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from bhsm.interface.current_semantic_normalization import (
    build_registries,
    validate_registries,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "artifacts/flagship_integration/BHSM_SPACETIME_EDGE_ONTOLOGY_AUDIT.json"
THEOREM = ROOT / "theory/n12_c2_1064_to_1222_nested_weyl_increment.md"


def ontology() -> dict[str, dict[str, object]]:
    registries = build_registries({})
    return {
        row["canonical_id"]: row
        for row in registries["BHSM_CURRENT_ONTOLOGY_REGISTRY.json"]["records"]
    }


def test_finite_core_truncation_is_not_spacetime_edge() -> None:
    rows = ontology()
    assert rows["FORM_CORE_TRUNCATION_BOUNDARY"]["semantic_layer"] == "MATHEMATICAL_OBJECT"
    assert rows["FORM_CORE_TRUNCATION_BOUNDARY"]["mathematical_class"] == "PROOF_TRUNCATION_BOUNDARY"
    assert rows["SPACETIME_EDGE"]["mathematical_class"] == "SPACETIME_TO_AETHER_PHASE_LIMIT"
    assert rows["FORM_CORE_TRUNCATION_BOUNDARY"]["mathematical_class"] != rows["SPACETIME_EDGE"]["mathematical_class"]


def test_proof_cutoff_cannot_be_promoted_to_physical_endpoint() -> None:
    registries = build_registries({})
    bad = deepcopy(registries)
    row = next(
        item for item in bad["BHSM_CURRENT_ONTOLOGY_REGISTRY.json"]["records"]
        if item["canonical_id"] == "FORM_CORE_TRUNCATION_BOUNDARY"
    )
    row["semantic_layer"] = "BHSM_ONTOLOGY"
    with pytest.raises(ValueError, match="promoted to physical ontology"):
        validate_registries(bad)


def test_canonical_stop_is_not_spacetime_edge_without_theorem() -> None:
    rows = ontology()
    assert rows["CANONICAL_STOP_EVENT"]["mathematical_class"] == "ACTION_OWNED_FORWARD_HISTORY_TERMINATION_OR_TRANSITION"
    target = rows["CANONICAL_STOP_TO_SPACETIME_EDGE_IDENTIFICATION"]
    assert target["current_status"] == "OPEN_ACTION_LEVEL_IDENTIFICATION_NOT_GATE7_PREREQUISITE"
    assert target["mathematical_class"] == "OPEN_THEOREM_DEPENDENCY"


@pytest.mark.parametrize("invented_formula", ["Delta=0 equals spacetime edge", "s=0 equals spacetime edge"])
def test_algebraic_or_euler_dirac_stop_does_not_define_spacetime_edge(invented_formula: str) -> None:
    registries = build_registries({})
    bad = deepcopy(registries)
    row = next(
        item for item in bad["BHSM_CURRENT_ONTOLOGY_REGISTRY.json"]["records"]
        if item["canonical_id"] == "SPACETIME_EDGE"
    )
    row["formula"] = invented_formula
    with pytest.raises(ValueError, match="unproved spacetime-edge equation"):
        validate_registries(bad)


def test_core_boundary_and_spacetime_edge_cannot_be_merged() -> None:
    registries = build_registries({})
    bad = deepcopy(registries)
    row = next(
        item for item in bad["BHSM_CURRENT_ONTOLOGY_REGISTRY.json"]["records"]
        if item["canonical_id"] == "CORE_BOUNDARY"
    )
    row["mathematical_class"] = "SPACETIME_TO_AETHER_PHASE_LIMIT"
    with pytest.raises(ValueError, match="silently merged"):
        validate_registries(bad)


def test_gate7_theorem_uses_form_core_truncation_boundary_not_far_edge() -> None:
    text = THEOREM.read_text(encoding="utf-8")
    assert "far form-core truncation boundary" in text
    assert ("far " + "edge") not in text.lower()
    assert "proof cutoff, not an event, canonical stop, core boundary, or spacetime" in text


def test_audit_materialization_is_deterministic_and_complete() -> None:
    spec = importlib.util.spec_from_file_location(
        "spacetime_edge_audit", ROOT / "scripts/materialize_bhsm_spacetime_edge_ontology_audit.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    first = module.deterministic_json(module.build_payload())
    second = module.deterministic_json(module.build_payload())
    assert first == second
    stored = AUDIT.read_text(encoding="utf-8")
    assert stored == first
    payload = json.loads(stored)
    assert payload["validation_passed"] is True
    assert payload["current_ambiguous_occurrences"] == []
    assert payload["frozen_predictions_changed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["occurrence_count"] == len(payload["occurrences"])
