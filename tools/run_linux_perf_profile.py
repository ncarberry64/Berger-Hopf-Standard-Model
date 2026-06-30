"""Collect Linux perf counters for the native BHSM coordinate kernels."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any


EVENTS = (
    "task-clock",
    "cycles",
    "instructions",
    "branches",
    "branch-misses",
    "cache-references",
    "cache-misses",
    "L1-dcache-loads",
    "L1-dcache-load-misses",
    "LLC-loads",
    "LLC-load-misses",
)


def parse_perf_stat(text: str) -> dict[str, float]:
    counters: dict[str, float] = {}
    for raw_line in text.splitlines():
        fields = [field.strip() for field in raw_line.split(";")]
        if len(fields) < 3:
            continue
        value, event = fields[0], fields[2]
        if not event or value.startswith("<"):
            continue
        try:
            counters[event] = float(value.replace(",", ""))
        except ValueError:
            continue
    return counters


def derived_metrics(counters: dict[str, float]) -> dict[str, float | None]:
    def ratio(numerator: str, denominator: str) -> float | None:
        bottom = counters.get(denominator, 0.0)
        return counters.get(numerator, 0.0) / bottom if bottom else None

    return {
        "instructions_per_cycle": ratio("instructions", "cycles"),
        "branch_miss_rate": ratio("branch-misses", "branches"),
        "cache_miss_rate": ratio("cache-misses", "cache-references"),
        "l1_dcache_load_miss_rate": ratio("L1-dcache-load-misses", "L1-dcache-loads"),
        "llc_load_miss_rate": ratio("LLC-load-misses", "LLC-loads"),
    }


def profile_kernel(
    perf: str,
    executable: Path,
    csv_path: Path,
    kernel: str,
    repetitions: int,
    replication_factor: int,
) -> dict[str, Any]:
    command = [
        perf,
        "stat",
        "-x",
        ";",
        "-r",
        str(repetitions),
        "-e",
        ",".join(EVENTS),
        "--",
        str(executable),
        "--kernel",
        kernel,
        "--csv",
        str(csv_path),
        "--repeats",
        "1",
        "--replication-factor",
        str(replication_factor),
    ]
    environment = dict(os.environ)
    environment["LC_ALL"] = "C"
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    counters = parse_perf_stat(completed.stderr)
    benchmark = None
    for line in reversed(completed.stdout.splitlines()):
        try:
            benchmark = json.loads(line)
            break
        except json.JSONDecodeError:
            continue
    status = "PERF_COUNTERS_COLLECTED"
    if completed.returncode != 0 or not {"cycles", "instructions"} <= counters.keys():
        status = "PERF_COUNTERS_UNAVAILABLE_OR_PERMISSION_DENIED"
    return {
        "status": status,
        "kernel": kernel,
        "returncode": completed.returncode,
        "command": command,
        "benchmark": benchmark,
        "counters": counters,
        "derived": derived_metrics(counters),
        "stderr_tail": completed.stderr.splitlines()[-12:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--replication-factor", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    perf = shutil.which("perf")
    rows = []
    if perf:
        rows = [
            profile_kernel(
                perf,
                args.executable,
                args.data,
                kernel,
                args.repetitions,
                args.replication_factor,
            )
            for kernel in ("angular", "direct")
        ]
    status = (
        "PERF_COUNTERS_COLLECTED"
        if rows and all(row["status"] == "PERF_COUNTERS_COLLECTED" for row in rows)
        else "PERF_COUNTERS_UNAVAILABLE_OR_PERMISSION_DENIED"
    )
    payload = {
        "status": status,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "perf_path": perf,
        "events_requested": list(EVENTS),
        "rows": rows,
        "claim_boundary": "Hardware explanation remains open unless counters are collected on identified bare metal.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status={status} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
