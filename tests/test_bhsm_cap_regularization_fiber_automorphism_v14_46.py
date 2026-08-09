from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from bhsm.interface.completion.cap_regularization_fiber_automorphism_v14_46 import (
    ChannelMap,
    cap_regularity_audit,
    channel_coefficients_from_local_hessians,
    completion_payload,
    covariant_operator_basis,
    fiber_automorphism_audit,
    fiber_stretch_local_derivative,
    finite_difference_fiber_derivative,
    local_hessians_from_channel_coefficients,
    modulus_stationarity_contract,
    no_fit_matching_protocol,
    q_round,
    stellar_structure_contract,
    validate_internal_contracts,
    worst_regular_cap_flux_power,
)


def test_channel_map_determinant_and_inverse() -> None:
    channel_map = ChannelMap()
    assert channel_map.matrix == ((5, 25), (12, 144))
    assert channel_map.determinant == 420
    assert channel_map.inverse == (
        (Fraction(12, 35), Fraction(-5, 84)),
        (Fraction(-1, 35), Fraction(1, 84)),
    )


def test_channel_round_trip_is_exact() -> None:
    expected = (Fraction(7, 3), Fraction(-2, 5))
    h2, h3 = local_hessians_from_channel_coefficients(*expected)
    assert channel_coefficients_from_local_hessians(h2, h3) == expected


def test_round_channel_costs() -> None:
    assert q_round(1) == 0
    assert q_round(2) == 5
    assert q_round(3) == 12


def test_smooth_cap_fluxes_vanish_separately() -> None:
    assert worst_regular_cap_flux_power(2) == 2
    assert worst_regular_cap_flux_power(3) == 4
    audit = cap_regularity_audit()
    assert audit["curvature_squared_fluxes_vanish_separately"]
    assert not audit["cross_cancellation_required"]
    assert audit["coefficient_relation_forced"] is None


def test_true_automorphism_does_not_include_fiber_stretch() -> None:
    audit = fiber_automorphism_audit()
    assert audit["covariant_local_invariants_are_separately_automorphism_invariant"]
    assert not audit["fiber_length_scaling_is_bundle_automorphism"]
    assert audit["automorphism_forced_relation"] is None


def test_fiber_stretch_derivative_matches_finite_difference() -> None:
    analytic = fiber_stretch_local_derivative(3, 2, 1.17, 0.4, -0.03)
    numeric = finite_difference_fiber_derivative(3, 2, 1.17, 0.4, -0.03)
    assert analytic == pytest.approx(numeric, rel=2e-8, abs=2e-8)


def test_weight_zero_channel_is_blind_to_fiber_stretch() -> None:
    assert fiber_stretch_local_derivative(3, 0, 1.17, 0.4, -0.03) == 0.0


def test_one_modulus_cannot_fix_two_coefficients() -> None:
    contract = modulus_stationarity_contract()
    assert contract["maximum_independent_relations"] == 1
    assert contract["counterterm_dimension_after_generic_stationarity"] == 1
    assert not contract["fixes_both_coefficients"]


def test_covariant_projection_contract_is_explicit() -> None:
    contract = covariant_operator_basis()
    assert contract["channel_inverse"]["determinant"] == 420
    assert "R^2" in contract["bulk_action"]
    assert "R_mn R^mn" in contract["bulk_action"]


def test_stellar_contract_contains_background_stability_and_tides() -> None:
    contract = stellar_structure_contract()
    assert any("p_prime" in equation for equation in contract["background_equations"])
    assert "omega_0^2>0" in contract["radial_stability"]
    assert "Love number" in contract["tidal_problem"]


def test_no_fit_firewall_is_active() -> None:
    protocol = no_fit_matching_protocol()
    assert not protocol["matching_executed"]
    assert any("retuning" in item for item in protocol["forbidden"])
    payload = completion_payload()
    assert not payload["frozen_predictions_changed"]
    assert not payload["physical_outputs_emitted"]
    assert not payload["usb_touched"]


def test_internal_contract_validation_all_true() -> None:
    assert all(validate_internal_contracts().values())


def test_materializer_is_byte_deterministic(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "materialize_cap_regularization_fiber_automorphism_v14_46.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    output = tmp_path / "artifacts"

    subprocess.run(
        [sys.executable, str(script), "--output-dir", str(output)],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )
    first = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob("*.json")}
    subprocess.run(
        [sys.executable, str(script), "--output-dir", str(output)],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )
    second = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob("*.json")}
    assert first == second
    assert len(first) == 4
    payload = json.loads((output / "BHSM_completion_gate_v14_46.json").read_text())
    assert payload["channel_map"]["determinant"] == 420
