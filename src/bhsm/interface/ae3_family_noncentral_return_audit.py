"""Finite provenance audit for an AE3 family-noncentral mass return."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ACTION_VERSION = "BHSM-AE-3.0.0"
CLASSIFICATION = "AE3_FAMILY_NONCENTRAL_RETURNED_MASS_PROVENANCE_AUDIT"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    action_owned: bool
    same_current_C2_domain: bool
    family_noncentral: bool
    three_distinct_values_possible: bool
    no_free_or_underived_family_input: bool
    noncircular_source: bool
    status: str

    @property
    def admissible(self) -> bool:
        return all(
            (
                self.action_owned,
                self.same_current_C2_domain,
                self.family_noncentral,
                self.three_distinct_values_possible,
                self.no_free_or_underived_family_input,
                self.noncircular_source,
            )
        )


def candidates() -> tuple[Candidate, ...]:
    """Return every retained structural family-return candidate class."""

    return (
        Candidate(
            "CURRENT_AE3_C2_LOCAL_RESET_ENCLOSURE_AND_PRODUCT_DIRAC_COMPOSITION",
            True,
            True,
            False,
            False,
            True,
            True,
            "EXCLUDED_BY_EXACT_A_NONFAMILY_TENSOR_I3_FACTORIZATION",
        ),
        Candidate(
            "V6_3_TRIALITY_BERGER_FAMILY_MASS_OPERATOR",
            False,
            False,
            True,
            True,
            False,
            True,
            "CONDITIONAL_ARCHITECTURE_WITH_UNDERIVED_MASS_ENTRIES",
        ),
        Candidate(
            "V14_38_CANONICAL_C3_ATTACHMENT_PROJECTION",
            False,
            False,
            True,
            False,
            True,
            True,
            "DERIVED_HISTORICAL_PROJECTION_PRESERVES_TWOFOLD_DEGENERACY",
        ),
        Candidate(
            "V6_10_OPTIONAL_C3_COMMUTANT_JUNCTION_BILINEAR",
            False,
            False,
            True,
            True,
            False,
            True,
            "ALGEBRAICALLY_SUFFICIENT_BUT_ABSENT_WITH_UNFIXED_COEFFICIENTS",
        ),
        Candidate(
            "V14_40_OFFDIAGONAL_FAMILY_COHERENCE_CHAIN",
            False,
            False,
            True,
            True,
            True,
            False,
            "REJECTED_CIRCULAR_UNOWNED_INITIAL_COHERENCE",
        ),
        Candidate(
            "V14_52_LAMBDA85_TANGENT_REDUCED_RESPONSE",
            True,
            False,
            False,
            False,
            True,
            True,
            "FAMILY_BLIND_CONSTRAINT_CANNOT_GENERATE_RELATIVE_BRIDGES",
        ),
        Candidate(
            "V14_79_DYNAMIC_STRATIFIED_BAND_OR_CYCLE",
            False,
            False,
            True,
            True,
            True,
            True,
            "STRUCTURAL_ORIGIN_ONLY_ACTION_SELECTED_BANDS_AND_SCALES_OPEN",
        ),
        Candidate(
            "V15_56_INTRINSIC_M4_YUKAWA_WILSON_OPERATORS",
            False,
            False,
            True,
            True,
            False,
            True,
            "FOUNDATIONAL_OPERATORS_NOT_DERIVED_FROM_THE_PARENT_ACTION",
        ),
        Candidate(
            "V15_85_TO_87_COMMON_ACTION_CYCLE_PUSHFORWARD",
            True,
            False,
            False,
            False,
            True,
            True,
            "NONZERO_VERTEX_IS_FAMILY_CENTRAL_AND_THE_BACKGROUND_MASS_IS_ZERO",
        ),
    )


def audit_certificate() -> dict[str, Any]:
    """Evaluate the retained candidates against the current interface."""

    rows = []
    for candidate in candidates():
        row = asdict(candidate)
        row["admissible"] = candidate.admissible
        rows.append(row)
    admissible = [row for row in rows if row["admissible"]]
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "candidate_rows": rows,
        "candidate_count": len(rows),
        "admissible_count": len(admissible),
        "selected_candidate": (
            admissible[0]["candidate_id"] if len(admissible) == 1 else None
        ),
        "historical_particle_and_family_projectors_reused": True,
        "particle_spectrum_rebuilt": False,
        "current_result": "NO_RETAINED_ACTION_OWNED_NONCENTRAL_RETURN_FOUND",
        "certificate_passed": len(admissible) == 0,
    }


def irreducible_family_decision_surface() -> dict[str, Any]:
    """Return the still-unselected physical action/domain alternatives."""

    return {
        "decision_classes": [
            {
                "decision": "DERIVE_ACTION_SELECTED_C3_BREAKING_RETURN",
                "required_object": (
                    "same_current_C2_projector_local_action_density_and_its_"
                    "three_nonfitted_return_eigenvalues"
                ),
            },
            {
                "decision": "DERIVE_TRIALITY_CHANGING_RETURN_INTERTWINER",
                "required_object": (
                    "same_current_C2_parent_action_term_domain_and_transport_"
                    "of_the_manifestation_map_to_its_mass_basis"
                ),
            },
            {
                "decision": "RETAIN_PRESENT_AE3_FAMILY_CENTRAL_ACTION",
                "consequence": (
                    "family_modes_remain_valid_particle_fibers_but_no_three_"
                    "family_mass_hierarchy_is_derived"
                ),
            },
        ],
        "choice_made_here": False,
        "family_mass_hierarchy_derived": False,
        "CKM_PMNS_derived": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "Candidate",
    "audit_certificate",
    "candidates",
    "irreducible_family_decision_surface",
]
