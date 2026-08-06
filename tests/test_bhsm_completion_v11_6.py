from __future__ import annotations

import numpy as np

from bhsm.interface.completion.ckm_action_equivalence_v11_6 import equivalence_payload
from bhsm.interface.completion.completion_gate_v11_6 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    completion_payload,
    materialize,
)
from bhsm.interface.completion.parent_action_charged_current_v11_6 import (
    action_owned_weak_basis_kernel,
    current_reduction_payload,
    parent_action_term_ledger,
)
from bhsm.interface.completion.spectral_current_uniqueness_v11_6 import uniqueness_payload


def test_live_action_mixed_variation_has_family_identity_kernel() -> None:
    kernel = action_owned_weak_basis_kernel()
    payload = current_reduction_payload()
    assert np.array_equal(kernel, np.eye(3))
    assert "delta_ij" in payload["calculation"]["mixed_variation"]
    assert payload["validation_passed"]
    assert payload["equivalence_result"].startswith("NOT_EQUIVALENT")


def test_provenance_ledger_does_not_promote_conditional_current_templates() -> None:
    ledger = parent_action_term_ledger()
    ownership = {row["ownership"] for row in ledger["sources"]}
    assert "EFFECTIVE_ACTION_OWNED" in ownership
    assert "AUTHOR_SELECTED_NO_FIT_ACTION_CANDIDATE" in ownership
    assert "ACTION_DERIVED_SPECTRAL_KERNEL" not in ownership
    assert ledger["parent_S8_current_source"] is None


def test_viability_axioms_leave_rephasing_inequivalent_continuous_family() -> None:
    payload = uniqueness_payload()
    assert payload["answer"] == "NO"
    assert payload["uniqueness_established"] is False
    assert payload["validation_passed"]
    assert payload["rephasing_invariant_magnitude_residual"] > 0
    assert all(abs(row["jarlskog"]) > 0 for row in payload["counterexamples"])


def test_action_equivalence_gate_fails_closed() -> None:
    payload = equivalence_payload()
    assert payload["validation_passed"]
    assert payload["physical_CKM_action_derived"] is False
    assert payload["result"].startswith("NOT_EQUIVALENT")


def test_v11_6_gate_identifies_one_narrower_action_object(tmp_path) -> None:
    gate = completion_payload()
    assert gate["validation_passed"]
    assert gate["Mark_III"] == "NOT_REACHED"
    assert gate["Mark_IV"] == "NOT_REACHED"
    assert gate["BHSM_1_0_release_complete"] is False
    assert gate["physical_CKM_derived"] is False
    assert gate["flavor_action_unconditionally_closed"] is False
    assert gate["exact_next_object"] == EXACT_NEXT_OBJECT
    assert gate["previous_exact_object"] == (
        "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL"
    )
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values()) | {
        "BHSM_1_0_completion_gate.json",
        "current_bhsm_status.json",
    }
