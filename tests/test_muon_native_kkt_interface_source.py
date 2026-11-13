"""Independent finite-action controls for the fixed-coordinate KKT source.

These controls do not supply the missing physical owner action or xi_psi.
"""
from dataclasses import replace

import pytest
import sympy as sp

from bhsm.interface.muon_native_kkt_interface_source import (
    OwnerAction,
    SignedSector,
    differentiate_owner_kkt,
    finite_control_action,
    finite_control_branch_jets,
    solve_owner_kkt,
)


@pytest.fixture
def independent_action():
    x, y, ell, s = sp.symbols("x y ell s", real=True)
    positive = 2*x**2 + x*y + 3*y**2 + s*(7*x + 11*y) + sp.Rational(13, 2)*s**2
    reset = 2*x + 2*y
    constraint = x + y + s*(3*x - 2*y) + 4*s + sp.Rational(5, 2)*s**2 + x**2/2
    return OwnerAction(
        eta=(x, y),
        multipliers=(ell,),
        source=s,
        action_sectors=(
            SignedSector("bulk_geometric", positive),
            SignedSector("reset", reset, sign=-1),
        ),
        constraints=(constraint,),
        base={x: 0, y: 0, ell: 2, s: 0},
        owner_identity={
            "action": "independent finite polynomial control",
            "domain": "two real configurations and one equality constraint",
            "pairing": "real Euclidean action dual",
            "branch": "stationary origin with ell=2",
        },
        source_provenance="independent finite displacement control; physical xi_psi unevaluated",
        b_psi=sp.Matrix(range(1, 8)),
        required_sectors=("bulk_geometric", "reset"),
        constraint_provenance=("signed polynomial constraint of the independent finite action",),
    )


def independent_lagrangian(action):
    bulk = sum(sector.sign*sector.expression for sector in action.action_sectors)
    return bulk + sum(multiplier*constraint for multiplier, constraint in
                      zip(action.multipliers, action.constraints))


def test_direct_fixed_coordinate_residual_derivative(independent_action):
    action = independent_action
    L = independent_lagrangian(action)
    residual = sp.Matrix([sp.diff(L, q) for q in action.eta] + list(action.constraints))
    expected = residual.diff(action.source).subs(action.base)
    result = differentiate_owner_kkt(action)
    assert expected == sp.Matrix([13, 7, 4])
    assert result["h_psi"] == expected
    # Differentiating at fixed multipliers introduces no response symbol.
    assert not result["h_psi"].free_symbols
    assert residual.subs(action.base) == sp.zeros(3, 1)


def test_mixed_constraint_and_multiplier_contacts_retained(independent_action):
    result = differentiate_owner_kkt(independent_action)
    assert result["S_eta_s"] == sp.Matrix([7, 11])
    assert result["R_eta_s"] == sp.Matrix([[3, -2]])
    assert result["R_s"] == sp.Matrix([4])
    assert result["h_psi"][:2, :] == sp.Matrix([7, 11]) + sp.Matrix([6, -4])
    # Both the nonlinear configuration contact and lambda*R_ss are needed.
    assert result["H_KKT"] == sp.Matrix([[6, 1, 1], [1, 6, 1], [1, 1, 0]])
    assert result["L_ss"] == 23


def test_one_column_response_retains_constraint_reaction(independent_action):
    result = solve_owner_kkt(independent_action)
    assert result["delta_psi"] == sp.Matrix([-sp.Rational(13, 5), -sp.Rational(7, 5), 4])
    assert result["H_KKT"]*result["delta_psi"] + result["h_psi"] == sp.zeros(3, 1)
    assert sum(result["delta_psi"][:2]) == -4
    assert result["delta_psi"][2] == 4
    # This finite control has negative reduced curvature and indefinite KKT.
    assert result["z_psi"] == -sp.Rational(23, 5)


def test_schur_matches_independent_full_action_quadratic(independent_action):
    action = independent_action
    result = solve_owner_kkt(action)
    L = independent_lagrangian(action)
    delta = result["delta_psi"]
    variables = action.eta + action.multipliers
    curve = {q: action.base[q] + action.source*delta[k] for k, q in enumerate(variables)}
    pulled = L.subs(curve, simultaneous=True)
    direct = sp.diff(pulled, action.source, 2).subs(action.source, 0)
    assert direct == result["z_psi"]
    assert direct == result["direct_quadratic"]


def test_arbitrary_residual_row_map_cannot_change_owner_impedance(independent_action):
    result = solve_owner_kkt(independent_action)
    H, h = result["H_KKT"], result["h_psi"]
    rows = sp.Matrix([[2, 1, 0], [0, 3, 1], [0, 0, 5]])
    delta_rows = -(rows*H).LUsolve(rows*h)
    assert delta_rows == result["delta_psi"]
    owner_result = result["L_ss"] + (h.T*delta_rows)[0]
    assert owner_result == result["z_psi"]
    naive_row_contraction = result["L_ss"] + ((rows*h).T*delta_rows)[0]
    assert naive_row_contraction != owner_result


def test_action_owned_constraint_rescaling_uses_contragredient_multiplier(independent_action):
    action = independent_action
    ell = action.multipliers[0]
    rescaled = replace(action, constraints=(5*action.constraints[0],),
                       base={**action.base, ell: sp.Rational(2, 5)})
    original = solve_owner_kkt(action)
    scaled = solve_owner_kkt(rescaled)
    assert scaled["delta_psi"][:2, :] == original["delta_psi"][:2, :]
    assert scaled["delta_psi"][2]*5 == original["delta_psi"][2]
    assert scaled["z_psi"] == original["z_psi"]
    assert scaled["L_ss"] == original["L_ss"]


