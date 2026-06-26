from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

DERIVED_FIXED = "DERIVED_FIXED"
DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
STRUCTURALLY_SUPPORTED_CANDIDATE = "STRUCTURALLY_SUPPORTED_CANDIDATE"
NORMALIZATION_FORK_OPEN = "NORMALIZATION_FORK_OPEN"
BLOCKED_BY_MISSING_NORMALIZATION_THEOREM = "BLOCKED_BY_MISSING_NORMALIZATION_THEOREM"
REJECTED_BY_REPO_CONVENTIONS = "REJECTED_BY_REPO_CONVENTIONS"

MISSING_SELECTION_THEOREM = "INTERNAL_BERGER_RADIUS_SELECTION_THEOREM"


@dataclass(frozen=True)
class RadiusSource:
    object_id: str
    symbol: str
    classification: str
    status: str
    value: float | str | None
    source_trace: tuple[str, ...]
    used_as_internal_profile_r: bool
    notes: str


@dataclass(frozen=True)
class RadiusNormalizationFork:
    route_id: str
    route_name: str
    candidate_value: float | str | None
    candidate_formula: str | None
    status: str
    source_trace: tuple[str, ...]
    repo_support: str
    rejection_or_blocker: str | None
    selected: bool
    notes: str


@dataclass(frozen=True)
class BergerMeasureDomain:
    status: str
    metric_form: str
    volume_form: str
    domain: str
    source_trace: tuple[str, ...]
    missing_theorem: str
    notes: str


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
    }


def collect_radius_measure_sources(repo_root: Path | None = None) -> Dict[str, RadiusSource]:
    root = _root(repo_root)
    return {
        "r_internal_profile": RadiusSource(
            object_id="r_internal_profile",
            symbol="r",
            classification="dimensionless internal/profile Berger radius",
            status=NORMALIZATION_FORK_OPEN,
            value=None,
            source_trace=_existing_paths(
                root,
                (
                    "artifacts/internal_profile_radius_normalization_v1.json",
                    "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
                    "theory/berger_base_action_coupling_normalization.md",
                ),
            ),
            used_as_internal_profile_r=True,
            notes="The internal radius is the target of this fork audit; no single convention is selected by repo axioms.",
        ),
        "R_H_cosmological": RadiusSource(
            object_id="R_H_cosmological",
            symbol="R_H_Gpc",
            classification="physical/cosmological hyperspherical radius",
            status=REJECTED_BY_REPO_CONVENTIONS,
            value=24.0,
            source_trace=_existing_paths(root, ("artifacts/hyperspherical_cosmology_desi_pipeline_v1.json",)),
            used_as_internal_profile_r=False,
            notes="Cosmological scale is not an internal/profile Berger radius.",
        ),
        "rho_star_collar_depth": RadiusSource(
            object_id="rho_star_collar_depth",
            symbol="rho_*",
            classification="collar normal-depth coordinate",
            status=STRUCTURALLY_SUPPORTED_CANDIDATE,
            value=None,
            source_trace=_existing_paths(
                root,
                (
                    "theory/theorem_discharge_normal_coupling_collar_convention.md",
                    "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
                    "theory/theorem_discharge_boundary_embedding_shape_operator.md",
                ),
            ),
            used_as_internal_profile_r=False,
            notes="Collar depth has conditional geometric formulas but no matching theorem to r_internal_profile.",
        ),
        "Lambda_BH_matching_scale": RadiusSource(
            object_id="Lambda_BH_matching_scale",
            symbol="Lambda_BH / mu_ref",
            classification="common-scale transport matching scale",
            status=REJECTED_BY_REPO_CONVENTIONS,
            value=None,
            source_trace=_existing_paths(root, ("artifacts/common_scale_charged_transport_interface_v1.json",)),
            used_as_internal_profile_r=False,
            notes="Common-scale transport object, not a profile-domain radius.",
        ),
        "Lambda_squared_overlap": RadiusSource(
            object_id="Lambda_squared_overlap",
            symbol="Lambda_squared",
            classification="heat/spectral cutoff",
            status=STRUCTURALLY_SUPPORTED_CANDIDATE,
            value="1/(4*pi)",
            source_trace=_existing_paths(root, ("artifacts/frozen_constants_v2.json",)),
            used_as_internal_profile_r=False,
            notes="Fixed cutoff value exists, but the repo lacks a Lambda-to-radius convention.",
        ),
        "S_overlap_width": RadiusSource(
            object_id="S_overlap_width",
            symbol="S",
            classification="overlap/stochastic width",
            status=STRUCTURALLY_SUPPORTED_CANDIDATE,
            value="1/(4*pi)",
            source_trace=_existing_paths(root, ("src/bhsm_v1.py", "artifacts/frozen_constants_v2.json")),
            used_as_internal_profile_r=False,
            notes="Frozen width exists, but the repo lacks an overlap-width-to-radius convention.",
        ),
    }


