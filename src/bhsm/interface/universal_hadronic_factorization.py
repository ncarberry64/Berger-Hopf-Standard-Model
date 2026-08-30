"""Hadronic factorization bridge for action-owned partonic cross sections.

This module performs the standard ordered-parton luminosity convolution.  It
does not derive or fit a PDF set, select collider data, or create a BHSM
amplitude.  The caller must supply a complete same-action partonic channel
ledger and frozen PDF provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable

import numpy as np


PDF = Callable[[str, str, float, float], float]
PartonicCrossSection = Callable[[float, float, float], float]


@dataclass(frozen=True)
class PartonicChannel:
    channel_id: str
    incoming_parton_ids: tuple[str, str]
    threshold_s: float
    cross_section_hat: PartonicCrossSection
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.channel_id
            or len(self.incoming_parton_ids) != 2
            or not all(self.incoming_parton_ids)
            or not math.isfinite(self.threshold_s)
            or self.threshold_s < 0.0
        ):
            raise ValueError("partonic channel identity, pair, and threshold are required")
        if not callable(self.cross_section_hat):
            raise ValueError("partonic cross section must be callable")
        if not self.action_version or not self.background_id or not self.provenance:
            raise ValueError("partonic channel action/background provenance is required")


@dataclass(frozen=True)
class HadronicFactorizationResult:
    collider_s: float
    beam_ids: tuple[str, str]
    factorization_scale: float
    renormalization_scale: float
    factorization_scheme_id: str
    pdf_set_id: str
    pdf_input_classification: str
    channel_contributions: dict[str, float]
    total_cross_section: float
    quadrature_absolute_error_upper: float | None
    cross_section_interval: tuple[float, float] | None
    quadrature_order: int
    pdf_evaluations: int
    complete_partonic_channel_ledger: bool
    pdf_frozen_before_prediction: bool
    gate7_closed: bool
    action_version: str
    background_id: str
    provenance: tuple[str, ...]

    def require_physical_promotion(self) -> None:
        blockers: list[str] = []
        if not self.gate7_closed:
            blockers.append("Gate7_closed_background")
        if not self.complete_partonic_channel_ledger:
            blockers.append("complete_same_action_partonic_channel_ledger")
        if not self.pdf_frozen_before_prediction:
            blockers.append("PDF_input_frozen_before_prediction")
        if self.quadrature_absolute_error_upper is None:
            blockers.append("outward_hadronic_quadrature_error")
        if not self.factorization_scheme_id or not self.pdf_set_id:
            blockers.append("factorization_and_PDF_provenance")
        if blockers:
            raise RuntimeError("hadronic prediction promotion blocked by: " + ", ".join(blockers))

    def metadata(self) -> dict:
        return {
            "collider_s": self.collider_s,
            "beam_ids": list(self.beam_ids),
            "factorization_scale": self.factorization_scale,
            "renormalization_scale": self.renormalization_scale,
            "factorization_scheme_id": self.factorization_scheme_id,
            "pdf_set_id": self.pdf_set_id,
            "pdf_input_classification": self.pdf_input_classification,
            "channel_contributions": dict(self.channel_contributions),
            "total_cross_section": self.total_cross_section,
            "cross_section_interval": (
                None if self.cross_section_interval is None
                else list(self.cross_section_interval)
            ),
            "complete_partonic_channel_ledger": self.complete_partonic_channel_ledger,
            "pdf_frozen_before_prediction": self.pdf_frozen_before_prediction,
            "gate7_closed": self.gate7_closed,
            "action_version": self.action_version,
            "background_id": self.background_id,
            "empirical_input_used": (
                self.pdf_input_classification == "EMPIRICAL_EXTERNAL_INPUT"
            ),
            "experimental_observable_used_to_select_BHSM_branch": False,
        }


def convolve_hadronic_cross_section(
    collider_s: float,
    beam_ids: tuple[str, str],
    channels: Iterable[PartonicChannel],
    pdf: PDF,
    *,
    factorization_scale: float,
    renormalization_scale: float,
    factorization_scheme_id: str,
    pdf_set_id: str,
    pdf_input_classification: str,
    pdf_provenance: tuple[str, ...],
    quadrature_order: int = 32,
    quadrature_absolute_error_upper: float | None = None,
    quadrature_error_provenance: tuple[str, ...] = (),
    complete_partonic_channel_ledger: bool,
    pdf_frozen_before_prediction: bool,
    gate7_closed: bool,
    provenance: tuple[str, ...],
) -> HadronicFactorizationResult:
    """Convolve ordered partonic channels with two beam PDF densities.

    For each channel this evaluates

    ``int_tau0^1 d tau int_tau^1 dx/x f_i/A(x) f_j/B(tau/x)
      sigma_hat_ij(tau*S)``.

    Reversed incoming partons are distinct ordered channels and must be
    included explicitly when required by the complete ledger.
    """

    rows = tuple(channels)
    if (
        not math.isfinite(collider_s)
        or collider_s <= 0.0
        or len(beam_ids) != 2
        or not all(beam_ids)
    ):
        raise ValueError("positive collider invariant and two beam ids are required")
    if (
        not math.isfinite(factorization_scale)
        or not math.isfinite(renormalization_scale)
        or factorization_scale <= 0.0
        or renormalization_scale <= 0.0
    ):
        raise ValueError("factorization and renormalization scales must be positive")
    if quadrature_order < 2:
        raise ValueError("hadronic quadrature order must be at least two")
    if not rows:
        raise ValueError("at least one partonic channel is required")
    channel_ids = [row.channel_id for row in rows]
    if len(channel_ids) != len(set(channel_ids)):
        raise ValueError("partonic channel ids must be unique")
    action_versions = {row.action_version for row in rows}
    backgrounds = {row.background_id for row in rows}
    if len(action_versions) != 1 or len(backgrounds) != 1:
        raise ValueError("all partonic channels must share one action and background")
    if pdf_input_classification not in {
        "EMPIRICAL_EXTERNAL_INPUT",
        "ACTION_DERIVED_INPUT",
    }:
        raise ValueError("PDF input classification is not recognized")
    if (
        not factorization_scheme_id
        or not pdf_set_id
        or not pdf_provenance
        or not provenance
    ):
        raise ValueError("factorization, PDF, and action provenance are required")
    if quadrature_absolute_error_upper is not None:
        if (
            not math.isfinite(quadrature_absolute_error_upper)
            or quadrature_absolute_error_upper < 0.0
            or not quadrature_error_provenance
        ):
            raise ValueError("quadrature error bound requires finite outward provenance")

    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    contributions: dict[str, float] = {}
    evaluations = 0
    for channel in rows:
        tau_lower = channel.threshold_s / collider_s
        if tau_lower >= 1.0:
            contributions[channel.channel_id] = 0.0
            continue
        tau_lower = max(0.0, tau_lower)
        tau_half_span = 0.5 * (1.0 - tau_lower)
        tau_midpoint = 0.5 * (1.0 + tau_lower)
        channel_terms: list[float] = []
        for tau_node, tau_weight in zip(nodes, weights):
            tau = tau_midpoint + tau_half_span * float(tau_node)
            x_half_span = 0.5 * (1.0 - tau)
            x_midpoint = 0.5 * (1.0 + tau)
            inner_terms: list[float] = []
            sigma_hat = float(channel.cross_section_hat(
                tau * collider_s,
                factorization_scale,
                renormalization_scale,
            ))
            if not math.isfinite(sigma_hat) or sigma_hat < 0.0:
                raise ValueError("partonic cross sections must be finite and nonnegative")
            for x_node, x_weight in zip(nodes, weights):
                x_first = x_midpoint + x_half_span * float(x_node)
                x_second = tau / x_first
                first_density = float(pdf(
                    beam_ids[0], channel.incoming_parton_ids[0],
                    x_first, factorization_scale,
                ))
                second_density = float(pdf(
                    beam_ids[1], channel.incoming_parton_ids[1],
                    x_second, factorization_scale,
                ))
                if (
                    not math.isfinite(first_density)
                    or not math.isfinite(second_density)
                    or min(first_density, second_density) < 0.0
                ):
                    raise ValueError("PDF densities must be finite and nonnegative")
                inner_terms.append(
                    float(x_weight)
                    * first_density
                    * second_density
                    * sigma_hat
                    / x_first
                )
                evaluations += 2
            inner_integral = x_half_span * math.fsum(inner_terms)
            channel_terms.append(float(tau_weight) * inner_integral)
        contributions[channel.channel_id] = (
            tau_half_span * math.fsum(channel_terms)
        )
    total = math.fsum(contributions.values())
    interval = None
    if quadrature_absolute_error_upper is not None:
        interval = (
            max(0.0, total - quadrature_absolute_error_upper),
            total + quadrature_absolute_error_upper,
        )
    return HadronicFactorizationResult(
        collider_s=collider_s,
        beam_ids=beam_ids,
        factorization_scale=factorization_scale,
        renormalization_scale=renormalization_scale,
        factorization_scheme_id=factorization_scheme_id,
        pdf_set_id=pdf_set_id,
        pdf_input_classification=pdf_input_classification,
        channel_contributions=contributions,
        total_cross_section=total,
        quadrature_absolute_error_upper=quadrature_absolute_error_upper,
        cross_section_interval=interval,
        quadrature_order=quadrature_order,
        pdf_evaluations=evaluations,
        complete_partonic_channel_ledger=bool(complete_partonic_channel_ledger),
        pdf_frozen_before_prediction=bool(pdf_frozen_before_prediction),
        gate7_closed=bool(gate7_closed),
        action_version=next(iter(action_versions)),
        background_id=next(iter(backgrounds)),
        provenance=provenance + pdf_provenance + quadrature_error_provenance,
    )


__all__ = [
    "HadronicFactorizationResult",
    "PartonicChannel",
    "convolve_hadronic_cross_section",
]
