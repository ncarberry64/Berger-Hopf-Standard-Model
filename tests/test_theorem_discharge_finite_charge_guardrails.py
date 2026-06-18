import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_algebra_charge as discharge  # noqa: E402


def test_mission_language_and_replacement_guardrails():
    discharge.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_finite_algebra_charge.md").read_text(encoding="utf-8")
    assert discharge.MISSION_LANGUAGE in text
    assert discharge.replacement_claim_ready() is False

    forbidden_phrases = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "replacement claim is ready",
        "full gauge dynamics are derived",
        "masses/Yukawas/mixings are derived",
    ]
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "theory" / "theorem_discharge_finite_algebra_charge.md",
            ROOT / "theory" / "derived_finite_algebra_uniqueness.md",
            ROOT / "theory" / "derived_boundary_charge_operator.md",
            ROOT / "theory" / "derived_boundary_hypercharge_operator.md",
            ROOT / "theory" / "finite_algebra_charge_non_tautology_audit.md",
        ]
    )
    for phrase in forbidden_phrases:
        assert phrase not in combined


def test_result_payload_keeps_downstream_work_open():
    payload = discharge.build_results_payload()
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert "anomaly cancellation as boundary consistency theorem" in payload["still_open_downstream"]
    assert "gauge group dynamics derivation" in payload["still_open_downstream"]
    assert "mass/Yukawa/mixing theorem-level derivation" in payload["still_open_downstream"]
