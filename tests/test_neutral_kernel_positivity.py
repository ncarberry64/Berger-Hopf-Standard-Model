from __future__ import annotations

from bhsm.interface.neutrino_spectral import audit_neutral_kernel_positivity


def test_raw_and_admissible_neutral_positivity_are_separate() -> None:
    result = audit_neutral_kernel_positivity()
    assert len(result.raw_eigenvalues) == 3
    assert min(result.raw_eigenvalues) < 0.0
    assert result.status == "RAW_KERNEL_NOT_POSITIVE_SEMIDEFINITE"
    assert result.raw_positive_semidefinite is False
    assert result.projected_response_nonnegative_by_definition is True
    assert result.admissible_positive_response_proven is False
    assert "proof" in result.remaining_missing_object

