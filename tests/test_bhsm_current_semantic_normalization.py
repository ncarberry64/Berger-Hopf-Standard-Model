from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.current_semantic_normalization import (
    REQUIRED_RECORD_FIELDS,
    build_registries,
    validate_registries,
)


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "artifacts/current_semantics"
SCRIPT = ROOT / "scripts/materialize_bhsm_current_semantic_registries.py"


def _load() -> dict[str, dict]:
    return {path.name: json.loads(path.read_text(encoding="utf-8")) for path in TARGET.glob("*.json")}


def test_nine_registries_are_complete_and_validated() -> None:
    registries = _load()
    assert len(registries) == 9
    validate_registries(registries)
    for payload in registries.values():
        assert payload["validation_passed"] is True
        assert payload["FULL_BHSM_COMPLETE"] is False
        for row in payload["records"]:
            assert set(REQUIRED_RECORD_FIELDS) <= set(row)


def test_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in TARGET.glob("*.json")}
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in TARGET.glob("*.json")}
    assert before == after


def test_guardrail_rejects_z_as_p_squared() -> None:
    registries = _load()
    bad = deepcopy(registries)
    row = next(row for row in bad["BHSM_CURRENT_FORMULA_REGISTRY.json"]["records"] if row["canonical_id"] == "NEUTRAL_SPECTRAL_PARAMETER")
    row["formula"] = "z=p^2"
    with pytest.raises(ValueError, match=r"p\^2"):
        validate_registries(bad)


def test_guardrail_rejects_wrong_live_owner() -> None:
    registries = _load()
    bad = deepcopy(registries)
    dag = bad["BHSM_CURRENT_COMPLETION_DAG.json"]["records"]
    next(row for row in dag if row["canonical_id"] == "G7_05_FACTORIZED_LAP")["current_status"] = "CLOSED"
    next(row for row in dag if row["canonical_id"] == "G7_06_E1_FINITE")["current_status"] = "OPEN_CURRENT_OWNER"
    with pytest.raises(ValueError, match="wrong current owner"):
        validate_registries(bad)


def test_guardrail_rejects_reopened_nonfermion_threshold() -> None:
    registries = _load()
    bad = deepcopy(registries)
    row = next(row for row in bad["BHSM_CURRENT_FORMULA_REGISTRY.json"]["records"] if row["canonical_id"] == "NONFERMION_THRESHOLD_CLOSURE")
    row["current_status"] = "OPEN"
    with pytest.raises(ValueError, match="reopened"):
        validate_registries(bad)


def test_builder_rejects_missing_registry() -> None:
    registries = build_registries({})
    registries.pop("BHSM_CURRENT_GATE_LEDGER.json")
    with pytest.raises(ValueError, match="nine"):
        validate_registries(registries)


def test_recovered_owner_ontology_is_complete_and_not_action_derived() -> None:
    ontology = {row["canonical_id"]: row for row in _load()["BHSM_CURRENT_ONTOLOGY_REGISTRY.json"]["records"]}
    for canonical_id in (
        "ONTOLOGY_GEOMETRY_FIRST", "ONTOLOGY_PARTICLE_CLASS", "ONTOLOGY_GENERATIONS",
        "ONTOLOGY_MASS_READOUT", "ONTOLOGY_NEUTRINO_MASS", "ONTOLOGY_CKM",
        "ONTOLOGY_GAUGE_127", "ONTOLOGY_BARE_DRESSED", "ONTOLOGY_FROZEN_NO_RETUNE",
        "ONTOLOGY_FULL_COMPLETION",
    ):
        assert ontology[canonical_id]["current_status"].startswith("OWNER_AUTHORIZED")
        assert "ACTION_DERIVED" not in ontology[canonical_id]["current_status"]
