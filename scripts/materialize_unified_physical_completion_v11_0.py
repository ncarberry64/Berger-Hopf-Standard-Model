"""Materialize deterministic BHSM v11.0 completion artifacts."""

from __future__ import annotations

from bhsm.interface.envelopment.final_physical_gate_v11_0 import materialize


if __name__ == "__main__":
    for artifact_path in materialize():
        print(artifact_path.relative_to(artifact_path.parents[1]))
