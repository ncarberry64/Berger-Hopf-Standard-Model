"""Materialize the final Track-1 start-condition adjudication."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.gate7_final_start_condition import (  # noqa: E402
    adjudicate_track1_start_condition,
)


F = ROOT / "artifacts/flagship_integration"
CENTER = F / "BHSM_N12_GATE7_CURRENT_GREEN_FULL_TRANSVERSE_QUADRATIC_CENTER.json"
MIXED = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_TRANSPORT.json"
RESULT = F / "BHSM_N12_GATE7_FINAL_START_CONDITION.json"
THEORY = ROOT / "theory/n12_gate7_final_start_condition.md"
MODULE = ROOT / "src/bhsm/interface/gate7_final_start_condition.py"
THIS_SCRIPT = Path(__file__).resolve()


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _verify_local_shards(work: Path, fingerprint: str) -> None:
    expected = [
        *(work / f"endpoint_{index:03d}.npz" for index in range(1, 371)),
        *(work / f"midpoint_{index:03d}.npz" for index in range(370)),
    ]
    missing = [path for path in expected if not path.is_file()]
    invalid: list[Path] = []
    for path in expected:
        if not path.is_file():
            continue
        try:
            with np.load(path) as source:
                valid = bool(
                    str(source["campaign_fingerprint"].item()) == fingerprint
                    and np.isfinite(float(source["quadratic_Frobenius_norm"]))
                    and np.all(np.isfinite(source["quadratic_output_Frobenius_norms"]))
                )
        except Exception:
            valid = False
        if not valid:
            invalid.append(path)
    if missing or invalid:
        raise RuntimeError(
            f"full-transverse shard validation failed: "
            f"missing={len(missing)}, invalid={len(invalid)}"
        )


def build_payload(verify_shards: Path | None = None) -> dict[str, object]:
    center = json.loads(CENTER.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    verdict = adjudicate_track1_start_condition(center, mixed)
    if verify_shards is not None:
        _verify_local_shards(verify_shards, verdict["campaign_fingerprint"])
    validation = {
        "center_aggregate_certificate_valid": center["validation_passed"] is True,
        "all_740_center_shards_certified_complete": (
            verdict["shards"]["missing_shards"] == 0
            and verdict["shards"]["invalid_shards"] == 0
        ),
        "campaign_fingerprint_frozen": bool(verdict["campaign_fingerprint"]),
        "mixed_causal_operator_reused": verdict["mixed_causal_operator"][
            "reused_without_recomputation"
        ],
        "center_majorant_not_promoted_to_outward_authority": not verdict[
            "full_transverse"
        ]["full_operator_bound_derived"],
        "two_radius_and_Gate7_not_fabricated": (
            verdict["two_radius_Volterra_screen"] == "NOT_DERIVED"
            and verdict["Gate7_mathematical_verdict"] == "OPEN"
        ),
        "Track2_mutation_authorized": False,
        "FULL_BHSM_COMPLETE": False,
    }
    passed = all(
        value for key, value in validation.items()
        if key not in {"Track2_mutation_authorized", "FULL_BHSM_COMPLETE"}
    ) and not validation["Track2_mutation_authorized"] and not validation[
        "FULL_BHSM_COMPLETE"
    ]
    inputs = {
        _relative(path): _sha(path)
        for path in (CENTER, MIXED, THEORY, MODULE, THIS_SCRIPT)
    }
    return {
        "artifact": "BHSM_N12_GATE7_FINAL_START_CONDITION",
        "status": "TRACK1_INCOMPLETE_AT_TRANSVERSE_OUTWARD_REMAINDER",
        "authority": (
            "FINAL_START_CONDITION_ADJUDICATION_FROM_CERTIFIED_CENTER_AGGREGATE_"
            "AND_REUSED_MIXED_CAUSAL_OPERATOR"
        ),
        **verdict,
        "Track2_final_integration_authorized": False,
        "claim_boundary": {
            "TRACK1_EXPENSIVE_FULL_TRANSVERSE_CENTER_CAMPAIGN_COMPLETE": True,
            "TRACK1_FULL_TRANSVERSE_OUTWARD_OPERATOR_DERIVED": False,
            "TRACK1_TWO_RADIUS_VOLTERRA_SCREEN_DERIVED": False,
            "TRACK1_GATE7_FINAL_VERDICT_RESOLVED": False,
            "TRACK2_FINAL_INTEGRATION_REACHED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": inputs,
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-shards", type=Path)
    parser.add_argument("--output", type=Path, default=RESULT)
    args = parser.parse_args()
    payload = build_payload(
        args.verify_shards.resolve() if args.verify_shards else None
    )
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "missing_shards": payload["shards"]["missing_shards"],
        "invalid_shards": payload["shards"]["invalid_shards"],
        "track1_final_start_condition_met": payload[
            "track1_final_start_condition_met"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
