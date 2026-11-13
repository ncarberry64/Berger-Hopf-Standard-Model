"""Independent two-source checks of the conditional AE4 event handoff."""

import mpmath as mp
import numpy as np
import pytest

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import solve_retarded_event_kkt
from bhsm.interface.ae4_event_response_jet_integration import (
    canonical_noether_flux_balance_jet,
    solve_retarded_event_kkt_jet,
)
from bhsm.interface.ae4_mixed_event_response import (
    canonical_noether_flux_balance_mixed_jet,
    solve_retarded_event_kkt_mixed_jet,
)


def _data():
    # Noncommuting complex finite theorem witnesses, never physical C2 inputs.
    return {
        "parent_jet": (
            np.array([[4, 0.2j], [-0.2j, 3]]),
            np.array([[0.2, 0.1], [0.1, -0.3]]),
            np.array([[0.4, -0.15j], [0.15j, -0.2]]),
            np.array([[0.1, 0.07 + 0.03j], [0.07 - 0.03j, 0.2]])),
        "coupling_jet": (
            np.array([[0.3, 0.1j], [0.2, 0.4]]),
            np.array([[0.1j, -0.2], [0.3, 0.1]]),
            np.array([[0.2, 0.3j], [-0.1j, 0.15]]),
            np.array([[0.2, 0.12], [0.08j, -0.1j]])),
        "child_retarded_jet": (
            np.array([[2 + 0.4j, 0.1], [0.1, 3 + 0.2j]]),
            np.array([[0.2j, 0.3], [-0.1, 0.2]]),
            np.array([[0.15, 0.04j], [0.2, -0.05j]]),
            np.array([[0.1j, 0.07], [-0.03j, 0.2j]])),
        "response_jet": (
            np.array([[1, 0.2j]]), np.array([[0.1j, 0.3]]),
            np.array([[0.12, -0.2j]]), np.array([[0.2, -0.1j]])),
        "source_jet": (
            np.array([1, 0.5j]), np.array([0.2j, 0.1]),
            np.array([-0.1, 0.3j]), np.array([0.3, -0.2])),
        "response_target_jet": (
            np.array([0.1]), np.array([0.2j]),
            np.array([0.15]), np.array([-0.1])),
    }


def _full_system(data):
    """Build the unreduced 5 by 5 system independently of any Schur solve."""
    jets = {name: [mp.matrix(entry.tolist()) for entry in values]
            for name, values in data.items()}

    def polynomial(name, u, v):
        a = jets[name]
        return a[0] + u*a[1] + v*a[2] + u*v*a[3]

    def evaluate(u, v):
        p, b, l, c, j, d = [polynomial(name, u, v) for name in data]
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

    return evaluate, polynomial


def test_mixed_jets_match_independent_bivariate_full_system_and_noether():
    data = _data()
    result = solve_retarded_event_kkt_mixed_jet(**data)
    generator = 1j * np.diag([1., 2.])
    noether = canonical_noether_flux_balance_mixed_jet(
        trace_jet=result["parent_trace_jet"],
        event_traction_jets=result["event_traction_jets"], generator=generator)
    with mp.workdps(60):
        evaluate, polynomial = _full_system(data)
        for index, orders in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            expected = np.array([complex(mp.diff(
                lambda u, v: evaluate(u, v)[i], (0, 0), orders)) for i in range(5)])
            actual = np.concatenate((result["parent_trace_jet"][index],
                                     result["future_child_state_jet"][index],
                                     result["response_multiplier_jet"][index]))
            np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-13)

        def source_flux(u, v):
            q = evaluate(u, v)
            j = polynomial("source_jet", u, v)
            return 2*mp.re(sum(mp.conj(mp.mpc(generator[i, i])*q[i])*j[i]
                               for i in range(2)))

        expected_flux = float(mp.diff(source_flux, (0, 0), (1, 1)))
        assert noether["canonical_noether_flux_term_jets"]["explicit_source"][3] == pytest.approx(
            expected_flux, rel=1e-12, abs=1e-13)
    for key in ("event_balance_residual_norms", "child_equation_residual_norms",
                "response_constraint_residual_norms"):
        assert len(result[key]) == 4
        assert max(result[key]) < 2e-14
    for key in ("event_canonical_flux_balance_jet", "child_equation_residual_jet",
                "response_constraint_residual_jet"):
        assert len(result[key]) == 4
    assert max(abs(v) for v in noether["canonical_noether_flux_residual_jet"]) < 2e-14
    q, t = result["parent_trace_jet"], data["source_jet"]
    omitted_cross_legs = 2*np.real(np.vdot(generator @ q[3], t[0])
                                  + np.vdot(generator @ q[0], t[3]))
    assert abs(expected_flux - omitted_cross_legs) > 1e-3
    assert result["residual_normalization"] == "RAW_UNREDUCED_EQUATIONS_IN_SUPPLIED_COORDINATES"
    assert not result["physical_sector_values_certified"]
    assert not result["explicit_inverse_formed"]
    assert not result["regularizer_or_pseudoinverse_used"]
    assert not noether["physical_Hamiltonian_readout_closed"]


