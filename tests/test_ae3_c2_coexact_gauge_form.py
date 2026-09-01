from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from bhsm.interface.ae3_c2_coexact_gauge_form import (
    coexact_gauge_puzzle_ledger,
    gauge_normalization_interface,
    lowest_coexact_gauge_form_shape,
)
from scripts.materialize_ae3_c2_coexact_gauge_form import TARGET, build_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/materialize_ae3_c2_coexact_gauge_form.py"


def test_lowest_coexact_gauge_shape_has_exact_curl_multiplicity() -> None:
    result = lowest_coexact_gauge_form_shape(
        log_radii=np.asarray((0.0, 0.1, 0.2, 0.3)),
        proper_durations=np.asarray((0.2, 0.3, 0.4)),
    )
    assert result["coexact_dimension"] == 3
    assert result["longitudinal_dimension"] == 0
    assert np.array_equal(result["curl_eigenvalues"], np.full(3, 2.0))
    assert result["component_pencil"]["generalized_gap_lower"] > 0.0
    assert result["BRST_longitudinal_sector_removed_by_coexact_projection"] is True


def test_three_gauge_components_are_identical_scalar_pencil_lifts() -> None:
    result = lowest_coexact_gauge_form_shape(
        log_radii=np.asarray((0.0, 0.1, 0.2)),
        proper_durations=np.asarray((0.2, 0.3)),
    )
    pencil = result["component_pencil"]
    expected = pencil["K_diagonal"][:, None, None] * np.eye(3)[None, :, :]
    assert np.array_equal(result["K_diagonal_blocks"], expected)


def test_normalization_interface_forbids_photon_overpromotion() -> None:
    interface = gauge_normalization_interface()
    assert interface["parent_Maxwell_action_owned"] is True
    assert interface["independent_gauge_normalization_allowed"] is False
    assert interface["historical_responses_define_one_Lorentzian_coefficient"] is False
    assert interface["current_C2_dynamic_frequency_response_available"] is False
    assert interface["form_shape_may_be_used_as_normalized_photon_propagator"] is False


def test_puzzle_ledger_advances_domain_but_not_observable() -> None:
    ledger = coexact_gauge_puzzle_ledger()
    assert ledger["coexact_gauge_form_shape_derived"] is True
    assert ledger["normalized_photon_propagator_derived"] is False
    assert ledger["muon_magnetic_moment_derived"] is False
    assert ledger["prediction_emitted"] is False


def test_actual_c2_gauge_form_artifact_is_fail_closed() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["CURRENT_C2_COEXACT_GAUGE_FORM_SHAPE_DERIVED"] is True
    assert payload["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"] is False
    assert payload["CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED"] is False
    assert payload["coexact_gauge_form"]["generalized_gap_lower"] > 0.0


def test_materialized_c2_gauge_form_is_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert first == second
    assert stored["validation_passed"] is True
