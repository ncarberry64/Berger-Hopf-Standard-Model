from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_n12_gate7_rank72_relative_form_tail.py"


def _module():
    spec = importlib.util.spec_from_file_location("rank72_relative_form_tail", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rank72_relative_form_tail_is_sharp_and_not_falsely_closed() -> None:
    payload = _module().build_payload()
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "RANK72_SOURCE_CONTRACTED_RELATIVE_FORM_CRITERION_SHARP_ACTUAL_TAIL_OPEN"
    )
    assert payload["numerical_identity_witness"]["seed_shape"] == [98, 72]
    assert payload["exact_criterion"]["ambient_adjoint_limit_required"] is False
    assert payload["common_scale_supersession"]["old_separate_optical_zeta_tail_obligation"] == "SUPERSEDED"
    assert payload["common_scale_supersession"]["seed_image_dimension_removed"] is False
    assert payload["availability_audit"]["rank72_maximal_relative_form_bound"] == "ACTUALLY_MISSING"
    assert payload["claim_boundary"]["rank72_joint_heat_minus_zeta_tail"] == "OPEN_CURRENT_OWNER"
    assert payload["FULL_BHSM_COMPLETE"] is False
