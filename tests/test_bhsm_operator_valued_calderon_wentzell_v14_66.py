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

from bhsm.interface.completion.operator_valued_calderon_wentzell_v14_66 import (
    VERSION,
    PRIMARY_VERDICT,
    EXACT_NEXT_OBJECT,
    FROZEN_BERGER_DIAGNOSTIC,
    VERTICES,
    EDGE_NAMES,
    spin_j_matrices,
    berger_dirac_block,
    berger_n1_expected_eigenvalues,
    berger_positive_tangential,
    positive_sqrt,
    plane_unitary,
    diagnostic_operator_data,
    kkt_schur_wentzell,
    diagnostic_wentzell_blocks,
    wentzell_extension_matrices,
    wentzell_extension_diagnostics,
    sample_wentzell_domain_data,
    boundary_green_form,
    operator_edge_weyl,
    assemble_operator_weyl,
    global_wentzell_matrix,
    response_operator,
    gauge_transform_operator_data,
    gauge_transform_global_matrix,
    wilson_loop,
    unitary_eigenphases,
    diagnostic_vertex_gauges,
    orthogonal_complement_basis,
    diagnostic_zero_modes,
    projected_response_operator,
    matrix_heat_trace,
    matrix_logdet_positive,
    berger_geometry_payload,
    operator_valued_weyl_payload,
    nonabelian_holonomy_payload,
    wentzell_payload,
    operator_no_collapse_payload,
    projector_heat_payload,
    neutrino_kill_screen_payload,
    status_payload,
    completion_gate_payload,
    next_object_payload,
    artifact_payloads,
    materialize,
)


def test_version_and_fail_closed_next_object():
    assert VERSION == "v14.66"
    assert "OPERATOR_VALUED" in PRIMARY_VERDICT
    assert "GRAM_HESSIAN" in EXACT_NEXT_OBJECT


def test_spin_j_generators_dimensions_and_commutator():
    jx, jy, jz = spin_j_matrices(2)
    assert jx.shape == jy.shape == jz.shape == (3, 3)
    assert np.linalg.norm(jx @ jy - jy @ jx - 1j * jz) < 1e-13


def test_berger_n1_matches_closed_spectrum():
    for beta in (1.0, FROZEN_BERGER_DIAGNOSTIC, 4.0):
        got = np.linalg.eigvalsh(berger_dirac_block(1, beta, 1.0))
        exp = berger_n1_expected_eigenvalues(beta, 1.0)
        assert np.max(np.abs(got-exp)) < 1e-12


def test_berger_n1_first_zero_crossing_witness_at_beta_four():
    ev = np.linalg.eigvalsh(berger_dirac_block(1, 4.0, 1.0))
    assert np.min(np.abs(ev)) < 1e-13


def test_frozen_berger_gap_is_nonzero():
    ev = np.linalg.eigvalsh(berger_dirac_block(1, FROZEN_BERGER_DIAGNOSTIC, 1.0))
    assert abs(np.min(np.abs(ev)) - 1.4214729321332835) < 1e-12


def test_n2_berger_blocks_do_not_commute_across_beta():
    a = berger_dirac_block(2, 1.04, 1.0)
    b = berger_dirac_block(2, 1.47, 1.0)
    assert np.linalg.norm(a @ b - b @ a) > 1.0


def test_positive_sqrt_round_trip():
    a = np.array([[2.0, 0.3j], [-0.3j, 1.4]], dtype=complex)
    r = positive_sqrt(a)
    assert np.linalg.norm(r @ r - a) < 1e-12
    assert np.min(np.linalg.eigvalsh(r)) > 0.0


def test_positive_tangential_is_strictly_positive():
    k = berger_positive_tangential(2, 1.31, 1.0, 0.35)
    assert k.shape == (6, 6)
    assert np.linalg.norm(k-k.conj().T) < 1e-13
    assert np.min(np.linalg.eigvalsh(k)) > 0.0


def test_plane_unitary_is_unitary():
    u = plane_unitary(6, 1, 4, 0.31, -0.22)
    assert np.linalg.norm(u.conj().T @ u - np.eye(6)) < 1e-13


def test_diagnostic_operator_data_is_dimensionally_consistent():
    ks, us, betas = diagnostic_operator_data()
    assert set(ks) == set(us) == set(betas) == set(EDGE_NAMES)
    assert all(x.shape == (6, 6) for x in ks.values())
    assert all(x.shape == (6, 6) for x in us.values())


def test_kkt_schur_wentzell_is_hermitian_positive():
    for i in range(4):
        w, diag = kkt_schur_wentzell(6, i)
        assert np.linalg.norm(w-w.conj().T) < 1e-13
        assert diag["min_Hii_eigenvalue"] > 0.0
        assert diag["min_W_eigenvalue"] > 0.0


