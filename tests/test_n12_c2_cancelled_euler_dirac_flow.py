from __future__ import annotations

import numpy as np
import importlib.util
from pathlib import Path

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (
    exact_cancelled_euler_dirac_field_action,
    exact_fixed_s_field_action,
)


ROOT = Path(__file__).resolve().parents[1]


def test_cancelled_field_recombines_exact_fixed_s_field() -> None:
    data = np.load(
        "artifacts/flagship_integration/"
        "BHSM_N12_C2_LOG_DESCRIPTOR_DELTA_STOP_RECONNAISSANCE.npz"
    )
    state = np.asarray(data["last_positive_state"], dtype=float)
    weights = np.asarray(data["state_weights"], dtype=float)
    reference = np.asarray(data["branch_reference"], dtype=float)
    import json
    record = json.loads(
        (ROOT / "artifacts" / "flagship_integration" /
         "BHSM_N12_C2_LOG_DESCRIPTOR_DELTA_STOP_RECONNAISSANCE.json")
        .read_text(encoding="utf-8")
    )
    descriptor = float(record["last_positive_signed_descriptor"])
    cancelled = exact_cancelled_euler_dirac_field_action(
        state=state, weights=weights, reference=reference,
        signed_descriptor=descriptor,
    )
    fixed = exact_fixed_s_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=descriptor,
    )
    assert cancelled["selected_branch"] == fixed["selected_branch"] == 24
    assert cancelled["selected_eigenline_gap"] > 0.0
    assert np.allclose(
        cancelled["cancelled_field_action"],
        float(cancelled["Delta"]) * np.asarray(fixed["field_action"]),
        rtol=2.0e-12,
        atol=1.0e-18,
    )
    assert np.isclose(
        cancelled["Dlambda_cancelled_field"], cancelled["Delta"],
        rtol=0.0, atol=0.0,
    )


def test_delta_zero_is_not_promoted_to_a_canonical_stop() -> None:
    script = ROOT / "scripts" / "audit_n12_c2_cancelled_euler_dirac_chart.py"
    spec = importlib.util.spec_from_file_location("cancelled_chart_audit", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"][
        "Delta_equals_zero_is_event_or_canonical_stop"
    ] is False
    assert payload["adjudication"]["validated_exact_family_crossing_Delta_zero"] is False
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
