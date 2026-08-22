"""Hash-lock the N12 continuum-majorant effectiveness checkpoint."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "artifacts/n12_continuum_majorant_effectiveness"
MANIFEST = TARGET / "BHSM_N12_CONTINUUM_MAJORANT_CHECKPOINT_MANIFEST.json"
FILES = (
    "BHSM_N12_CONTINUUM_MAJORANT_OWNERSHIP_AUDIT.json",
    "BHSM_N12_EFFECTIVE_INVERSE_LOCALIZATION.json",
    "BHSM_N12_POSITIVE_DURATION_CALDERON_HISTORY.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    file_records = []
    for name in FILES:
        path = TARGET / name
        if not path.is_file():
            raise FileNotFoundError(path)
        file_records.append({
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        })

    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    payload = {
        "checkpoint": "N12_CONTINUUM_MAJORANT_EFFECTIVENESS_LOCALIZED",
        "scientific_base_commit": base,
        "classification": (
            "QUALITATIVE_SOURCE_RESTRICTED_CLOSED_RANGE_RETAINED;_"
            "NUMERICAL_CONTINUUM_RADIUS_REQUIRES_AN_EFFECTIVE_"
            "POSITIVE_DURATION_OBSERVATION_MODULUS"
        ),
        "claims": {
            "N12_static_Calderon_gap": 0.029146859835472938,
            "minimum_sampled_positive_duration_gap": 0.02882113423436863,
            "sampled_duration": 1.0e-10,
            "sampled_history_is_an_interval_proof": False,
            "principal_high_tail_bound_is_the_full_inverse_K": False,
            "qualitative_source_restricted_closed_range_invalidated": False,
            "soft_channel_classification": (
                "CATEGORY_2_DYNAMICALLY_CONTROLLED_NORMAL_DIRECTION"
            ),
            "category_3_collapse_sequence_constructed": False,
            "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "effective_dependency": {
            "first_missing_object": (
                "EFFECTIVE_SOURCE_RESTRICTED_POSITIVE_DURATION_"
                "OBSERVATION_COMPACTNESS_MODULUS"
            ),
            "finite_core_lemma": (
                "ENCLOSE_THE_N12_POSITIVE_DURATION_CALDERON_SYMBOL_GAP_"
                "ON_A_WHOLE_INTERVAL_WITH_AN_ACTION_OWNED_TIME_"
                "LIPSCHITZ_MAJORANT"
            ),
            "tail_lemma": (
                "BOUND_THE_INVERSE_SQUARE_SOURCE_RESTRICTED_STRONG_"
                "GRAPH_TAIL_IN_THE_POSITIVE_DURATION_OBSERVATION_NORM"
            ),
            "conclusion_if_closed": (
                "K<=1/(c_M0-epsilon_obs(M0))_WHEN_"
                "epsilon_obs(M0)<c_M0"
            ),
        },
        "promotion_boundary": (
            "THIS_CHECKPOINT LOCALIZES THE FIRST NON_EFFECTIVE CONSTANT. "
            "IT DOES NOT CERTIFY A CONTINUUM CHILD, Q_XI, DELTA_H, MASS, "
            "FAMILY SELECTION, OR A PREDICTION."
        ),
        "reproduction": [
            "$env:PYTHONPATH='src'; $env:BHSM_N12_CONTINUUM_MAJORANT_OWNERSHIP_RESULT='artifacts/n12_continuum_majorant_effectiveness/BHSM_N12_CONTINUUM_MAJORANT_OWNERSHIP_AUDIT.json'; python scripts/audit_n12_continuum_majorant_ownership.py",
            "$env:PYTHONPATH='src'; python scripts/materialize_n12_effective_inverse_localization.py",
            "$env:PYTHONPATH='src'; $env:BHSM_N12_HISTORY_CALDERON_RESULT='artifacts/n12_continuum_majorant_effectiveness/BHSM_N12_POSITIVE_DURATION_CALDERON_HISTORY.json'; python scripts/audit_n12_positive_duration_calderon_history.py",
            "$env:PYTHONPATH='src'; python scripts/materialize_n12_continuum_majorant_checkpoint.py",
        ],
        "files": file_records,
    }
    with MANIFEST.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
