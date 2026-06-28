from __future__ import annotations

from bhsm.interface.charged_closure import audit_charged_closure_dimensions


def test_charged_dimensions_pass_without_physical_normalization_claim() -> None:
    result = audit_charged_closure_dimensions()
    assert result.status == "DIMENSIONAL_AUDIT_PASSED"
    assert not result.inconsistent_formulas
    assert result.coefficient_dimensions["rho_ch"] == "dimensionless ratio k_j/k_q"
    assert result.coefficient_dimensions["physical_charged_stiffness"] == "not available"
    assert result.physical_stiffness_claim_allowed is False
    assert result.physical_mass_claim_allowed is False
    assert result.empirical_inputs_used is False
