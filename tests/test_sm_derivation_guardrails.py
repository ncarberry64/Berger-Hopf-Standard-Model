from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_sm_derivation_gate import replacement_obligation_registry  # noqa: E402


FORBIDDEN_ASSERTIONS = [
    "BHSM has derived the Standard Model",
    "BHSM has replaced the Standard Model",
    "full gauge-group derivation is complete",
    "dark matter is a core particle-sector proof",
]


def test_no_forbidden_replacement_claims_in_new_docs() -> None:
    paths = [
        ROOT / "theory" / "sm_low_energy_limit_derivation_gate.md",
        ROOT / "theory" / "sm_input_dependency_audit.md",
        ROOT / "theory" / "bhsm_boundary_primitives_for_sm_derivation.md",
        ROOT / "theory" / "sm_representation_derivation_obligations.md",
        ROOT / "theory" / "sm_low_energy_limit_derivation_results.json",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for phrase in FORBIDDEN_ASSERTIONS:
        assert phrase not in text
    assert "collective curvature extension remains separate" in text


def test_replacement_obligations_are_complete() -> None:
    obligations = replacement_obligation_registry()
    assert len(obligations) == 15
    text = (ROOT / "theory" / "sm_representation_derivation_obligations.md").read_text(
        encoding="utf-8"
    )
    for row in obligations:
        assert row["status"] == "open_derivation_obligation"
        assert row["obligation"] in text
    assert "Recover the local SM Lagrangian as a low-energy effective limit." in text


def test_collective_curvature_is_separate_extension_not_core_proof() -> None:
    payload = json.loads(
        (ROOT / "theory" / "sm_low_energy_limit_derivation_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["core_particle_sector_only"] is True
    assert payload["collective_curvature_extension_separate"] is True
    assert "Collective-curvature/dark matter" in payload["connected_extension_targets"]
