from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_bare_yukawa_gate import (  # noqa: E402
    PARAMETER_POLICY,
    build_gate_payload,
    parameter_grid,
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


def test_main_scan_uses_single_universal_parameter_set() -> None:
    payload = build_gate_payload()
    assert payload["main_scan"]["parameter_policy"] == PARAMETER_POLICY
    assert payload["parameter_guardrails"]["uses_single_universal_parameter_set"] is True
    assert payload["parameter_guardrails"]["uses_sector_specific_tau"] is False
    assert payload["parameter_guardrails"]["uses_sector_specific_xi"] is False
    assert payload["parameter_guardrails"]["uses_sector_specific_beta"] is False
    assert payload["parameter_guardrails"]["uses_sector_specific_epsilon"] is False


def test_best_parameters_have_only_allowed_universal_keys() -> None:
    payload = build_gate_payload()
    keys = set(payload["main_scan"]["best_parameters"])
    assert keys == {"epsilon", "tau0", "beta_eff", "xi"}
    assert not (keys & FORBIDDEN_SECTOR_KEYS)


def test_parameter_grid_is_broad_finite_and_non_sector_specific() -> None:
    grid = parameter_grid()
    assert len(grid) == 14994
    assert min(row.epsilon for row in grid) == 0.0
    assert max(row.epsilon for row in grid) == 0.05
    assert min(row.tau0 for row in grid) == 0.0
    assert max(row.tau0 for row in grid) == 1.0
    assert min(row.beta_eff for row in grid) == 0.0
    assert max(row.beta_eff for row in grid) == 0.05
    assert min(row.xi for row in grid) == 0.0
    assert max(row.xi for row in grid) == 2.0


def test_forbidden_sector_fit_control_is_not_used_as_evidence() -> None:
    payload = build_gate_payload()
    control = payload["forbidden_sector_fit_control"]
    assert control["status"] == "FORBIDDEN_SECTOR_FIT_CONTROL"
    assert control["used_as_evidence"] is False

    serialized = json.dumps(payload)
    for key in FORBIDDEN_SECTOR_KEYS:
        assert key not in serialized
