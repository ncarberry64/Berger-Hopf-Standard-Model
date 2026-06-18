from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_residual_autopsy import (  # noqa: E402
    PARAMETER_POLICY,
    VARIANTS,
    build_autopsy_payload,
)


FORBIDDEN_SECTOR_KEYS = {
    "tau_l",
    "tau_u",
    "tau_d",
    "xi_l",
    "xi_u",
    "xi_d",
    "beta_l",
    "beta_u",
    "beta_d",
    "epsilon_l",
    "epsilon_u",
    "epsilon_d",
}


def test_variants_a_to_d_use_universal_parameter_policy() -> None:
    payload = build_autopsy_payload()
    for row in payload["variant_results"]:
        if row["variant_id"] != "E_branch_relative":
            assert row["parameter_policy"] == PARAMETER_POLICY
            assert set(row["best_parameters"]) == {"epsilon", "tau0", "beta_eff", "xi"}
            assert row["primary_evidence_allowed"] is True


def test_branch_relative_variant_is_control_only_not_primary_evidence() -> None:
    variants = {variant.variant_id: variant for variant in VARIANTS}
    assert variants["E_branch_relative"].status == "BRANCH_RELATIVE_ACTION_STRUCTURAL_CANDIDATE_CONTROL"
    assert variants["E_branch_relative"].control_only is True
    assert variants["E_branch_relative"].primary_evidence_allowed is False

    payload = build_autopsy_payload()
    rows = [row for row in payload["variant_results"] if row["variant_id"] == "E_branch_relative"]
    assert rows
    assert all(row["control_only"] is True for row in rows)
    assert all(row["primary_evidence_allowed"] is False for row in rows)
    assert all(row["verdict"] == "BARE_YUKAWA_INVARIANT_VARIANT_TIER_D_FAIL" for row in rows)


def test_no_sector_specific_parameters_or_forbidden_fit_controls_are_used() -> None:
    payload = build_autopsy_payload()
    assert payload["parameter_policy"]["sector_specific_parameters_used"] is False
    assert payload["parameter_policy"]["forbidden_sector_fit_control_implemented"] is False

    serialized = json.dumps(payload)
    for key in FORBIDDEN_SECTOR_KEYS:
        assert key not in serialized
