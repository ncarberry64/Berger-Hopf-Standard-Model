from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from pathlib import Path
from typing import Dict, Iterable, Mapping


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

DERIVED_FIXED = "DERIVED_FIXED"
DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH = "OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH"
BLOCKED_BY_MISSING_OBJECT = "BLOCKED_BY_MISSING_OBJECT"
BLOCKED_BY_MISSING_OBJECTS = "BLOCKED_BY_MISSING_OBJECTS"
REJECTED_AS_UNSUPPORTED = "REJECTED_AS_UNSUPPORTED"
OPEN_LOCALIZABLE = "OPEN_LOCALIZABLE"

ALLOWED_CLOSURE_STATUSES = {
    DERIVED_FIXED,
    DERIVED_CONDITIONAL,
    OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
    BLOCKED_BY_MISSING_OBJECT,
    REJECTED_AS_UNSUPPORTED,
}


@dataclass(frozen=True)
class ScaleSource:
    name: str
    status: str
    value: float | None
    formula: str | None
    source_trace: tuple[str, ...]
    classification: str
    missing_objects: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class RadiusSymbol:
    symbol: str
    classification: str
    profile_radius_candidate: bool
    value: float | str | None
    source_trace: tuple[str, ...]
    status: str
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


def _source_to_dict(source: ScaleSource) -> Dict[str, object]:
    return asdict(source)


def collect_boundary_profile_scale_sources(repo_root: Path | None = None) -> Dict[str, ScaleSource]:
    """Return the exact localized source/obstruction objects for kappa_H, Z_H, and r."""
    return {
        "r": classify_r_source(repo_root),
        "Z_H": classify_Z_H_source(repo_root),
        "kappa_H": classify_kappa_H_source(repo_root),
    }


def disambiguate_radius_symbols(repo_root: Path | None = None) -> list[RadiusSymbol]:
    root = _root(repo_root)
    return [
        RadiusSymbol(
            symbol="r",
            classification="dimensionless internal/profile Berger radius required by tau=1/(4 sigma r^2)",
            profile_radius_candidate=True,
            value=None,
            source_trace=_existing_paths(
                root,
                (
                    "artifacts/tau_sigma_boundary_derivation_closure_or_obstruction_v1.json",
                    "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
                ),
            ),
            status=BLOCKED_BY_MISSING_OBJECT,
            notes=(
                "The symbol is required by the tau/sigma gate, but no repo-derived value or "
                "radius-normalization theorem fixes it."
            ),
        ),
        RadiusSymbol(
            symbol="R_H_Gpc",
            classification="physical/cosmological hyperspherical scale",
            profile_radius_candidate=False,
            value=24.0,
            source_trace=_existing_paths(root, ("artifacts/hyperspherical_cosmology_desi_pipeline_v1.json",)),
            status=REJECTED_AS_UNSUPPORTED,
            notes="Cosmological scaffold radius; not the internal Berger/profile radius used by tau.",
        ),
        RadiusSymbol(
            symbol="Lambda_squared",
            classification="spectral heat cutoff scale",
            profile_radius_candidate=False,
            value="1/(4*pi)",
            source_trace=_existing_paths(root, ("artifacts/frozen_constants_v2.json",)),
            status=REJECTED_AS_UNSUPPORTED,
            notes="Heat/spectral cutoff notation, not a geometric radius for tau.",
        ),
        RadiusSymbol(
            symbol="S",
            classification="universal overlap/stochastic width constant",
            profile_radius_candidate=False,
            value="1/(4*pi)",
            source_trace=_existing_paths(root, ("src/bhsm_v1.py", "artifacts/frozen_constants_v2.json")),
            status=REJECTED_AS_UNSUPPORTED,
            notes="Frozen overlap width constant; not the internal profile radius r.",
        ),
        RadiusSymbol(
            symbol="rho / collar depth",
            classification="collar normal coordinate",
            profile_radius_candidate=False,
            value=None,
            source_trace=_existing_paths(
                root,
                (
                    "theory/theorem_discharge_scalar_topographic_level_set_boundary_embedding.md",
                    "docs/open_blockers_backlog.md",
                ),
            ),
            status=OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            notes="Collar coordinate enters J(Y,rho); it is not an evaluated internal radius.",
        ),
        RadiusSymbol(
            symbol="Lambda_BH / mu_ref",
            classification="common-scale transport/matching scale",
            profile_radius_candidate=False,
            value=None,
            source_trace=_existing_paths(root, ("artifacts/common_scale_charged_transport_interface_v1.json",)),
            status=BLOCKED_BY_MISSING_OBJECT,
            notes="Common-scale transport placeholders; not the tau profile radius.",
        ),
    ]


