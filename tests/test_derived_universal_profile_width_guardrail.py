import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_universal_profile_width_guardrail_forbids_flavor_generation_tuning():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_universal_profile_width_guardrail.md").read_text()

    assert fw.universal_width_guardrail() == (
        "sigma must be fixed by internal geometry and cannot be tuned by flavor or generation"
    )
    assert fw.universal_width_guardrail() in text
    assert "cannot be chosen separately by flavor, generation, or matrix entry" in text
    assert "UNIVERSAL_PROFILE_WIDTH_GUARDRAIL_DERIVED_CONDITIONAL" in text
