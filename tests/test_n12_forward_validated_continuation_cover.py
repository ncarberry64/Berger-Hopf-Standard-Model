import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_VALIDATED_CONTINUATION_COVER.json"
)


def test_forward_validated_cover_has_exact_outcome_c_and_preserves_claims():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["hard_outcome"] == "C"
    assert float(payload["cover"]["certified_interval_extension_factor"]) > 1
    assert float(payload["event_and_domain_enclosure"][
        "ordered_event_lower_throughout_cover"
    ]) > 0
    assert payload["event_and_domain_enclosure"]["terminal_chart_hit"] is False
    assert payload["event_and_domain_enclosure"]["physical_domain_exit"] is False
    assert payload["cover_exhaustion"]["retained_action_obstruction_proved"] is False
    assert payload["claim_boundaries"]["Q_xi_or_Delta_H_unlocked"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