def classify_radius_symbols(repo_root: Path | None = None) -> list[Dict[str, object]]:
    return [asdict(source) for source in collect_radius_measure_sources(repo_root).values()]


def derive_unit_radius_if_repo_implies(repo_root: Path | None = None) -> RadiusNormalizationFork:
    root = _root(repo_root)
    return RadiusNormalizationFork(
        route_id="unit_internal_radius",
        route_name="Unit internal Berger radius",
        candidate_value=1.0,
        candidate_formula="r_internal_profile = 1",
        status=STRUCTURALLY_SUPPORTED_CANDIDATE,
        source_trace=_existing_paths(
            root,
            (
                "theory/hopf_fiber_connection_Aq.md",
                "theory/explicit_hopf_berger_boundary_oneforms.md",
                "theory/berger_base_action_coupling_normalization.md",
            ),
        ),
        repo_support=(
            "The repo uses normalized Hopf/contact forms and symbolic dimensionless geometry, "
            "but it does not state a unit internal radius convention."
        ),
        rejection_or_blocker=MISSING_SELECTION_THEOREM,
        selected=False,
        notes="Supported as a candidate convention only; not promoted to DERIVED_CONDITIONAL.",
    )


def derive_lambda_radius_if_repo_implies(repo_root: Path | None = None) -> RadiusNormalizationFork:
    root = _root(repo_root)
    return RadiusNormalizationFork(
        route_id="lambda_radius",
        route_name="Lambda radius",
        candidate_value="sqrt(1/(4*pi))",
        candidate_formula="r_internal_profile^2 = Lambda_squared = 1/(4*pi)",
        status=STRUCTURALLY_SUPPORTED_CANDIDATE,
        source_trace=_existing_paths(root, ("artifacts/frozen_constants_v2.json",)),
        repo_support="Lambda_squared is frozen as 1/(4*pi), but appears as a heat/spectral cutoff.",
        rejection_or_blocker=MISSING_SELECTION_THEOREM,
        selected=False,
        notes="Candidate only because no Laplacian/profile convention identifies Lambda_squared with radius squared.",
    )


def derive_overlap_radius_if_repo_implies(repo_root: Path | None = None) -> RadiusNormalizationFork:
    root = _root(repo_root)
    return RadiusNormalizationFork(
        route_id="overlap_width_radius",
        route_name="Overlap width radius",
        candidate_value="sqrt(1/(4*pi))",
        candidate_formula="r_internal_profile^2 = S = 1/(4*pi)",
        status=STRUCTURALLY_SUPPORTED_CANDIDATE,
        source_trace=_existing_paths(root, ("src/bhsm_v1.py", "artifacts/frozen_constants_v2.json")),
        repo_support="S is frozen as 1/(4*pi) in the overlap/stochastic width convention.",
        rejection_or_blocker=MISSING_SELECTION_THEOREM,
        selected=False,
        notes="Candidate only because no theorem identifies overlap width with profile area/radius squared.",
    )


def derive_berger_volume_measure_if_possible(repo_root: Path | None = None) -> RadiusNormalizationFork:
    root = _root(repo_root)
    return RadiusNormalizationFork(
        route_id="berger_volume_normalization",
        route_name="Berger volume normalization",
        candidate_value=None,
        candidate_formula=(
            "For g_Berger = r_base^2(sigma_1^2+sigma_2^2)+r_fiber^2 sigma_3^2, "
            "dmu_Berger depends on the sigma_i/Maurer-Cartan convention and chosen total volume."
        ),
        status=NORMALIZATION_FORK_OPEN,
        source_trace=_existing_paths(
            root,
            (
                "src/bhsm_berger_base_action_coupling.py",
                "theory/berger_base_action_coupling_normalization.md",
                "src/bhsm_hopf_berger_oneforms.py",
                "theory/explicit_hopf_berger_boundary_oneforms.md",
            ),
        ),
        repo_support="Symbolic metric and one-forms exist, but no total internal volume or sigma_i volume convention is selected.",
        rejection_or_blocker=MISSING_SELECTION_THEOREM,
        selected=False,
        notes="Does not assume SU(2), unit S^3, Hopf-coordinate, or normalized Maurer-Cartan volume coefficients.",
    )


def derive_collar_matched_radius_if_possible(repo_root: Path | None = None) -> RadiusNormalizationFork:
    root = _root(repo_root)
    return RadiusNormalizationFork(
        route_id="collar_depth_matching",
        route_name="Collar-depth matching",
        candidate_value=None,
        candidate_formula="r_internal_profile = F(rho_*, J(Y,rho), S(Y), K_collar)",
        status=NORMALIZATION_FORK_OPEN,
        source_trace=_existing_paths(
            root,
            (
                "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
                "theory/theorem_discharge_boundary_embedding_shape_operator.md",
                "theory/theorem_discharge_complete_scalar_topographic_collar_action.md",
                "docs/open_blockers_backlog.md",
            ),
        ),
        repo_support="Collar Jacobian formulas exist conditionally, but collar depth/domain and shape-operator values are open.",
        rejection_or_blocker=MISSING_SELECTION_THEOREM,
        selected=False,
        notes="Candidate route only; no boundary matching condition equates collar depth to the internal profile radius.",
    )


