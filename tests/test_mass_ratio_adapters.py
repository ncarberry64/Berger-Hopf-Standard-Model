import hashlib
from pathlib import Path

from bhsm.interface.mass_ratio_adapters import load_charged_lepton_ratio_artifact, load_mass_ratio_predictions_artifact, load_quark_ratio_artifact

ROOT = Path(__file__).resolve().parents[1]
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_mass_ratio_adapters_read_frozen_internal_artifact():
    all_ratios = load_mass_ratio_predictions_artifact(ROOT)
    leptons = load_charged_lepton_ratio_artifact(ROOT)
    quarks = load_quark_ratio_artifact(ROOT)
    assert all_ratios.source_status == leptons.source_status == quarks.source_status == "DISCOVERED"
    assert all_ratios.provenance.frozen_prediction is True
    assert all_ratios.provenance.empirical_derivation_input is False
    assert quarks.value["BHSM_BARE_V1"]["up_quark_ratios"]["middle"] == 0.008310500554068288
    assert quarks.value["BHSM_DRESSED_V1_CANDIDATE"]["up_quark_ratios"]["middle"] == 0.004155250277034144


def test_frozen_prediction_files_are_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
