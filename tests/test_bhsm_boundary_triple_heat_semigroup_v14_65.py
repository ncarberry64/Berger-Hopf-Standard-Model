from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.boundary_triple_heat_semigroup_v14_65 import (
    VERSION,
    PRIMARY_VERDICT,
    EXACT_NEXT_OBJECT,
    VERTICES,
    EDGES,
    principal_phase,
    diamond_holonomy,
    gauge_transform_edge_phases,
    endpoint_layout,
    vertex_endpoint_indices,
    self_adjoint_extension_matrices,
    self_adjoint_extension_diagnostics,
    sample_domain_boundary_data,
    boundary_green_form,
    local_edge_dtn,
    global_vertex_dtn,
    gauge_transform_vertex_matrix,
    dtn_gauge_witness,
    total_length,
    circle_eigenvalue,
    heat_trace_primal,
    heat_trace_poisson,
    relative_heat_trace,
    exact_relative_logdet,
    truncated_relative_logdet,
    holonomy_force,
    holonomy_curvature,
    spectral_collapse_payload,
    solve_monotone_global_scale,
    no_retuning_pipeline_payload,
    self_adjoint_domain_payload,
    heat_zeta_payload,
    status_payload,
    next_object_payload,
    completion_gate_payload,
    artifact_payloads,
    materialize,
)


def test_version_and_fail_closed_status():
    assert VERSION == "v14.65"
    assert "SELF_ADJOINT" in PRIMARY_VERDICT
    assert "OPERATOR_VALUED" in EXACT_NEXT_OBJECT


def test_diamond_endpoint_layout_is_degree_two():
    assert len(VERTICES) == 4
    assert len(EDGES) == 4
    assert len(endpoint_layout()) == 4
    assert all(len(v) == 2 for v in vertex_endpoint_indices().values())


def test_principal_phase_is_bounded():
    for x in (-100.0, -3.3, 0.0, 7.7, 100.0):
        p = principal_phase(x)
        assert -math.pi <= p <= math.pi


def test_holonomy_is_vertex_gauge_invariant():
    phases = {"e_8p": 0.21, "e_p4": 0.44, "e_m4": 0.13, "e_8m": -0.37}
    theta = {"M8": 0.31, "M5_plus": -0.27, "M5_minus": 0.52, "M4": -0.11}
    pg = gauge_transform_edge_phases(phases, theta)
    d = principal_phase(diamond_holonomy(pg) - diamond_holonomy(phases))
    assert abs(d) < 1e-14


def test_self_adjoint_extension_matrix_criterion():
    a, b = self_adjoint_extension_matrices()
    assert a.shape == (8, 8)
    assert b.shape == (8, 8)
    assert np.linalg.matrix_rank(np.concatenate((a, b), axis=1)) == 8
    assert np.linalg.norm(a @ np.conjugate(b.T) - b @ np.conjugate(a.T)) < 1e-14


def test_domain_boundary_data_satisfies_AB_condition():
    a, b = self_adjoint_extension_matrices()
    g0, g1 = sample_domain_boundary_data()
    assert np.linalg.norm(a @ g0 + b @ g1) < 1e-14


def test_boundary_green_form_vanishes_on_domain():
    f0, f1 = sample_domain_boundary_data(1)
    g0, g1 = sample_domain_boundary_data(2)
    assert abs(boundary_green_form(f0, f1, g0, g1)) < 1e-13


def test_self_adjoint_diagnostics_pass():
    p = self_adjoint_extension_diagnostics()
    assert p["rank_A_B"] == 8
    assert p["self_adjoint_extension_criterion_pass"] is True


def test_local_edge_dtn_is_hermitian_positive():
    for ell, kap, phi in ((0.7, 0.4, 0.2), (1.3, 1.1, -1.0), (2.0, 0.2, 2.3)):
        m = local_edge_dtn(ell, kap, phi)
        assert np.linalg.norm(m - np.conjugate(m.T)) < 1e-14
        assert np.min(np.linalg.eigvalsh(m)) > 0.0


def test_local_edge_dtn_rejects_bad_parameters():
    for ell, kap in ((0.0, 1.0), (-1.0, 1.0), (1.0, 0.0), (1.0, -1.0)):
        try:
            local_edge_dtn(ell, kap, 0.0)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid DtN parameters accepted")


def test_global_dtn_is_hermitian_positive():
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    phases = {"e_8p": 0.21, "e_p4": 0.44, "e_m4": 0.13, "e_8m": -0.37}
    m = global_vertex_dtn(lengths, 0.83, phases)
    assert np.linalg.norm(m - np.conjugate(m.T)) < 1e-13
    assert np.min(np.linalg.eigvalsh(m)) > 0.0


def test_global_dtn_vertex_gauge_covariance():
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    phases = {"e_8p": 0.21, "e_p4": 0.44, "e_m4": 0.13, "e_8m": -0.37}
    theta = {"M8": 0.31, "M5_plus": -0.27, "M5_minus": 0.52, "M4": -0.11}
    m0 = global_vertex_dtn(lengths, 0.83, phases)
    m1 = global_vertex_dtn(lengths, 0.83, gauge_transform_edge_phases(phases, theta))
    exp = gauge_transform_vertex_matrix(m0, theta)
    assert np.linalg.norm(m1-exp) < 1e-12


