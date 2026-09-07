"""Independent full-system checks of the conditional response handoff."""

import mpmath as mp
import numpy as np
import pytest

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    solve_retarded_event_kkt,
)
from bhsm.interface.ae4_current_c2_factorized_hs_calderon import (
    factorized_product_dirac_hs_weyl_jet,
    terminal_hs_jet_transport_coefficients,
)

from bhsm.interface.ae4_event_response_jet_integration import (
    solve_retarded_event_kkt_jet, substitute_terminal_hs_jets,
    canonical_noether_flux_balance_jet,
)


def _data():
    # Deliberately noncommuting complex blocks and moving constraints. These
    # are numerical theorem witnesses, never current-C2 physical data.
    return {
        "parent_jet": (
            np.array([[4, 0.2j], [-0.2j, 3]]),
            np.array([[0.2, 0.1], [0.1, -0.3]]), np.diag([0.1, 0.2])),
        "coupling_jet": (
            np.array([[0.3, 0.1j], [0.2, 0.4]]),
            np.array([[0.1j, -0.2], [0.3, 0.1]]), np.diag([0.2, -0.1j])),
        "child_retarded_jet": (
            np.array([[2 + 0.4j, 0.1], [0.1, 3 + 0.2j]]),
            np.array([[0.2j, 0.3], [-0.1, 0.2]]), np.diag([0.1j, 0.2j])),
        "response_jet": (np.array([[1, 0.2j]]), np.array([[0.1j, 0.3]]), np.array([[0.2, -0.1j]])),
        "source_jet": (np.array([1, 0.5j]), np.array([0.2j, 0.1]), np.array([0.3, -0.2])),
        "response_target_jet": (np.array([0.1]), np.array([0.2j]), np.array([-0.1])),
    }


def _full_system_derivatives(data):
    """Differentiate unreduced parent-child KKT; no Schur formula reused."""
    with mp.workdps(55):
        jets = {key: [mp.matrix(a.tolist()) for a in values] for key, values in data.items()}

        def evaluate(t):
            p, b, l, c, j, d = [values[0] + t * values[1] + t*t/2 * values[2]
                                for values in jets.values()]
            full = mp.zeros(5)
            for row in range(2):
                for col in range(2):
                    full[row, col] = p[row, col]
                    full[row, col + 2] = b[row, col]
                    full[row + 2, col] = mp.conj(b[col, row])
                    full[row + 2, col + 2] = l[row, col]
                full[row, 4] = mp.conj(c[0, row])
                full[4, row] = c[0, row]
            return mp.lu_solve(full, mp.matrix([-j[0], -j[1], 0, 0, d[0]]))

        return [np.array([complex(mp.diff(lambda t: evaluate(t)[i], 0, order))
                          for i in range(5)]) for order in range(3)]


def test_response_jets_match_independent_unreduced_high_precision_system():
    data = _data()
    actual = solve_retarded_event_kkt_jet(**data)
    expected = _full_system_derivatives(data)
    for order in range(3):
        combined = np.concatenate((actual["parent_trace_jet"][order],
                                   actual["future_child_state_jet"][order],
                                   actual["response_multiplier_jet"][order]))
        np.testing.assert_allclose(combined, expected[order], rtol=1e-12, atol=1e-13)
    for key in ("event_balance_residual_norms", "child_equation_residual_norms",
                "response_constraint_residual_norms"):
        assert max(actual[key]) < 2e-14
    assert not actual["physical_sector_values_certified"]
    noether = canonical_noether_flux_balance_jet(
        trace_jet=actual["parent_trace_jet"],
        event_traction_jets=actual["event_traction_jets"], generator=1j * np.diag([1, 2]))
    assert max(abs(v) for v in noether["canonical_noether_flux_residual_jet"]) < 2e-14
    # Each traction's derivative includes variation of the trace as well.
    q0, q1, q2 = actual["parent_trace_jet"]
    t0, t1, t2 = actual["event_traction_jets"]["explicit_source"]
    transform = 1j * np.diag([1, 2])
    expected_second = 2 * np.real(np.vdot(transform @ q2, t0)
                                 + 2*np.vdot(transform @ q1, t1)
                                 + np.vdot(transform @ q0, t2))
    assert noether["canonical_noether_flux_term_jets"]["explicit_source"][2] == pytest.approx(expected_second)


