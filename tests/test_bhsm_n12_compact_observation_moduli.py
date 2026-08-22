import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_COMPACT_OBSERVATION_MODULI_AUDIT.json"
)


def test_compact_moduli_audit_fails_closed_in_one_norm() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    closed = payload["closed_same_norm_constants"]
    assert closed["complete_four_row_direct_trace_tail"] == 0.0
    assert closed[
        "common_analytic_Fortin_envelope_for_every_integer_M_ge_12"
    ] == "C_F(M)<=4/sqrt(M)"
    assert closed["source_restricted_weighted_pole_H2_inverse_upper"] > 0.0
    assert closed["full_rank_two_weighted_pole_H2_inverse_upper"] > 0.0
    assert closed[
        "source_restricted_full_mixed_graph_architecture_assembled"
    ] is True
    assert payload["epsilon_obs_M_evaluable"] is False
    assert payload["M_star_certified"] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
    blocks = payload["four_compact_blocks"]
    assert blocks["interior_lower_order_Euler_Dirac"][
        "same_norm_coefficient_enclosed"
    ] is True
    assert blocks["interior_lower_order_Euler_Dirac"]["C_ED_G_upper"] > 0.0
    assert blocks["ordered_event_projector"][
        "same_norm_coefficient_enclosed"
    ] is True
    assert blocks["ordered_event_projector"]["C_event_G_upper"] > 0.0
    assert blocks["canonical_momentum_dynamic_flux"][
        "same_norm_coefficient_enclosed"
    ] is True
    assert blocks["canonical_momentum_dynamic_flux"]["C_flux_G_upper"] > 0.0
    assert blocks["Gauss_consistency"][
        "same_norm_coefficient_enclosed"
    ] is True
    assert blocks["Gauss_consistency"]["C_GQ_upper"] > 0.0
    assert all(
        row["same_norm_coefficient_enclosed"] is True
        for row in blocks.values()
    )
    assert payload["conditional_cutoff_identity_not_a_certificate"][
        "C_compact_currently_available"
    ] is True
    assert payload["validation_passed"] is True
    assert payload["validation"][
        "full_rank_two_source_restricted_pole_inverse_is_closed"
    ] is True
