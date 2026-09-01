import hashlib

import numpy as np
import pytest

from bhsm.interface.ae31_c2_color_singlet_residual_response_bridge import (
    baryon_probe_operators,
    baryon_response,
    baryon_singlet_state,
    claim_boundary,
    enclosure_response_contract,
    meson_probe_operators,
    meson_response,
    meson_singlet_state,
    schur_polarizability,
)
from scripts.materialize_ae31_c2_color_singlet_residual_response_bridge import (
    TARGET,
    build_payload,
    main,
)


def test_uniform_color_probe_has_no_singlet_charge_or_transition():
    meson = meson_response((1.0, 1.0))
    baryon = baryon_response((2.0, 2.0, 2.0))
    assert meson["linear_color_charge_zero"]
    assert baryon["linear_color_charge_zero"]
    assert meson["uniform_long_wavelength_probe_annihilates_singlet"]
    assert baryon["uniform_long_wavelength_probe_annihilates_singlet"]


def test_exact_finite_size_mesonic_and_baryonic_numerators():
    meson = meson_response((2.0, -0.5))
    baryon = baryon_response((2.0, -0.5, 0.7))
    assert meson["linear_color_charge_zero"]
    assert baryon["linear_color_charge_zero"]
    assert meson["formula_residual"] < 1.0e-12
    assert baryon["formula_residual"] < 1.0e-12
    assert meson["transition_channel_nonzero"]
    assert baryon["transition_channel_nonzero"]


def test_schur_polarizability_is_nonzero_and_negative_semidefinite():
    for state, probes in (
        (meson_singlet_state(), meson_probe_operators((1.0, 0.0))),
        (baryon_singlet_state(), baryon_probe_operators((1.0, 0.0, 0.0))),
    ):
        projector = np.outer(state, state.conj())
        result = schur_polarizability(state, probes, (np.eye(state.size) - projector) / 3.0)
        assert result["negative_semidefinite"]
        assert result["nonzero"]
        with pytest.raises(ValueError):
            schur_polarizability(state, probes, -np.eye(state.size))


def test_claim_boundary_keeps_dynamics_and_hadron_spectrum_open():
    contract = enclosure_response_contract()
    boundary = claim_boundary()
    assert not contract["wilson_source_is_action_term"]
    assert not contract["returned_hadron_resolvent_derived"]
    assert boundary["CURRENT_C2_COLOR_SINGLET_LINEAR_EXTERIOR_CHARGE_ZERO_DERIVED"]
    assert boundary["CURRENT_C2_COLOR_SINGLET_SCHUR_POLARIZABILITY_SIGN_DERIVED"]
    assert not boundary["CURRENT_C2_NONZERO_PHYSICAL_RESIDUAL_NUCLEAR_FORCE_DERIVED"]
    assert not boundary["CURRENT_C2_GLOBAL_ASYMPTOTIC_CONFINEMENT_THEOREM_DERIVED"]
    assert not boundary["CURRENT_C2_HADRON_MASS_DERIVED"]


def test_artifact_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
