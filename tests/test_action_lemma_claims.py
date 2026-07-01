import hashlib
from pathlib import Path

from bhsm.interface.action_lemmas import build_action_lemma_closure_report


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_claims_and_frozen_outputs_remain_guarded():
    report = build_action_lemma_closure_report()
    assert report["full_completion_claimed"] is False
    assert report["official_predictions_modified"] is False
    assert report["ckm_application"]["ckm_exponent_derived"] is False
    for section in ("source_search", "primitive_lattice", "maximal_overlap", "abstract_log_transport", "ckm_application"):
        assert report[section]["empirical_inputs_used"] is False
        assert report[section]["forbidden_theorem_inputs_used"] == []
    for relative, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
