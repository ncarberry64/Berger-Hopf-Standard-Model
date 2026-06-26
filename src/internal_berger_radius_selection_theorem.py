from __future__ import annotations

from dataclasses import asdict, dataclass
from math import pi, sqrt
from pathlib import Path
from typing import Dict, Iterable


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
AUTHOR_SELECTION = "AUTHOR_SUPPLIED_BHSM_OVERLAP_NORMALIZATION"
THEOREM_STATUS = "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM"
RADIUS_STATUS = "DERIVED_CONDITIONAL"
FORK_STATUS = "RESOLVED_BY_AUTHOR_AXIOM"

SELECTED_BY_AUTHOR_AXIOM = "SELECTED_BY_AUTHOR_AXIOM"
REJECTED_BY_AUTHOR_NORMALIZATION = "REJECTED_BY_AUTHOR_NORMALIZATION"
NOT_PRIMARY_ROUTE = "NOT_PRIMARY_ROUTE"
OPEN_LOCALIZABLE = "OPEN_LOCALIZABLE"
BLOCKED_BY_MISSING_OBJECTS = "BLOCKED_BY_MISSING_OBJECTS"


@dataclass(frozen=True)
class AuthorRadiusAxiom:
    status: str
    statement: str
    S_formula: str
    Lambda_squared_formula: str
    r_squared_formula: str
    r_formula: str
    source_trace: tuple[str, ...]
    semantic_equivalence: str
    empirical_inputs_used: bool


@dataclass(frozen=True)
class RouteVerdict:
    route_id: str
    route_name: str
    verdict: str
    selected: bool
    reason: str
    source_trace: tuple[str, ...]


def _root(repo_root: Path | None = None) -> Path:
    return repo_root or Path(__file__).resolve().parents[1]


def _existing_paths(root: Path, paths: Iterable[str]) -> tuple[str, ...]:
    resolved: list[str] = []
    for item in paths:
        path = root / item
        resolved.append(str(path) if path.exists() else item)
    return tuple(resolved)


def _guardrails() -> Dict[str, object]:
    return {
        "public_status_before_gate": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "observed_masses_used": False,
        "observed_Higgs_used": False,
        "observed_gauge_values_used": False,
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
        "radius_selected_by": AUTHOR_SELECTION,
    }


def _frozen_trace(repo_root: Path | None = None) -> tuple[str, ...]:
    root = _root(repo_root)
    return _existing_paths(root, ("artifacts/frozen_constants_v2.json", "src/bhsm_v1.py"))


def author_supplied_overlap_radius_axiom(repo_root: Path | None = None) -> Dict[str, object]:
    axiom = AuthorRadiusAxiom(
        status=THEOREM_STATUS,
        statement=(
            "The internal/profile Berger radius is selected by the author-supplied BHSM "
            "overlap-scale normalization: r_internal_profile^2 = Lambda_squared = S = 1/(4*pi)."
        ),
        S_formula="S = 1/(4*pi)",
        Lambda_squared_formula="Lambda_squared = 1/(4*pi)",
        r_squared_formula="r_internal_profile^2 = S = Lambda_squared = 1/(4*pi)",
        r_formula="r_internal_profile = sqrt(S) = 1/sqrt(4*pi)",
        source_trace=_frozen_trace(repo_root),
        semantic_equivalence=(
            "Lambda-radius and overlap-radius are equivalent because the author-supplied "
            "BHSM normalization identifies both with the same frozen overlap-scale object, "
            "not merely because their numeric strings match."
        ),
        empirical_inputs_used=False,
    )
    return {**_guardrails(), **asdict(axiom)}


def validate_lambda_squared_equals_overlap_width(repo_root: Path | None = None) -> Dict[str, object]:
    return {
        **_guardrails(),
        "S_formula": "1/(4*pi)",
        "Lambda_squared_formula": "1/(4*pi)",
        "S_value": 1.0 / (4.0 * pi),
        "Lambda_squared_value": 1.0 / (4.0 * pi),
        "equal": True,
        "source_trace": _frozen_trace(repo_root),
        "semantic_equivalence": (
            "The equality is treated as the author-supplied overlap-scale normalization "
            "used by BHSM, not as a post-hoc numerical coincidence."
        ),
    }


def derive_internal_profile_radius_from_overlap(repo_root: Path | None = None) -> Dict[str, object]:
    value = 1.0 / sqrt(4.0 * pi)
    return {
        **_guardrails(),
        "status": RADIUS_STATUS,
        "derived": True,
        "r_internal_profile_squared_formula": "S = Lambda_squared = 1/(4*pi)",
        "r_internal_profile_squared": 1.0 / (4.0 * pi),
        "r_internal_profile_formula": "1/sqrt(4*pi)",
        "r_internal_profile": value,
        "source_trace": _frozen_trace(repo_root),
        "cosmological_R_H_used": False,
        "empirical_inputs_used": False,
    }


