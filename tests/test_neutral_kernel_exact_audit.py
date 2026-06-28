from __future__ import annotations

import pytest

from bhsm.interface.neutrino_spectral import audit_neutral_kernel_exact


def test_exact_kernel_audit_preserves_rationals_and_raw_indefiniteness() -> None:
    result = audit_neutral_kernel_exact()
    assert result.kernel_matrix_exact == (
        ("0", "1/3", "0"),
        ("1/3", "3", "1/6"),
        ("0", "1/6", "5/3"),
    )
    assert "lambda^3" in result.characteristic_polynomial
    assert result.raw_eigenvalues_numeric[0] == pytest.approx(-0.0367859219792249)
    assert result.raw_psd is False
    assert result.negative_eigendirection is not None
    assert any(value < 0 for value in result.negative_eigendirection)
    assert any(value > 0 for value in result.negative_eigendirection)