def test_wentzell_extension_exact_self_adjoint_criterion():
    ws = diagnostic_wentzell_blocks(6)
    a, b = wentzell_extension_matrices(6, ws)
    assert a.shape == b.shape == (48, 48)
    assert np.linalg.matrix_rank(np.concatenate((a, b), axis=1)) == 48
    assert np.linalg.norm(a @ b.conj().T - b @ a.conj().T) < 1e-12


def test_wentzell_domain_green_form_vanishes():
    f0, f1 = sample_wentzell_domain_data(6, 1466)
    g0, g1 = sample_wentzell_domain_data(6, 1467)
    assert abs(boundary_green_form(f0, f1, g0, g1)) < 1e-11


def test_wentzell_diagnostics_pass():
    p = wentzell_extension_diagnostics(6)
    assert p["rank_A_B"] == 48
    assert p["self_adjoint_Wentzell_extension_pass"] is True
    assert p["all_Wentzell_blocks_positive"] is True


def test_operator_edge_weyl_is_hermitian_positive():
    ks, us, _ = diagnostic_operator_data()
    for name in EDGE_NAMES:
        m = operator_edge_weyl(0.9, ks[name], us[name])
        assert m.shape == (12, 12)
        assert np.linalg.norm(m-m.conj().T) < 1e-12
        assert np.min(np.linalg.eigvalsh(m)) > 0.0


def test_operator_edge_weyl_rejects_nonpositive_k():
    u = np.eye(2, dtype=complex)
    try:
        operator_edge_weyl(1.0, np.diag([1.0, 0.0]), u)
    except ValueError:
        pass
    else:
        raise AssertionError("nonpositive tangential block accepted")


def test_global_operator_weyl_is_hermitian_positive():
    ks, us, _ = diagnostic_operator_data()
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    m = assemble_operator_weyl(lengths, ks, us)
    assert m.shape == (24, 24)
    assert np.linalg.norm(m-m.conj().T) < 1e-12
    assert np.min(np.linalg.eigvalsh(m)) > 0.0


def test_operator_weyl_vertex_gauge_covariance():
    ks, us, _ = diagnostic_operator_data()
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    d = 6
    g = diagnostic_vertex_gauges(d)
    m = assemble_operator_weyl(lengths, ks, us)
    kg, ug = gauge_transform_operator_data(ks, us, g)
    mg = assemble_operator_weyl(lengths, kg, ug)
    expected = gauge_transform_global_matrix(m, g)
    assert np.linalg.norm(mg-expected) < 1e-11


def test_nonabelian_wilson_loop_is_unitary():
    _, us, _ = diagnostic_operator_data()
    w = wilson_loop(us)
    assert np.linalg.norm(w.conj().T @ w - np.eye(6)) < 1e-12
    assert len(unitary_eigenphases(w)) == 6


def test_wilson_eigenphases_are_vertex_gauge_invariant():
    ks, us, _ = diagnostic_operator_data()
    g = diagnostic_vertex_gauges(6)
    _, ug = gauge_transform_operator_data(ks, us, g)
    p0 = unitary_eigenphases(wilson_loop(us))
    p1 = unitary_eigenphases(wilson_loop(ug))
    assert np.max(np.abs(p0-p1)) < 1e-12


def test_global_wentzell_matrix_is_hermitian_positive():
    w = global_wentzell_matrix(6)
    assert w.shape == (24, 24)
    assert np.linalg.norm(w-w.conj().T) < 1e-13
    assert np.min(np.linalg.eigvalsh(w)) > 0.0


def test_response_operator_is_positive():
    ks, us, _ = diagnostic_operator_data()
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    h = response_operator(lengths, ks, us)
    assert np.min(np.linalg.eigvalsh(h)) > 0.0


def test_equal_total_length_partition_collapse_is_lifted_in_response():
    p = operator_no_collapse_payload()
    assert p["same_total_length"] is True
    assert p["operator_response_spectrum_max_difference"] > 0.1
    assert p["operator_response_trace_difference"] > 0.1
    assert p["scalar_circle_partition_collapse_persists_at_operator_response_level"] is False


def test_orthogonal_complement_basis_removes_modes():
    z = diagnostic_zero_modes(6)
    q = orthogonal_complement_basis(z, 24)
    assert q.shape == (24, 22)
    assert np.linalg.norm(q.conj().T @ q - np.eye(22)) < 1e-12
    assert np.linalg.norm(q.conj().T @ z) < 1e-12


