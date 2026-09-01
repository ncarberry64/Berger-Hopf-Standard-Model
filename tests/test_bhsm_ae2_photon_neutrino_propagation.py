from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from bhsm.interface.action_extension_ae2_neutrino_photon_propagation import (
    dimensionless_splitting_ratio,
    electroweak_null_channel,
    final_adjudication,
    neutral_seed_spectrum,
    oscillation_phase_scaling_gate,
    propagation_family_adjudication,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_bhsm_ae2_photon_neutrino_propagation.py"
TARGET = ROOT / "artifacts/flagship_integration"
OUTPUTS = (
    "BHSM_AE2_PHOTON_NEUTRINO_PROPAGATION_PROVENANCE.json",
    "BHSM_AE2_NEUTRAL_PROPAGATION_OPERATOR.json",
    "BHSM_AE2_NEUTRINO_PROPAGATION_STIFFNESS.json",
    "BHSM_AE2_NEUTRINO_OSCILLATION_PHASE_GATE.json",
    "BHSM_AE2_NEUTRINO_DIMENSIONLESS_SPLITTING_RATIO.json",
    "BHSM_AE2_PHOTON_NULL_CHANNEL_AUDIT.json",
    "BHSM_AE2_PMNS_ACTION_REDERIVATION_AUDIT.json",
    "BHSM_AE2_NEUTRINO_CP_HOLONOMY_AUDIT.json",
    "BHSM_AE2_NEUTRINO_GATE7_RECONVERGENCE.json",
)


def test_q_em_null_is_algebraic_but_physical_channel_remains_open() -> None:
    row = electroweak_null_channel(1.0, 0.6, 4.0)
    assert row["Q_em_null_residual"] < 1.0e-12
    assert row["rank"] == 3
    assert row["nullity"] == 1
    assert row["representation_null_direction_derived"] is True
    assert row["physical_photon_null_channel_derived"] is False


def test_raw_neutral_boundary_seed_is_not_positive() -> None:
    row = neutral_seed_spectrum(
        [[0.0, 1.0 / 3.0, 0.0], [1.0 / 3.0, 3.0, 1.0 / 6.0], [0.0, 1.0 / 6.0, 5.0 / 3.0]]
    )
    assert min(row["eigenvalues"]) < 0.0
    assert row["positive_semidefinite"] is False
    assert row["raw_seed_may_be_used_as_physical_mass_matrix"] is False


def test_phase_gate_requires_stiffness_and_owned_generators() -> None:
    open_row = oscillation_phase_scaling_gate(
        [1.0, 2.0, 4.0],
        translation_energy_generator_owned=False,
        physical_momentum_map_owned=True,
    )
    assert open_row["status"] == "OPEN"
    derived = oscillation_phase_scaling_gate(
        [1.0, 2.0, 4.0],
        translation_energy_generator_owned=True,
        physical_momentum_map_owned=True,
    )
    assert derived["status"] == "DERIVED"


def test_splitting_ratio_is_not_assigned_to_degenerate_or_absent_block() -> None:
    assert dimensionless_splitting_ratio(None)["status"] == "OPEN"
    degenerate = dimensionless_splitting_ratio([0.0, 0.0, 0.0])
    assert degenerate["ratio"] is None
    assert degenerate["reason"] == "THREEFOLD_DEGENERACY_MAKES_RATIO_UNDEFINED"
    assert dimensionless_splitting_ratio([1.0, 2.0, 5.0])["ratio"] == pytest.approx(0.25)


def test_common_family_and_final_adjudication_are_claim_safe() -> None:
    assert propagation_family_adjudication()["status"] == "PARTIAL"
    final = final_adjudication()
    assert final["PHYSICAL PHOTON NULL CHANNEL"] == "OPEN"
    assert final["ACTION-OWNED NEUTRAL THREE-SLOT PROPAGATION OPERATOR"] == "OPEN"
    assert final["PI/3 CP HOLONOMY ATTACHMENT"] == "FLAVOR-SEED-ONLY"
    assert final["GATE-7 RECONVERGENCE"] == "PARTIAL_SHARED_GEOMETRY"
    assert final["FROZEN PREDICTIONS CHANGED"] is False
    assert final["FULL_BHSM_COMPLETE"] is False


def test_invalid_inputs_fail() -> None:
    with pytest.raises(ValueError):
        electroweak_null_channel(0.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        neutral_seed_spectrum([[0.0, 1.0], [0.0, 0.0]])
    with pytest.raises(ValueError):
        dimensionless_splitting_ratio([1.0, 2.0])


def test_nine_artifacts_are_validated_and_deterministic() -> None:
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    first = {
        name: hashlib.sha256((TARGET / name).read_bytes()).hexdigest()
        for name in OUTPUTS
    }
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    second = {
        name: hashlib.sha256((TARGET / name).read_bytes()).hexdigest()
        for name in OUTPUTS
    }
    assert first == second
    payloads = {
        name: json.loads((TARGET / name).read_text(encoding="utf-8"))
        for name in OUTPUTS
    }
    assert all(payload["validation_passed"] is True for payload in payloads.values())
    final = payloads["BHSM_AE2_NEUTRINO_GATE7_RECONVERGENCE.json"]["final_adjudication"]
    assert final["1/E OSCILLATION PHASE LAW"] == "OPEN"
    assert final["DIMENSIONLESS DELTA-M-SQUARED RATIO"] == "OPEN"
    assert final["ABSOLUTE NEUTRINO MASS SCALE"] == "OPEN"
    reconvergence = payloads["BHSM_AE2_NEUTRINO_GATE7_RECONVERGENCE.json"]
    assert reconvergence["Gate7_current_owner"] == "G7_08_FORCE"
    assert "physical force net" in reconvergence["Gate7_current_owner_detail"]
    assert reconvergence["superseded_current_owner"] == "G7_07_ANGULAR_TAIL"
    assert reconvergence["completion_DAG_dependency_changed_by_this_sprint"] is False
    assert reconvergence["validation"]["current_completion_DAG_consumed"] is True
    assert (
        "artifacts/current_semantics/BHSM_CURRENT_COMPLETION_DAG.json"
        in reconvergence["inputs"]
    )
