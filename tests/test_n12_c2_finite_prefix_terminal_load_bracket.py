from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from derive_n12_c2_finite_prefix_terminal_load_bracket import build_payload  # noqa: E402


ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_FINITE_PREFIX_TERMINAL_LOAD_BRACKET.json"
)


def test_terminal_load_bracket_replays() -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    replayed = build_payload()
    assert replayed == stored
    assert replayed["validation_passed"] is True


def test_every_sampled_bracket_is_ordered() -> None:
    payload = build_payload()
    for row in payload["sampled_crosschecks"]:
        for channel in row["channels"].values():
            assert Decimal(channel["zero_terminal_load_birth_Weyl_decimal"]) < Decimal(
                channel["Dirichlet_terminal_limit_birth_Weyl_decimal"]
            )


def test_current_prefix_does_not_close_maximal_value_or_force() -> None:
    payload = build_payload()
    assert payload["adjudication"][
        "additional_same_scale_prefix_refinement_can_replace_tail_theorem"
    ] is False
    assert payload["claim_boundary"]["maximal_C2_Weyl_value"].startswith("OPEN")
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
