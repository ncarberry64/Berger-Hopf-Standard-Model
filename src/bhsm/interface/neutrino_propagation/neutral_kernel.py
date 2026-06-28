"""Artifact-backed neutral boundary field and kernel loader."""

from __future__ import annotations

import json
from pathlib import Path

from .common import NeutralBoundaryField, NeutralKernelArtifact, repository_path


NEUTRAL_KERNEL_ARTIFACT = "artifacts/neutral_operator_no_fit_output_v1.json"


def load_neutral_kernel(repository: str | Path | None = None) -> NeutralKernelArtifact:
    root = repository_path(repository)
    path = root / NEUTRAL_KERNEL_ARTIFACT
    if not path.is_file():
        raise FileNotFoundError(f"neutral kernel artifact is missing: {NEUTRAL_KERNEL_ARTIFACT}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = ("K_nu", "eta_nu", "g_nu", "beta_nu", "kappa_nu", "H_nu")
    if any(key not in payload for key in required):
        raise ValueError("neutral kernel artifact is incomplete")
    matrix = tuple(tuple(float(value) for value in row) for row in payload["K_nu"])
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("K_nu must be a three-by-three neutral boundary kernel")
    return NeutralKernelArtifact(
        matrix=matrix,
        eta_nu=float(payload["eta_nu"]),
        g_nu=float(payload["g_nu"]),
        beta_nu=float(payload["beta_nu"]),
        kappa_nu=float(payload["kappa_nu"]),
        mode_labels=tuple(tuple(int(value) for value in row) for row in payload["H_nu"]),
        status="ESTABLISHED_ARTIFACT_BACKED",
        source_artifact=NEUTRAL_KERNEL_ARTIFACT,
    )


def build_neutral_boundary_field(kernel: NeutralKernelArtifact) -> NeutralBoundaryField:
    return NeutralBoundaryField(
        symbol="Psi_nu_boundary",
        basis=("neutral_channel_1", "neutral_channel_2", "neutral_channel_3"),
        mode_labels=kernel.mode_labels,
        interpretation="physical neutral boundary-local field under the BHSM author ontology",
        status="CONDITIONAL_PROPAGATION_THEOREM",
        source_artifacts=(kernel.source_artifact, "artifacts/BHSM_author_ontology_v0_8.json"),
    )
