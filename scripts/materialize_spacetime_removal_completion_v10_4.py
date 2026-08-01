"""Materialize deterministic BHSM v10.4 completion artifacts."""

from __future__ import annotations

from bhsm.interface.envelopment.final_completion_gate_v10_4 import materialize


if __name__ == "__main__":
    for artifact_path in materialize():
        print(artifact_path.relative_to(artifact_path.parents[1]))
