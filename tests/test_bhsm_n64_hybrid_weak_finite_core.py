import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/n12_continuum_majorant_effectiveness"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_v_m_fiber_localizes_eta_boundary_before_finite_core_closure():
    payload = _load("BHSM_N64_HYBRID_WEAK_FINITE_CORE.json")
    assert payload["final"]["exact_hybrid_weak_norm"] > 0.1
    assert 0.0 < payload["final"]["eta"]["event"] < 1.0e-3
    assert payload["history"][-1]["accepted_factor"] == 0.0
    assert payload["final"]["normal_rank"] == 258
    assert payload["final"]["boundary_norm"] < 1.0e-12
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_existing_geometry_directions_remain_proposal_only():
    payload = _load("BHSM_N64_HYBRID_WEAK_SCALE_STEP.json")
    assert payload["accepted"] is True
    assert payload["exact_norm_after"] < payload["exact_norm_before"]
    assert payload["eta"]["event"] > 0.0
    assert payload["boundary_norm"] < 1.0e-12
    assert payload["normal_rank"] == 258
    assert payload["geometry_direction"]["joint_boundary_linear_defect"] < 1.0e-12
    assert payload["state_artifact"]["status"] == (
        "FINITE_ANALYTIC_CORE_NOT_A_COMPLETE_CHILD_ROOT"
    )
    assert payload["M_star_certified"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