@pytest.mark.parametrize("with_response", [True, False])
def test_zero_order_preserves_existing_event_solver(with_response):
    data = _data()
    if not with_response:
        data["response_jet"] = tuple(np.empty((0, 2)) for _ in range(3))
        data["response_target_jet"] = tuple(np.empty(0) for _ in range(3))
    result = solve_retarded_event_kkt_jet(**data)
    old = solve_retarded_event_kkt(
        parent_block=data["parent_jet"][0], parent_child_coupling=data["coupling_jet"][0],
        child_retarded_block=data["child_retarded_jet"][0], response_operator=data["response_jet"][0],
        source=data["source_jet"][0], response_target=data["response_target_jet"][0])
    np.testing.assert_allclose(result["parent_trace_jet"][0], old["parent_trace"], atol=1e-14)


@pytest.mark.parametrize("bad", [
    (np.eye(2),), (np.eye(2), np.ones((1, 2)), np.eye(2)),
    (np.eye(2), np.full((2, 2), np.nan), np.eye(2)), (1, 2, 3),
    (np.eye(2), np.array([[0, 1], [0, 0]]), np.eye(2)),
])
def test_invalid_or_incomplete_jets_fail_closed(bad):
    data = _data()
    data["parent_jet"] = bad
    with pytest.raises(ValueError):
        solve_retarded_event_kkt_jet(**data)


def test_missing_and_singular_child_data_are_not_replaced_by_zero():
    data = _data()
    del data["child_retarded_jet"]
    with pytest.raises(TypeError):
        solve_retarded_event_kkt_jet(**data)
    data = _data()
    data["child_retarded_jet"] = tuple(np.zeros((2, 2)) for _ in range(3))
    with pytest.raises(np.linalg.LinAlgError):
        solve_retarded_event_kkt_jet(**data)


@pytest.mark.parametrize("chirality", [-1, 1])
def test_terminal_substitution_matches_full_segment_jet_transport(chirality):
    arguments = dict(log_radii=np.array([0., 0.1, -0.2, 0.05]),
                     proper_durations=np.array([0.2, 0.3, 0.1]),
                     source_profile=np.array([1., -0.5, 0.25]),
                     dirac_eigenvalue_at_unit_radius=1.5, chirality=chirality,
                     spectral_parameter=-1., terminal_load=0.5, decimal_precision=60)
    coefficients = terminal_hs_jet_transport_coefficients(**arguments)
    substituted = substitute_terminal_hs_jets(
        coefficients, terminal_load_first="0.375", terminal_load_second="-0.25")
    propagated = factorized_product_dirac_hs_weyl_jet(
        **arguments, terminal_load_first="0.375", terminal_load_second="-0.25")
    with mp.workdps(60):
        for key in ("Weyl_birth_value_decimal", "D_H_Weyl_birth_decimal", "D2_H_Weyl_birth_decimal"):
            assert abs(mp.mpf(substituted[key]) - mp.mpf(propagated[key])) < mp.mpf("1e-50")
    assert not substituted["finite_core_recomputed"]
    assert not substituted["physical_terminal_HS_jets_selected"]
    with pytest.raises(TypeError):
        substitute_terminal_hs_jets(coefficients, terminal_load_first=0)
    with pytest.raises(ValueError):
        substitute_terminal_hs_jets(coefficients, terminal_load_first="nan", terminal_load_second=0)


def test_saved_full_core_handoff_materializes_deterministically_without_core_solve(monkeypatch):
    import bhsm.interface.ae4_current_c2_factorized_hs_calderon as core
    import scripts.materialize_ae4_event_response_jet_integration as materializer

    def no_recomputation(**kwargs):
        raise AssertionError("saved transport handoff must not rerun the core")

    monkeypatch.setattr(core, "factorized_product_dirac_hs_weyl_jet", no_recomputation)
    import json
    first = json.dumps(materializer.build_payload(), sort_keys=True)
    second = json.dumps(materializer.build_payload(), sort_keys=True)
    assert first == second
    payload = json.loads(first)
    assert payload["validation_passed"]
    assert not payload["current_C2_physical_event_response_evaluated"]
    assert not payload["Gate7_action_center_caches_or_proof_contract_changed"]