def classify_r_source(repo_root: Path | None = None) -> ScaleSource:
    root = _root(repo_root)
    return ScaleSource(
        name="r",
        status=BLOCKED_BY_MISSING_OBJECT,
        value=None,
        formula="tau = 1 / (4 sigma r^2)",
        source_trace=_existing_paths(
            root,
            (
                "artifacts/tau_sigma_boundary_derivation_closure_or_obstruction_v1.json",
                "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
            ),
        ),
        classification="dimensionless internal/profile Berger radius",
        missing_objects=("internal/profile Berger radius normalization theorem",),
        notes=(
            "The repo localizes a Berger/profile radius symbol but does not derive a numerical value. "
            "Cosmological R_H_Gpc, heat Lambda_squared, S=1/(4*pi), collar rho, and matching scales "
            "are distinct symbols and are rejected as substitutes."
        ),
    )


def classify_Z_H_source(repo_root: Path | None = None) -> ScaleSource:
    root = _root(repo_root)
    return ScaleSource(
        name="Z_H",
        status=OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
        value=None,
        formula="Z_H = integral_B |Phi(y)|^2 dmu_Berger = integral |Phi|^2 J(Y,rho) dY drho",
        source_trace=_existing_paths(
            root,
            (
                "theory/derived_universal_higgs_topographic_profile.md",
                "theory/theorem_discharge_scalar_topographic_level_set_boundary_embedding.md",
                "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
                "docs/open_blockers_backlog.md",
            ),
        ),
        classification="Higgs/profile kinetic normalization",
        missing_objects=(
            "explicit Phi(y) solution",
            "Phi_0 threshold/normalization",
            "internal Berger measure/domain",
            "collar Jacobian J(Y,rho) value",
        ),
        notes=(
            "The normalization formula is localized from profile and collar-measure scaffolds, "
            "but the profile solution and measure data needed for a value remain open."
        ),
    )


def classify_kappa_H_source(repo_root: Path | None = None) -> ScaleSource:
    root = _root(repo_root)
    return ScaleSource(
        name="kappa_H",
        status=OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
        value=None,
        formula="kappa_H = delta^2 S_eff^(H) / delta Phi^2 |_{Phi=Phi_H} = V_eff''(Phi_H)",
        source_trace=_existing_paths(
            root,
            (
                "docs/open_blockers_backlog.md",
                "theory/theorem_discharge_scalar_topographic_profile_eom_source_audit.md",
                "theory/theorem_discharge_scalar_topographic_boundary_condition_normal_form.md",
                "artifacts/Higgs_EW_closure_or_obstruction_v1.json",
            ),
        ),
        classification="Higgs/profile second variation or curvature stiffness",
        missing_objects=(
            "S_eff^(H) Higgs/profile action",
            "profile saddle Phi_H",
            "H_H Higgs saddle Hessian",
            "V_eff'' value",
            "boundary potential curvature coefficients",
        ),
        notes=(
            "The second-variation route is localized, but the complete Higgs/profile action and "
            "Hessian coefficients are not evaluated by the repo."
        ),
    )


def _is_derived(source: ScaleSource) -> bool:
    return source.status in (DERIVED_FIXED, DERIVED_CONDITIONAL) and source.value is not None


def derive_Z_H_if_possible(
    sources: Mapping[str, ScaleSource] | None = None,
    repo_root: Path | None = None,
) -> Dict[str, object]:
    source = (sources or collect_boundary_profile_scale_sources(repo_root))["Z_H"]
    if _is_derived(source):
        return {
            **_guardrails(),
            "name": "Z_H",
            "status": source.status,
            "derived": True,
            "value": source.value,
            "formula": source.formula,
            "source_trace": source.source_trace,
            "missing_objects": [],
        }
    return {
        **_guardrails(),
        "name": "Z_H",
        "status": source.status,
        "derived": False,
        "value": None,
        "formula": source.formula,
        "source_trace": source.source_trace,
        "missing_objects": source.missing_objects,
        "obstruction": "Z_H is localized as a profile normalization but cannot be evaluated without the listed source objects.",
    }


