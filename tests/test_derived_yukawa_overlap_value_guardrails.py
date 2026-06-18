import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_overlap_value_guardrail_document_forbids_fitting_and_hidden_tuning():
    d.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_overlap_value_guardrails.md").read_text()
    for phrase in [
        "no fitting measured masses",
        "no CKM/PMNS input",
        "no changing frozen outputs",
        "no sector exponent tuning",
        "no hidden post-hoc normalization",
    ]:
        assert phrase in text
