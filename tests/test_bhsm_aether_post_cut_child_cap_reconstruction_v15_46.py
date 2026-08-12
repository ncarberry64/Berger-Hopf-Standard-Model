import json
import math
from pathlib import Path

import numpy as np

from bhsm.interface import aether_post_cut_child_cap_reconstruction_v15_46 as child


ROOT = Path(__file__).resolve().parents[1]


def test_event_data_define_the_negative_response_cap_without_metric_transport():
    contract = child.post_cut_variational_contract()
    assert contract["domain"].startswith("C_child=B4_times_S3")
    assert "sigma(L)=0" in contract["transported_boundary_data"]
    assert contract["metric_firewall_respected"] is True
    assert contract["pre_firewall_metric_used_as_boundary_data"] is False
    assert contract["new_continuous_coefficient"] is False


def test_response_endpoints_and_regular_cap_chart_are_exact():
    fields = child.child_cap_fields(child._round_cap_seed(), points=160)
    assert np.min(np.asarray(fields["A"])) > 0.0
    assert np.min(np.asarray(fields["B"])) > 0.0
    assert np.min(np.asarray(fields["f_prime"])) > 0.0
    assert np.min(np.asarray(fields["eta_legendre"])) > 0.0
    assert np.min(np.asarray(fields["sigma"])) > -0.500001
    assert np.max(np.asarray(fields["sigma"])) < 0.0001


def test_minimum_norm_cmc_tt_reconstruction_closes_constraints():
    result = child.solve_minimal_round_cap_cmc_tt_reconstruction(points=500)
    assert result["radius"] == pytest_approx((343.0 / 5.0) ** (1.0 / 6.0), 2e-12)
    assert result["trace_rate"] < 0.0
    assert result["FR_charge"] == pytest_approx(0.5, 2e-12)
    assert abs(result["minimum_TT_radicand"]) < 3e-10
    assert result["maximum_Hamiltonian_residual"] < 3e-10
    assert result["minimum_eta_Legendre"] > 0.0
    assert result["pre_firewall_metric_imported"] is False


def pytest_approx(value: float, relative: float):
    import pytest

    return pytest.approx(value, rel=relative)


def test_completion_payload_and_materialized_artifact_are_deterministic(tmp_path):
    payload = child.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["post_cut_metric_child_reconstructed"] is True
    assert payload["claim_boundary"]["persistent_particle_derived"] is False
    path = child.materialize(tmp_path)
    assert json.loads(path.read_text(encoding="utf-8"))["validation_passed"] is True
    assert path.read_text(encoding="utf-8") == child.deterministic_json(payload)
    assert child.deterministic_json(payload) == child.deterministic_json(
        child.completion_payload()
    )


def test_repository_artifact_matches_current_payload():
    path = ROOT / "artifacts" / "BHSM_aether_post_cut_child_cap_reconstruction_v15_46.json"
    if path.exists():
        assert path.read_text(encoding="utf-8") == child.deterministic_json(
            child.completion_payload()
        )

