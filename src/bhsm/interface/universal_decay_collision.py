"""Shared decay and collision phase-space readout for BHSM amplitudes.

The formulas are general relativistic phase-space identities.  Masses,
external residues, degeneracy averages, symmetry factors, and amplitudes must
be supplied by the BHSM spectrum/vertex engine; this module does not fit or
identify them.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Iterable

import numpy as np


def kallen(x: float, y: float, z: float) -> float:
    return x * x + y * y + z * z - 2.0 * (x * y + x * z + y * z)


@dataclass(frozen=True)
class TwoBodyDecayResult:
    open_channel: bool
    momentum: float
    width: float


@dataclass(frozen=True)
class ThreeBodyDecayResult:
    open_channel: bool
    width: float
    s12_lower: float
    s12_upper: float
    invariant_quadrature_order: int
    angular_quadrature_order: int
    minimum_amplitude_squared: float
    maximum_amplitude_squared: float


@dataclass(frozen=True)
class MultiBodyDecayResult:
    open_channel: bool
    width: float
    daughter_count: int
    invariant_quadrature_order: int
    angular_quadrature_order: int
    azimuthal_quadrature_order: int
    amplitude_evaluations: int
    minimum_amplitude_squared: float
    maximum_amplitude_squared: float


def two_body_decay_width(
    parent_mass: float,
    first_mass: float,
    second_mass: float,
    amplitude_squared: float,
    *,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> TwoBodyDecayResult:
    values = (
        parent_mass, first_mass, second_mass, amplitude_squared,
        initial_state_average, identical_final_state_factor,
    )
    if any(not math.isfinite(value) for value in values):
        raise ValueError("decay inputs must be finite")
    if parent_mass <= 0.0 or min(first_mass, second_mass, amplitude_squared) < 0.0:
        raise ValueError("masses and amplitude squared must be physical")
    if initial_state_average <= 0.0 or identical_final_state_factor <= 0.0:
        raise ValueError("averaging and symmetry factors must be positive")
    if parent_mass < first_mass + second_mass:
        return TwoBodyDecayResult(False, 0.0, 0.0)
    lam = max(0.0, kallen(parent_mass**2, first_mass**2, second_mass**2))
    momentum = math.sqrt(lam) / (2.0 * parent_mass)
    width = (
        momentum * amplitude_squared
        / (8.0 * math.pi * parent_mass**2)
        / initial_state_average
        / identical_final_state_factor
    )
    return TwoBodyDecayResult(True, momentum, width)


def three_body_decay_width(
    parent_mass: float,
    daughter_masses: tuple[float, float, float],
    amplitude_squared: Callable[[float, float], float],
    *,
    invariant_quadrature_order: int = 32,
    angular_quadrature_order: int = 24,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> ThreeBodyDecayResult:
    """Integrate a scalar-parent ``1->3`` amplitude over exact phase space.

    The amplitude is evaluated as ``amplitude_squared(s12, cos_theta_star)``,
    where ``theta_star`` is the daughter-1 helicity angle in the 12-pair rest
    frame.  All masses and invariants use the same units as the supplied BHSM
    spectrum.  Spin sums, LSZ residues, and internal indices must already be
    included in the action-derived amplitude.
    """

    values = (
        parent_mass, *daughter_masses, initial_state_average,
        identical_final_state_factor,
    )
    if any(not math.isfinite(value) for value in values):
        raise ValueError("three-body decay inputs must be finite")
    if parent_mass <= 0.0 or min(daughter_masses) < 0.0:
        raise ValueError("three-body masses must be physical")
    if initial_state_average <= 0.0 or identical_final_state_factor <= 0.0:
        raise ValueError("averaging and symmetry factors must be positive")
    if invariant_quadrature_order < 2 or angular_quadrature_order < 2:
        raise ValueError("three-body quadrature orders must be at least two")

    first_mass, second_mass, third_mass = daughter_masses
    s12_lower = (first_mass + second_mass) ** 2
    s12_upper = max(s12_lower, (parent_mass - third_mass) ** 2)
    if parent_mass < sum(daughter_masses):
        return ThreeBodyDecayResult(
            False, 0.0, s12_lower, s12_upper,
            invariant_quadrature_order, angular_quadrature_order, 0.0, 0.0,
        )
    if s12_upper == s12_lower:
        return ThreeBodyDecayResult(
            True, 0.0, s12_lower, s12_upper,
            invariant_quadrature_order, angular_quadrature_order, 0.0, 0.0,
        )

    invariant_nodes, invariant_weights = np.polynomial.legendre.leggauss(
        invariant_quadrature_order
    )
    angular_nodes, angular_weights = np.polynomial.legendre.leggauss(
        angular_quadrature_order
    )
    half_span = 0.5 * (s12_upper - s12_lower)
    midpoint = 0.5 * (s12_upper + s12_lower)
    invariant_values = midpoint + half_span * invariant_nodes
    amplitude_values = np.empty(
        (invariant_quadrature_order, angular_quadrature_order), dtype=float
    )
    phase_values = np.empty(invariant_quadrature_order, dtype=float)
    for index, s12 in enumerate(invariant_values):
        first_lambda = max(
            0.0, kallen(parent_mass**2, float(s12), third_mass**2)
        )
        second_lambda = max(
            0.0, kallen(float(s12), first_mass**2, second_mass**2)
        )
        phase_values[index] = (
            math.sqrt(first_lambda) * math.sqrt(second_lambda) / float(s12)
        )
        amplitude_values[index] = [
            float(amplitude_squared(float(s12), float(cosine)))
            for cosine in angular_nodes
        ]
    if not np.all(np.isfinite(amplitude_values)) or np.min(amplitude_values) < 0.0:
        raise ValueError("amplitude-squared function must be finite and nonnegative")

    angular_integrals = amplitude_values @ angular_weights
    phase_integral = half_span * float(
        np.dot(invariant_weights, phase_values * angular_integrals)
    )
    width = phase_integral / (
        512.0
        * math.pi**3
        * parent_mass**3
        * initial_state_average
        * identical_final_state_factor
    )
    return ThreeBodyDecayResult(
        True,
        width,
        s12_lower,
        s12_upper,
        invariant_quadrature_order,
        angular_quadrature_order,
        float(np.min(amplitude_values)),
        float(np.max(amplitude_values)),
    )


def _rotationless_boost(vector: np.ndarray, frame: np.ndarray) -> np.ndarray:
    """Boost a rest-frame four-vector into the frame of ``frame``."""

    beta = frame[1:] / frame[0]
    beta_squared = float(beta @ beta)
    if beta_squared == 0.0:
        return vector.copy()
    if beta_squared >= 1.0:
        raise ValueError("phase-space recursion produced a non-timelike cluster")
    gamma = 1.0 / math.sqrt(1.0 - beta_squared)
    projection = float(beta @ vector[1:])
    boosted = np.empty(4, dtype=float)
    boosted[0] = gamma * (vector[0] + projection)
    boosted[1:] = vector[1:] + (
        (gamma - 1.0) * projection / beta_squared + gamma * vector[0]
    ) * beta
    return boosted


def multi_body_decay_width(
    parent_mass: float,
    daughter_masses: tuple[float, ...],
    amplitude_squared: Callable[[tuple[np.ndarray, ...]], float],
    *,
    invariant_quadrature_order: int = 10,
    angular_quadrature_order: int = 6,
    azimuthal_quadrature_order: int = 8,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> MultiBodyDecayResult:
    """Integrate a general ``1->n`` amplitude by sequential factorization.

    The callback receives the daughter four-momenta in the parent rest frame,
    ordered like ``daughter_masses``.  The root solid angle is integrated as
    ``4*pi``; this requires the spin-summed or initial-state-averaged squared
    amplitude to be invariant under a common spatial rotation.  Every lower
    cluster split retains its polar and azimuthal angles, so correlations in
    the action-derived amplitude are preserved.

    The recursion uses

    ``dPhi_n = ds/(2*pi) dPhi_2(P; Q,p_n) dPhi_(n-1)(Q)``

    with deterministic Gauss-Legendre invariant/polar quadrature and a
    periodic midpoint rule in azimuth.  This is numerical readout machinery,
    not an interval enclosure of quadrature error.
    """

    daughter_count = len(daughter_masses)
    values = (
        parent_mass, *daughter_masses, initial_state_average,
        identical_final_state_factor,
    )
    if daughter_count < 2:
        raise ValueError("multi-body decay requires at least two daughters")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("multi-body decay inputs must be finite")
    if parent_mass <= 0.0 or min(daughter_masses) < 0.0:
        raise ValueError("multi-body masses must be physical")
    if initial_state_average <= 0.0 or identical_final_state_factor <= 0.0:
        raise ValueError("averaging and symmetry factors must be positive")
    if invariant_quadrature_order < 2 or angular_quadrature_order < 2:
        raise ValueError("multi-body Gaussian quadrature orders must be at least two")
    if azimuthal_quadrature_order < 2:
        raise ValueError("azimuthal quadrature order must be at least two")

    threshold = math.fsum(daughter_masses)
    if parent_mass < threshold:
        return MultiBodyDecayResult(
            False, 0.0, daughter_count, invariant_quadrature_order,
            angular_quadrature_order, azimuthal_quadrature_order,
            0, 0.0, 0.0,
        )
    if parent_mass == threshold:
        return MultiBodyDecayResult(
            True, 0.0, daughter_count, invariant_quadrature_order,
            angular_quadrature_order, azimuthal_quadrature_order,
            0, 0.0, 0.0,
        )

    invariant_nodes, invariant_weights = np.polynomial.legendre.leggauss(
        invariant_quadrature_order
    )
    polar_nodes, polar_weights = np.polynomial.legendre.leggauss(
        angular_quadrature_order
    )
    azimuths = 2.0 * math.pi * (
        np.arange(azimuthal_quadrature_order, dtype=float) + 0.5
    ) / azimuthal_quadrature_order
    azimuthal_weight = 2.0 * math.pi / azimuthal_quadrature_order
    lower_cluster_masses = tuple(
        math.fsum(daughter_masses[:index])
        for index in range(1, daughter_count)
    )
    momenta: list[np.ndarray | None] = [None] * daughter_count
    contributions: list[float] = []
    sampled_amplitudes: list[float] = []

    def split_and_continue(
        cluster_count: int,
        cluster: np.ndarray,
        cluster_squared: float,
        residual_squared: float,
        weight: float,
    ) -> None:
        emitted_mass = daughter_masses[cluster_count - 1]
        lam = max(
            0.0,
            kallen(cluster_squared, residual_squared, emitted_mass**2),
        )
        momentum_norm = math.sqrt(lam) / (2.0 * math.sqrt(cluster_squared))
        emitted_energy = (
            cluster_squared + emitted_mass**2 - residual_squared
        ) / (2.0 * math.sqrt(cluster_squared))
        residual_energy = (
            cluster_squared + residual_squared - emitted_mass**2
        ) / (2.0 * math.sqrt(cluster_squared))
        phase_density = math.sqrt(lam) / (
            32.0 * math.pi**2 * cluster_squared
        )
        if cluster_count == daughter_count:
            angles = ((1.0, 0.0, 4.0 * math.pi),)
        else:
            angles = (
                (float(cosine), float(phi), float(polar_weight * azimuthal_weight))
                for cosine, polar_weight in zip(polar_nodes, polar_weights)
                for phi in azimuths
            )
        for cosine, phi, angular_weight in angles:
            sine = math.sqrt(max(0.0, 1.0 - cosine * cosine))
            direction = np.asarray((
                sine * math.cos(phi), sine * math.sin(phi), cosine,
            ))
            emitted_rest = np.r_[emitted_energy, momentum_norm * direction]
            residual_rest = np.r_[residual_energy, -momentum_norm * direction]
            momenta[cluster_count - 1] = _rotationless_boost(
                emitted_rest, cluster
            )
            residual = _rotationless_boost(residual_rest, cluster)
            next_weight = weight * phase_density * angular_weight
            if cluster_count == 2:
                momenta[0] = residual
                physical_momenta = tuple(
                    np.asarray(momentum, dtype=float).copy()
                    for momentum in momenta
                    if momentum is not None
                )
                if len(physical_momenta) != daughter_count:
                    raise RuntimeError("incomplete phase-space momentum recursion")
                amplitude_value = float(amplitude_squared(physical_momenta))
                if not math.isfinite(amplitude_value) or amplitude_value < 0.0:
                    raise ValueError(
                        "amplitude-squared function must be finite and nonnegative"
                    )
                sampled_amplitudes.append(amplitude_value)
                contributions.append(next_weight * amplitude_value)
            else:
                integrate_cluster(
                    cluster_count - 1,
                    residual,
                    residual_squared,
                    next_weight,
                )

    def integrate_cluster(
        cluster_count: int,
        cluster: np.ndarray,
        cluster_squared: float,
        weight: float,
    ) -> None:
        if cluster_count == 2:
            split_and_continue(
                2, cluster, cluster_squared, daughter_masses[0] ** 2, weight
            )
            return
        lower = lower_cluster_masses[cluster_count - 2] ** 2
        upper = (
            math.sqrt(cluster_squared) - daughter_masses[cluster_count - 1]
        ) ** 2
        if upper <= lower:
            return
        half_span = 0.5 * (upper - lower)
        midpoint = 0.5 * (upper + lower)
        for node, node_weight in zip(invariant_nodes, invariant_weights):
            residual_squared = midpoint + half_span * float(node)
            invariant_weight = half_span * float(node_weight) / (2.0 * math.pi)
            split_and_continue(
                cluster_count,
                cluster,
                cluster_squared,
                residual_squared,
                weight * invariant_weight,
            )

    integrate_cluster(
        daughter_count,
        np.asarray((parent_mass, 0.0, 0.0, 0.0)),
        parent_mass**2,
        1.0,
    )
    phase_integral = math.fsum(contributions)
    width = phase_integral / (
        2.0
        * parent_mass
        * initial_state_average
        * identical_final_state_factor
    )
    return MultiBodyDecayResult(
        True,
        width,
        daughter_count,
        invariant_quadrature_order,
        angular_quadrature_order,
        azimuthal_quadrature_order,
        len(sampled_amplitudes),
        min(sampled_amplitudes, default=0.0),
        max(sampled_amplitudes, default=0.0),
    )


@dataclass(frozen=True)
class TwoToTwoResult:
    open_channel: bool
    incoming_momentum: float
    outgoing_momentum: float
    differential_cross_section_domega: float


def two_to_two_differential_cross_section(
    s: float,
    incoming_masses: tuple[float, float],
    outgoing_masses: tuple[float, float],
    amplitude_squared: float,
    *,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> TwoToTwoResult:
    if not all(math.isfinite(value) for value in (
        s, *incoming_masses, *outgoing_masses, amplitude_squared,
        initial_state_average, identical_final_state_factor,
    )):
        raise ValueError("collision inputs must be finite")
    if s <= 0.0 or min(*incoming_masses, *outgoing_masses, amplitude_squared) < 0.0:
        raise ValueError("collision invariants, masses, and amplitude squared must be physical")
    root_s = math.sqrt(s)
    if root_s < sum(incoming_masses) or root_s < sum(outgoing_masses):
        return TwoToTwoResult(False, 0.0, 0.0, 0.0)
    incoming = math.sqrt(max(0.0, kallen(s, incoming_masses[0] ** 2, incoming_masses[1] ** 2))) / (2.0 * root_s)
    outgoing = math.sqrt(max(0.0, kallen(s, outgoing_masses[0] ** 2, outgoing_masses[1] ** 2))) / (2.0 * root_s)
    if incoming == 0.0:
        return TwoToTwoResult(False, incoming, outgoing, 0.0)
    differential = (
        amplitude_squared
        * outgoing / incoming
        / (64.0 * math.pi**2 * s)
        / initial_state_average
        / identical_final_state_factor
    )
    return TwoToTwoResult(True, incoming, outgoing, differential)


@dataclass(frozen=True)
class DecayLedgerResult:
    total_width: float
    inverse_width_lifetime: float
    branching_fractions: dict[str, float]


def combine_decay_channels(
    channels: Iterable[
        tuple[str, TwoBodyDecayResult | ThreeBodyDecayResult | MultiBodyDecayResult]
    ],
) -> DecayLedgerResult:
    """Combine a complete list of action-derived partial widths.

    The lifetime is returned in inverse units of the supplied width.  A
    seconds conversion belongs after the universal BHSM scale and physical
    unit convention are fixed.
    """

    entries = tuple(channels)
    names = [name for name, _ in entries]
    if len(names) != len(set(names)):
        raise ValueError("duplicate decay-channel id")
    widths = {name: result.width for name, result in entries}
    if any(not math.isfinite(width) or width < 0.0 for width in widths.values()):
        raise ValueError("partial widths must be finite and nonnegative")
    total = math.fsum(widths.values())
    branching = (
        {name: width / total for name, width in widths.items()}
        if total > 0.0
        else {name: 0.0 for name in widths}
    )
    return DecayLedgerResult(
        total_width=total,
        inverse_width_lifetime=math.inf if total == 0.0 else 1.0 / total,
        branching_fractions=branching,
    )


@dataclass(frozen=True)
class IntegratedTwoToTwoResult:
    open_channel: bool
    total_cross_section: float
    quadrature_order: int
    minimum_amplitude_squared: float
    maximum_amplitude_squared: float


def integrate_two_to_two_cross_section(
    s: float,
    incoming_masses: tuple[float, float],
    outgoing_masses: tuple[float, float],
    amplitude_squared: Callable[[float], float],
    *,
    quadrature_order: int = 32,
    initial_state_average: float = 1.0,
    identical_final_state_factor: float = 1.0,
) -> IntegratedTwoToTwoResult:
    """Integrate an azimuth-symmetric ``2->2`` BHSM amplitude over angle."""

    if quadrature_order < 2:
        raise ValueError("quadrature order must be at least two")
    root_s = math.sqrt(s) if s > 0.0 else 0.0
    if root_s < sum(incoming_masses) or root_s < sum(outgoing_masses):
        return IntegratedTwoToTwoResult(False, 0.0, quadrature_order, 0.0, 0.0)
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    amplitudes = np.asarray([float(amplitude_squared(float(node))) for node in nodes])
    if not np.all(np.isfinite(amplitudes)) or np.min(amplitudes) < 0.0:
        raise ValueError("amplitude-squared function must be finite and nonnegative")
    differential = np.asarray([
        two_to_two_differential_cross_section(
            s,
            incoming_masses,
            outgoing_masses,
            value,
            initial_state_average=initial_state_average,
            identical_final_state_factor=identical_final_state_factor,
        ).differential_cross_section_domega
        for value in amplitudes
    ])
    # dOmega = dphi d(cos(theta)); azimuth symmetry supplies 2*pi.
    total = float(2.0 * math.pi * np.dot(weights, differential))
    return IntegratedTwoToTwoResult(
        open_channel=True,
        total_cross_section=total,
        quadrature_order=quadrature_order,
        minimum_amplitude_squared=float(np.min(amplitudes)),
        maximum_amplitude_squared=float(np.max(amplitudes)),
    )


__all__ = [
    "DecayLedgerResult",
    "IntegratedTwoToTwoResult",
    "MultiBodyDecayResult",
    "ThreeBodyDecayResult",
    "TwoBodyDecayResult",
    "TwoToTwoResult",
    "combine_decay_channels",
    "integrate_two_to_two_cross_section",
    "kallen",
    "multi_body_decay_width",
    "two_body_decay_width",
    "three_body_decay_width",
    "two_to_two_differential_cross_section",
]
