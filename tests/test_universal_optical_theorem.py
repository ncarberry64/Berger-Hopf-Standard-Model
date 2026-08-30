import pytest

from bhsm.interface.universal_optical_theorem import reconcile_optical_theorem


def report(imaginary, channels, *, complete=True, gate7=True):
    return reconcile_optical_theorem(
        100.0,
        (0.0, 0.0),
        2.0 + 1.0j * imaginary,
        channels,
        complete_channel_ledger=complete,
        gate7_closed=gate7,
        action_version="TEST-ACTION",
        background_id="test-background",
        provenance=("unit-test inclusive ledger",),
    )


def test_complete_massless_ledger_satisfies_optical_theorem() -> None:
    result = report(5.0, (("elastic", 0.02), ("inelastic", 0.03)))
    assert result.optical_total_cross_section == 0.05
    assert result.inclusive_ledger_cross_section == 0.05
    assert result.relative_equality_residual < 1.0e-15
    result.require_physical_promotion()


def test_incomplete_ledger_may_leave_positive_absorptive_remainder() -> None:
    result = report(5.0, (("known", 0.02),), complete=False)
    result.require_consistency()
    assert result.inclusive_ledger_cross_section < result.optical_total_cross_section
    with pytest.raises(RuntimeError, match="complete_inclusive_channel_ledger"):
        result.require_physical_promotion()


def test_incomplete_ledger_cannot_exceed_forward_total() -> None:
    result = report(5.0, (("overcounted", 0.06),), complete=False)
    assert result.incomplete_ledger_excess > 0.0
    with pytest.raises(RuntimeError, match="cannot_exceed"):
        result.require_consistency()


def test_negative_absorptive_part_fails_closed() -> None:
    result = report(-1.0, (("channel", 0.0),))
    assert result.absorptive_part_nonnegative is False
    with pytest.raises(RuntimeError, match="nonnegative_forward_absorptive_part"):
        result.require_consistency()


def test_duplicate_channel_ids_are_rejected() -> None:
    with pytest.raises(ValueError, match="unique"):
        report(1.0, (("same", 0.005), ("same", 0.005)))