def test_projected_response_remains_positive_hermitian():
    ks, us, _ = diagnostic_operator_data()
    lengths = {"e_8p": 1.15, "e_p4": 0.73, "e_m4": 0.91, "e_8m": 1.31}
    h = response_operator(lengths, ks, us)
    hp, q = projected_response_operator(h, 6)
    assert hp.shape == (22, 22)
    assert q.shape == (24, 22)
    assert np.linalg.norm(hp-hp.conj().T) < 1e-12
    assert np.min(np.linalg.eigvalsh(hp)) > 0.0


def test_matrix_heat_trace_and_logdet_are_finite():
    h = np.diag([1.0, 2.0, 3.0])
    assert math.isfinite(matrix_heat_trace(h, 0.5))
    assert abs(matrix_logdet_positive(h)-math.log(6.0)) < 1e-14


def test_berger_payload_is_fail_closed():
    p = berger_geometry_payload()
    assert p["n1_closed_form_residual"] < 1e-12
    assert p["n2_Berger_blocks_noncommuting_across_beta"] is True
    assert p["physical_BHSM_prediction"] is False


def test_operator_weyl_payload_passes_numeric_gates():
    p = operator_valued_weyl_payload()
    assert p["global_Weyl_hermiticity_residual"] < 1e-12
    assert p["global_Weyl_positive"] is True
    assert p["vertex_gauge_covariance_residual"] < 1e-11
    assert p["tangential_blocks_are_not_all_mutually_commuting"] is True


def test_nonabelian_holonomy_payload_is_fail_closed():
    p = nonabelian_holonomy_payload()
    assert p["wilson_unitarity_residual"] < 1e-12
    assert p["gauge_invariant_eigenphase_residual"] < 1e-12
    assert p["more_than_one_relative_phase_available_kinematically"] is True
    assert p["physical_connection_holonomy_derived"] is False


def test_wentzell_payload_distinguishes_theorem_from_physics():
    p = wentzell_payload()
    assert p["retained_mode_Wentzell_domain_closed"] is True
    assert p["physical_action_normalized_core_wall_Gram_Hessian_inserted"] is False


def test_projector_heat_payload_is_finite_and_fail_closed():
    p = projector_heat_payload()
    assert p["QstarQ_identity_residual"] < 1e-12
    assert p["Qstar_zero_modes_residual"] < 1e-12
    assert p["projected_response_minimum_eigenvalue"] > 0.0
    assert math.isfinite(p["diagnostic_relative_response_heat_trace"])
    assert math.isfinite(p["diagnostic_relative_response_logdet"])
    assert p["full_continuum_relative_heat_supertrace_computed"] is False


def test_neutrino_kill_screen_blocks_physical_execution():
    p = neutrino_kill_screen_payload()
    assert p["all_required_inputs_present"] is False
    assert p["physical_execution_allowed"] is False
    assert p["current_result"] == "PHYSICAL_EXECUTION_BLOCKED"
    assert p["postcomparison_parameter_adjustment_allowed"] is False


def test_status_ledger_has_hindsight_categories():
    p = status_payload()
    assert len(p["validated"]) >= 8
    assert len(p["invalidated"]) >= 3
    assert len(p["reclassified"]) >= 4
    assert len(p["open"]) >= 10


def test_next_object_targets_physical_gram_hessian():
    p = next_object_payload()
    assert "Gram-Hessian" in p["highest_upstream_physical_blocker"]
    assert p["postcomparison_choice_forbidden"] is True


def test_completion_gate_fails_closed_and_usb_untouched():
    p = completion_gate_payload()
    assert p["full_BHSM_complete"] is False
    assert p["mark_III"] == "NOT_REACHED"
    assert p["usb_touched"] is False
    assert p["operator_valued_retained_mode_Weyl_gate_closed"] is True
    assert p["retained_mode_Wentzell_self_adjoint_gate_closed"] is True
    assert p["physical_action_normalized_response_Gram_Hessian_closed"] is False
    assert p["neutrino_physical_execution_allowed"] is False
    assert len(p["missing_checks"]) >= 10


def test_artifact_payloads_are_finite_json():
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
    assert len(payloads) == 11
    for p in payloads.values():
        s = json.dumps(p, sort_keys=True, separators=(",", ":"), allow_nan=False)
        assert s.startswith("{")
        walk(p)


def test_materialization_is_byte_deterministic(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    materialize(a)
    materialize(b)
    names = sorted(p.name for p in a.iterdir())
    assert len(names) == 11
    assert names == sorted(p.name for p in b.iterdir())
    for name in names:
        assert (a/name).read_bytes() == (b/name).read_bytes()
