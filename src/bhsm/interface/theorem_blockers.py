"""Artifact-traced closure attempts for unresolved collider-interface theorems."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

OPEN = "OPEN_EXACT_MISSING_THEOREM"
ALLOWED_CLOSURE_STATUSES = (
    OPEN,
    "OPEN_MISSING_ACTION_SOURCE",
    "OPEN_MISSING_FIELD_REPRESENTATION",
    "OPEN_MISSING_PHYSICAL_BASIS",
    "DERIVED_FROM_REPO_ARTIFACT",
    "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM",
    "PARTIAL_INTERFACE_CONVENTION_ONLY",
    "FORBIDDEN_TO_PROMOTE_WITHOUT_NEW_THEOREM",
)


@dataclass(frozen=True)
class TheoremBlocker:
    blocker_key: str
    display_name: str
    current_status: str
    required_theorem: str
    affected_registry_entries: tuple[str, ...]
    source_artifacts_checked: tuple[str, ...]
    missing_object: str
    claim_boundary: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("affected_registry_entries", "source_artifacts_checked", "notes"):
            payload[key] = list(payload[key])
        return payload


@dataclass(frozen=True)
class TheoremAttemptResult:
    blocker_key: str
    closure_attempted: bool
    closure_status: str
    closure_result: str
    missing_object: str | None
    source_artifacts_checked: tuple[str, ...]
    theorem_input_used: bool
    empirical_inputs_used: bool
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["source_artifacts_checked"] = list(self.source_artifacts_checked)
        return payload


@dataclass
class TheoremBlockerRegistry:
    blockers: dict[str, TheoremBlocker]

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_name": "BHSM Theorem Blocker Registry",
            "version": "0.2",
            "allowed_closure_statuses": list(ALLOWED_CLOSURE_STATUSES),
            "blockers": [self.blockers[key].to_dict() for key in sorted(self.blockers)],
        }


def default_theorem_blockers() -> TheoremBlockerRegistry:
    rows = (
        TheoremBlocker("X_ch", "Charged boundary-response interaction", "OPEN_MISSING_FIELD_REPRESENTATION",
                       "explicit X_ch production interaction theorem", ("charged_boundary_response_matrix",),
                       ("artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json", "artifacts/BHSM_interaction_theorem_closure_audit_v1_1.json", "artifacts/BHSM_x_ch_theorem_closure_attempt_v0_4.json", "artifacts/BHSM_x_ch_minimal_action_closure_v0_8.json"),
                       "action-derived X_ch field representation", "The boundary source matrix does not define the X_ch field."),
        TheoremBlocker("neutrino_basis_scale_dirac_majorana", "Neutrino basis, scale, and Dirac/Majorana convention", "OPEN_MISSING_PHYSICAL_BASIS",
                       "physical neutrino basis, dimensional scale, and Dirac/Majorana theorem", ("neutral_operator_kernel_BH",),
                       ("artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json", "artifacts/BHSM_interaction_theorem_closure_audit_v1_1.json", "artifacts/BHSM_neutrino_basis_scale_theorem_closure_attempt_v0_4.json", "artifacts/BHSM_neutrino_basis_scale_minimal_action_closure_v0_8.json"),
                       "map from neutral boundary channels to physical neutrino states", "The boundary kernel does not define the physical basis."),
        TheoremBlocker("cp_o_int", "Standalone CP O_int attachment", "OPEN_MISSING_ACTION_SOURCE",
                       "action-derived standalone CP O_int field/action theorem", ("cp_holonomy_phase_attachment",),
                       ("artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json", "artifacts/BHSM_interaction_theorem_closure_audit_v1_1.json", "artifacts/BHSM_cp_o_int_theorem_closure_attempt_v0_4.json", "artifacts/BHSM_cp_o_int_attachment_report_v0_5.json", "artifacts/BHSM_cp_o_int_field_action_report_v0_6.json", "artifacts/BHSM_cp_o_int_minimal_action_closure_v0_8.json"),
                       "action-derived CP O_int source with normalized coupling, measure, variation, and production rule", "The callable symbolic candidate does not supply an action source."),
    )
    return TheoremBlockerRegistry({row.blocker_key: row for row in rows})


def attempt_theorem_closure(
    blocker_key: str,
    repository_root: Path | None = None,
    theorem_input: Mapping[str, Any] | None = None,
) -> TheoremAttemptResult:
    registry = default_theorem_blockers()
    blocker = registry.blockers.get(blocker_key)
    if blocker is None:
        raise KeyError(blocker_key)
    root = repository_root or Path(__file__).resolve().parents[3]
    checked = tuple(path for path in blocker.source_artifacts_checked if (root / path).is_file())
    conditional = bool(
        theorem_input
        and theorem_input.get("author_supplied") is True
        and blocker_key in theorem_input.get("affected_blockers", [])
        and theorem_input.get("allowed_status_if_loaded") == "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM"
    )
    if conditional:
        return TheoremAttemptResult(blocker_key, True, "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM",
                                    "Author-supplied axiom loaded conditionally; production promotion remains unavailable.",
                                    blocker.missing_object, checked, True, False, blocker.claim_boundary)
    return TheoremAttemptResult(blocker_key, True, blocker.current_status,
                                "Repository artifacts record the attempted interface and exact missing theorem; no closure artifact is present.",
                                blocker.missing_object, checked, False, False, blocker.claim_boundary)


def attempt_all_theorem_closures(repository_root: Path | None = None) -> list[TheoremAttemptResult]:
    return [attempt_theorem_closure(key, repository_root) for key in sorted(default_theorem_blockers().blockers)]
