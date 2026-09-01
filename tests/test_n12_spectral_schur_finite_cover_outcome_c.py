import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_SPECTRAL_SCHUR_FINITE_COVER_OUTCOME_C.json"
)


def test_spectral_schur_finite_cover_outcome_c() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["classification"].startswith("OUTCOME_C_")
    frontier = payload["authoritative_frontier"]
    assert frontier["coordinate_time"] == 8.327231167169652e-16
    assert frontier["corrected_event_lower"] > 0.0
    assert frontier["terminal_event_hit"] is False
    assert frontier["physical_domain_exit"] is False
    assert payload["cover_exhaustion"]["physical_obstruction_identified"] is False
    assert payload["claim_boundary"]["intrinsic_state_selection"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
