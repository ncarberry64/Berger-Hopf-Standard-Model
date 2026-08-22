import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_NORMAL_QUOTIENT_ISOMETRY.json"
)


def test_source_normal_reconstruction_is_an_action_graph_quotient_isometry():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    identities = payload["exact_Hilbert_space_identities"]
    assert identities["representative_norm"] == "norm(s_Y)=1"
    assert identities["normal_projection_norm"] == "norm(P_N)=1"
    consequence = payload["compact_operator_consequence"]
    assert consequence[
        "separate_reconstruction_multiplier_required_for_C_ED_G"
    ] is False
    inverse = payload["right_inverse_separation"]
    assert inverse["status"] == "QUANTITATIVE_BOUND_OPEN"
    assert inverse["count_K_once"] is True
    assert inverse[
        "trace_or_principal_subblock_gaps_alone_prove_beta_src"
    ] is False
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
