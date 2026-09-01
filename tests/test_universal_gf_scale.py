import pytest

from bhsm.interface.universal_gf_scale import UniversalGFScaleMap


def scale() -> UniversalGFScaleMap:
    return UniversalGFScaleMap(
        dimensionless_fermi_coefficient=4.0,
        fermi_constant=0.25,
        action_version="BHSM-TEST",
        background_id="background",
        coefficient_provenance=("action current-current response",),
        calibration_provenance=("owner-authorized sole G_F calibration",),
    )


def test_one_gf_calibration_sets_every_dimensional_readout() -> None:
    item = scale()
    assert item.mass_scale == 4.0
    assert item.length_scale == 0.25
    assert item.mass(2.0) == 8.0
    assert item.width(0.5) == 2.0
    assert item.inverse_mass_squared(16.0) == 1.0
    assert item.metadata()["calibration_count"] == 1
    assert item.metadata()["sector_specific_scales_allowed"] is False


def test_non_action_fermi_coefficient_without_provenance_is_rejected() -> None:
    with pytest.raises(ValueError, match="coefficient provenance"):
        UniversalGFScaleMap(
            dimensionless_fermi_coefficient=1.0,
            fermi_constant=1.0,
            action_version="BHSM-TEST",
            background_id="background",
            coefficient_provenance=(),
            calibration_provenance=("G_F",),
        )


def test_negative_sector_readout_is_rejected() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        scale().mass(-1.0)
