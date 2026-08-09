from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.action_attachment_wentzell_v14_67 import (
    VERSION,
    PRIMARY_VERDICT,
    EXACT_NEXT_OBJECT,
    H_CORE_REPRESENTATIVE,
    constraint_jacobian,
    tangent_basis,
    action_whitened_kinetic,
    action_whitened_hessian,
    reduced_attachment_matrices,
    attachment_characteristic_coefficients,
    attachment_response_roots,
    inverse_sqrt_positive,
    attachment_wentzell_response,
    attachment_generalized_eigenvectors,
    lifted_attachment_wentzell,
    lifted_operator_data,
    uniform_theorem_wentzell_blocks,
    uniform_wentzell_diagnostics,
    sample_uniform_wentzell_domain_data,
    lifted_response_operator,
    lifted_projected_response,
    recovered_gram_hessian_payload,
    normalization_reconciliation_payload,
    attachment_wentzell_payload,
    operator_response_insertion_payload,
    provenance_gate_payload,
    neutrino_kill_screen_payload,
    status_payload,
    completion_gate_payload,
    next_object_payload,
    artifact_payloads,
    materialize,
)
from bhsm.interface.completion.operator_valued_calderon_wentzell_v14_66 import boundary_green_form


def test_version_and_fail_closed_next_object():
    assert VERSION == "v14.67"
    assert "GRAM_HESSIAN" in PRIMARY_VERDICT
    assert "GLOBAL_ENVELOPMENT" in EXACT_NEXT_OBJECT


def test_constraint_and_tangent_basis_are_exact():
    b = constraint_jacobian()
    n = tangent_basis()
    assert np.array_equal(b, np.array([[-1.0, 1.0, 1.0]]))
    assert np.linalg.norm(b @ n) == 0.0


def test_recovered_action_whitened_kinetic_is_identity():
    assert np.array_equal(action_whitened_kinetic(), np.eye(3))


def test_recovered_hessian_has_critical_wall_zero():
    h = action_whitened_hessian()
    assert h[0, 0] == H_CORE_REPRESENTATIVE
    assert h[1, 1] == 0.0
    assert h[2, 2] == 1.0


def test_reduced_matrices_match_v11_4_corrected_forms():
    k, h = reduced_attachment_matrices()
    assert np.array_equal(k, np.array([[2.0, 1.0], [1.0, 2.0]]))
    assert np.max(np.abs(h - np.array([[H_CORE_REPRESENTATIVE, H_CORE_REPRESENTATIVE], [H_CORE_REPRESENTATIVE, H_CORE_REPRESENTATIVE + 1.0]]))) < 1e-15


def test_characteristic_polynomial_matches_direct_determinant():
    k, h = reduced_attachment_matrices()
    a, b, c = attachment_characteristic_coefficients()
    for mu in (0.03, 0.4, 1.1):
        direct = np.linalg.det(h - mu * k)
        poly = a * mu * mu + b * mu + c
        assert abs(direct - poly) < 1e-13


def test_response_roots_match_representative_values():
    lo, hi = attachment_response_roots()
    assert abs(lo - 0.08620600507952429) < 1e-14
    assert abs(hi - 0.7013884550193837) < 1e-14


def test_response_roots_are_positive_for_positive_inputs():
    for h in (0.01, 0.2, 2.0, 11.0):
        for k in (0.03, 1.0, 8.0):
            lo, hi = attachment_response_roots(h, k)
            assert 0.0 < lo < hi


