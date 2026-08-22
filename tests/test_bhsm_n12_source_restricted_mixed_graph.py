import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_MIXED_GRAPH.json"
)


def test_source_restricted_mixed_graph_is_trace_compatible_and_fail_closed():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["spaces"]["energy_XE"] == (
        "H1_q_CROSS_L2_velocity_CROSS_H1_lapse_shift"
    )
    for side in payload["mixed_projector"]["finite_roundoff_diagnostics"].values():
        for row in side:
            assert row["complete_four_row_q_trace_tail_defect"] < 2.0e-9
            assert row["finite_diagnostic_is_the_analytic_tail_proof"] is False
    assert payload["epsilon_obs_M_evaluable"] is False
    assert payload["M_star_certified"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
