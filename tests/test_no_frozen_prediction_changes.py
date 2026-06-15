from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN_MD_SHA256 = "A413C72F731A15B5AF0ED4DDDC3A58D428A60BA3367676FFCDA03FF546593439"
FROZEN_JSON_SHA256 = "A9735A4A17934B524C4DE317254AE40838078FBA99274C95C0DBAE11A43C6C17"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_frozen_prediction_files_are_unchanged_by_candidate_theory_sprint() -> None:
    assert _sha(ROOT / "docs" / "frozen_predictions.md") == FROZEN_MD_SHA256
    assert _sha(ROOT / "docs" / "frozen_predictions.json") == FROZEN_JSON_SHA256


def test_frozen_branch_labels_and_dressing_rule_are_unchanged() -> None:
    payload = json.loads((ROOT / "docs" / "frozen_predictions.json").read_text(encoding="utf-8"))

    assert payload["branches"]["bare"] == "BHSM_BARE_V1"
    assert payload["branches"]["dressed_candidate"] == "BHSM_DRESSED_V1_CANDIDATE"
    assert payload["dressing_rule"] == {
        "affects_only": "c/t",
        "factor": 0.5,
        "status": "CANDIDATE",
    }
    assert payload["constants"]["a"] == 1.157054135733433
    assert payload["constants"]["S"] == 0.07957747154594767
    assert payload["outputs"]["c/t"]["changed"] is True
    assert payload["outputs"]["u/t"]["changed"] is False
    assert payload["outputs"]["sin_theta_13"]["changed"] is False


def test_candidate_theory_files_do_not_modify_official_values() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "theory" / "full_bhsm_candidate_theory_line_v0_1.md",
            ROOT / "theory" / "sector_target_degree_law.md",
            ROOT / "theory" / "generation_count_fourth_order_stability.md",
            ROOT / "theory" / "bare_yukawa_spectral_action.md",
            ROOT / "theory" / "boundary_interface_mixing_kernel.md",
            ROOT / "theory" / "neutrino_conjugate_cover_mass_engine.md",
        ]
    ).lower()
    assert "must not update official predictions" in text or "no official prediction is changed" in text
    assert "hidden retuning" not in text
    assert "derived full standard model" not in text
