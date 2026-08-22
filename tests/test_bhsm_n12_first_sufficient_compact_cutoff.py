import json
from decimal import Decimal, localcontext
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FIRST_SUFFICIENT_COMPACT_CUTOFF.json"
)


def test_first_sufficient_compact_cutoff_closes_strict_gap():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    row = payload["directed_decimal_bounds"]
    threshold = Decimal(row["strict_threshold"])
    cutoff = int(row["M0_first_sufficient"])
    epsilon = Decimal(row["epsilon_obs_M0_upper"])
    core = Decimal(row["c_core_lower"])
    gap = Decimal(row["observation_gap_lower"])
    assert Decimal(cutoff - 1) <= threshold < Decimal(cutoff)
    assert Decimal(0) < epsilon < core
    with localcontext() as context:
        context.prec = 420
        assert gap == core - epsilon
    assert Decimal(row["K_normal_right_inverse_upper"]) > 0
    assert payload["M_star_certified"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
