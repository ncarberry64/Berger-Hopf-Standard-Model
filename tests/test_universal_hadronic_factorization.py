import math

import numpy as np
import pytest

from bhsm.interface.universal_hadronic_factorization import (
    PartonicChannel,
    convolve_hadronic_cross_section,
)


def channel(
    channel_id: str = "ij->X",
    *,
    threshold_s: float = 25.0,
    value: float = 3.0,
) -> PartonicChannel:
    return PartonicChannel(
        channel_id,
        ("i", "j"),
        threshold_s,
        lambda _s_hat, _mu_f, _mu_r: value,
        "BHSM-TEST-ACTION",
        "BHSM-TEST-BACKGROUND",
        ("complete same-action partonic amplitude",),
    )


def densities(_beam: str, parton: str, x: float, _scale: float) -> float:
    return x if parton == "i" else 1.0


def convolve(channels, **overrides):
    arguments = dict(
        collider_s=100.0,
        beam_ids=("A", "B"),
        channels=channels,
        pdf=densities,
        factorization_scale=10.0,
        renormalization_scale=10.0,
        factorization_scheme_id="MSBAR",
        pdf_set_id="FROZEN-PDF",
        pdf_input_classification="EMPIRICAL_EXTERNAL_INPUT",
        pdf_provenance=("PDF set frozen before BHSM comparison",),
        quadrature_order=12,
        quadrature_absolute_error_upper=1.0e-12,
        quadrature_error_provenance=("outward test bound",),
        complete_partonic_channel_ledger=True,
        pdf_frozen_before_prediction=True,
        gate7_closed=True,
        provenance=("same-action partonic ledger",),
    )
    arguments.update(overrides)
    return convolve_hadronic_cross_section(**arguments)


def test_polynomial_pdf_luminosity_matches_exact_convolution() -> None:
    result = convolve((channel(),))
    tau_zero = 0.25
    expected = 3.0 * (1.0 - tau_zero) ** 2 / 2.0
    assert np.isclose(result.total_cross_section, expected, rtol=2.0e-14)
    assert result.channel_contributions["ij->X"] == result.total_cross_section
    assert result.cross_section_interval is not None
    assert result.cross_section_interval[0] <= expected <= result.cross_section_interval[1]
    assert result.metadata()["empirical_input_used"] is True
    result.require_physical_promotion()


def test_ordered_channels_sum_and_threshold_closed_channel_is_zero() -> None:
    result = convolve((
        channel("open", value=2.0),
        channel("closed", threshold_s=100.0, value=100.0),
    ))
    assert result.channel_contributions["open"] > 0.0
    assert result.channel_contributions["closed"] == 0.0
    assert math.isclose(result.total_cross_section, result.channel_contributions["open"])


def test_incomplete_ledger_unfrozen_pdf_and_missing_error_fail_promotion() -> None:
    result = convolve(
        (channel(),),
        complete_partonic_channel_ledger=False,
        pdf_frozen_before_prediction=False,
        gate7_closed=False,
        quadrature_absolute_error_upper=None,
        quadrature_error_provenance=(),
    )
    with pytest.raises(RuntimeError) as caught:
        result.require_physical_promotion()
    message = str(caught.value)
    assert "Gate7_closed_background" in message
    assert "complete_same_action_partonic_channel_ledger" in message
    assert "PDF_input_frozen_before_prediction" in message
    assert "outward_hadronic_quadrature_error" in message


def test_negative_pdf_or_partonic_cross_section_is_rejected() -> None:
    with pytest.raises(ValueError, match="PDF densities"):
        convolve((channel(),), pdf=lambda *_args: -1.0)
    with pytest.raises(ValueError, match="partonic cross sections"):
        convolve((channel(value=-1.0),))


def test_duplicate_or_mixed_provenance_channels_are_rejected() -> None:
    first = channel()
    with pytest.raises(ValueError, match="unique"):
        convolve((first, first))
    mixed = PartonicChannel(
        "mixed", ("i", "j"), 25.0, lambda *_args: 1.0,
        "OTHER-ACTION", "BHSM-TEST-BACKGROUND", ("other",),
    )
    with pytest.raises(ValueError, match="one action and background"):
        convolve((first, mixed))


def test_outward_error_requires_provenance() -> None:
    with pytest.raises(ValueError, match="outward provenance"):
        convolve(
            (channel(),),
            quadrature_absolute_error_upper=1.0e-6,
            quadrature_error_provenance=(),
        )
