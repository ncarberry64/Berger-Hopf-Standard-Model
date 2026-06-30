"""Run process-isolated ROOT implicit-multithreading scaling rows."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any


def parse_threads(value: str) -> list[int]:
    threads = [int(item) for item in value.split(",") if item.strip()]
    if not threads or any(item <= 0 for item in threads) or len(set(threads)) != len(threads):
        raise ValueError("thread counts must be unique positive integers")
    return threads


def run_row(executable: Path, threads: int, entries: int, repeats: int) -> dict[str, Any]:
    completed = subprocess.run(
        [
            str(executable),
            "--threads",
            str(threads),
            "--entries",
            str(entries),
            "--repeats",
            str(repeats),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout)
    for line in reversed(completed.stdout.splitlines()):
        try:
            payload = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    else:
        raise RuntimeError("ROOT IMT executable did not emit JSON")
    if payload.get("checksum_ok") is not True:
        raise RuntimeError("ROOT IMT checksum failed")
    return payload


def add_scaling_metrics(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline = next((row for row in rows if row["threads"] == 1), None)
    if baseline is None:
        raise ValueError("thread scan must include a one-thread baseline")
    baseline_rate = float(baseline["entries_per_second"])
    for row in rows:
        speedup = float(row["entries_per_second"]) / baseline_rate
        row["speedup_vs_one_thread"] = speedup
        row["parallel_efficiency"] = speedup / int(row["threads"])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--threads", default="1,2,4")
    parser.add_argument("--entries", type=int, default=2_000_000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    thread_counts = parse_threads(args.threads)
    rows = add_scaling_metrics(
        [run_row(args.executable, count, args.entries, args.repeats) for count in thread_counts]
    )
    payload = {
        "status": "ROOT_IMT_SCALING_MEASURED_ENVIRONMENT_SPECIFIC",
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "entries": args.entries,
        "repeats": args.repeats,
        "rows": rows,
        "all_checksums_pass": all(row["checksum_ok"] for row in rows),
        "claim_boundaries": [
            "environment-specific concurrency measurement",
            "no linear scaling claim from a two-core hosted runner",
            "no detector reconstruction workload",
            "larger 16/32/64-core scans require allocated bare-metal or cluster nodes",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status={payload['status']} rows={len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