def test_dtn_payload_is_fail_closed_and_positive():
    p = dtn_gauge_witness()
    assert p["hermiticity_residual"] < 1e-13
    assert p["gauge_covariance_residual"] < 1e-12
    assert p["positive_resolvent_DtN_positive"] is True
    assert p["physical_BHSM_prediction"] is False


def test_total_length_and_circle_spectrum_are_positive():
    lengths = {"e_8p": 1.0, "e_p4": 1.0, "e_m4": 1.0, "e_8m": 1.0}
    ell = total_length(lengths)
    assert ell == 4.0
    for n in range(-5, 6):
        assert circle_eigenvalue(n, ell, 0.7, 0.5) > 0.0


def test_heat_trace_primal_poisson_duality():
    ell, phi, m = 4.1, 0.73, 0.7
    for t in (0.05, 0.2, 0.7, 2.0):
        a = heat_trace_primal(t, ell, phi, m, 300)
        b = heat_trace_poisson(t, ell, phi, m, 300)
        assert abs(a-b) < 2e-12


def test_relative_heat_trace_vanishes_at_zero_holonomy():
    for t in (0.1, 1.0, 3.0):
        assert abs(relative_heat_trace(t, 4.0, 0.0, 0.7)) < 1e-14


def test_exact_relative_logdet_vanishes_at_zero_holonomy():
    assert exact_relative_logdet(4.0, 0.0, 0.7) == 0.0


def test_truncated_spectral_product_approaches_exact_logdet():
    ell, phi, m = 4.1, 0.73, 0.7
    exact = exact_relative_logdet(ell, phi, m)
    trunc = truncated_relative_logdet(ell, phi, m, 20000)
    assert abs(trunc-exact) < 2e-6


def test_holonomy_force_and_curvature_at_zero():
    assert holonomy_force(4.0, 0.0, 0.7) == 0.0
    assert holonomy_curvature(4.0, 0.0, 0.7) > 0.0


def test_scalar_diamond_collapse_is_exact_for_same_total_length():
    p = spectral_collapse_payload()
    assert p["same_total_length"] is True
    assert p["sample_spectrum_max_difference"] == 0.0
    assert p["minimal_scalar_Kirchhoff_realization_retains_independent_stratum_lengths"] is False


def test_global_scale_diagnostic_is_unique_and_stationary():
    x = solve_monotone_global_scale()
    f = 8*.04*math.exp(8*x)+6*.08*math.exp(6*x)+3*.20*math.exp(3*x)-1.0
    assert abs(f) < 1e-14


def test_no_retuning_pipeline_freezes_inputs_before_outputs():
    p = no_retuning_pipeline_payload()
    assert p["all_fixture_inputs_frozen_before_solve"] is True
    assert p["postcomparison_adjustment_performed"] is False
    assert p["global_scale_stationarity_residual"] < 1e-14
    assert p["physical_BHSM_prediction"] is False


def test_self_adjoint_domain_payload_distinguishes_reduced_from_full():
    p = self_adjoint_domain_payload()
    assert p["reduced_continuum_self_adjoint_domain_closed"] is True
    assert p["full_BHSM_operator_domain_closed"] is False


def test_heat_zeta_payload_has_exact_duality_and_fail_closed_physics():
    p = heat_zeta_payload()
    assert p["heat_trace_duality_residual"] < 2e-12
    assert p["truncated_product_residual"] < 2e-6
    assert p["full_BHSM_supertrace_holonomy_selected"] is False
    assert p["physical_BHSM_prediction"] is False


def test_status_ledger_has_required_categories():
    p = status_payload()
    assert len(p["validated"]) >= 6
    assert len(p["invalidated"]) >= 3
    assert len(p["reclassified"]) >= 4
    assert len(p["open"]) >= 7


def test_next_object_requires_operator_valued_upgrade():
    p = next_object_payload()
    assert "operator-valued" in p["mandatory_upgrade"]
    assert p["postcomparison_choice_forbidden"] is True


def test_completion_gate_fails_closed_and_usb_untouched():
    p = completion_gate_payload()
    assert p["full_BHSM_complete"] is False
    assert p["mark_III"] == "NOT_REACHED"
    assert p["usb_touched"] is False
    assert p["reduced_self_adjoint_boundary_domain_closed"] is True
    assert p["full_operator_valued_BHSM_boundary_domain_closed"] is False
    assert len(p["missing_checks"]) >= 12


def test_artifacts_are_finite_json():
    def walk(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    payloads = artifact_payloads()
    assert len(payloads) == 9
    for payload in payloads.values():
        s = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        assert s.startswith("{")
        walk(payload)


def test_materialization_is_byte_deterministic(tmp_path):
    a, b = tmp_path/"a", tmp_path/"b"
    materialize(a)
    materialize(b)
    names = sorted(p.name for p in a.iterdir())
    assert len(names) == 9
    assert names == sorted(p.name for p in b.iterdir())
    for name in names:
        assert (a/name).read_bytes() == (b/name).read_bytes()