def test_missing_sector_remains_unevaluated(independent_action):
    action = replace(independent_action, required_sectors=independent_action.required_sectors + ("contact",))
    with pytest.raises(ValueError):
        differentiate_owner_kkt(action)


def test_unknown_sector_is_not_a_zero(independent_action):
    with pytest.raises((TypeError, ValueError)):
        unknown = SignedSector("bulk_geometric", None)
        action = replace(independent_action, action_sectors=(unknown, independent_action.action_sectors[1]))
        differentiate_owner_kkt(action)


@pytest.mark.parametrize("size", [6, 8])
def test_exactly_seven_boundary_coordinates_required(independent_action, size):
    with pytest.raises(ValueError):
        differentiate_owner_kkt(replace(independent_action, b_psi=sp.ones(size, 1)))


def test_nonstationary_base_fails_closed(independent_action):
    action = independent_action
    with pytest.raises(ValueError):
        differentiate_owner_kkt(replace(action, base={**action.base, action.multipliers[0]: 0}))


def test_multiplier_response_occurs_only_in_total_residual_derivative(independent_action):
    action = independent_action
    data = differentiate_owner_kkt(action)
    dx, dy, lambda_s = sp.symbols("dx dy lambda_s", real=True)
    response = sp.Matrix([dx, dy, lambda_s])
    curve = {q: action.base[q] + action.source*response[k]
             for k, q in enumerate(data["variables"])}
    total = data["E"].subs(curve, simultaneous=True).diff(action.source).subs(action.source, 0)
    assert total == data["H_KKT"]*response + data["h_psi"]
    assert total.diff(lambda_s) == sp.Matrix([1, 1, 0])
    assert data["h_psi"].diff(lambda_s) == sp.zeros(3, 1)


def test_source_source_multiplier_contact_changes_only_reduced_curvature(independent_action):
    action = independent_action
    without_contact = replace(action, constraints=(
        action.constraints[0] - sp.Rational(5, 2)*action.source**2,
    ))
    full = solve_owner_kkt(action)
    removed = solve_owner_kkt(without_contact)
    assert full["H_KKT"] == removed["H_KKT"]
    assert full["h_psi"] == removed["h_psi"]
    assert full["delta_psi"] == removed["delta_psi"]
    assert full["z_psi"] - removed["z_psi"] == 10


def test_irrational_derivative_is_not_silently_narrowed_for_arb(independent_action):
    action = independent_action
    first, second = action.action_sectors
    changed = replace(first, expression=first.expression + sp.sqrt(2)*action.source*action.eta[0])
    irrational = replace(action, action_sectors=(changed, second))
    assert differentiate_owner_kkt(irrational)["h_psi"][0] == 13 + sp.sqrt(2)
    with pytest.raises(ValueError, match="rational"):
        solve_owner_kkt(irrational)


def test_constraints_cannot_depend_on_their_multipliers(independent_action):
    action = independent_action
    changed = replace(action, constraints=(action.constraints[0] + action.source*action.multipliers[0],))
    with pytest.raises(ValueError, match="independent"):
        differentiate_owner_kkt(changed)


def test_duplicate_sector_and_unproven_zero_fail_closed(independent_action):
    action = independent_action
    with pytest.raises(ValueError, match="double counted"):
        differentiate_owner_kkt(replace(action, action_sectors=action.action_sectors + (action.action_sectors[0],)))
    zero = replace(action.action_sectors[1], expression=sp.S.Zero)
    with pytest.raises(ValueError, match="zero needs"):
        differentiate_owner_kkt(replace(action, action_sectors=(action.action_sectors[0], zero)))


def test_arb_replay_encloses_exact_owner_result(independent_action):
    from flint import arb
    data = solve_owner_kkt(independent_action)
    assert all(value.contains(0) for value in data["arb_replay"].entries())
    assert data["arb_direct_minus_schur"].contains(0)
    assert data["arb_z"].contains(arb("-23/5"))


def test_control_port_is_existing_trace_momentum_dynamic_flux_order():
    q = sp.Rational
    action = finite_control_action()
    expected = sp.Matrix([
        q(1, 5) + q(1, 11), q(2, 7) - q(1, 13), -q(1, 3) + q(1, 17),
        q(2, 5), -q(3, 7),
        q(11, 13) - q(1, 19) - q(3, 29) - q(7, 37),
        q(5, 17) + q(2, 23) + q(5, 31) - q(11, 41),
    ])
    assert action.b_psi == expected
    assert action.b_psi.shape == (7, 1)


def test_total_impedance_branch_jets_follow_same_stationary_control_action():
    v, J = sp.symbols("v J", real=True)
    action = finite_control_action(v, J)
    L = independent_lagrangian(action)
    residual = sp.Matrix([sp.diff(L, q) for q in action.eta] + list(action.constraints))
    assert residual.subs(action.base, simultaneous=True) == sp.zeros(3, 1)
    H = residual.jacobian(action.eta + action.multipliers).subs(action.base, simultaneous=True)
    h = residual.diff(action.source).subs(action.base, simultaneous=True)
    Lss = sp.diff(L, action.source, 2).subs(action.base, simultaneous=True)
    delta = H.LUsolve(-h)
    z = Lss + (h.T*delta)[0]
    expected = {"value": z, "v": sp.diff(z, v), "J": sp.diff(z, J), "vJ": sp.diff(z, v, J)}
    reported = finite_control_branch_jets()["owner_z"]
    for key, value in expected.items():
        assert sp.sympify(reported[key]) == sp.simplify(value.subs({v: 0, J: 0}))
