from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_minimal_branch_threshold import build_payload  # noqa: E402


FORBIDDEN_COEFFICIENTS = {
    "a_lepton",
    "a_up",
    "a_down",
    "mu_factor",
    "electron_factor",
    "charm_factor",
    "up_factor",
    "strange_factor",
    "down_factor",
}


def test_candidate_laws_are_unofficial_and_universal() -> None:
    payload = build_payload(ROOT)
    for law in payload["candidate_law_results"]:
        assert law["official"] is False
        assert law["parameter_policy"] == "single_universal_parameter_set"
        assert set(law["coefficients"]).isdisjoint(FORBIDDEN_COEFFICIENTS)


def test_no_sector_or_per_particle_coefficients_are_used() -> None:
    serialized = json.dumps(build_payload(ROOT))
    for key in FORBIDDEN_COEFFICIENTS:
        assert key not in serialized
    assert "sector-specific" not in serialized.lower()
    assert "per-particle" not in serialized.lower()


def test_overfit_warning_present_for_high_parameter_laws() -> None:
    laws = {law["law_id"]: law for law in build_payload(ROOT)["candidate_law_results"]}
    assert laws["A_branch_rank_only"]["overfit_risk"] is False
    for law_id in (
        "B_branch_rank_plus_type",
        "C_bounded_norm_plus_type",
        "D_log_threshold_plus_type",
        "E_branch_rank_mixed_penalty",
        "F_orientation_cross",
    ):
        assert laws[law_id]["overfit_risk"] is True
    assert "OVERFIT_RISK_WARNING" in build_payload(ROOT)["verdict_labels"]


def test_base_candidate_claims_not_upgraded() -> None:
    text = (ROOT / "theory" / "minimal_branch_threshold_reconstruction.md").read_text(
        encoding="utf-8"
    )
    assert "`BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived" in text
    assert "`FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived" in text
    assert "`RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived" in text
