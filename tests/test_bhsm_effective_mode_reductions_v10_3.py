import pytest
import sympy as sp

from bhsm.interface.envelopment import effective_mode_reductions_v10_3 as reductions


def test_exact_schur_complement_identity():
    a, b, d = sp.symbols("a b d", nonzero=True)
    matrix = sp.Matrix([[a, b], [b, d]])
    assert reductions.schur_complement(matrix, (0,)) == sp.Matrix([[a - b**2 / d]])


def test_singular_schur_block_fails_closed():
    with pytest.raises(ValueError):
        reductions.schur_complement(sp.Matrix([[1, 0], [0, 0]]), (0,))


def test_historical_operators_are_recovered_but_common_reduction_is_unresolved():
    payload = reductions.effective_reduction_payload()
    assert payload["historical_operator_recovery_without_duplicate_derivation"] is True
    assert payload["Schur_complement_equivalence"] == "EQUIVALENCE_UNRESOLVED"
    assert payload["H_eff_psi"] is payload["H_eff_zeta"] is payload["H_eff_F"] is None
    assert payload["physically_inequivalent"] is False
