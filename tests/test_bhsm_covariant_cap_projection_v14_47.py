from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from bhsm.interface.completion.covariant_cap_projection_v14_47 import (
    berger_modulus_constraint,
    completion_gate,
    covariant_projection_contract,
    determinant_factor,
    neutron_star_preregistration_contract,
    projection_row,
    q_l,
    solve_local_coefficients,
    two_channel_determinant,
)


def test_q_values() -> None:
    assert q_l(1) == 0
    assert q_l(2) == 5
    assert q_l(3) == 12


def test_invalid_level() -> None:
    with pytest.raises(ValueError):
        q_l(0)


def test_normalized_rows() -> None:
    assert projection_row(2).r2 == 5
    assert projection_row(2).ricci2 == 25
    assert projection_row(3).r2 == 12
    assert projection_row(3).ricci2 == 144


def test_structural_determinant_is_independent_of_B() -> None:
    for b in (-9.0, 0.0, 3.25, 100.0):
        assert two_channel_determinant(b_ricci2=b) == pytest.approx(420.0)


def test_general_determinant_factor() -> None:
    assert determinant_factor(2, 3) == 420
    assert two_channel_determinant(a_r2=2.0, c_ricci2=3.0) == pytest.approx(2520.0)


def test_inverse_projection_roundtrip() -> None:
    c1, c2 = 1.75, -0.3
    b = 4.2
    r2 = projection_row(2, b_ricci2=b)
    r3 = projection_row(3, b_ricci2=b)
    t2 = r2.r2 * c1 + r2.ricci2 * c2
    t3 = r3.r2 * c1 + r3.ricci2 * c2
    got = solve_local_coefficients(t2, t3, b_ricci2=b)
    assert got == pytest.approx((c1, c2))


def test_singular_projection_fails_closed() -> None:
    with pytest.raises(ValueError):
        solve_local_coefficients(0.0, 0.0, c_ricci2=0.0)


def test_one_modulus_leaves_one_dimension() -> None:
    result = berger_modulus_constraint(2.0, -3.0, 1.0)
    assert result["constraint_rank"] == 1
    assert result["remaining_parameter_dimension"] == 1


def test_projection_contract_claim_boundary() -> None:
    payload = covariant_projection_contract()
    assert payload["determinant_integer_factor_L2_L3"] == 420
    assert payload["physical_counterterm_values_emitted"] is False
    assert payload["cap_regularity_fixes_ratio"] is False


def test_neutron_star_contract_is_protocol_only() -> None:
    payload = neutron_star_preregistration_contract()
    assert payload["status"] == "PROTOCOL_ONLY_NOT_EXECUTED"
    assert payload["observational_values_loaded"] is False
    assert payload["counts_as_microscopic_derivation"] is False


def test_completion_gate_stays_open() -> None:
    payload = completion_gate()
    assert payload["BHSM_complete"] is False
    assert payload["frozen_predictions_changed"] is False
    assert payload["usb_touched"] is False


def test_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    script = Path(__file__).parents[1] / "scripts" / "materialize_v14_47_covariant_projection.py"
    env = {"PYTHONPATH": str(Path(__file__).parents[1] / "src")}
    subprocess.run([sys.executable, str(script), "--output-dir", str(tmp_path)], check=True, env=env)
    first = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    subprocess.run([sys.executable, str(script), "--output-dir", str(tmp_path)], check=True, env=env)
    second = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert first == second
    for raw in second.values():
        json.loads(raw)
