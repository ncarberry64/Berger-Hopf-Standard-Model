"""Promote the already-certified N12 persistence witness to a durable input."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
RESULT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_PERSISTENCE_WITNESS.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    direct = json.loads(DIRECT.read_text(encoding="utf-8"))
    candidates = [
        (name, digest)
        for name, digest in direct["certificate_inputs"].items()
        if name.endswith("persistence_final.json")
    ]
    if len(candidates) != 1:
        raise RuntimeError("direct certificate must own exactly one persistence input")
    source_name, expected_hash = candidates[0]
    source = ROOT / Path(source_name.replace("\\", "/"))
    if not source.is_file() or _sha256(source) != expected_hash:
        raise RuntimeError("certified persistence source is absent or hash-mismatched")
    witness = json.loads(source.read_text(encoding="utf-8"))
    retained_witness_checks = {
        name: bool(witness["validation"][name])
        for name in (
            "same_existing_persistence_domain_and_gates",
            "nonzero_motion_retained",
            "local_positive_duration_existence",
            "coarse_fine_numerical_witness",
        )
    }
    retained_witness_checks["no_new_physics_equation_constraint_or_gate"] = (
        witness["validation"]["new_physics_equation_constraint_or_gate"] is False
    )
    if not (
        direct["DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"]
        and all(retained_witness_checks.values())
    ):
        raise RuntimeError("direct promotion does not own this persistence witness")
    payload = {
        "artifact": "BHSM_N12_POSITIVE_DURATION_PERSISTENCE_WITNESS",
        "classification": witness["classification"],
        "source": source_name.replace("\\", "/"),
        "source_SHA256": expected_hash,
        "checkpoint": witness["checkpoint"].replace("\\", "/"),
        "checkpoint_SHA256": witness["checkpoint_SHA256"],
        "coarse_evolution": witness["coarse_evolution"],
        "fine_evolution": witness["fine_evolution"],
        "coarse_fine_relative_difference": witness[
            "coarse_fine_relative_difference"
        ],
        "local_existence": witness["local_existence"],
        "original_witness_validation": witness["validation"],
        "promotion_validation": {
            "source_hash_matches_direct_certificate": True,
            "direct_certificate_closes_root_ball": True,
            "retained_witness_checks": retained_witness_checks,
            "original_pre_promotion_root_ball_flag_was_false": (
                witness["validation"]["direct_N12_root_ball_certified"] is False
            ),
        },
        "validation_passed": True,
        "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED": True,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "result": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
        "source_SHA256": expected_hash,
        "validation_passed": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
