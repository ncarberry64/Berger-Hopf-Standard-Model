"""Independent checks of the photon-diagnostic scope and spectral derivatives."""
import hashlib
import json

import pytest
import sympy as sp

from bhsm.interface.ae3_c2_photon_symbol_audit import (
    flat_half_space_control, spectral_dtn, spectral_solution,
    stable_weight_and_log_derivative,
)
from scripts.materialize_ae3_c2_photon_symbol_audit import build_payload, main, TARGET


@pytest.fixture(scope="module")
def audit():
    return build_payload()


@pytest.mark.parametrize("rho", [1.0e-8, 1.0e-3, 0.0499, 0.0501, 0.7])
def test_stable_weight_matches_high_precision_retained_formula(rho):
    x = sp.Float(rho, 80)
    sigma = -sp.Rational(1, 2) + x/sp.pi - sp.sin(2*x)/(2*sp.pi)
    weight = 1-4*sigma**2
    log_derivative = -8*sigma*(1-sp.cos(2*x))/(sp.pi*weight)
    w, dw = stable_weight_and_log_derivative(rho)
    assert w == pytest.approx(float(weight.evalf(70)), rel=2e-13, abs=0)
    assert dw == pytest.approx(float(log_derivative.evalf(70)), rel=2e-13, abs=0)


def test_flat_square_root_is_an_exact_counterexample_to_universal_ratio_test():
    s, q2 = sp.symbols("s q2", positive=True)
    kernel = sp.sqrt(s-q2)
    n0 = kernel.subs(q2, 0)
    temporal = -sp.diff(kernel, q2).subs(q2, 0)
    spatial = sp.diff(kernel, s).subs(q2, 0)
    assert sp.simplify(s*temporal/n0) == sp.Rational(1, 2)
    assert sp.simplify(temporal/spatial) == 1
    control = flat_half_space_control(4)
    assert control["complete_mode_ratio"] == 0.5
    assert control["derivative_ratio"] == 1
    assert not control["BHSM_replacement"]


def test_energy_envelopes_include_the_cutoff_boundary_variation(audit):
    row = audit["mode_witnesses"][0]
    assert row["finite_cutoff_Robin_energy"] > 0
    assert row["finite_cutoff_Robin_spatial_derivative"] > 0
    assert row["static_energy_residual"] < 1e-10
    assert row["spectral_envelope_residual"] < 1e-10
    assert row["frequency_envelope_residual"] < 1e-10
    assert row["spatial_centered_difference_residual"] < 2e-8
    assert row["frequency_centered_difference_residual"] < 2e-8


def test_direct_derivative_does_not_repair_lowest_mode(audit):
    row = audit["mode_witnesses"][0]
    assert row["complete_mode_ratio"] == pytest.approx(0.590609601652908, abs=2e-10)
    assert row["derivative_ratio"] == pytest.approx(0.908932991228275, abs=2e-10)
    assert row["dN_d_spatial_eigenvalue"] < row["static_quotient"]
    assert audit["validation_passed"]


def test_sampled_high_modes_approach_different_reference_ratios(audit):
    rows = audit["mode_witnesses"]
    assert all(a["complete_mode_ratio"] > b["complete_mode_ratio"] > .5
               for a, b in zip(rows, rows[1:]))
    assert all(a["derivative_ratio"] < b["derivative_ratio"] < 1
               for a, b in zip(rows, rows[1:]))
    # Numerical trend check, not an asymptotic proof or a photon pole.
    assert rows[-1]["N_over_level"] > .99
    assert not audit["claim_boundary"]["physical_photon_pole_derived"]


def test_spatial_parameter_is_not_integer_truncated():
    assert spectral_dtn(4.125) > spectral_dtn(4.0)


def test_two_physical_modes_at_same_invariant_still_differ(audit):
    pair = audit["equal_s_minus_q_squared_comparison"]
    assert pair["N_level4_q_squared12"] > pair["N_level2_q_squared0"]


def test_reference_maxwell_shell_does_not_make_the_trace_vanish(audit):
    shell = audit["reference_Maxwell_shell_witness"]
    assert shell["q_squared"] == shell["spatial_eigenvalue"]
    assert shell["N_on_reference_Maxwell_shell"] > 0
    assert audit["validation"]["independent_retained_solver_agrees_on_reference_shell"]


@pytest.mark.parametrize("s,q2", [(0, 0), (4, 5), (float("nan"), 0)])
def test_invalid_spectral_problem_rejected(s, q2):
    with pytest.raises(ValueError):
        spectral_solution(s, q2)


def test_twice_materialized_report_preserves_tracked_certificate(tmp_path):
    original = TARGET.read_bytes() if TARGET.exists() else None
    output = tmp_path / "audit.json"
    main(["--output", str(output)])
    first = hashlib.sha256(output.read_bytes()).digest()
    main(["--output", str(output)])
    assert hashlib.sha256(output.read_bytes()).digest() == first
    assert json.loads(output.read_text())["validation_passed"]
    assert (TARGET.read_bytes() if TARGET.exists() else None) == original
