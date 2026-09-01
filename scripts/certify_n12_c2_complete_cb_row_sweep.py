"""Run resumable signed C2 ``D2(cb)`` row shards on the non-scale sector."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
ENDPOINT_ROW_ENGINE = (
    ROOT / "scripts" / "audit_n12_c2_reduced_ddelta_operator_majorant.py"
)
SEGMENT_ROW_ENGINE = (
    ROOT / "scripts" / "audit_n12_c2_segment1214_joint_ddelta_operator_majorant.py"
)
ONE_AXIS = (
    ROOT / "src" / "bhsm" / "interface"
    / "aether_retained_action_one_axis_interval.py"
)
ENDPOINT_ROW_DIRECTORY = BASE / ".n12_c2_complete_cb_rows"
SEGMENT_ROW_DIRECTORY = BASE / ".n12_c2_segment1214_joint_cb_rows"
ENDPOINT_RADIUS = 5.5104723095444935e-11
SEGMENT_RADIUS = 5.5212888273161885e-11


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def provenance_paths(row_engine: Path) -> list[Path]:
    names = [
        "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.json",
        "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz",
        "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.json",
        "BHSM_N12_C2_DIRECT_DDELTA_ROW_RECONNAISSANCE.npz",
        "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json",
        "BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.npz",
        "BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP.json",
        "BHSM_N12_C2_FRESH_CHART_FIXED_S_GROWTH.json",
        "BHSM_N12_C2_SIGNED_FIRST_COEFFICIENT_VECTORS.json",
        "BHSM_N12_C2_SIGNED_FIRST_COEFFICIENT_VECTORS.npz",
        "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json",
    ]
    engines = [row_engine, ONE_AXIS]
    if row_engine == SEGMENT_ROW_ENGINE:
        engines.insert(0, ENDPOINT_ROW_ENGINE)
    return [BASE / name for name in names] + engines


def parse_rows(specification: str) -> list[int]:
    rows: set[int] = set()
    for item in specification.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            start_text, stop_text = item.split(":", 1)
            rows.update(range(int(start_text), int(stop_text)))
        else:
            rows.add(int(item))
    result = sorted(rows)
    if not result or any(row < 1 or row >= 98 for row in result):
        raise ValueError("row shards must be a nonempty subset of 1,...,97")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", default="1:98")
    parser.add_argument("--result")
    parser.add_argument("--no-reuse", action="store_true")
    parser.add_argument(
        "--profile", choices=("endpoint", "segment1214"), default="endpoint"
    )
    args = parser.parse_args()
    rows = parse_rows(args.rows)
    segment_profile = args.profile == "segment1214"
    row_engine = SEGMENT_ROW_ENGINE if segment_profile else ENDPOINT_ROW_ENGINE
    row_directory = (
        SEGMENT_ROW_DIRECTORY if segment_profile else ENDPOINT_ROW_DIRECTORY
    )
    radius = SEGMENT_RADIUS if segment_profile else ENDPOINT_RADIUS
    paths = provenance_paths(row_engine)
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing cb row-sweep inputs: " + ", ".join(missing))
    inputs = {path.relative_to(ROOT).as_posix(): sha256(path) for path in paths}
    fingerprint = hashlib.sha256(
        json.dumps(inputs, sort_keys=True).encode("utf-8")
    ).hexdigest().upper()
    row_directory.mkdir(parents=True, exist_ok=True)
    result_path = (
        Path(args.result).resolve() if args.result else
        BASE / (
            f".tmp_BHSM_N12_C2_{'SEGMENT1214_JOINT_' if segment_profile else ''}"
            f"COMPLETE_CB_ROWS_{rows[0]:03d}_{rows[-1]:03d}.json"
        )
    )
    records: list[dict[str, object]] = []
    for count, row in enumerate(rows, start=1):
        row_path = row_directory / f"row_{row:03d}.json"
        reusable = False
        if row_path.is_file() and not args.no_reuse:
            stored = json.loads(row_path.read_text(encoding="utf-8"))
            reusable = (
                stored.get("row") == row
                and stored.get("sweep_input_fingerprint") == fingerprint
                and all(stored.get("validation", {}).values())
            )
        if reusable:
            record = stored
            print(f"REUSE row {row:03d} ({count}/{len(rows)})", flush=True)
        else:
            print(f"START row {row:03d} ({count}/{len(rows)})", flush=True)
            environment = os.environ.copy()
            environment["BHSM_C2_DIAGNOSTIC_ROW_RESULT"] = str(row_path)
            completed = subprocess.run(
                [
                    sys.executable, str(row_engine), "--signed-row", str(row),
                    "--cb-only",
                ],
                cwd=ROOT,
                env=environment,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if completed.returncode != 0:
                print(completed.stdout, flush=True)
                raise RuntimeError(f"cb row {row} failed")
            record = json.loads(row_path.read_text(encoding="utf-8"))
            record["sweep_input_fingerprint"] = fingerprint
            record["sweep_inputs"] = inputs
            row_path.write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n",
                encoding="utf-8", newline="\n",
            )
            print(
                f"DONE row {row:03d}: "
                f"{float(record['complete_cb_row_upper']):.17g}",
                flush=True,
            )
        if not all(record.get("validation", {}).values()):
            raise ArithmeticError(f"row {row} coefficient bootstrap did not close")
        records.append(record)
        partial_frobenius = math.nextafter(math.sqrt(math.fsum(
            float(item["complete_cb_row_upper"]) ** 2 for item in records
        )), math.inf)
        partial = {
            "artifact": "BHSM_N12_C2_COMPLETE_CB_ROW_SWEEP_PARTIAL",
            "status": "SIGNED_NON_SCALE_CB_ROW_SHARD_CERTIFIED",
            "rows_requested": rows,
            "rows_completed": [int(item["row"]) for item in records],
            "row_count": len(records),
            "partial_Frobenius_upper": partial_frobenius,
            "maximum_row_upper": max(
                float(item["complete_cb_row_upper"]) for item in records
            ),
            "maximum_b_i_radius_needed": max(
                float(item["b_i_radius_needed"]) for item in records
            ),
            "maximum_c_i_radius_needed": max(
                float(item["c_i_radius_needed"]) for item in records
            ),
            "lambda_i_radius_needed_global": math.nextafter(
                986.016684739049 * radius, math.inf
            ),
            "common_scale_row_0": (
                "EXCLUDED_FROM_PATHWISE_JACOBI_BY_CERTIFIED_EXACT_"
                "COMMON_SCALE_WEYL_COVARIANCE"
            ),
            "sweep_input_fingerprint": fingerprint,
            "profile": args.profile,
            "state_action_radius": radius,
            "inputs": inputs,
            "rows": records,
            "validation_passed": True,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        }
        result_path.write_text(
            json.dumps(partial, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(json.dumps({
        "status": partial["status"],
        "rows_completed": partial["row_count"],
        "partial_Frobenius_upper": partial["partial_Frobenius_upper"],
        "maximum_row_upper": partial["maximum_row_upper"],
        "result": str(result_path),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
