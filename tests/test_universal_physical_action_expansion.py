import itertools

import jax
import jax.numpy as jnp
import numpy as np
import pytest

from bhsm.interface.universal_physical_action_expansion import (
    JaxDirectionalActionOracle,
    PhysicalActionExpansion,
    PhysicalBackground,
)


jax.config.update("jax_enable_x64", True)


def polynomial_action(x):
    return (
        0.5 * x @ jnp.diag(jnp.asarray([2.0, 3.0, 5.0])) @ x
        + x[0] * x[1] * x[2]
        + 0.25 * x[0] ** 2 * x[1] ** 2
    )


def expansion(gate7_closed: bool = False) -> PhysicalActionExpansion:
    angle = 0.37
    frame = np.asarray([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
        [0.0, 0.0],
    ])
    background = PhysicalBackground(
        state=np.asarray([0.2, -0.3, 0.7]),
        physical_frame=frame,
        action_version="TEST-ACTION",
        background_id="test-background",
        gate7_closed=gate7_closed,
        provenance=("unit-test",),
    )
    return PhysicalActionExpansion(JaxDirectionalActionOracle(polynomial_action), background)


def test_quadratic_matrix_is_the_projected_action_hessian() -> None:
    result = expansion()
    hessian = np.asarray(jax.hessian(polynomial_action)(jnp.asarray(result.background.state)))
    expected = result.background.physical_frame.T @ hessian @ result.background.physical_frame
    assert np.allclose(result.quadratic_matrix(), expected, rtol=2.0e-13, atol=2.0e-13)


def test_cubic_and_quartic_vertices_are_permutation_symmetric() -> None:
    result = expansion()
    directions = (np.asarray([1.0, 0.0]), np.asarray([0.0, 1.0]), np.asarray([0.6, -0.8]))
    cubic = [result.vertex(3, order) for order in itertools.permutations(directions)]
    assert np.max(cubic) - np.min(cubic) < 1.0e-12

    fourth_directions = directions + (np.asarray([0.3, 0.4]),)
    fourth = [result.vertex(4, order) for order in itertools.permutations(fourth_directions)]
    assert np.max(fourth) - np.min(fourth) < 1.0e-12


def test_complex_polarizations_use_multilinear_real_action_extension() -> None:
    result = expansion()
    first = np.asarray([1.0 + 2.0j, -0.3j])
    second = np.asarray([0.4 - 0.2j, 0.7])

    direct = result.s2(first, second)
    expanded = (
        result.s2(first.real, second.real)
        + 1.0j * result.s2(first.imag, second.real)
        + 1.0j * result.s2(first.real, second.imag)
        - result.s2(first.imag, second.imag)
    )
    assert abs(direct - expanded) < 1.0e-13


def test_gate7_is_a_physical_promotion_boundary() -> None:
    provisional = expansion(gate7_closed=False)
    assert provisional.metadata()["promotion_status"] == "PROVISIONAL_BACKGROUND_ONLY"
    with pytest.raises(RuntimeError, match="Gate 7 is not closed"):
        provisional.require_physical_promotion()

    promoted = expansion(gate7_closed=True)
    promoted.require_physical_promotion()
    assert promoted.metadata()["promotion_status"] == "PHYSICAL_BACKGROUND_FROZEN"
    assert promoted.metadata()["dense_fourth_tensor_formed"] is False
