"""Materialize deterministic BHSM v10.3 deformation-domain artifacts."""

from __future__ import annotations

from bhsm.interface.envelopment.deformation_selection_gate_v10_3 import materialize


if __name__ == "__main__":
    for artifact_path in materialize():
        print(artifact_path.relative_to(artifact_path.parents[1]))
