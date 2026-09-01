"""Deterministically replay the selected quarter-step Gate-7 center chain."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, environment: dict[str, str], *arguments: str) -> None:
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
    environment = os.environ.copy()
    environment["BHSM_N12_SIGNED_JET_WORKERS"] = str(args.workers)
    environment["BHSM_N12_SIGNED_FULL_TRANSVERSE_WORKERS"] = str(args.workers)

    ordered = (
        "derive_n12_gate7_exact_signed_directional_field_curvature.py",
        "derive_n12_gate7_exact_signed_mixed_field_curvature.py",
        "certify_n12_gate7_correction_direction_action_majorants.py",
        "derive_n12_gate7_retained_correction_eigenline_first_jets.py",
        "derive_n12_gate7_retained_correction_bordered_response_first_jets.py",
        "derive_n12_gate7_correction_bordered_response_second_jets.py",
        "certify_n12_gate7_two_free_leg_action_majorants.py",
        "derive_n12_gate7_exact_signed_selected_multiplier_jets.py",
        "derive_n12_gate7_exact_signed_full_transverse_curvature.py",
        "adjudicate_n12_gate7_exact_full_transverse_curvature.py",
        "derive_n12_gate7_signed_causal_vector_bootstrap.py",
        "derive_n12_gate7_exact_center_causal_vector_certificate.py",
        "derive_n12_gate7_outward_closure_budget.py",
    )
    for script in ordered:
        _run(script, environment)

    _run(
        "replay_n12_gate7_quarter_step_common_frame_operands.py",
        environment,
        "--workers", str(args.workers),
    )
    _run("audit_n12_gate7_selected_center_provenance.py", environment)
    _run("derive_n12_gate7_normalized_field_common_frame_identity.py", environment)
    _run("audit_n12_gate7_dop853_system_adapter_matching.py", environment)
    _run("materialize_bhsm_current_system_integration_map.py", environment)


if __name__ == "__main__":
    main()
