from __future__ import annotations

import json
from pathlib import Path

import pytest

from bhsm.interface.action_extension_ae2_nonfermion_threshold import (
    seam_wronskian_lower,
    transverse_gauge_wentzell_lower,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"
)


def test_ae2_nonfermion_threshold_margin() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    margins = payload["certified_margins"]
    assert payload["validation_passed"] is True
    assert payload["action_version"] == "BHSM-AE-2.0.0"
    assert payload["claim_boundary"]["nonfermion_critical_zero_graph_excluded"] is True
    assert payload["claim_boundary"]["factorized_product_Dirac_two_sided_margin"] == "OPEN"
    assert margins["positive_scalar_derham_child_and_seam_lower"] > 0.0
    assert margins["transverse_gauge_total_seam_lower"] > 650.0
    assert margins["constant_scalar_log_radius_first_vertex_zero"] is True
    assert margins["global_gauge_zero_mode_quotiented"] is True


def test_threshold_helpers_preserve_quadratic_form_order() -> None:
    assert seam_wronskian_lower(0.0, 2.0, 3.0) == pytest.approx(5.0)
    assert transverse_gauge_wentzell_lower(10.0, 1.0, 4.0, 2.0) == pytest.approx(10.0)
    with pytest.raises(ValueError):
        seam_wronskian_lower(-1.0, 2.0)
