from __future__ import annotations

import numpy as np
import pytest

from bhsm.interface.completion.collective_dirac_vacuum_polarization_v14_42 import (
    ARTIFACT_FILES,
    EXACT_NEXT_OBJECT,
    collective_dirac_action_ownership_payload,
    compact_dirac_domain_payload,
    completion_payload,
    commutator_norm,
    filled_sea_transition_susceptibility,
    kosmann_vertex_payload,
    massive_round_s3_energy,
    materialize,
    normalized_shift_eigenvalue,
    polarization_sign_and_renormalization_payload,
    round_s3_dirac_eigenvalue,
    round_s3_dirac_multiplicity,
    total_renormalized_channel_coefficient,
)


def test_round_s3_dirac_spectrum() -> None:
    assert round_s3_dirac_eigenvalue(0, +1) == 1.5
    assert round_s3_dirac_eigenvalue(0, -1) == -1.5
    assert round_s3_dirac_eigenvalue(2, +1, radius=2.0) == 1.75
    assert round_s3_dirac_multiplicity(0) == 2
    assert round_s3_dirac_multiplicity(2) == 12
    assert massive_round_s3_energy(0, mass=2.0) == pytest.approx(2.5)


def test_invalid_spectrum_inputs_fail_closed() -> None:
    with pytest.raises(ValueError):
        round_s3_dirac_eigenvalue(-1)
    with pytest.raises(ValueError):
        round_s3_dirac_eigenvalue(0, sign=0)
    with pytest.raises(ValueError):
        round_s3_dirac_eigenvalue(0, radius=0.0)
    with pytest.raises(ValueError):
        massive_round_s3_energy(0, mass=-1.0)


def test_filled_sea_susceptibility_is_nonpositive() -> None:
    h = np.diag([-2.0, -1.0, 1.0, 3.0])
    v = np.array(
        [
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.3, 0.5],
            [1.0, 0.3, 0.0, 0.0],
            [0.0, 0.5, 0.0, 0.0],
        ]
    )
    assert filled_sea_transition_susceptibility(h, v) < 0.0


def test_commuting_vertex_has_zero_transition_susceptibility() -> None:
    h = np.diag([-3.0, -1.0, 2.0, 4.0])
    v = np.diag([0.1, 0.2, 0.3, 0.4])
    assert commutator_norm(h, v) == 0.0
    assert filled_sea_transition_susceptibility(h, v) == 0.0


def test_gap_and_shape_checks_fail_closed() -> None:
    with pytest.raises(ValueError):
        filled_sea_transition_susceptibility(np.diag([-1.0, 0.0, 1.0]), np.eye(3))
    with pytest.raises(ValueError):
        filled_sea_transition_susceptibility(np.eye(2), np.eye(3))


def test_renormalized_channel_contract_includes_four_derivative_term() -> None:
    assert normalized_shift_eigenvalue(2) == 5
    assert normalized_shift_eigenvalue(3) == 12
    assert total_renormalized_channel_coefficient(
        2, c2=1.0, c4=0.1, nonlocal_polarization=-7.5
    ) == pytest.approx(0.0)
    assert total_renormalized_channel_coefficient(
        3, c2=1.0, c4=0.0, nonlocal_polarization=-12.0
    ) == pytest.approx(0.0)


def test_action_ownership_remains_open() -> None:
    payload = collective_dirac_action_ownership_payload()
    assert payload["validation_passed"]
    assert payload["ownership_status"]["local_collective_Dirac_principal_symbol"] == "OPEN_NOT_DERIVED_FROM_MODULI_ACTION"
    assert "not an additional independent ultraviolet" in payload["no_double_counting"]


def test_domain_and_vertex_are_conditional_not_promoted() -> None:
    domain = compact_dirac_domain_payload()
    vertex = kosmann_vertex_payload()
    assert domain["validation_passed"]
    assert vertex["validation_passed"]
    assert domain["operator_contract"]["domain"] == "H1(S3,E_total)"
    assert vertex["relative_core_wall_vertex"]["status"] == "OPEN"


def test_polarization_payload_records_sign_and_renormalization_boundary() -> None:
    payload = polarization_sign_and_renormalization_payload()
    assert payload["validation_passed"]
    assert payload["requested_channels"]["L2"]["status"] == "OPEN"
    assert payload["requested_channels"]["L3"]["status"] == "OPEN"
    assert "q_L^2" in payload["renormalization_audit"]["dimensionless_channel_normal_form"]


def test_completion_gate_fails_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["BHSM_complete"] is False
    assert payload["Dirac_action_gate"] == "OPEN_NOT_DERIVED_FROM_FR_MODULI_DYNAMICS"
    assert payload["renormalized_L2_crossing_gate"] == "OPEN_NOT_NUMERICALLY_DEFINED"
    assert payload["renormalized_L3_crossing_gate"] == "OPEN_NOT_NUMERICALLY_DEFINED"
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_materialization_is_deterministic(tmp_path) -> None:
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
