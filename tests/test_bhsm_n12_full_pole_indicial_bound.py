import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FULL_POLE_INDICIAL_BOUND.json"
)


def test_full_rank_two_source_restricted_indicial_bound_closes():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload[
        "full_rank_two_source_restricted_indicial_solvability_closed"
    ] is True
    assert payload["source_restricted_weighted_proof"][
        "exact_H2_symbol_inverse_upper_before_c0"
    ] == str(Fraction(1684, 35))
    assert payload[
        "previous_scalar_Berger_bound_is_sufficient_for_full_rank_two_block"
    ] is False
    assert payload["C_ED_G_evaluable_after_desingularized_remainder_enclosure"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
