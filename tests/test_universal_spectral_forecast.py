from bhsm.interface.universal_spectral_forecast import (
    CertifiedInterval,
    DecayChannelInterval,
    SpectralMode,
    classify_mode_stability,
    decay_channel_status,
    spectral_exclusion,
)


def mode(mode_id: str, mass: tuple[float, float]) -> SpectralMode:
    return SpectralMode(
        mode_id=mode_id,
        mass=CertifiedInterval(*mass),
        spin_twice=1,
        electric_charge=CertifiedInterval(0.0, 0.0),
        color_representation="singlet",
        weak_representation="singlet",
        action_version="TEST-ACTION",
        domain_id="test-domain",
        provenance=("unit-test",),
    )


def test_open_nonzero_decay_channel_certifies_instability() -> None:
    modes = [mode("P", (10.0, 10.1)), mode("a", (2.0, 2.1)), mode("b", (3.0, 3.1))]
    channel = DecayChannelInterval(
        "P", ("a", "b"), CertifiedInterval(0.4, 0.5), ("S3",),
    )
    assert decay_channel_status(channel, {item.mode_id: item for item in modes}) == "OPEN_NONZERO"
    result = classify_mode_stability("P", modes, [channel], complete_channel_ledger=True)
    assert result["verdict"] == "CERTIFIED_UNSTABLE_HAS_OPEN_NONZERO_CHANNEL"


def test_complete_closed_or_exact_zero_ledger_certifies_stability() -> None:
    modes = [mode("P", (4.0, 4.1)), mode("a", (3.0, 3.1)), mode("b", (2.0, 2.1))]
    closed = DecayChannelInterval(
        "P", ("a", "b"), CertifiedInterval(1.0, 1.1), ("S3",),
    )
    zero = DecayChannelInterval(
        "P", ("a",), CertifiedInterval(0.0, 0.0), ("selection-rule",),
    )
    result = classify_mode_stability("P", modes, [closed, zero], complete_channel_ledger=True)
    assert result["verdict"] == "CERTIFIED_STABLE_ON_COMPLETE_CHANNEL_LEDGER"


def test_spectral_null_forecast_uses_only_declared_intervals() -> None:
    modes = [mode("X", (1.0, 1.1)), mode("Y", (5.0, 5.2))]
    result = spectral_exclusion(modes, CertifiedInterval(2.0, 4.0))
    assert result["spectrum_excluded_on_declared_domain"] is True
    assert result["experimental_search_result_used"] is False
