from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "artifacts/n12_continuum_majorant_effectiveness"
    / "BHSM_N12_SOURCE_RESTRICTED_INDICIAL_BOUND.json"
)


def test_source_restricted_indicial_bound_closes_only_the_missing_pole_lemma() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["source_restricted_indicial_solvability_closed"] is True
    assert payload["unrestricted_static_Weyl_sequence_invalidated"] is False
    assert payload["category_3_positive_duration_collapse_sequence_constructed"] is False
    assert payload["M_star_certified"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    proof = payload["weighted_symbol_proof"]
    assert proof["minimum_symbol_modulus"] == 1.0
    assert math.isclose(
        proof["H2_graph_multiplier_maximum"], math.sqrt(65.0) / 4.0
    )
    sectors = payload["root_ball_coefficient_enclosure"]["sectors"]
    assert all(row["root_ball_c_lower"] > 0.0 for row in sectors.values())
    assert payload["joint_source_restricted_weighted_H2_inverse_upper"] < 0.005