def route_verdicts(repo_root: Path | None = None) -> list[RouteVerdict]:
    trace = _frozen_trace(repo_root)
    root = _root(repo_root)
    symbolic_trace = _existing_paths(
        root,
        (
            "artifacts/internal_radius_normalization_forks_v1.json",
            "theory/berger_base_action_coupling_normalization.md",
            "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
        ),
    )
    return [
        RouteVerdict(
            "unit_internal_radius",
            "Unit internal Berger radius",
            REJECTED_BY_AUTHOR_NORMALIZATION,
            False,
            "Author normalization fixes r_internal_profile^2=1/(4*pi), not r=1.",
            symbolic_trace,
        ),
        RouteVerdict(
            "lambda_radius",
            "Lambda radius",
            SELECTED_BY_AUTHOR_AXIOM,
            True,
            "Lambda_squared is semantically identified with the frozen overlap-scale normalization.",
            trace,
        ),
        RouteVerdict(
            "overlap_width_radius",
            "Overlap width radius",
            SELECTED_BY_AUTHOR_AXIOM,
            True,
            "S is the frozen overlap width and is semantically identified with r_internal_profile^2.",
            trace,
        ),
        RouteVerdict(
            "berger_volume_normalization",
            "Berger volume normalization",
            NOT_PRIMARY_ROUTE,
            False,
            "Volume normalization remains useful for measure work but does not select r in this author theorem.",
            symbolic_trace,
        ),
        RouteVerdict(
            "collar_depth_matching",
            "Collar-depth matching",
            NOT_PRIMARY_ROUTE,
            False,
            "Collar-depth matching remains a separate geometry problem and is not the primary radius selection route.",
            symbolic_trace,
        ),
    ]


def close_internal_radius_selection(repo_root: Path | None = None) -> Dict[str, object]:
    return {
        **_guardrails(),
        "internal_berger_radius_selection_theorem": THEOREM_STATUS,
        "r_internal_profile_status": RADIUS_STATUS,
        "radius_normalization_fork": FORK_STATUS,
        "selected_route": "Lambda/overlap radius equivalence",
        "route_verdicts": [asdict(row) for row in route_verdicts(repo_root)],
        "radius": derive_internal_profile_radius_from_overlap(repo_root),
        "axiom": author_supplied_overlap_radius_axiom(repo_root),
    }


def propagate_radius_to_tau_sigma_obstruction_chain(repo_root: Path | None = None) -> Dict[str, object]:
    radius = derive_internal_profile_radius_from_overlap(repo_root)
    return {
        **_guardrails(),
        "r_internal_profile_status": RADIUS_STATUS,
        "r_internal_profile": radius["r_internal_profile"],
        "r_internal_profile_squared": radius["r_internal_profile_squared"],
        "Z_H_status": OPEN_LOCALIZABLE,
        "kappa_H_status": OPEN_LOCALIZABLE,
        "sigma_from_boundary_geometry": OPEN_LOCALIZABLE,
        "tau_from_boundary_geometry": OPEN_LOCALIZABLE,
        "sigma_derived": False,
        "tau_derived": False,
        "sigma_formula": "sigma = (1/2) sqrt(kappa_H / Z_H)",
        "tau_formula_before_substitution": "tau = sqrt(Z_H/kappa_H)/(2*r_internal_profile^2)",
        "tau_symbolic_after_radius_substitution": "tau(Z_H,kappa_H) = 2*pi*sqrt(Z_H/kappa_H)",
        "tau_numeric_computed": False,
        "charged_outputs_at_tau_exported": False,
        "remaining_blockers": ("Z_H", "kappa_H"),
    }


def build_author_radius_selection_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    closure = close_internal_radius_selection(repo_root)
    tau = propagate_radius_to_tau_sigma_obstruction_chain(repo_root)
    return {
        **_guardrails(),
        "artifact": "internal_berger_radius_selection_theorem_v1",
        "targeted_followup_to": "PR #49 internal radius fork",
        "author_radius_axiom_encoded": True,
        "internal_berger_radius_selection_theorem": THEOREM_STATUS,
        "r_internal_profile_status": RADIUS_STATUS,
        "r_internal_profile_value": closure["radius"]["r_internal_profile"],
        "r_internal_profile_squared": closure["radius"]["r_internal_profile_squared"],
        "radius_normalization_fork": FORK_STATUS,
        "selected_route": closure["selected_route"],
        "route_verdicts": closure["route_verdicts"],
        "lambda_overlap_equivalence": validate_lambda_squared_equals_overlap_width(repo_root),
        "tau_sigma_obstruction_chain": tau,
        "Z_H_status": tau["Z_H_status"],
        "kappa_H_status": tau["kappa_H_status"],
        "sigma_derived": tau["sigma_derived"],
        "tau_derived": tau["tau_derived"],
        "charged_outputs_at_tau_exported": tau["charged_outputs_at_tau_exported"],
        "public_status_after_gate": PUBLIC_STATUS,
    }
