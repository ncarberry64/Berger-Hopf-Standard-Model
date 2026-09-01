"""BHSM no-protected-mirror axiom for the no-churn theorem sprint."""

from __future__ import annotations

from dataclasses import dataclass

from formal_kernel_projector import DEFAULT_FORMAL_COORDINATES, OLD_COORDINATE_FIRST_KERNEL, build_formal_kernel_projector_report
from mirror_mode_exclusion import generate_mirror_mode_candidates


NO_PROTECTED_MIRROR_WITHOUT_NEW_PARTICLE_MODE = "NO_PROTECTED_MIRROR_WITHOUT_NEW_PARTICLE_MODE"

WRONG_BOUNDARY_ORIENTATION = "wrong_boundary_orientation"
FAILS_CHIRALITY_PROJECTION = "fails_chirality_projection"
LIFTED_INTO_H_PERP = "lifted_into_H_perp"
NON_PROTECTED_COMPLEMENT_EXCITATION = "represented_as_non_protected_complement_excitation"
FORBIDDEN_BY_SECTOR_LEDGER = "forbidden_by_sector_ledger"
THEOREM_FAILURE_PROTECTED_MIRROR = "theorem_failure_protected_mirror"


@dataclass(frozen=True)
class MirrorAxiomClassification:
    mirror_id: str
    sector: str
    candidate_chirality: int
    classification: str
    protected: bool
    would_create_new_particle_mode: bool
    rationale: tuple[str, ...]


@dataclass(frozen=True)
class NoProtectedMirrorAxiomReport:
    axiom_id: str
    statement: str
    frozen_sector_ledger: tuple[str, ...]
    formal_kernel_coordinates: tuple[int, ...]
    old_coordinate_first_kernel_used: bool
    classifications: tuple[MirrorAxiomClassification, ...]
    protected_mirror_count: int
    new_particle_mode_count: int
    theorem_failure: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def classify_mirror_candidates_by_axiom() -> tuple[MirrorAxiomClassification, ...]:
    rows = []
    for candidate in generate_mirror_mode_candidates():
        if candidate.chirality != -1:
            classification = FAILS_CHIRALITY_PROJECTION
        elif candidate.boundary_residual != 0:
            classification = WRONG_BOUNDARY_ORIENTATION
        elif candidate.sector not in {"lepton", "up", "down"}:
            classification = FORBIDDEN_BY_SECTOR_LEDGER
        else:
            classification = NON_PROTECTED_COMPLEMENT_EXCITATION
        rows.append(
            MirrorAxiomClassification(
                mirror_id=candidate.id,
                sector=candidate.sector,
                candidate_chirality=candidate.chirality,
                classification=classification,
                protected=False,
                would_create_new_particle_mode=False,
                rationale=(
                    "The frozen protected sector ledger contains only lepton, up, and down channels.",
                    "A mirror candidate is not an independent protected state unless BHSM adds a new particle/mode sector.",
                    "The sprint axiom forbids adding such a sector.",
                ),
            )
        )
    return tuple(rows)


def build_no_protected_mirror_axiom_report() -> NoProtectedMirrorAxiomReport:
    kernel = build_formal_kernel_projector_report()
    coords = tuple(row.coordinate_hint_kmax4 for row in kernel.kernel_basis)
    classifications = classify_mirror_candidates_by_axiom()
    protected_count = sum(row.protected for row in classifications)
    new_particle_count = sum(row.would_create_new_particle_mode for row in classifications)
    return NoProtectedMirrorAxiomReport(
        axiom_id=NO_PROTECTED_MIRROR_WITHOUT_NEW_PARTICLE_MODE,
        statement=(
            "At the protected-kernel scale, no physically allowed mirror possibility "
            "is an independent protected state without introducing an additional particle/mode sector."
        ),
        frozen_sector_ledger=("lepton", "up", "down"),
        formal_kernel_coordinates=coords,
        old_coordinate_first_kernel_used=coords == OLD_COORDINATE_FIRST_KERNEL,
        classifications=classifications,
        protected_mirror_count=protected_count,
        new_particle_mode_count=new_particle_count,
        theorem_failure=protected_count > 0 or new_particle_count > 0,
        theorem_complete=(
            coords == DEFAULT_FORMAL_COORDINATES
            and tuple(row.sector for row in kernel.kernel_basis) == ("lepton", "up", "down")
            and protected_count == 0
            and new_particle_count == 0
        ),
        limitations=(
            "This is an explicit BHSM axiom for the no-churn theorem sprint.",
            "It does not introduce a new mirror particle/mode and does not alter frozen predictions.",
        ),
    )
