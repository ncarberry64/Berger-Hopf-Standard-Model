from __future__ import annotations

from bhsm.interface.neutrino_spectral import build_projected_neutral_kernel


def test_cone_restriction_is_not_mislabeled_as_linear_projection() -> None:
    result = build_projected_neutral_kernel()
    assert result.admissible_domain_defined is True
    assert result.projection_matrix is None
    assert result.projected_kernel is None
    assert result.projected_eigenvalues == ()
    assert result.projected_psd is None
    assert result.restriction_kind == "nonnegative_response_cone_not_linear_projection"
    assert result.raw_psd is False