def build_radius_normalization_forks(repo_root: Path | None = None) -> list[RadiusNormalizationFork]:
    return [
        derive_unit_radius_if_repo_implies(repo_root),
        derive_lambda_radius_if_repo_implies(repo_root),
        derive_overlap_radius_if_repo_implies(repo_root),
        derive_berger_volume_measure_if_possible(repo_root),
        derive_collar_matched_radius_if_possible(repo_root),
    ]


def select_unique_radius_normalization_if_possible(repo_root: Path | None = None) -> Dict[str, object]:
    forks = build_radius_normalization_forks(repo_root)
    selected = [fork for fork in forks if fork.selected and fork.status in (DERIVED_FIXED, DERIVED_CONDITIONAL)]
    if len(selected) == 1:
        fork = selected[0]
        return {
            **_guardrails(),
            "status": DERIVED_CONDITIONAL,
            "selected_route": fork.route_id,
            "r_internal_profile": fork.candidate_value,
            "missing_theorem": None,
            "forks": [asdict(item) for item in forks],
        }
    if any(fork.status in (STRUCTURALLY_SUPPORTED_CANDIDATE, NORMALIZATION_FORK_OPEN) for fork in forks):
        return {
            **_guardrails(),
            "status": NORMALIZATION_FORK_OPEN,
            "selected_route": None,
            "r_internal_profile": None,
            "missing_theorem": MISSING_SELECTION_THEOREM,
            "requires_one_of": (
                "unit-radius convention theorem",
                "Lambda-to-radius theorem",
                "overlap-width-to-radius theorem",
                "Berger-volume normalization theorem",
                "collar-depth matching theorem",
            ),
            "forks": [asdict(item) for item in forks],
        }
    return {
        **_guardrails(),
        "status": BLOCKED_BY_MISSING_NORMALIZATION_THEOREM,
        "selected_route": None,
        "r_internal_profile": None,
        "missing_theorem": MISSING_SELECTION_THEOREM,
        "forks": [asdict(item) for item in forks],
    }


def build_berger_measure_domain_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    root = _root(repo_root)
    selection = select_unique_radius_normalization_if_possible(repo_root)
    measure = BergerMeasureDomain(
        status=NORMALIZATION_FORK_OPEN,
        metric_form="g_Berger = r_base^2 (sigma_1^2 + sigma_2^2) + r_fiber^2 sigma_3^2",
        volume_form="dmu_Berger = sqrt(det g_Berger) dtheta dphi dpsi, coefficient depends on sigma_i convention",
        domain="internal Berger/Hopf profile domain B_int, not numerically selected",
        source_trace=_existing_paths(
            root,
            (
                "theory/berger_base_action_coupling_normalization.md",
                "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
                "theory/theorem_discharge_scalar_topographic_level_set_boundary_embedding.md",
            ),
        ),
        missing_theorem=MISSING_SELECTION_THEOREM,
        notes=(
            "The metric and domain are localized but cannot produce a normalized measure until "
            "the radius/volume convention is selected."
        ),
    )
    return {
        **_guardrails(),
        "artifact": "berger_measure_domain_v1",
        "berger_measure_domain": asdict(measure),
        "selection": selection,
        "dmu_Berger_domain_status": measure.status,
        "profile_normalization_supported": False,
    }


def build_radius_measure_closure_or_obstruction_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_radius_measure_sources(repo_root)
    selection = select_unique_radius_normalization_if_possible(repo_root)
    measure = build_berger_measure_domain_artifact(repo_root)
    closes = selection["status"] == DERIVED_CONDITIONAL and selection["r_internal_profile"] is not None
    return {
        **_guardrails(),
        "artifact": "berger_radius_measure_normalization_v1",
        "targeted_followup_to": "PR #48 first blocker: r_internal_profile",
        "radius_symbols": [asdict(source) for source in sources.values()],
        "radius_normalization_forks": selection["forks"],
        "selected_route": selection["selected_route"],
        "r_internal_profile_status": selection["status"],
        "r_internal_profile_value": selection["r_internal_profile"],
        "dmu_Berger_domain_status": measure["dmu_Berger_domain_status"],
        "missing_theorem": selection["missing_theorem"],
        "requires_one_of": selection.get("requires_one_of", ()),
        "berger_measure_domain": measure["berger_measure_domain"],
        "Z_H_updated": False,
        "sigma_derived": False,
        "tau_derived": False,
        "charged_outputs_at_tau_exported": False,
        "public_status_after_gate": PUBLIC_STATUS,
        "obstruction": (
            None
            if closes
            else f"r_internal_profile remains {selection['status']} pending {MISSING_SELECTION_THEOREM}."
        ),
    }
