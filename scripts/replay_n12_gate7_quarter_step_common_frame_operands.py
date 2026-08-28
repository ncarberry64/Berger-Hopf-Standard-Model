"""Replay the selected quarter-step Gate-7 common-frame operands.

This wrapper fixes the center and output names before invoking the existing
first-hit, dense-residual, and exact graph-Jacobian implementations.  It then
rebuilds the common-frame matching audit.  No numerical method or proof
threshold is changed here.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
FIRST_HIT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json"
RESIDUAL = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.json"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.json"
HYBRID_AUDIT = BASE / "BHSM_N12_GATE7_QUARTER_STEP_HYBRID_GRAPH_JACOBIAN_EQUIVALENCE_AUDIT.json"


def _run(script: str, arguments: list[str], environment: dict[str, str]) -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *arguments],
        cwd=ROOT,
        env=environment,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(6, os.cpu_count() or 1))
    args = parser.parse_args()
    if not CENTER.is_file():
        raise FileNotFoundError(CENTER)

    base_environment = os.environ.copy()
    base_environment["BHSM_N12_STOP_CENTER_DATA"] = str(CENTER)

    environment = base_environment.copy()
    environment["BHSM_N12_STOP_FIRST_HIT_RESULT"] = str(FIRST_HIT)
    _run("audit_n12_c2_stop_dense_descriptor_first_hit.py", [], environment)

    environment = base_environment.copy()
    environment["BHSM_N12_STOP_DENSE_RESIDUAL_RESULT"] = str(RESIDUAL)
    _run(
        "recon_n12_c2_stop_dop853_dense_residual.py",
        ["--workers", str(args.workers), "--samples-per-interval", "12"],
        environment,
    )

    environment = base_environment.copy()
    environment["BHSM_N12_STOP_JACOBIAN_RESULT"] = str(JACOBIAN)
    _run(
        "recon_n12_c2_stop_graph_jacobian_profile.py",
        ["--workers", str(args.workers)],
        environment,
    )

    environment = base_environment.copy()
    environment["BHSM_N12_STOP_JACOBIAN_DATA"] = str(JACOBIAN.with_suffix(".npz"))
    environment["BHSM_N12_HYBRID_GRAPH_AUDIT_RESULT"] = str(HYBRID_AUDIT)
    _run("audit_n12_hybrid_graph_jacobian_equivalence.py", [], environment)

    _run("audit_n12_gate7_signed_common_frame_data_matching.py", [], os.environ.copy())


if __name__ == "__main__":
    main()
