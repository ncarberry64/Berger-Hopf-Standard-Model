import pytest

from bhsm.interface.universal_channel_ledger import (
    ChannelAmplitudeCertificate,
    ChannelMode,
    InitialChannelState,
    build_complete_channel_ledger,
)
from bhsm.interface.universal_spectral_forecast import CertifiedInterval


def mode(mode_id: str, mass: tuple[float, float], charge: int) -> ChannelMode:
    return ChannelMode(
        mode_id,
        CertifiedInterval(*mass),
        (charge,),
        0,
        "BHSM-TEST-ACTION",
        "BHSM-TEST-BACKGROUND",
        ("action-derived test spectrum",),
    )


def certificate(
    state_id: str,
    daughters: tuple[str, ...],
    amplitude: tuple[float, float],
) -> ChannelAmplitudeCertificate:
    return ChannelAmplitudeCertificate(
        state_id,
        daughters,
        CertifiedInterval(*amplitude),
        ("same-action amplitude enclosure",),
    )


def test_complete_decay_inventory_certifies_unstable_parent() -> None:
    modes = (
        mode("H", (10.0, 10.0), 0),
        mode("a", (3.0, 3.0), 1),
        mode("b", (3.0, 3.0), -1),
        mode("c", (6.0, 6.0), 0),
    )
    ledger = build_complete_channel_ledger(
        "decay-ledger",
        modes,
        (InitialChannelState(
            "H-decay", "DECAY", ("H",), modes[0].mass,
            ("parent mass from same spectrum",),
        ),),
        (
            certificate("H-decay", ("a", "b"), (2.0, 2.1)),
            certificate("H-decay", ("c", "c"), (0.0, 0.0)),
        ),
        maximum_final_multiplicity=2,
        allowed_final_mode_ids=("a", "b", "c"),
        spectrum_complete=True,
        selection_rules_complete=True,
        provenance=("complete declared decay inventory",),
    )
    assert ledger.complete is True
    ledger.require_complete()
    entries = {entry.final_mode_ids: entry for entry in ledger.entries}
    assert set(entries) == {("a", "b"), ("c", "c")}
    assert entries[("c", "c")].identical_final_state_factor == 2
    report = ledger.initial_state_report("H-decay")
    assert report["verdict"] == "CERTIFIED_UNSTABLE_HAS_OPEN_NONZERO_CHANNEL"
    assert report["open_nonzero_channel_ids"] == ["H-decay->a+b"]


def test_missing_amplitude_or_threshold_separation_fails_closed() -> None:
    parent = mode("P", (5.9, 6.1), 0)
    daughters = (mode("x", (3.0, 3.0), 1), mode("y", (3.0, 3.0), -1))
    ledger = build_complete_channel_ledger(
        "unresolved",
        (parent, *daughters),
        (InitialChannelState(
            "P-decay", "DECAY", ("P",), parent.mass, ("same spectrum",),
        ),),
        (),
        maximum_final_multiplicity=2,
        allowed_final_mode_ids=("x", "y"),
        spectrum_complete=True,
        selection_rules_complete=True,
        provenance=("test",),
    )
    assert ledger.complete is False
    assert ledger.entries[0].kinematic_status == "UNRESOLVED"
    assert ledger.entries[0].amplitude_status == "UNRESOLVED"
    assert ledger.initial_state_report("P-decay")["verdict"] == "STABILITY_UNRESOLVED"
    with pytest.raises(RuntimeError, match="physical_channel_status_unresolved"):
        ledger.require_complete()


def test_scattering_ledger_uses_modular_charge_and_complete_open_channels() -> None:
    modes = (
        mode("i", (1.0, 1.0), 1),
        mode("x", (2.0, 2.0), 1),
        mode("z", (3.0, 3.0), 0),
    )
    initial = InitialChannelState(
        "ii-scattering",
        "SCATTERING",
        ("i", "i"),
        CertifiedInterval(10.0, 10.0),
        ("same-action center-of-mass energy",),
    )
    ledger = build_complete_channel_ledger(
        "scattering-ledger",
        modes,
        (initial,),
        (
            certificate("ii-scattering", ("x", "x"), (1.0, 1.0)),
            certificate("ii-scattering", ("z", "z"), (0.0, 0.0)),
        ),
        maximum_final_multiplicity=2,
        quantum_number_moduli=(2,),
        allowed_final_mode_ids=("x", "z"),
        spectrum_complete=True,
        selection_rules_complete=True,
        provenance=("complete two-body scattering inventory",),
    )
    assert ledger.complete is True
    assert ledger.initial_state_report("ii-scattering")["verdict"] == (
        "COMPLETE_OPEN_CHANNEL_LEDGER"
    )


