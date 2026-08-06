from __future__ import annotations

from math import isclose

import numpy as np

from bhsm.interface.completion.completion_gate_v11_5 import ARTIFACT_FILES, EXACT_NEXT_OBJECT, completion_payload, materialize
from bhsm.interface.completion.spectral_charged_current_v11_5 import current_payload, spectral_angles, spectral_current_kernel


def test_spectral_rule_reproduces_frozen_no_fit_ckm_candidate() -> None:
    angles = spectral_angles()
    assert isclose(angles["sin_theta_12"], 0.2256184580048353)
    assert isclose(angles["sin_theta_23"], 0.04386794299087895)
    assert isclose(angles["sin_theta_13"], 0.0035623676140463315)
    assert isclose(angles["delta"], 1.1283791670955126)


def test_spectral_kernel_is_full_rank_unitary_and_cp_odd() -> None:
    kernel = spectral_current_kernel()
    payload = current_payload()
    assert np.linalg.matrix_rank(kernel) == 3
    assert np.linalg.norm(kernel.conj().T @ kernel - np.eye(3)) < 1e-12
    assert payload["jarlskog"] > 0
    assert payload["validation_passed"]
    assert payload["measured_mixing_inputs"] == []
    assert payload["action_derived"] is False
    assert payload["provenance_gate_satisfied"] is False


def test_weak_current_closes_su2_without_neutral_fcnc() -> None:
    payload = current_payload()
    assert max(payload["SU2_residuals"].values()) < 1e-12
    assert payload["validation"]["neutral_current_family_central"]
    assert payload["new_coefficients"] == []


def test_v11_5_gate_keeps_mark_iii_open_at_provenance_boundary(tmp_path) -> None:
    gate = completion_payload()
    assert gate["validation_passed"]
    assert gate["Mark_III"] == "NOT_REACHED"
    assert gate["Mark_IV"] == "NOT_REACHED"
    assert gate["BHSM_1_0_release_complete"] is False
    assert gate["exact_next_object"] == EXACT_NEXT_OBJECT
    assert gate["spectral_charged_current"]["action_derived"] is False
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values()) | {"BHSM_1_0_completion_gate.json"}
