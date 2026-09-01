from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface.localization_carrier_audit import (
    LocalizationCandidate,
    evaluate_localization_candidates,
)
from bhsm.interface.physical_encapsulation_identification import (
    KERNEL_REDUCTION,
    action_dependency_closure,
    tensor_factor_intertwiner_certificate,
)
from scripts.materialize_n12_gate7_localization_carrier_kill_screen import (
    build_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_n12_gate7_localization_carrier_kill_screen.py"
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_LOCALIZATION_CARRIER_KILL_SCREEN.json"
)


def test_current_unchanged_ae2_has_no_qualifying_carrier() -> None:
    payload = build_payload()
    audit = payload["carrier_audit"]
    assert audit["carrier_exists_in_audited_unchanged_ae2"] is False
    assert audit["qualifying_candidate_ids"] == []
    assert len(audit["candidates"]) == 6
    assert payload["action_extension_boundary"]["extension_authorized_here"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_four_kernel_reduction_and_subclosures_are_explicit() -> None:
    payload = build_payload()
    assert len(KERNEL_REDUCTION) == 4
    assert [row["kernel_id"] for row in payload["four_kernel_reduction"]] == [
        "KERNEL_A",
        "KERNEL_B",
        "KERNEL_C",
        "KERNEL_D",
    ]
    assert payload["four_kernel_reduction"][0]["status"].startswith(
        "UNCHANGED_AE2_KILL_SCREEN_COMPLETE"
    )
    subrows = payload["subrequirement_resolution"]
    assert subrows["PEI_05a_fermionic_event_child_reset_trace_matching"] == "AVAILABLE"
    assert subrows["PEI_11a_tensor_factor_family_reset_intertwiner"] == "AVAILABLE"
    assert subrows["PEI_11b_family_mode_projector_instantiated_on_actual_C2_parent"] == "OPEN"


def test_tensor_factor_intertwiner_is_exact_but_not_physical_transport() -> None:
    lift = np.array([[0.0, 1.0], [-1.0, 0.0]])
    projector = np.diag([0.0, 1.0, 0.0])
    certificate = tensor_factor_intertwiner_certificate(lift, projector)
    assert certificate["algebraic_intertwiner_certified"] is True
    assert certificate["commutator_residual"] == 0.0
    assert certificate["c2_family_mode_slot_instantiated"] is False
    assert certificate["physical_enclosure_transport_proved"] is False


def test_dependency_closure_is_transitive_and_sector_scoped() -> None:
    dependencies = {
        "charged_mode": {"fermion_trace", "family_projector"},
        "fermion_trace": {"spin_gauge_bundle", "current"},
        "current": {"gauge_trace"},
        "unrelated_sector": {"unused"},
    }
    assert action_dependency_closure({"charged_mode"}, dependencies) == {
        "charged_mode",
        "fermion_trace",
        "family_projector",
        "spin_gauge_bundle",
        "current",
        "gauge_trace",
    }


def test_candidate_evaluator_requires_the_full_carrier_type() -> None:
    partial = LocalizationCandidate(
        "partial", "partial", True, False, False, True, False, "evidence", "wrong type"
    )
    result = evaluate_localization_candidates([partial])
    assert result["carrier_exists_in_audited_unchanged_ae2"] is False


def test_materialized_kill_screen_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    payload = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert payload["validation_passed"] is True
    assert payload["status"].startswith("UNCHANGED_AE2_LOCALIZATION_CARRIER_NOT_FOUND")
