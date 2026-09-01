from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_n12_gate7_seed_image_ward_gauge.py"


def _module():
    spec = importlib.util.spec_from_file_location("seed_image_ward_gauge", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rank72_seed_image_is_not_removed_by_a_Ward_or_gauge_shortcut() -> None:
    payload = _module().build_payload()
    linear = payload["exact_linear_algebra"]
    assert payload["validation_passed"] is True
    assert payload["status"] == "WARD_GAUGE_SHORTCUT_EXHAUSTED_RANK72_TAIL_RETAINED"
    assert linear["rank"] == 26
    assert linear["nullity"] == 72
    assert linear["seed_image_equation_residual_norm"] < 1.0e-10
    assert linear["seed_image_kernel_projector_residual_norm"] < 1.0e-10
    assert payload["Ward_BRST_adjudication"]["universal_closed_functional_zero_force"] is False
    assert payload["gauge_time_adjudication"]["global_98_state_Cauchy_generator_supplied"] is False
    assert payload["remaining_owner"]["dimension"] == 72
    assert payload["claim_boundary"]["remaining_reset_generated_seed_image_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["FULL_BHSM_COMPLETE"] is False
