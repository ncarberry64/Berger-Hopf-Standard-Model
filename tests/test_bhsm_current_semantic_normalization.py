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
    next(row for row in dag if row["canonical_id"] == "G7_07_ANGULAR_TAIL")["current_status"] = "OPEN_CURRENT_OWNER"
    next(row for row in dag if row["canonical_id"] == "G7_08_FORCE")["current_status"] = "PENDING"
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
        "ONTOLOGY_FINITE_ENCAPSULATION", "ONTOLOGY_ENCAPSULATION_CHRONOLOGY",
    ):
        assert ontology[canonical_id]["current_status"].startswith("OWNER_AUTHORIZED")
        assert "ACTION_DERIVED" not in ontology[canonical_id]["current_status"]


def test_source_dini_is_canonical_and_strict_power_excess_is_not_compulsory() -> None:
    registries = _load()
    formula = next(
        row for row in registries["BHSM_CURRENT_FORMULA_REGISTRY.json"]["records"]
        if row["canonical_id"] == "SOURCE_WEIGHTED_THRESHOLD_MEASURE"
    )
    assert formula["formula"] == "integral_(0,1]_lambda^(-1)*d|nu_h|(lambda)<infinity"
    assert formula["current_status"] == "DINI_CLOSED_ALL_ADMISSIBLE_TAILS_BY_COMPACT_VOL_TERRA_TRACE_CLASS"
    deprecation = next(
        row for row in registries["BHSM_FORMULA_DEPRECATION_LEDGER.json"]["records"]
        if row["canonical_id"] == "DEPRECATE_STRICT_POWER_EXCESS"
    )
    assert deprecation["current_status"] == "SUFFICIENT_NOT_NECESSARY_AFTER_CRITICAL_BESSEL_THEOREM"


def test_one_sided_w_only_event_initialization_is_superseded() -> None:
    registries = _load()
    basis = {
        row["canonical_id"]: row
        for row in registries["BHSM_CURRENT_MATHEMATICAL_BASIS.json"]["records"]
    }
    seam = basis["AE2_SEAM_OPERATOR"]
    assert seam["formula"] == (
        "S_AE2(z)=M_event(z)+U_R^dagger*M_child(z)*U_R+W_phys"
    )
    assert seam["current_status"] == (
        "BROADLY_ENCLOSED_FULL_NEGATIVE_AXIS_ACTUAL_TRACE_OPEN"
    )
    deprecations = {
        row["canonical_id"]: row
        for row in registries["BHSM_FORMULA_DEPRECATION_LEDGER.json"]["records"]
    }
    assert deprecations["DEPRECATE_W_ONLY_EVENT_INITIALIZATION"][
        "current_status"
    ] == "SUPERSEDED_BY_TWO_SIDED_AE2_SEAM"


def test_replacement_force_is_constraint_projected_without_reset_selection() -> None:
    registries = _load()
    basis = {
        row["canonical_id"]: row
        for row in registries["BHSM_CURRENT_MATHEMATICAL_BASIS.json"]["records"]
    }
    projected = basis["CONSTRAINT_PROJECTED_REPLACEMENT_FORCE"]
    assert projected["formula"].startswith("N_phys^dagger*q_rep=0")
    assert projected["current_status"] == (
        "DERIVED_CRITERION_ACTUAL_PROJECTED_FORCE_AND_JOINT_SADDLE_OPEN"
    )
    assert "choose a reset-fiber representative by hand" in projected[
        "forbidden_interpretations"
    ]
    oracle = basis["PARAMETRIC_RESET_FIBER_EXTERIOR_ORACLE"]
    assert oracle["current_status"] == (
        "REGULARITY_THEOREM_DERIVED_ACTUAL_PARAMETRIC_ORACLE_OR_"
        "FIBER_INVARIANCE_OPEN"
    )
    assert "one reset representative determines the fiber force" in oracle[
        "forbidden_interpretations"
    ]
    radius_jet = basis["RESET_FIBER_RADIUS_CAUCHY_JET"]
    assert radius_jet["current_status"] == (
        "DERIVED_PARAMETRIC_EXTERIOR_ORACLE_STILL_OPEN"
    )
    assert "common scale is an exact gauge of the complete retained action" in (
        radius_jet["forbidden_interpretations"]
    )
    solver = basis["FINITE_STRATUM_WEYL_JET_SOLVER"]
    assert solver["current_status"] == (
        "DERIVED_ACTUAL_PARAMETRIC_FINITE_STRATUM_DATA_OPEN"
    )
    assert "the two-chord validation cutoff is a physical force endpoint" in (
        solver["forbidden_interpretations"]
    )
    dag = {
        row["canonical_id"]: row
        for row in registries["BHSM_CURRENT_COMPLETION_DAG.json"]["records"]
    }
    assert dag["G7_08_FORCE"]["current_status"] == "OPEN_CURRENT_OWNER"
    assert (
        "infinite nonencapsulating NHIM histories are preserved as nonrealized mathematics"
        in dag["G7_08_FORCE"]["physical_meaning"]
    )
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_ASYMPTOTIC_NHIM_ANGULAR_FORCE_NO_GO.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert "quotient-Cauchy tail" in dag["G7_08_FORCE"]["physical_meaning"]
    assert "ambient absolute weighted norm is sufficient but not necessary" in dag[
        "G7_08_FORCE"
    ]["physical_meaning"]
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_C2_PROJECTED_ADJOINT_CAUCHY_CRITERION.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert "common-scale Jacobi zeta optical Cauchy tail" in dag[
        "G7_08_FORCE"
    ]["physical_meaning"]
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_C2_INFINITE_HEAT_ZETA_COMPATIBILITY.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert "analytic full 57 by 196 historical reset Jacobian" in dag[
        "G7_08_FORCE"
    ]["physical_meaning"]
    assert "event block has certified rank 32" in dag[
        "G7_08_FORCE"
    ]["physical_meaning"]
    assert "projection onto the 73-dimensional constrained child manifold is submersive" in dag[
        "G7_08_FORCE"
    ]["physical_meaning"]
    assert "E0 -> C1 ->[T>0] E1 -> C2" in dag["G7_08_FORCE"]["physical_meaning"]
    assert "positive-duration local existence is now closed" in dag[
        "G7_08_FORCE"
    ]["physical_meaning"]
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_LOCAL_RESET_TERMINAL_TRANSVERSALITY_AUDIT.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_FINITE_TERMINAL_FORWARD_COMPONENT_COMPATIBILITY.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert (
        "artifacts/flagship_integration/"
        "BHSM_N12_FINITE_TERMINAL_TWO_SIDED_FORWARD_INTERFACE.json"
        in dag["G7_08_FORCE"]["provenance"]
    )
    assert dag["G7_09_SADDLE"]["current_status"] == (
        "PENDING_COUPLED_TO_G7_08"
    )