def test_incomplete_spectrum_or_rules_prevents_completeness() -> None:
    parent = mode("P", (4.0, 4.0), 0)
    daughter = mode("d", (1.0, 1.0), 0)
    ledger = build_complete_channel_ledger(
        "incomplete",
        (parent, daughter),
        (InitialChannelState(
            "P-decay", "DECAY", ("P",), parent.mass, ("same spectrum",),
        ),),
        (certificate("P-decay", ("d", "d"), (0.0, 0.0)),),
        maximum_final_multiplicity=2,
        allowed_final_mode_ids=("d",),
        spectrum_complete=False,
        selection_rules_complete=False,
        provenance=("test",),
    )
    assert ledger.candidate_inventory_complete is False
    assert "spectrum_not_complete" in ledger.blockers
    assert "selection_rules_not_complete" in ledger.blockers


def test_extra_or_duplicate_amplitude_certificates_are_rejected() -> None:
    parent = mode("P", (4.0, 4.0), 0)
    daughter = mode("d", (1.0, 1.0), 0)
    initial = InitialChannelState(
        "P-decay", "DECAY", ("P",), parent.mass, ("same spectrum",),
    )
    cert = certificate("P-decay", ("d", "d"), (1.0, 1.0))
    with pytest.raises(ValueError, match="duplicate"):
        build_complete_channel_ledger(
            "bad", (parent, daughter), (initial,), (cert, cert),
            maximum_final_multiplicity=2,
            allowed_final_mode_ids=("d",),
            spectrum_complete=True,
            selection_rules_complete=True,
            provenance=("test",),
        )
    extra = certificate("P-decay", ("P", "P"), (1.0, 1.0))
    with pytest.raises(ValueError, match="does not match"):
        build_complete_channel_ledger(
            "bad", (parent, daughter), (initial,), (extra,),
            maximum_final_multiplicity=2,
            allowed_final_mode_ids=("d",),
            spectrum_complete=True,
            selection_rules_complete=True,
            provenance=("test",),
        )


def test_zero_candidate_sector_is_complete_and_scattering_input_is_local() -> None:
    stable = mode("stable", (2.0, 2.0), 1)
    neutral = mode("neutral", (0.5, 0.5), 0)
    incoming = InitialChannelState(
        "stable-decay", "DECAY", ("stable",), stable.mass, ("same spectrum",),
    )
    closed_scattering = InitialChannelState(
        "threshold-scattering",
        "SCATTERING",
        ("neutral", "neutral"),
        CertifiedInterval(0.9, 1.1),
        ("uncertain threshold",),
    )
    ledger = build_complete_channel_ledger(
        "mixed-ledger",
        (stable, neutral),
        (incoming, closed_scattering),
        (),
        maximum_final_multiplicity=2,
        allowed_final_mode_ids=("neutral",),
        spectrum_complete=True,
        selection_rules_complete=True,
        provenance=("complete test spectrum",),
    )
    stable_report = ledger.initial_state_report("stable-decay")
    assert stable_report["channel_count"] == 0
    assert stable_report["state_ledger_complete"] is True
    assert stable_report["verdict"] == "CERTIFIED_STABLE_ON_COMPLETE_CHANNEL_LEDGER"
    scattering_report = ledger.initial_state_report("threshold-scattering")
    assert scattering_report["initial_state_certified_open"] is False
    assert scattering_report["state_ledger_complete"] is False
    assert scattering_report["verdict"] == "OPEN_CHANNEL_LEDGER_UNRESOLVED"
    assert "threshold-scattering:initial_state_not_certified_open" in ledger.blockers
