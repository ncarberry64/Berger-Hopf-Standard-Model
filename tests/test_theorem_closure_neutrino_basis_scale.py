from pathlib import Path

from bhsm.interface.theorem_closure.neutrino_basis_scale import evaluate_neutrino_basis_scale_candidate

ROOT = Path(__file__).resolve().parents[1]


def test_neutrino_attempt_preserves_boundary_seed_boundary():
    result = evaluate_neutrino_basis_scale_candidate(repository=ROOT)
    assert result.closure_status == "OPEN_EXACT_MISSING_THEOREM"
    assert result.promotion_allowed is False
    assert result.callable_available is False
    assert "basis map U_nu" in result.missing_objects[0]
    assert "dimensional scale Lambda_nu" in result.missing_objects[0]
    assert "Dirac/Majorana" in result.missing_objects[0]
    assert result.reference_values_used_as_derivation_inputs is False
    assert "physical neutrino mass matrix" in result.claim_boundary
