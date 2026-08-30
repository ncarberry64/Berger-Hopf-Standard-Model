import numpy as np
import pytest

from bhsm.interface.universal_external_state_sum import (
    ExternalStateBasis,
    external_state_amplitude_squared,
)


def basis(label: str = "physical-q") -> ExternalStateBasis:
    return ExternalStateBasis(np.eye(2, dtype=complex), label)


def test_unpolarized_incoming_average_and_outgoing_sum() -> None:
    spaces = (basis(), basis(), basis())

    def amplitude(modes):
        first, second, final = (int(np.argmax(np.abs(mode))) for mode in modes)
        return complex(1 + first + 2 * second + 3 * final)

    result = external_state_amplitude_squared(
        amplitude,
        spaces,
        incoming_legs=(0, 1),
    )
    expected = sum(
        abs(1 + first + 2 * second + 3 * final) ** 2
        for first in range(2)
        for second in range(2)
        for final in range(2)
    ) / 4.0
    assert result.amplitude_squared == expected
    assert result.amplitude_evaluations == 8
    assert result.basis_dimensions == (2, 2, 2)


def test_coherent_density_matrix_preserves_interference() -> None:
    space = basis()
    plus = np.asarray([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    result = external_state_amplitude_squared(
        lambda modes: modes[0][0] + 1.0j * modes[0][1],
        (space,),
        incoming_legs=(0,),
        incoming_density_matrices={0: plus},
    )
    assert np.isclose(result.amplitude_squared, 1.0)
    assert result.coherent_density_matrices_used is True


def test_external_phase_and_outgoing_basis_sum_are_invariant() -> None:
    real = basis("real")
    phased = ExternalStateBasis(
        np.asarray([[1.0j, 0.0], [0.0, -1.0j]]),
        "phased",
    )
    amplitude = lambda modes: 2.0 * modes[0][0] - 3.0j * modes[0][1]
    first = external_state_amplitude_squared(amplitude, (real,), incoming_legs=())
    second = external_state_amplitude_squared(amplitude, (phased,), incoming_legs=())
    assert np.isclose(first.amplitude_squared, 13.0)
    assert np.isclose(second.amplitude_squared, first.amplitude_squared)


def test_invalid_density_or_nonorthonormal_basis_fails_closed() -> None:
    with pytest.raises(ValueError, match="orthonormal"):
        ExternalStateBasis(np.asarray([[1.0, 0.0], [1.0, 0.0]]), "bad")
    with pytest.raises(ValueError, match="positive semidefinite"):
        external_state_amplitude_squared(
            lambda _modes: 1.0,
            (basis(),),
            incoming_legs=(0,),
            incoming_density_matrices={0: np.diag([1.2, -0.2])},
        )
