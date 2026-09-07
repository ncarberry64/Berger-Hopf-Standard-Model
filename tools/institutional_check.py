"""Offline, bounded institutional readiness check; never starts proof workers."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CORE = ("numpy", "scipy", "sympy", "mpmath", "pytest")
SMOKE_TESTS = (
    "tests/test_engine_invariant_preservation.py",
    "tests/test_engine_physics_status_separation.py",
    "tests/test_ae4_event_response_jet_integration.py",
)
FROZEN = {
    "docs/frozen_predictions.md": "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    "docs/frozen_predictions.json": "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def check(profile="core", smoke=False):
    requirements = CORE + (("python-flint",) if profile == "rigorous" else ())
    packages = {}
    for name in requirements:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    files = {}
    for name, expected in FROZEN.items():
        path = ROOT / name
        actual = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest().upper() if path.is_file() else None
        files[name] = {"sha256": actual, "unchanged": actual == expected}
    revision = None
    if shutil.which("git"):
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10)
        if proc.returncode == 0:
            revision = proc.stdout.strip()
    system_map = ROOT / "artifacts/current_semantics/BHSM_CURRENT_SYSTEM_INTEGRATION_MAP.json"
    payload = json.loads(system_map.read_text(encoding="utf-8")) if system_map.is_file() else {}
    checks = {
        "supported_python": sys.version_info >= (3, 10),
        "required_dependencies_present": all(packages.values()),
        "frozen_prediction_integrity": all(row["unchanged"] for row in files.values()),
        "current_system_map_present_and_valid": payload.get("validation_passed") is True,
        "completion_not_overclaimed": payload.get("FULL_BHSM_COMPLETE") is False,
    }
    smoke_result = {"requested": smoke, "executed": False}
    if smoke and all(checks.values()):
        try:
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", *SMOKE_TESTS], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
            smoke_result.update(executed=True, exit_code=proc.returncode, output=proc.stdout + proc.stderr)
            checks["bounded_smoke_passed"] = proc.returncode == 0
        except subprocess.TimeoutExpired:
            smoke_result.update(executed=True, timed_out=True)
            checks["bounded_smoke_passed"] = False
    elif smoke:
        checks["bounded_smoke_passed"] = False
    return {
        "schema": "BHSM_INSTITUTIONAL_READINESS_V1", "profile": profile,
        "python": platform.python_version(), "platform": platform.system(),
        "revision": revision, "packages": packages, "frozen_files": files,
        "checks": checks, "smoke": smoke_result, "passed": all(checks.values()),
        "optional_runtimes": {name: bool(shutil.which(name)) for name in ("root-config", "cmake", "wolframscript", "docker", "node")},
        "scientific_status": "GATE7_ACTIVE__PHYSICAL_COMPLETION_OPEN",
        "network_or_proof_campaign_started": False,
        "license": "Noncommercial academic evaluation permission; see ACADEMIC_USE.md",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("core", "rigorous"), default="core")
    parser.add_argument("--smoke", action="store_true", help="run a bounded offline test set, with a 180-second timeout")
    parser.add_argument("--json", type=Path, dest="output", help="write a machine-readable local report")
    args = parser.parse_args()
    report = check(args.profile, args.smoke)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("BHSM institutional check: " + ("PASS" if report["passed"] else "FAIL"))
    for name, passed in report["checks"].items():
        print(f"{'PASS' if passed else 'FAIL'} {name}")
    print("Software and evidence checks only; physical completion remains open.")
    if not report["passed"]:
        missing = [name for name, version in report["packages"].items() if version is None]
        if missing:
            print("Missing dependencies: " + ", ".join(missing))
        if report["smoke"].get("output"):
            print(report["smoke"]["output"])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
