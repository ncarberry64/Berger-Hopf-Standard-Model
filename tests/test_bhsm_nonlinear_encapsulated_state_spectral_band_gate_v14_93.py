import json
import math

import numpy as np
import pytest

from bhsm.interface.completion.nonlinear_encapsulated_state_spectral_band_gate_v14_93 import (
    EXACT_NEXT_OBJECT,
    PATH_A_STATUS,
    action_block_ledger,
    completion_payload,
    conformal_energy,
    conformal_profile,
    conserved_charge_ledger,
    materialize,
    radial_hessian_eigenvalue,
    radial_stability_theorem,
    seed_data,
    state_band_bundle_status,
    virial_ledger,
)


def test_action_ledger_contains_only_retained_state_bearing_blocks() -> None:
    rows = {row["block"]: row for row in action_block_ledger()}
    assert rows["Lorentzian_M8_P1_gravity"]["action_owned"] is True
    assert rows["eta_p2_plus_p8_unit_map"]["retained_in_Path_A"] is True
    assert rows["intrinsic_M4_gauge_Dirac_Higgs"]["retained_in_Path_A"] is False


def test_degree_one_seed_is_exact_but_not_encapsulated_or_selected() -> None:
    seed = seed_data()
    assert seed["degree"] == 1
    assert seed["X_eta"] ** 3 == pytest.approx(5.0)
    assert seed["action_selected"] is False
    assert seed["encapsulated_state"] is False


def test_flat_and_compact_virials_are_not_conflated() -> None:
    ledger = virial_ledger()
    assert ledger["flat_eta_required_ratio"] == 5.0
    assert ledger["v14_91_identity_seed_eta_ratio"] == 1.25
    assert ledger["flat_identity_is_not_compact_virial_test"] is True
    assert ledger["stationary_localization_verdict"] == "NOT_FORBIDDEN_BY_DERRICK_SCREEN"


def test_conformal_family_preserves_endpoints_and_reversal_energy() -> None:
    assert conformal_profile(0.0, 0.7) == pytest.approx(0.0)
    assert conformal_profile(math.pi, 0.7) == pytest.approx(math.pi)
    grid = np.linspace(0.0, math.pi, 20)
    assert np.all(np.diff(conformal_profile(grid, 0.4)) > 0.0)
    assert conformal_energy(0.3) == pytest.approx(conformal_energy(-0.3), abs=2.0e-12)


def test_radial_sturm_liouville_spectrum_has_unique_zero_mode() -> None:
    values = [radial_hessian_eigenvalue(n) for n in range(7)]
    assert values == [0, 9, 20, 33, 48, 65, 84]
    with pytest.raises(ValueError):
        radial_hessian_eigenvalue(-1)


def test_exact_quartic_conformal_lift_is_positive() -> None:
    theorem = radial_stability_theorem()
    x0 = seed_data()["X_eta"]
    assert theorem["conformal_D2_E"] == 0.0
    assert theorem["conformal_D3_E"] == 0.0
    assert theorem["conformal_D4_E"] == pytest.approx(27.0 * math.pi * x0**4 / 128.0)
    assert conformal_energy(0.25) > conformal_energy(0.0)
    assert theorem["global_nonexistence_proved"] is False


def test_degree_is_only_available_localization_protection() -> None:
    rows = {row["charge"]: row for row in conserved_charge_ledger()}
    assert rows["degree_eta_in_pi7_S7"]["status"].startswith("EXACT_INTEGER_ONE")
    assert rows["arbitrary_wave_action"]["status"] is None


def test_no_state_means_band_projector_and_bundle_are_undefined() -> None:
    status = state_band_bundle_status()
    assert status["nonlinear_bound_state_branch"] is None
    assert status["physical_linearized_operator_about_Phi_enc"] is None
    assert status["projector"] is None
    assert status["projector_rank"] is None
    assert status["E_enc"] is None
    assert status["EMERGENT_COLOR_ELIGIBILITY"] is False
    assert status["DIRAC_EMERGENCE_ELIGIBILITY"] is False


def test_terminal_path_a_verdict_is_not_fabricated() -> None:
    payload = completion_payload()
    assert PATH_A_STATUS.startswith("OPEN_NO_A_TO_E")
    assert payload["Path_B_fallback_status"] == "NOT_ACTIVATED_NO_OUTCOME_E_PROVED"
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["completion_status"]["FULL_BHSM_COMPLETE"] is False
    assert payload["completion_status"]["USB_SYNCHRONIZATION_ELIGIBLE"] is False
    assert payload["validation_passed"] is True


def test_materializer_is_deterministic_and_strict_json(tmp_path) -> None:
    target = tmp_path / "v14_93.json"
    first = materialize(target).read_bytes()
    second = materialize(target).read_bytes()
    assert first == second
    assert json.loads(first) == completion_payload()