def test_equal_source_directions_recover_existing_scalar_second_jet():
    original = _data()
    mixed_data = {name: (values[0], values[1], values[1], values[3])
                  for name, values in original.items()}
    scalar_data = {name: (values[0], values[1], values[3])
                   for name, values in original.items()}
    mixed = solve_retarded_event_kkt_mixed_jet(**mixed_data)
    scalar = solve_retarded_event_kkt_jet(**scalar_data)
    for key in ("parent_trace_jet", "future_child_state_jet", "response_multiplier_jet",
                "effective_retarded_parent_jet"):
        for left, right in ((0, 0), (1, 1), (2, 1), (3, 2)):
            np.testing.assert_allclose(mixed[key][left], scalar[key][right], atol=1e-14)
    generator = 1j*np.diag([1., 2.])
    mixed_flux = canonical_noether_flux_balance_mixed_jet(
        trace_jet=mixed["parent_trace_jet"],
        event_traction_jets=mixed["event_traction_jets"], generator=generator)
    scalar_flux = canonical_noether_flux_balance_jet(
        trace_jet=scalar["parent_trace_jet"],
        event_traction_jets=scalar["event_traction_jets"], generator=generator)
    for name in mixed_flux["canonical_noether_flux_term_jets"]:
        assert mixed_flux["canonical_noether_flux_term_jets"][name][3] == pytest.approx(
            scalar_flux["canonical_noether_flux_term_jets"][name][2], abs=1e-14)


def test_swapping_sources_exchanges_first_leaves_and_preserves_mixed_response():
    data = _data()
    swapped = {name: (a[0], a[2], a[1], a[3]) for name, a in data.items()}
    first = solve_retarded_event_kkt_mixed_jet(**data)
    second = solve_retarded_event_kkt_mixed_jet(**swapped)
    for key in ("parent_trace_jet", "future_child_state_jet", "response_multiplier_jet",
                "effective_retarded_parent_jet"):
        for left, right in ((0, 0), (1, 2), (2, 1), (3, 3)):
            np.testing.assert_allclose(first[key][left], second[key][right], atol=1e-14)


@pytest.mark.parametrize("with_response", [True, False])
def test_zero_order_matches_existing_retarded_event_solve(with_response):
    data = _data()
    if not with_response:
        data["response_jet"] = tuple(np.empty((0, 2)) for _ in range(4))
        data["response_target_jet"] = tuple(np.empty(0) for _ in range(4))
    result = solve_retarded_event_kkt_mixed_jet(**data)
    existing = solve_retarded_event_kkt(
        parent_block=data["parent_jet"][0], parent_child_coupling=data["coupling_jet"][0],
        child_retarded_block=data["child_retarded_jet"][0], response_operator=data["response_jet"][0],
        source=data["source_jet"][0], response_target=data["response_target_jet"][0])
    np.testing.assert_allclose(result["parent_trace_jet"][0], existing["parent_trace"], atol=1e-14)


