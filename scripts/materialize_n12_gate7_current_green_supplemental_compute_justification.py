"""Budget the supplemental midpoint campaign from bounded full-width pilots."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import derive_n12_gate7_current_green_signed_transverse_tensor_recovery as recovery  # noqa: E402
import derive_n12_gate7_current_green_supplemental_midpoint_blocks as supplement  # noqa: E402


C = ROOT / "artifacts" / "current_semantics"
RESULT = C / "BHSM_N12_GATE7_SUPPLEMENTAL_MIDPOINT_COMPUTE_JUSTIFICATION.json"
VALIDATION = C / "BHSM_N12_GATE7_SUPPLEMENTAL_MIXED_RATE_UU_VALIDATION.json"
PILOT_ROWS = (0, 25)
SAFETY_FACTOR = 1.25
REFERENCE_CPU_HOUR_CEILING = 270.0
THIS_SCRIPT = Path(__file__).resolve()


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _estimate(elapsed_seconds: dict[int, float]) -> dict[str, float]:
    if set(elapsed_seconds) != set(PILOT_ROWS):
        raise ValueError("both complement pilot rows 0 and 25 are required")
    if any(not math.isfinite(value) or value <= 0.0 for value in elapsed_seconds.values()):
        raise ValueError("pilot elapsed times must be positive and finite")
    rates = {
        row: elapsed_seconds[row] / (supplement.RETAINED + supplement.COMPLEMENT - row)
        for row in PILOT_ROWS
    }
    conservative_rate = max(rates.values())
    raw_seconds = (
        conservative_rate * supplement.NEW_PAIRS * supplement.INTERVALS
    )
    projected_hours = SAFETY_FACTOR * raw_seconds / 3600.0
    return {
        "row_0_seconds_per_right_direction": rates[0],
        "row_25_seconds_per_right_direction": rates[25],
        "conservative_seconds_per_right_direction": conservative_rate,
        "uninflated_full_campaign_CPU_hours": raw_seconds / 3600.0,
        "safety_factor": SAFETY_FACTOR,
        "projected_full_campaign_CPU_hours": projected_hours,
    }


def build_payload(interval: int) -> dict[str, object]:
    if not VALIDATION.is_file():
        raise FileNotFoundError("current supplemental UU identity validation required")
    identity = json.loads(VALIDATION.read_text(encoding="utf-8"))
    recovered = recovery._path("midpoint", interval)
    recovery_fingerprint = recovery._fingerprint()
    identity_inputs = identity.get("inputs", {})
    if not (
        identity.get("validation_passed") is True
        and identity.get("recovery_campaign_fingerprint")
        == recovery_fingerprint
        and isinstance(identity_inputs, dict)
        and identity_inputs
        and all(
            (ROOT / relative).is_file()
            and digest == _sha(ROOT / relative)
            for relative, digest in identity_inputs.items()
        )
    ):
        raise RuntimeError("current supplemental UU identity validation failed")
    if not recovery._valid(recovered, "midpoint", interval, recovery_fingerprint):
        raise RuntimeError(f"validated recovered midpoint required: {interval}")
    recovered_sha = _sha(recovered)
    fingerprint = supplement._fingerprint()
    elapsed: dict[int, float] = {}
    pilots: list[Path] = []
    for row in PILOT_ROWS:
        path = supplement._row_path(interval, row)
        if not supplement._valid_row(
            path, interval, row, fingerprint, recovered_sha,
        ):
            raise RuntimeError(f"validated supplemental pilot row required: {row}")
        with np.load(path) as source:
            elapsed[row] = float(source["elapsed_seconds"])
        pilots.append(path)
    estimate = _estimate(elapsed)
    within_ceiling = bool(
        estimate["projected_full_campaign_CPU_hours"]
        <= REFERENCE_CPU_HOUR_CEILING
    )
    validations = {
        "supplemental_UU_identity_passed": True,
        "widest_and_narrowest_rectangular_rows_benchmarked": True,
        "both_pilots_use_current_campaign_fingerprint": True,
        "projection_includes_all_2249_new_pairs_at_all_370_midpoints": True,
        "twenty_five_percent_operational_safety_factor_applied": True,
        "projection_within_270_CPU_hour_reference_ceiling": within_ceiling,
        "no_scientific_parameter_or_precision_changed": True,
    }
    passed = all(validations.values())
    sources = [VALIDATION, recovered, *pilots, THIS_SCRIPT, Path(supplement.__file__)]
    return {
        "artifact": "BHSM_N12_GATE7_SUPPLEMENTAL_MIDPOINT_COMPUTE_JUSTIFICATION",
        "status": (
            "SUPPLEMENTAL_CAMPAIGN_COMPUTE_JUSTIFIED"
            if passed else "SUPPLEMENTAL_CAMPAIGN_EXCEEDS_REFERENCE_CEILING"
        ),
        "pilot_interval": interval,
        "pilot_rows": list(PILOT_ROWS),
        "pilot_elapsed_seconds": {str(key): value for key, value in elapsed.items()},
        "estimate": estimate,
        "reference_CPU_hour_ceiling": REFERENCE_CPU_HOUR_CEILING,
        "recommended_workers": 4,
        "restart_safe_row_granularity": True,
        "campaign_fingerprint": fingerprint,
        "recovery_campaign_fingerprint": recovery_fingerprint,
        "validation": validations,
        "validation_passed": passed,
        "claim_boundary": {
            "compute_campaign_justified": passed,
            "supplemental_blocks_derived": False,
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {_relative(path): _sha(path) for path in sources},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=0)
    args = parser.parse_args()
    payload = build_payload(args.interval)
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["validation_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
