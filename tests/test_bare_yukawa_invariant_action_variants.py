from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_gate import BareYukawaParameters, ModeRatio  # noqa: E402
from candidate_bare_yukawa_residual_autopsy import (  # noqa: E402
    build_autopsy_payload,
    lambda_branch,
    lambda_channel,
    lambda_degree,
    lambda_for_variant,
    lambda_mixed,
    lambda_raw,
)


def test_lambda_variants_have_expected_relationships_for_up_middle_mode() -> None:
    params = BareYukawaParameters(epsilon=0.0, tau0=0.2, beta_eff=0.0, xi=0.0)
    row = ModeRatio("up", "middle", 6, 0, 0.007, "test", True)

    assert lambda_raw(row, params) == 36.0
    assert lambda_degree(row, params) == 1.0
    assert lambda_mixed(row, params) == 6.0
    assert lambda_channel(row, params) == 36.0 / 35.0
    assert lambda_branch(row, params) == 0.0


def test_variant_dispatch_covers_all_declared_variants() -> None:
    params = BareYukawaParameters(epsilon=0.05, tau0=0.2, beta_eff=0.0, xi=0.0)
    row = ModeRatio("down", "light", 4, 2, 0.001, "test", True)
    for variant_id in [
        "A_raw",
        "B_target_degree_normalized",
        "C_mixed_raw_degree",
        "D_channel_dimension_normalized",
        "E_branch_relative",
    ]:
        assert lambda_for_variant(row, params, variant_id) >= 0.0


def test_no_invariant_variant_improperly_upgrades_the_mass_engine() -> None:
    payload = build_autopsy_payload()
    assert payload["best_variant"]["verdict"].startswith("BARE_YUKAWA_INVARIANT_VARIANT_")
    assert payload["best_variant"]["variant_id"] in {"A_raw", "B_target_degree_normalized", "C_mixed_raw_degree", "D_channel_dimension_normalized"}
    assert payload["best_variant"]["verdict"] != "BARE_YUKAWA_INVARIANT_VARIANT_TIER_A_STRONG"

    text = (ROOT / "theory" / "bare_yukawa_invariant_action_alternatives.md").read_text(
        encoding="utf-8"
    )
    assert "BARE_YUKAWA_INVARIANT_ACTION_VARIANTS_CANDIDATE" in text
    assert "BRANCH_RELATIVE_ACTION_STRUCTURAL_CANDIDATE_CONTROL" in text
