"""Threshold-aware running architecture for BHSM precision QCD/RG comparison."""

from __future__ import annotations

from dataclasses import dataclass

from quark_running import (
    MZ,
    PIECEWISE_NF_APPROX,
    alpha_s_one_loop,
    alpha_s_piecewise_one_loop,
    default_thresholds,
    mass_running_factor_one_loop,
    mass_running_piecewise,
    run_mass_one_loop,
    run_mass_piecewise,
)


ONE_LOOP_BASELINE = "ONE_LOOP_BASELINE"
THRESHOLD_AWARE_ONE_LOOP = "THRESHOLD_AWARE_ONE_LOOP"
TWO_LOOP_PLACEHOLDER = "TWO_LOOP_PLACEHOLDER"
THREE_LOOP_PLACEHOLDER = "THREE_LOOP_PLACEHOLDER"


@dataclass(frozen=True)
class ThresholdMatchingConfig:
    """Configuration for the QCD/RG running scaffold."""

    target_scale_gev: float = MZ
    alpha_s_mz: float = 0.1180
    mz: float = MZ
    method: str = THRESHOLD_AWARE_ONE_LOOP
    exponent_policy: str = PIECEWISE_NF_APPROX
    notes: tuple[str, ...] = (
        "One-loop-inspired scaffold; not precision QCD.",
        "Two-/three-loop matching is placeholder-only unless explicitly implemented.",
    )


@dataclass(frozen=True)
class RunningMassResult:
    """One running mass result row."""

    particle: str
    mass_initial: float
    scale_initial_gev: float
    mass_running: float | None
    scale_target_gev: float
    running_factor: float | None
    method: str
    implemented: bool
    source_label: str
    notes: tuple[str, ...]


def running_mass(
    particle: str,
    mass: float,
    scale_from_gev: float,
    config: ThresholdMatchingConfig,
) -> RunningMassResult:
    """Run a quark mass according to the selected scaffold method."""

    if config.method == ONE_LOOP_BASELINE:
        factor = mass_running_factor_one_loop(scale_from_gev, config.target_scale_gev, config.alpha_s_mz, config.mz)
        value = run_mass_one_loop(mass, scale_from_gev, config.target_scale_gev, config.alpha_s_mz, config.mz)
        return RunningMassResult(particle, mass, scale_from_gev, value, config.target_scale_gev, factor, config.method, True, "one_loop_running_scaffold", config.notes)
    if config.method == THRESHOLD_AWARE_ONE_LOOP:
        factor = mass_running_piecewise(scale_from_gev, config.target_scale_gev, config.alpha_s_mz, config.mz, default_thresholds(), config.exponent_policy)
        value = run_mass_piecewise(mass, scale_from_gev, config.target_scale_gev, config.alpha_s_mz, config.mz, default_thresholds(), config.exponent_policy)
        return RunningMassResult(particle, mass, scale_from_gev, value, config.target_scale_gev, factor, config.method, True, "threshold_aware_running_scaffold", config.notes)
    if config.method in {TWO_LOOP_PLACEHOLDER, THREE_LOOP_PLACEHOLDER}:
        return RunningMassResult(
            particle=particle,
            mass_initial=mass,
            scale_initial_gev=scale_from_gev,
            mass_running=None,
            scale_target_gev=config.target_scale_gev,
            running_factor=None,
            method=config.method,
            implemented=False,
            source_label=config.method,
            notes=("Placeholder only; higher-loop matching is not implemented.",),
        )
    raise ValueError(f"unknown running method: {config.method}")


def alpha_s_at_target(config: ThresholdMatchingConfig) -> float | None:
    """Return alpha_s at target for implemented one-loop scaffold methods."""

    if config.method == ONE_LOOP_BASELINE:
        return alpha_s_one_loop(config.target_scale_gev, config.alpha_s_mz, config.mz)
    if config.method == THRESHOLD_AWARE_ONE_LOOP:
        return alpha_s_piecewise_one_loop(config.target_scale_gev, config.alpha_s_mz, config.mz)
    return None
