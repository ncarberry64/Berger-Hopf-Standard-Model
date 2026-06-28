"""Offline index for Norman Carberry's legacy curvature-threshold papers."""

from __future__ import annotations

import hashlib
from pathlib import Path

from .common import repository_path
from .legacy_curvature_threshold import LegacyCurvatureArtifact


LEGACY_SOURCE_DIR = "theory/legacy_sources/v1_1"

LEGACY_SOURCE_SPECS = (
    (
        "local_curvature_threshold_eft",
        f"{LEGACY_SOURCE_DIR}/mass_from_local_curvature_thresholds_scalar_topographic_eft.pdf",
        "Mass from Local Curvature Thresholds in a Scalar Topographic Effective Field Theory",
        (
            "K[rho] = -nabla^2 ln rho",
            "k_loc = K[rho](r_c)",
            "N_K = integral sigma K[rho](r) dr; N_K = 1",
            "m = (c^2/(2G)) r_c^2 k_loc",
            "E = (c^4/(2G)) r_c^2 k_loc",
        ),
        (
            "The document explicitly describes the mass formula as a geometric matching ansatz rather than an action-derived result.",
            "Its experimental examples are not BHSM theorem inputs.",
        ),
    ),
    (
        "curvature_mass_gap_eft",
        f"{LEGACY_SOURCE_DIR}/mass_gap.pdf",
        "A Curvature-Threshold Scalar Topographic EFT as a Mass-Gap Analogue of Yang-Mills Theory",
        (
            "L = 1/2(dt phi)^2 - 1/2(grad phi)^2 - lambda/2(-nabla^2 phi - k_loc)^2",
            "m_gap = sqrt(lambda) k_loc",
        ),
        (
            "Used only as scalar-EFT action and spectral support.",
            "No Yang-Mills proof or BHSM neutrino mass follows from this analogue.",
        ),
    ),
    (
        "hyperspherical_mass_framework",
        f"{LEGACY_SOURCE_DIR}/mass_without_higgs.pdf",
        "Mass Without Higgs: A Geometric Framework for Emergent Particle Mass and Hyperspherical Gravity",
        (
            "m = (c^2/(2G)) r^2 k",
            "S = integral_{S^3} d^3x sqrt(g) [R/(16 pi G) - field kinetic and potential terms]",
            "S^3 harmonic overlap integrals",
        ),
        (
            "The representative particle table assumes r = 10^-15 m and is illustrative calibration material.",
            "That table is forbidden as a no-fit BHSM derivation input.",
        ),
    ),
    (
        "origin_of_mass_latex",
        f"{LEGACY_SOURCE_DIR}/origin_of_mass_latex.docx",
        "The Origin of Mass",
        (
            "S_T = integral d^4x [1/2(d_mu T)(d^mu T) + B/2(Box T)^2 + S(x)T]",
            "m = (c^2/(2G)) r^2 k_loc",
            "E = (c^4/(2G)) r^2 k_loc",
        ),
        (
            "Provides an author-supplied EFT narrative and Newtonian matching argument.",
            "It does not identify a BHSM neutral propagation radius or physical neutral curvature value.",
        ),
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_legacy_curvature_artifacts(
    repository: str | Path | None = None,
) -> tuple[LegacyCurvatureArtifact, ...]:
    """Index bundled legacy sources using predeclared, auditable formula recognition."""

    root = repository_path(repository)
    rows = []
    for key, relative, title, formulas, notes in LEGACY_SOURCE_SPECS:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"legacy theory artifact missing: {relative}")
        rows.append(
            LegacyCurvatureArtifact(
                artifact_key=key,
                source_file=relative,
                source_document_title=title,
                recognized_formulas=formulas,
                candidate_status="AUTHOR_SUPPLIED_LEGACY_THEORY_ARTIFACT",
                use_allowed_for_theory=True,
                use_allowed_for_empirical_calibration=False,
                sha256=_sha256(path),
                notes=notes,
            )
        )
    return tuple(rows)

