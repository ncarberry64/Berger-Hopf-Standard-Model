"""Dimensionless curvature-threshold response for neutral boundary propagation."""

from __future__ import annotations

from math import sqrt

from .common import BackgroundCoupling, CurvatureThreshold, NeutralKernelArtifact, PropagationState


def build_curvature_threshold(kernel: NeutralKernelArtifact) -> CurvatureThreshold:
    return CurvatureThreshold(
        value=kernel.kappa_nu,
        symbol="kappa_nu",
        response_law="R_excess = max(0, p*g_nu*||K_nu psi||/||psi|| - kappa_nu)",
        interpretation="Push-back is the coupled neutral-kernel response exceeding the artifact-backed dimensionless curvature threshold.",
        status="ESTABLISHED_ARTIFACT_BACKED",
        source_artifacts=(kernel.source_artifact,),
    )


def build_background_coupling(kernel: NeutralKernelArtifact) -> BackgroundCoupling:
    return BackgroundCoupling(
        value=kernel.g_nu,
        symbol="g_nu",
        status="ESTABLISHED_ARTIFACT_BACKED",
        source_artifact=kernel.source_artifact,
    )


def kernel_response_norm(
    kernel: NeutralKernelArtifact,
    state: PropagationState,
) -> float:
    if len(state.amplitudes) != len(kernel.matrix):
        raise ValueError("propagation state dimension does not match K_nu")
    output = tuple(
        sum(row[column] * state.amplitudes[column] for column in range(len(row)))
        for row in kernel.matrix
    )
    return sqrt(sum(value * value for value in output))


def threshold_response(
    kernel: NeutralKernelArtifact,
    state: PropagationState,
    threshold: CurvatureThreshold,
    background: BackgroundCoupling,
) -> tuple[float, float, float]:
    """Return kernel norm, coupled response, and positive threshold excess."""

    response_norm = kernel_response_norm(kernel, state)
    coupled = state.propagation_response * background.value * response_norm
    excess = max(0.0, coupled - threshold.value)
    return response_norm, coupled, excess
