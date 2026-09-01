import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_exact_affine_terminal_abscissa_is_the_physical_stop() -> None:
    fine = _load("BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.json")
    with np.load(BASE / "BHSM_N12_GATE7_ARB_INTERACTION_TAYLOR26_FINE_CENTER.npz") as source:
        times = np.asarray(source["fine_action_lengths"], dtype=float)
    assert fine["validation_passed"] is True
    assert times.shape == (371,)
    assert times[-3:].tolist() == [92.0, 92.25, 92.30513924040065]
    assert times[-1] < 92.5


def test_exact_affine_adaptive_response_cover_closes() -> None:
    response = _load(
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RHS_RESPONSE.json"
    )
    mesh = response["mesh"]
    histogram = {
        int(key): int(value)
        for key, value in mesh["adaptive_parent_refinement_histogram"].items()
    }
    assert response["validation_passed"] is True
    assert mesh["parent_cells"] == 3009
    assert mesh["cells"] == 16709
    assert mesh["adaptive_complete_uniform_prefix_parents"] == 953
    assert sum(histogram.values()) == 3009
    assert sum(refinement * parents for refinement, parents in histogram.items()) == 16709
    assert response["summary"][
        "maximum_relative_bordered_operator_perturbation_upper"
    ] < 1.0


def test_exact_affine_response_variations_use_identical_adaptive_cover() -> None:
    first = _load(
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_FIRST_VARIATION.json"
    )
    second = _load(
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_SECOND_VARIATION.json"
    )
    assert first["validation_passed"] is True
    assert second["validation_passed"] is True
    assert first["mesh"]["response_cells"] == 16709
    assert second["mesh"]["response_cells"] == 16709
    assert second["validation"][
        "identical_final_exact_adaptive_zero_first_second_response_cover_consumed"
    ] is True


def test_exact_affine_taylor_volterra_z2_fits_all_certified_tubes() -> None:
    causal = _load(
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_CAUSAL_VECTOR_CERTIFICATE.json"
    )
    z2 = _load("BHSM_N12_GATE7_EXACT_AFFINE_CENTER_INTERNAL_RESPONSE_Z2.json")
    assert causal["validation_passed"] is True
    assert z2["validation_passed"] is True
    assert len(z2["rows"]) == 48
    assert z2["summary"]["selected_cone_radius_utilization"] < 1.0
    assert z2["summary"]["maximum_local_proof_tube_utilization"] < 1.0
    assert z2["summary"]["budget_ratio"] < 1.0
    assert z2["summary"][
        "minimum_response_second_identity_denominator_lower"
    ] > 0.0
    assert z2["validation"]["historical_Gauss12_center_not_consumed"] is True
    assert z2["FULL_BHSM_COMPLETE"] is False
