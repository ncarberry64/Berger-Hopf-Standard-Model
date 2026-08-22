import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_GAUSS_COMPACT_MODULUS.json"
)


def test_gauss_compact_modulus_uses_analytic_triangle_not_sample_fit():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["fourth_compact_block_closed"] is True
    bounds = payload["bounds"]
    assert math.isfinite(bounds["C_GQ_upper_by_triangle"])
    assert (
        bounds["C_GQ_upper_by_triangle"]
        == 2.0 * bounds["common_exact_or_Gauss_map_upper"]
    )
    assert payload["finite_core_consistency"]["role"].endswith(
        "NOT_THE_ANALYTIC_TAIL_BOUND"
    )
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
