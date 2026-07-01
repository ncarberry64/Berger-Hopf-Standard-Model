import hashlib
import json
from pathlib import Path

from bhsm.interface.primitive_charged_incidence import build_primitive_charged_incidence_report


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_no_empirical_inputs_or_frozen_changes():
    report = build_primitive_charged_incidence_report()
    for section in ("omega_trace", "rho_gcd", "projector_reduction", "overlap", "bridge_beta", "ckm_transport", "physical_normalization"):
        assert report[section]["empirical_inputs_used"] is False
        assert report[section]["forbidden_theorem_inputs_used"] == []
    for relative, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected


def test_all_v2_artifacts_parse_without_completion_claims():
    paths = sorted((ROOT / "artifacts").glob("BHSM_*_v2_0.json"))
    assert len(paths) == 10
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload
        assert "full Standard Model derivation" not in json.dumps(payload)
