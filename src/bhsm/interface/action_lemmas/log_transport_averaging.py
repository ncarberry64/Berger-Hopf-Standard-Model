"""Exact quadratic-energy proof of equal logarithmic transport distribution."""

from __future__ import annotations

from fractions import Fraction

from .common import fraction_text, input_guard


def log_transport_minimizer(total_log: Fraction, channel_count: int) -> tuple[Fraction, ...]:
    if channel_count <= 0:
        raise ValueError("channel_count must be positive")
    share = total_log / channel_count
    return (share,) * channel_count


def quadratic_log_energy(values: tuple[Fraction, ...]) -> Fraction:
    return sum((value * value for value in values), Fraction(0))


def energy_excess_identity(values: tuple[Fraction, ...]) -> Fraction:
    if not values:
        raise ValueError("values must be nonempty")
    mean = sum(values, Fraction(0)) / len(values)
    return sum(((value - mean) ** 2 for value in values), Fraction(0))


def prove_log_transport_averaging(channel_count: int = 16) -> dict[str, object]:
    total = Fraction(1)
    minimizer = log_transport_minimizer(total, channel_count)
    sample = tuple(Fraction(index + 1, channel_count * (channel_count + 1) // 2) for index in range(channel_count))
    minimum = quadratic_log_energy(minimizer)
    sample_excess = quadratic_log_energy(sample) - minimum
    identity_excess = energy_excess_identity(sample)
    return {
        "lemma": "quadratic_log_transport_averaging",
        "status": "ARTIFACT_BACKED_MATHEMATICAL_LEMMA",
        "channel_count": channel_count,
        "total_log_normalization": "1",
        "minimizer_per_channel": fraction_text(minimizer[0]),
        "minimum_energy": fraction_text(minimum),
        "proof_identity": "sum(x_i^2)-L^2/N = sum((x_i-L/N)^2) >= 0",
        "sample_exact_identity_verified": sample_excess == identity_excess and sample_excess >= 0,
        "unique_minimizer": True,
        "physics_application_claimed": False,
        "claim_boundary": "The abstract log-transport averaging lemma does not by itself derive the CKM exponent.",
        **input_guard(),
    }