def derive_kappa_H_if_possible(
    sources: Mapping[str, ScaleSource] | None = None,
    repo_root: Path | None = None,
) -> Dict[str, object]:
    source = (sources or collect_boundary_profile_scale_sources(repo_root))["kappa_H"]
    if _is_derived(source):
        return {
            **_guardrails(),
            "name": "kappa_H",
            "status": source.status,
            "derived": True,
            "value": source.value,
            "formula": source.formula,
            "source_trace": source.source_trace,
            "missing_objects": [],
        }
    return {
        **_guardrails(),
        "name": "kappa_H",
        "status": source.status,
        "derived": False,
        "value": None,
        "formula": source.formula,
        "source_trace": source.source_trace,
        "missing_objects": source.missing_objects,
        "obstruction": "kappa_H is localized as a profile second variation but cannot be evaluated without the listed source objects.",
    }


def derive_sigma_tau_if_possible(
    sources: Mapping[str, ScaleSource] | None = None,
    repo_root: Path | None = None,
) -> Dict[str, object]:
    resolved = dict(sources or collect_boundary_profile_scale_sources(repo_root))
    missing = [name for name in ("kappa_H", "Z_H", "r") if not _is_derived(resolved[name])]
    if missing:
        return {
            **_guardrails(),
            "status": BLOCKED_BY_MISSING_OBJECTS,
            "sigma_from_boundary_geometry": OPEN_LOCALIZABLE,
            "tau_from_boundary_geometry": OPEN_LOCALIZABLE,
            "sigma_derived": False,
            "tau_derived": False,
            "sigma": None,
            "tau": None,
            "missing_objects": missing,
            "sigma_formula": "sigma = (1/2) sqrt(kappa_H / Z_H)",
            "tau_formula": "tau = 1 / (4 sigma r^2)",
            "charged_outputs_at_tau_exported": False,
        }
    kappa_h = float(resolved["kappa_H"].value)
    z_h = float(resolved["Z_H"].value)
    r_value = float(resolved["r"].value)
    sigma = 0.5 * sqrt(kappa_h / z_h)
    tau = 1.0 / (4.0 * sigma * r_value**2)
    return {
        **_guardrails(),
        "status": DERIVED_CONDITIONAL,
        "sigma_from_boundary_geometry": DERIVED_CONDITIONAL,
        "tau_from_boundary_geometry": DERIVED_CONDITIONAL,
        "sigma_derived": True,
        "tau_derived": True,
        "sigma": sigma,
        "tau": tau,
        "missing_objects": [],
        "sigma_formula": "sigma = (1/2) sqrt(kappa_H / Z_H)",
        "tau_formula": "tau = 1 / (4 sigma r^2)",
        "charged_outputs_at_tau_exported": True,
    }


def build_boundary_profile_scale_closure_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_boundary_profile_scale_sources(repo_root)
    sigma_tau = derive_sigma_tau_if_possible(sources, repo_root)
    all_closed = sigma_tau["tau_derived"] is True
    return {
        **_guardrails(),
        "artifact": "boundary_profile_scale_closure_v1",
        "targeted_followup_to": "PR #46 tau_sigma first blocker",
        "scope": "kappa_H, Z_H, and r only",
        "boundary_profile_scale_closure": DERIVED_CONDITIONAL if all_closed else BLOCKED_BY_MISSING_OBJECTS,
        "sigma_from_boundary_geometry": sigma_tau["sigma_from_boundary_geometry"],
        "tau_from_boundary_geometry": sigma_tau["tau_from_boundary_geometry"],
        "r": _source_to_dict(sources["r"]),
        "Z_H": _source_to_dict(sources["Z_H"]),
        "kappa_H": _source_to_dict(sources["kappa_H"]),
        "radius_disambiguation": [asdict(row) for row in disambiguate_radius_symbols(repo_root)],
        "Z_H_result": derive_Z_H_if_possible(sources, repo_root),
        "kappa_H_result": derive_kappa_H_if_possible(sources, repo_root),
        "sigma_tau_result": sigma_tau,
        "missing_objects": sigma_tau["missing_objects"],
        "charged_outputs_at_tau_exported": sigma_tau["charged_outputs_at_tau_exported"],
        "public_status_after_gate": DERIVED_CONDITIONAL if all_closed else PUBLIC_STATUS,
        "obstruction": (
            None
            if all_closed
            else "Boundary/profile scale closure remains blocked until kappa_H, Z_H, and r are repo-derived."
        ),
    }
