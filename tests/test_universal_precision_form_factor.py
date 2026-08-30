import numpy as np
import pytest

from bhsm.interface.universal_precision_form_factor import (
    LeptonGMinus2Readout,
    MuonGMinus2Readout,
    lepton_gminus2_from_renormalized_vertex,
    muon_gminus2_from_renormalized_vertex,
    project_electromagnetic_form_factors,
)
from bhsm.interface.universal_loop_renormalization import RenormalizedVertex
from bhsm.interface.universal_lsz import LSZExternalMode


def test_form_factor_projection_recovers_synthetic_F1_F2() -> None:
    dirac = np.asarray([1.0, 0.0, 1.0j, 0.0])
    pauli = np.asarray([0.0, 2.0, 0.0, -1.0j])
    vertex = 1.0 * dirac + 0.00123 * pauli
    result = project_electromagnetic_form_factors(
        vertex, dirac, pauli, q_squared=0.0,
    )
    assert abs(result.F1 - 1.0) < 1.0e-14
    assert abs(result.F2 - 0.00123) < 1.0e-14
    assert result.relative_projection_residual < 1.0e-14


def test_muon_g_minus_two_promotion_is_fail_closed() -> None:
    dirac = np.asarray([1.0, 0.0])
    pauli = np.asarray([0.0, 1.0])
    factors = project_electromagnetic_form_factors(
        dirac + 0.002 * pauli, dirac, pauli, q_squared=0.0,
    )
    provisional = MuonGMinus2Readout(
        factors, "TEST-ACTION", "test-background", None,
        False, False, False,
    )
    with pytest.raises(RuntimeError, match="Gate7_closed_background"):
        provisional.anomalous_magnetic_moment()

    promoted = MuonGMinus2Readout(
        factors, "TEST-ACTION", "test-background", "test-renormalization",
        True, True, True,
    )
    assert promoted.anomalous_magnetic_moment() == pytest.approx(0.002)
    assert promoted.metadata()["experimental_target_used"] is False


def test_promoted_loop_vertex_and_lsz_chain_returns_f2_zero() -> None:
    vertex = RenormalizedVertex(
        finite_value=np.asarray([1.0, 0.25], dtype=complex),
        summed_laurent_coefficients={-1: np.zeros(2), 0: np.asarray([1.0, 0.25])},
        maximum_relative_pole_residual=0.0,
        maximum_relative_ward_residual=0.0,
        action_version="BHSM-TEST",
        background_id="background",
        scheme_id="same-action-scheme",
        diagram_ids=("complete-ledger",),
        sectors=("electromagnetic",),
        complete_diagram_ledger=True,
        complete_counterterm_ledger=True,
        gate7_closed=True,
    )
    mode = LSZExternalMode(
        spectral_parameter=1.0,
        right_mode=np.asarray([1.0]),
        left_mode=np.asarray([1.0]),
        descriptor_normalization_residual=0.0,
        pole_simple=True,
        action_selected=True,
        mode_id="action-muon-mode",
        provenance=("same-action pole",),
    )
    result = muon_gminus2_from_renormalized_vertex(
        vertex,
        np.asarray([1.0, 0.0]),
        np.asarray([0.0, 1.0]),
        mode,
        mode,
        q_squared=0.0,
        modes_identified_as_muon_by_action_spectrum=True,
    )
    assert result.anomalous_magnetic_moment() == 0.25
    assert result.metadata()["experimental_target_used"] is False


def test_generic_action_identified_lepton_readout_covers_non_muon_modes() -> None:
    vertex = RenormalizedVertex(
        finite_value=np.asarray([1.0, 0.125], dtype=complex),
        summed_laurent_coefficients={0: np.asarray([1.0, 0.125])},
        maximum_relative_pole_residual=0.0,
        maximum_relative_ward_residual=0.0,
        action_version="BHSM-TEST",
        background_id="background",
        scheme_id="same-action-scheme",
        diagram_ids=("complete-electron-ledger",),
        sectors=("electromagnetic",),
        complete_diagram_ledger=True,
        complete_counterterm_ledger=True,
        gate7_closed=True,
    )
    mode = LSZExternalMode(
        spectral_parameter=0.01,
        right_mode=np.asarray([1.0]),
        left_mode=np.asarray([1.0]),
        descriptor_normalization_residual=0.0,
        pole_simple=True,
        action_selected=True,
        mode_id="action-electron-mode",
        provenance=("same-action electron pole",),
    )
    result = lepton_gminus2_from_renormalized_vertex(
        vertex,
        np.asarray([1.0, 0.0]),
        np.asarray([0.0, 1.0]),
        mode,
        mode,
        q_squared=0.0,
        mode_identified_as_charged_lepton_by_action_spectrum=True,
    )
    assert isinstance(result, LeptonGMinus2Readout)
    assert result.mode_id == "action-electron-mode"
    assert result.anomalous_magnetic_moment() == 0.125
    assert result.metadata()["experimental_target_used"] is False


def test_generic_lepton_readout_rejects_external_particle_naming() -> None:
    factors = project_electromagnetic_form_factors(
        np.asarray([1.0, 0.0]),
        np.asarray([1.0, 0.0]),
        np.asarray([0.0, 1.0]),
        q_squared=0.0,
    )
    result = LeptonGMinus2Readout(
        factors,
        "unclassified-mode",
        "BHSM-TEST",
        "background",
        "scheme",
        True,
        True,
        True,
        False,
    )
    with pytest.raises(RuntimeError, match="action_identified_charged_lepton_mode"):
        result.anomalous_magnetic_moment()