def test_invalid_nonpositive_inputs_fail_closed():
    for args in ((0.0, 1.0), (1.0, 0.0), (-1.0, 1.0)):
        try:
            attachment_response_roots(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("nonpositive response input accepted")


def test_inverse_sqrt_positive_round_trip():
    a = np.array([[2.0, 1.0], [1.0, 2.0]], dtype=complex)
    r = inverse_sqrt_positive(a)
    assert np.linalg.norm(r @ a @ r - np.eye(2)) < 1e-13


def test_attachment_wentzell_is_hermitian_positive_and_root_matched():
    w = attachment_wentzell_response()
    ev = np.linalg.eigvalsh(w)
    roots = np.asarray(attachment_response_roots())
    assert np.linalg.norm(w - w.conj().T) < 1e-14
    assert np.min(ev) > 0.0
    assert np.max(np.abs(ev - roots)) < 1e-13


def test_attachment_wentzell_representative_matrix_is_stable():
    w = attachment_wentzell_response()
    expected = np.array([[0.105122095454641, -0.106202769950546], [-0.106202769950546, 0.682472364644267]])
    assert np.max(np.abs(w.real - expected)) < 2e-15


def test_generalized_eigenvectors_are_tangent_and_normalized():
    v, vals = attachment_generalized_eigenvectors()
    assert v.shape == (3, 2)
    assert np.linalg.norm(constraint_jacobian() @ v) < 1e-13
    assert np.linalg.norm(v.conj().T @ v - np.eye(2)) < 1e-13
    assert np.max(np.abs(vals - np.asarray(attachment_response_roots()))) < 1e-13


def test_lifted_attachment_wentzell_spectrum_repeats_by_mode_dimension():
    w = lifted_attachment_wentzell(6)
    ev = np.linalg.eigvalsh(w)
    lo, hi = attachment_response_roots()
    assert w.shape == (12, 12)
    assert np.sum(np.isclose(ev, lo, atol=1e-13)) == 6
    assert np.sum(np.isclose(ev, hi, atol=1e-13)) == 6


def test_lifted_operator_data_dimension_doubles_v14_66_mode():
    ks, us, betas = lifted_operator_data()
    assert set(ks) == set(us) == set(betas)
    assert all(x.shape == (12, 12) for x in ks.values())
    assert all(np.linalg.norm(u.conj().T @ u - np.eye(12)) < 1e-12 for u in us.values())


def test_uniform_theorem_wentzell_blocks_are_positive():
    ws = uniform_theorem_wentzell_blocks(6)
    assert len(ws) == 4
    for w in ws.values():
        assert w.shape == (12, 12)
        assert np.min(np.linalg.eigvalsh(w)) > 0.0


def test_uniform_wentzell_self_adjoint_extension_passes():
    d = uniform_wentzell_diagnostics()
    assert d["boundary_dimension"] == 96
    assert d["rank_A_B"] == 96
    assert d["ABstar_minus_BAstar_norm"] < 1e-11
    assert d["self_adjoint_extension_pass"] is True
    assert d["physical_incidence_placement_claim"] is False


def test_uniform_wentzell_green_form_vanishes():
    f0, f1 = sample_uniform_wentzell_domain_data(6, 1467)
    g0, g1 = sample_uniform_wentzell_domain_data(6, 1468)
    assert abs(boundary_green_form(f0, f1, g0, g1)) < 1e-10


def test_lifted_response_operator_is_positive_hermitian():
    h = lifted_response_operator()
    assert h.shape == (48, 48)
    assert np.linalg.norm(h - h.conj().T) < 1e-11
    assert np.min(np.linalg.eigvalsh(h)) > 0.0


def test_lifted_projected_response_remains_positive():
    hp, q = lifted_projected_response()
    assert hp.shape == (46, 46)
    assert q.shape == (48, 46)
    assert np.linalg.norm(q.conj().T @ q - np.eye(46)) < 1e-12
    assert np.min(np.linalg.eigvalsh(hp)) > 0.0


def test_recovered_payload_records_conditional_provenance():
    p = recovered_gram_hessian_payload()
    assert p["source"]["pull_request"] == 218
    assert p["classification_recovered"] == "DERIVED_ON_AUTHOR_SELECTED_FINITE_RADIUS_CORE_BRANCH"
    assert p["source_ledger"]["depth_curvature"] == "CONDITIONAL_SPECTRAL_ACTION_ASSIGNMENT"
    assert p["physical_unconditional_Gram_Hessian_claim"] is False


def test_normalization_reconciliation_rejects_mixed_pencil():
    p = normalization_reconciliation_payload()
    assert p["mixed_whitened_unwhitened_pencil_forbidden"] is True
    assert p["earlier_manual_unwhitened_packet_pencil_authoritative"] is False


def test_attachment_wentzell_payload_replaces_arbitrary_theorem_schur_block():
    p = attachment_wentzell_payload()
    assert p["attachment_response_positive"] is True
    assert p["generalized_root_match_residual"] < 1e-12
    assert p["uniform_theorem_lift"]["self_adjoint_extension_pass"] is True
    assert p["arbitrary_v14_66_diagnostic_Schur_block_needed_for_this_theorem_lift"] is False
    assert p["physical_diamond_incidence_map_derived"] is False


def test_operator_response_insertion_is_finite_and_fail_closed():
    p = operator_response_insertion_payload()
    assert p["response_minimum_eigenvalue"] > 0.0
    assert p["projected_minimum_eigenvalue"] > 0.0
    assert math.isfinite(p["diagnostic_attachment_increment_heat_trace"])
    assert math.isfinite(p["diagnostic_attachment_increment_logdet"])
    assert p["actual_M8_M5_M4_tangential_operators_inserted"] is False


def test_provenance_gate_is_fail_closed():
    p = provenance_gate_payload()
    assert p["recovered_algebraic_Gram_Hessian_available"] is True
    assert p["recovered_Gram_Hessian_unconditional_physical"] is False
    assert p["all_physical_provenance_inputs_present"] is False
    assert p["postcomparison_parameter_choice_allowed"] is False


def test_neutrino_kill_screen_blocks_physical_execution():
    p = neutrino_kill_screen_payload()
    assert p["physical_execution_allowed"] is False
    assert p["current_result"] == "PHYSICAL_EXECUTION_BLOCKED"
    assert p["physical_mass_PMNS_or_splitting_emitted"] is False


def test_status_ledger_has_hindsight_categories():
    p = status_payload()
    assert len(p["validated"]) >= 8
    assert len(p["invalidated"]) >= 3
    assert len(p["reclassified"]) >= 4
    assert len(p["open"]) >= 10


def test_completion_gate_fails_closed_and_usb_untouched():
    p = completion_gate_payload()
    assert p["full_BHSM_complete"] is False
    assert p["mark_III"] == "NOT_REACHED"
    assert p["usb_touched"] is False
    assert p["physical_unconditional_common_attachment_response_closed"] is False


def test_next_object_is_global_provenance_not_missing_algebra():
    p = next_object_payload()
    assert "global action provenance" in p["highest_upstream_blocker"]
    assert p["postcomparison_choice_forbidden"] is True


def test_artifact_payload_set_is_complete():
    payloads = artifact_payloads()
    assert len(payloads) == 10
    assert "BHSM_completion_gate_v14_67.json" in payloads


def test_materialize_is_byte_deterministic(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    pa = materialize(a)
    pb = materialize(b)
    assert [x.name for x in pa] == [x.name for x in pb]
    for x, y in zip(pa, pb):
        assert x.read_bytes() == y.read_bytes()
