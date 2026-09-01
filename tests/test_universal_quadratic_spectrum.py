import numpy as np
import pytest

from bhsm.interface.universal_quadratic_spectrum import QuadraticDescriptorPencil


def pencil(*, promoted: bool = False) -> QuadraticDescriptorPencil:
    return QuadraticDescriptorPencil(
        constant=np.diag([4.0, 9.0, 16.0]),
        linear=-np.diag([1.0, 2.0, 4.0]),
        action_version="TEST-ACTION",
        background_id="test-background",
        domain_id="test-physical-domain",
        gate7_closed=promoted,
        quotient_applied=True,
        brst_cancellation_accounted=promoted,
        scale_map_id="test-scale" if promoted else None,
    )


def test_generalized_poles_and_residues_are_inverse_free_and_normalized() -> None:
    result = pencil().poles_and_residues()
    values = sorted(round(item.spectral_parameter.real, 12) for item in result)
    assert values == [4.0, 4.0, 4.5]
    assert sum(item.simple for item in result) == 1
    for item in result:
        assert item.finite is True
        assert np.allclose(
            pencil().symbol(item.spectral_parameter) @ item.right_mode,
            0.0,
            atol=1.0e-12,
        )
        assert np.allclose(
            item.left_mode.conj().T @ pencil().linear @ item.residue,
            item.left_mode.conj().T,
            atol=1.0e-12,
        )


def test_physical_promotion_requires_background_brst_and_scale() -> None:
    provisional = pencil(promoted=False)
    assert provisional.metadata()["physical_promotion_ready"] is False
    with pytest.raises(RuntimeError, match="Gate7_closed_background"):
        provisional.require_physical_promotion()
    promoted = pencil(promoted=True)
    promoted.require_physical_promotion()
    assert promoted.metadata()["physical_promotion_ready"] is True
