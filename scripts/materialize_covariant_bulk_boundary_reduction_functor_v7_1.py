"""Materialize the authoritative BHSM v7.1 reduction record."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.claim_input_completion_consistency import (  # noqa: E402
    canonical_completion_gate_payload,
)
from bhsm.interface.master_action.reduction import (  # noqa: E402
    deterministic_json,
    payload,
)


def main() -> None:
    artifact = (
        ROOT
        / "artifacts"
        / "BHSM_covariant_bulk_boundary_reduction_functor_v7_1.json"
    )
    gate = ROOT / "artifacts" / "BHSM_1_0_completion_gate.json"
    artifact.write_text(deterministic_json(payload()), encoding="utf-8")
    gate.write_text(
        deterministic_json(canonical_completion_gate_payload()),
        encoding="utf-8",
    )
    print(artifact.relative_to(ROOT))
    print(gate.relative_to(ROOT))


if __name__ == "__main__":
    main()