def test_fixed_nonunitary_chart_changes_preserve_unreduced_response():
    data = _data()
    a = np.array([[1.3, 0.2j], [0.1, 0.8]])
    e = np.array([[0.9, 0.15], [0.05j, 1.4]])
    r = np.array([[1.2 + 0.1j]])
    changed = {
        "parent_jet": tuple(a.conj().T @ v @ a for v in data["parent_jet"]),
        "coupling_jet": tuple(a.conj().T @ v @ e for v in data["coupling_jet"]),
        "child_retarded_jet": tuple(e.conj().T @ v @ e for v in data["child_retarded_jet"]),
        "response_jet": tuple(r @ v @ a for v in data["response_jet"]),
        "source_jet": tuple(a.conj().T @ v for v in data["source_jet"]),
        "response_target_jet": tuple(r @ v for v in data["response_target_jet"]),
    }
    first = solve_retarded_event_kkt_mixed_jet(**data)
    second = solve_retarded_event_kkt_mixed_jet(**changed)
    for order in range(4):
        np.testing.assert_allclose(second["parent_trace_jet"][order],
                                   np.linalg.solve(a, first["parent_trace_jet"][order]), atol=1e-14)
        np.testing.assert_allclose(second["future_child_state_jet"][order],
                                   np.linalg.solve(e, first["future_child_state_jet"][order]), atol=1e-14)
        np.testing.assert_allclose(second["response_multiplier_jet"][order],
                                   np.linalg.solve(r.conj().T, first["response_multiplier_jet"][order]), atol=1e-14)
        for name in first["event_traction_jets"]:
            np.testing.assert_allclose(second["event_traction_jets"][name][order],
                                       a.conj().T @ first["event_traction_jets"][name][order], atol=1e-14)


@pytest.mark.parametrize("name", tuple(_data()))
def test_every_leaf_is_mandatory_and_unknown_mixed_leaf_is_rejected(name):
    data = _data()
    data[name] = data[name][:3]
    with pytest.raises(ValueError):
        solve_retarded_event_kkt_mixed_jet(**data)
    data = _data()
    data[name] = (*data[name][:3], np.full(data[name][3].shape, np.nan))
    with pytest.raises(ValueError):
        solve_retarded_event_kkt_mixed_jet(**data)
    data = _data()
    del data[name]
    with pytest.raises(TypeError):
        solve_retarded_event_kkt_mixed_jet(**data)


@pytest.mark.parametrize("name,bad", [
    ("parent_jet", (np.ones((2, 3)),)*4),
    ("coupling_jet", (np.ones((2, 3)),)*4),
    ("response_jet", (np.ones((1, 3)),)*4),
    ("source_jet", (np.ones((2, 1)),)*4),
    ("response_target_jet", (np.ones(2),)*4),
    ("child_retarded_jet", (np.ones((1, 2)),)*4),
    ("parent_jet", (1, 2, 3, 4)),
])
def test_incompatible_jets_are_rejected(name, bad):
    data = _data()
    data[name] = bad
    with pytest.raises(ValueError):
        solve_retarded_event_kkt_mixed_jet(**data)


def test_nonhermitian_mixed_parent_and_singular_blocks_fail_closed():
    data = _data()
    data["parent_jet"] = (*data["parent_jet"][:3], np.array([[0, 1], [0, 0]]))
    with pytest.raises(ValueError):
        solve_retarded_event_kkt_mixed_jet(**data)
    data = _data()
    data["child_retarded_jet"] = tuple(np.zeros((2, 2)) for _ in range(4))
    with pytest.raises(np.linalg.LinAlgError):
        solve_retarded_event_kkt_mixed_jet(**data)
    data = _data()
    data["response_jet"] = tuple(np.zeros((1, 2)) for _ in range(4))
    with pytest.raises(np.linalg.LinAlgError):
        solve_retarded_event_kkt_mixed_jet(**data)


def test_finite_inputs_with_unrepresentable_solution_do_not_return_nan_jets():
    data = _data()
    data["child_retarded_jet"] = (
        1e-320*np.eye(2), np.zeros((2, 2)), np.zeros((2, 2)), np.zeros((2, 2)))
    with pytest.raises(ArithmeticError, match="finite solved response"):
        solve_retarded_event_kkt_mixed_jet(**data)


@pytest.mark.parametrize("trace,tractions,generator", [
    ((np.ones(2),)*3, {"source": (np.ones(2),)*4}, 1j*np.eye(2)),
    ((np.ones(2),)*4, {"source": (np.ones(2),)*3}, 1j*np.eye(2)),
    ((np.ones(2),)*4, {}, 1j*np.eye(2)),
    ((np.ones(2),)*4, {"source": (np.ones(3),)*4}, 1j*np.eye(2)),
    ((np.ones(2),)*4, {"source": (np.ones(2),)*4}, np.eye(2)),
    ((np.ones(2),)*4, {"source": (np.ones(2),)*4}, 1j*np.eye(3)),
])
def test_mixed_noether_rejects_incomplete_or_incompatible_inputs(trace, tractions, generator):
    with pytest.raises(ValueError):
        canonical_noether_flux_balance_mixed_jet(
            trace_jet=trace, event_traction_jets=tractions, generator=generator)
