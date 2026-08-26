"""Reissue the decisive and complete suppressed-R bounds on segment 1214."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RADIUS = 5.5212888273161885e-11
THEORY = ROOT / "theory" / "n12_c2_segment1214_joint_domain_extension.md"
REDUCED = BASE / "BHSM_N12_C2_SEGMENT1214_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"
SUPPRESSED_ROW = BASE / "BHSM_N12_C2_SEGMENT1214_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE.json"
COMPLETE = BASE / "BHSM_N12_C2_SEGMENT1214_JOINT_COMPLETE_SUPPRESSED_R_OPERATOR.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def run(script: str, environment: dict[str, str]) -> None:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script)],
        cwd=ROOT,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(completed.stdout, end="")
    if completed.returncode != 0:
        raise RuntimeError(f"{script} failed with exit code {completed.returncode}")


def mark_segment(path: Path, artifact: str, status: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["artifact"] = artifact
    payload["status"] = status
    payload["segment_joint_domain"] = {
        "segment": [1214, 1215],
        "state_action_radius": RADIUS,
        "strict_extension_of_endpoint_tube": True,
    }
    payload.setdefault("inputs", {})[
        THEORY.relative_to(ROOT).as_posix()
    ] = sha256(THEORY)
    driver = Path(__file__).resolve()
    payload["inputs"][driver.relative_to(ROOT).as_posix()] = sha256(driver)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-reduced", action="store_true")
    args = parser.parse_args()
    environment = os.environ.copy()
    environment["BHSM_C2_TUBE_RADIUS"] = repr(RADIUS)
    environment["BHSM_C2_REDUCED_ROW_RESULT"] = str(REDUCED)
    if not args.reuse_reduced or not REDUCED.is_file():
        run("certify_n12_c2_fully_reduced_signed_row.py", environment)
    reduced = mark_segment(
        REDUCED,
        "BHSM_N12_C2_SEGMENT1214_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE",
        "C2_SEGMENT1214_DOMINANT_FULLY_REDUCED_cb_ROW_CERTIFIED;_s_HARD_ROW_OPEN",
    )
    if reduced.get("validation_passed") is not True:
        raise ArithmeticError("segment decisive reduced row did not validate")

    environment.update({
        "BHSM_C2_REDUCED_ROW_INPUT": str(REDUCED),
        "BHSM_C2_SUPPRESSED_ROW_RESULT": str(SUPPRESSED_ROW),
        "BHSM_C2_SUPPRESSED_ROW_THEORY": str(THEORY),
    })
    run("certify_n12_c2_suppressed_hard_response_row.py", environment)
    suppressed = mark_segment(
        SUPPRESSED_ROW,
        "BHSM_N12_C2_SEGMENT1214_SUPPRESSED_HARD_RESPONSE_ROW_CERTIFICATE",
        "C2_SEGMENT1214_COMPLETE_SIGNED_D2DELTA_DOMINANT_ROW_CERTIFIED",
    )
    if suppressed.get("validation_passed") is not True:
        raise ArithmeticError("segment suppressed hard-response row did not validate")

    environment.update({
        "BHSM_C2_SUPPRESSED_ROW_INPUT": str(SUPPRESSED_ROW),
        "BHSM_C2_COMPLETE_SUPPRESSED_R_RESULT": str(COMPLETE),
        "BHSM_C2_COMPLETE_SUPPRESSED_R_THEORY": str(THEORY),
    })
    run("certify_n12_c2_complete_suppressed_r_operator.py", environment)
    complete = mark_segment(
        COMPLETE,
        "BHSM_N12_C2_SEGMENT1214_JOINT_COMPLETE_SUPPRESSED_R_OPERATOR",
        "C2_SEGMENT1214_JOINT_COMPLETE_SUPPRESSED_R_OPERATOR_CERTIFIED",
    )
    complete["adjudication"]["segment1214_joint_non_scale_sR_operator"] = (
        "CERTIFIED"
    )
    complete["exact_next_dependency"] = (
        "ADD_THIS_REISSUED_SEGMENT1214_JOINT_sR_BOUND_TO_THE_REISSUED_"
        "JOINT_NON_SCALE_cb_OPERATOR"
    )
    COMPLETE.write_text(
        json.dumps(complete, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    if complete.get("validation_passed") is not True:
        raise ArithmeticError("segment complete suppressed-R operator did not validate")
    print(json.dumps({
        "status": complete["status"],
        "joint_action_radius": RADIUS,
        "decisive_cb_row_upper": reduced["fully_reduced_cb_row_2_norm_upper"],
        "suppressed_row_upper": suppressed[
            "s_suppressed_R_second_row_2_norm_upper"
        ],
        "complete_sR_operator_upper": complete[
            "complete_s_suppressed_R_second_operator_2_norm_upper"
        ],
        "validation_passed": True,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
