from pathlib import Path

from bhsm.interface.theorem_closure.cp_o_int_coupling import build_coupling_factor

ROOT = Path(__file__).resolve().parents[1]


def test_coupling_symbol_is_source_traced_but_normalization_open():
    factor = build_coupling_factor(ROOT)
    assert factor.symbol == "G_raw"
    assert factor.status == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert factor.is_artifact_backed is True
    assert factor.operator_mass_dimension == "not derived"
    assert "No W anchor" in factor.claim_boundary
