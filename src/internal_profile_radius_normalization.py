from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from typing import Dict, Iterable, Mapping


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

DERIVED_FIXED = "DERIVED_FIXED"
DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH = "OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH"
BLOCKED_BY_MISSING_OBJECT = "BLOCKED_BY_MISSING_OBJECT"
BLOCKED_BY_MISSING_OBJECTS = "BLOCKED_BY_MISSING_OBJECTS"
BLOCKED_BY_MISSING_NORMALIZATION_THEOREM = "BLOCKED_BY_MISSING_NORMALIZATION_THEOREM"
BLOCKED_BY_MISSING_PROFILE_MEASURE = "BLOCKED_BY_MISSING_PROFILE_MEASURE"
BLOCKED_BY_MISSING_EFFECTIVE_ACTION = "BLOCKED_BY_MISSING_EFFECTIVE_ACTION"
BLOCKED_BY_MISSING_BOUNDARY_POTENTIAL_COEFFICIENTS = "BLOCKED_BY_MISSING_BOUNDARY_POTENTIAL_COEFFICIENTS"
REJECTED_AS_UNSUPPORTED = "REJECTED_AS_UNSUPPORTED"
OPEN_LOCALIZABLE = "OPEN_LOCALIZABLE"

DERIVED_STATUSES = {DERIVED_FIXED, DERIVED_CONDITIONAL}


@dataclass(frozen=True)
class ClosureObject:
    name: str
    status: str
    value: float | str | None
    formula: str | None
    source_trace: tuple[str, ...]
    missing_objects: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class RadiusDisambiguation:
    object_id: str
    symbol: str
    classification: str
    value: float | str | None
    used_as_internal_profile_r: bool
    status: str
    source_trace: tuple[str, ...]
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


def _asdict(obj: ClosureObject | RadiusDisambiguation) -> Dict[str, object]:
    return asdict(obj)


def collect_radius_sources(repo_root: Path | None = None) -> Dict[str, ClosureObject]:
    root = _root(repo_root)
    return {
        "r_internal_profile": ClosureObject(
            name="r_internal_profile",
            status=BLOCKED_BY_MISSING_NORMALIZATION_THEOREM,
            value=None,
            formula="tau = 1/(4 sigma r_internal_profile^2)",
            source_trace=_existing_paths(
                root,
                (
                    "artifacts/boundary_profile_scale_closure_v1.json",
                    "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
                    "artifacts/frozen_constants_v2.json",
                ),
            ),
            missing_objects=(
                "Hopf fiber-radius normalization theorem",
                "Berger volume normalization theorem",
                "internal profile-domain measure theorem",
                "collar-depth matching condition",
                "Lambda-to-radius convention",
            ),
            notes=(
                "Repo constants localize alpha-anchored anisotropy, S=1/(4*pi), and Lambda_squared=1/(4*pi), "
                "but no theorem identifies those constants with the internal/profile radius."
            ),
        ),
        "R_H_cosmological": ClosureObject(
            name="R_H_cosmological",
            status=REJECTED_AS_UNSUPPORTED,
            value=24.0,
            formula=None,
            source_trace=_existing_paths(root, ("artifacts/hyperspherical_cosmology_desi_pipeline_v1.json",)),
            missing_objects=(),
            notes="Cosmological scaffold radius; explicitly not an internal/profile Berger radius.",
        ),
        "rho_star_collar_depth": ClosureObject(
            name="rho_star_collar_depth",
            status=OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            value=None,
            formula="J(Y,rho)=det(I+rho S(Y))",
            source_trace=_existing_paths(
                root,
                (
                    "theory/theorem_discharge_normal_coupling_collar_convention.md",
                    "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
                ),
            ),
            missing_objects=("collar edge/depth selection theorem", "shape operator S(Y) value"),
            notes="Collar depth is a normal-coordinate object; it is not tau's internal/profile radius.",
        ),
        "Lambda_BH_matching_scale": ClosureObject(
            name="Lambda_BH_matching_scale",
            status=BLOCKED_BY_MISSING_OBJECT,
            value=None,
            formula=None,
            source_trace=_existing_paths(root, ("artifacts/common_scale_charged_transport_interface_v1.json",)),
            missing_objects=("common-scale matching theorem",),
            notes="Matching-scale placeholder, not a geometric radius.",
        ),
        "Lambda_squared_overlap": ClosureObject(
            name="Lambda_squared_overlap",
            status=REJECTED_AS_UNSUPPORTED,
            value="1/(4*pi)",
            formula="Lambda_squared = 1/(4*pi)",
            source_trace=_existing_paths(root, ("artifacts/frozen_constants_v2.json",)),
            missing_objects=("Lambda-to-radius convention",),
            notes="Heat/spectral cutoff value is fixed but not identified with r_internal_profile.",
        ),
        "S_overlap_width": ClosureObject(
            name="S_overlap_width",
            status=REJECTED_AS_UNSUPPORTED,
            value="1/(4*pi)",
            formula="S = 1/(4*pi)",
            source_trace=_existing_paths(root, ("src/bhsm_v1.py", "artifacts/frozen_constants_v2.json")),
            missing_objects=("overlap-width-to-radius convention",),
            notes="Frozen overlap/stochastic width constant, not a profile-domain radius.",
        ),
    }


def disambiguate_radius_symbols(repo_root: Path | None = None) -> list[RadiusDisambiguation]:
    sources = collect_radius_sources(repo_root)
    return [
        RadiusDisambiguation(
            object_id="r_internal_profile",
            symbol="r",
            classification="dimensionless internal/profile Berger radius",
            value=sources["r_internal_profile"].value,
            used_as_internal_profile_r=True,
            status=sources["r_internal_profile"].status,
            source_trace=sources["r_internal_profile"].source_trace,
            notes=sources["r_internal_profile"].notes,
        ),
        RadiusDisambiguation(
            object_id="R_H_cosmological",
            symbol="R_H_Gpc",
            classification="physical/cosmological radius",
            value=sources["R_H_cosmological"].value,
            used_as_internal_profile_r=False,
            status=sources["R_H_cosmological"].status,
            source_trace=sources["R_H_cosmological"].source_trace,
            notes=sources["R_H_cosmological"].notes,
        ),
        RadiusDisambiguation(
            object_id="rho_star_collar_depth",
            symbol="rho_*",
            classification="collar normal-depth coordinate",
            value=sources["rho_star_collar_depth"].value,
            used_as_internal_profile_r=False,
            status=sources["rho_star_collar_depth"].status,
            source_trace=sources["rho_star_collar_depth"].source_trace,
            notes=sources["rho_star_collar_depth"].notes,
        ),
        RadiusDisambiguation(
            object_id="Lambda_BH_matching_scale",
            symbol="Lambda_BH / mu_ref",
            classification="common-scale transport/matching scale",
            value=sources["Lambda_BH_matching_scale"].value,
            used_as_internal_profile_r=False,
            status=sources["Lambda_BH_matching_scale"].status,
            source_trace=sources["Lambda_BH_matching_scale"].source_trace,
            notes=sources["Lambda_BH_matching_scale"].notes,
        ),
        RadiusDisambiguation(
            object_id="Lambda_squared_overlap",
            symbol="Lambda_squared",
            classification="heat/spectral cutoff",
            value=sources["Lambda_squared_overlap"].value,
            used_as_internal_profile_r=False,
            status=sources["Lambda_squared_overlap"].status,
            source_trace=sources["Lambda_squared_overlap"].source_trace,
            notes=sources["Lambda_squared_overlap"].notes,
        ),
        RadiusDisambiguation(
            object_id="S_overlap_width",
            symbol="S",
            classification="overlap/stochastic width",
            value=sources["S_overlap_width"].value,
            used_as_internal_profile_r=False,
            status=sources["S_overlap_width"].status,
            source_trace=sources["S_overlap_width"].source_trace,
            notes=sources["S_overlap_width"].notes,
        ),
    ]


def attempt_internal_profile_radius_derivation(repo_root: Path | None = None) -> Dict[str, object]:
    source = collect_radius_sources(repo_root)["r_internal_profile"]
    return {
        **_guardrails(),
        "name": "r_internal_profile",
        "status": source.status,
        "derived": False,
        "value": None,
        "formula": source.formula,
        "source_trace": source.source_trace,
        "missing_objects": source.missing_objects,
        "cosmological_R_H_used": False,
        "S_or_Lambda_silently_used_as_radius": False,
        "obstruction": "No internal/profile Berger radius normalization theorem is present.",
    }


def collect_profile_sources(repo_root: Path | None = None) -> Dict[str, ClosureObject]:
    root = _root(repo_root)
    common_trace = _existing_paths(
        root,
        (
            "theory/derived_universal_higgs_topographic_profile.md",
            "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
            "theory/theorem_discharge_scalar_topographic_level_set_boundary_embedding.md",
        ),
    )
    return {
        "Phi(y)": ClosureObject(
            "Phi(y)",
            DERIVED_CONDITIONAL,
            None,
            "Phi(y)=Phi_0 exp[-sigma d_B(y,y_0)^2]",
            common_trace,
            ("sigma value", "Phi_0 normalization", "d_B metric distance value"),
            "Gaussian/topographic normal form is localized as a conditional profile ansatz, not numerically solved.",
        ),
        "Phi_0": ClosureObject(
            "Phi_0",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            "1/sqrt(integral exp[-2 sigma d_B(y,y_0)^2] dmu_Berger)",
            "Phi_0 = 1 / sqrt(integral exp[-2 sigma d_B(y,y_0)^2] dmu_Berger)",
            common_trace,
            ("sigma value", "internal domain", "dmu_Berger", "normalization theorem"),
            "Symbolic normalization is available if a normalized profile convention is assumed, but no numeric value is allowed.",
        ),
        "y_0": ClosureObject(
            "y_0",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "grad_y S_eff^(H)(y_0)=0",
            common_trace
            + _existing_paths(root, ("theory/theorem_discharge_neutral_saddle_displacement.md",)),
            ("Higgs/profile saddle-selection theorem",),
            "The distinguished point is localized as the profile center/saddle but not selected by a completed action.",
        ),
        "d_B": ClosureObject(
            "d_B",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "d_B(y,y_0) from internal Berger metric g_B",
            common_trace,
            ("explicit internal Berger metric normalization", "radius convention"),
            "Metric-distance notation is localized, but radius/metric normalization remains open.",
        ),
        "internal_domain": ClosureObject(
            "internal_domain",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "B or collar-neighborhood domain for profile integration",
            common_trace,
            ("profile-domain selection theorem", "boundary/collar domain limits"),
            "The integration domain is named but not fixed for numerical normalization.",
        ),
        "dmu_Berger": ClosureObject(
            "dmu_Berger",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "dmu_Berger = sqrt(det g_B) dy",
            common_trace,
            ("metric determinant", "Berger volume normalization", "internal radius convention"),
            "Measure form is localizable but not numerically evaluated.",
        ),
        "J(Y,rho)": ClosureObject(
            "J(Y,rho)",
            DERIVED_CONDITIONAL,
            None,
            "J(Y,rho)=det(I+rho S(Y))=1+rho K(Y)+O(rho^2)",
            _existing_paths(
                root,
                (
                    "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
                    "theory/theorem_discharge_scalar_topographic_level_set_boundary_embedding.md",
                ),
            ),
            ("shape operator S(Y) value", "normal orientation", "collar depth/domain"),
            "The collar Jacobian identity is conditionally derived, but its value remains open.",
        ),
    }


def attempt_phi_normal_form(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_profile_sources(repo_root)
    return {
        **_guardrails(),
        "artifact": "Phi_profile_normal_form_v1",
        "status": DERIVED_CONDITIONAL,
        "Phi_profile": _asdict(sources["Phi(y)"]),
        "objects": {name: _asdict(obj) for name, obj in sources.items()},
        "normalization_condition": "1 = integral |Phi(y)|^2 dmu_Berger",
        "symbolic_Phi_0": sources["Phi_0"].value,
        "Phi_0_numerical_assigned": False,
        "missing_objects": (
            "sigma value",
            "internal profile-domain measure",
            "dmu_Berger value",
            "J(Y,rho) value if collar form is used",
        ),
    }


def attempt_Z_H_derivation(repo_root: Path | None = None) -> Dict[str, object]:
    profile = collect_profile_sources(repo_root)
    return {
        **_guardrails(),
        "name": "Z_H",
        "status": BLOCKED_BY_MISSING_PROFILE_MEASURE,
        "derived": False,
        "value": None,
        "formula": "Z_H = integral_B |Phi(y)|^2 dmu_Berger = integral |Phi(Y,rho)|^2 J(Y,rho) dY drho",
        "source_trace": profile["Phi(y)"].source_trace + profile["J(Y,rho)"].source_trace,
        "normalized_profile_would_imply_Z_H_equals_one": "CONDITIONAL_ONLY",
        "Z_H_set_to_one": False,
        "missing_objects": (
            "profile normalization theorem identifying Z_H with unit norm",
            "sigma value",
            "internal domain",
            "dmu_Berger value",
            "J(Y,rho) value if collar form is used",
        ),
        "obstruction": "Z_H cannot be set to 1 or evaluated until the profile measure and normalization theorem are supplied.",
    }


def collect_higgs_profile_action_sources(repo_root: Path | None = None) -> Dict[str, ClosureObject]:
    root = _root(repo_root)
    trace = _existing_paths(
        root,
        (
            "docs/open_blockers_backlog.md",
            "theory/theorem_discharge_scalar_topographic_profile_eom_source_audit.md",
            "theory/theorem_discharge_scalar_topographic_boundary_condition_normal_form.md",
            "theory/theorem_discharge_neutral_saddle_displacement.md",
            "artifacts/Higgs_EW_closure_or_obstruction_v1.json",
        ),
    )
    return {
        "S_eff^(H)": ClosureObject(
            "S_eff^(H)",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "S_eff^(H)[Phi]",
            trace,
            ("Higgs/profile effective action", "profile source term", "regularization/boundary terms"),
            "The Higgs effective action is named as a dependency but not constructed/evaluated.",
        ),
        "profile_saddle": ClosureObject(
            "profile_saddle",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "delta S_eff^(H)/delta Phi |_{Phi_H}=0",
            trace,
            ("S_eff^(H)", "saddle-selection theorem", "boundary conditions"),
            "A saddle condition can be stated, but the action and boundary conditions are open.",
        ),
        "H_H": ClosureObject(
            "H_H",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "H_H = delta^2 S_eff^(H)|_{Phi_H}",
            trace,
            ("S_eff^(H)", "profile saddle Phi_H", "Hessian coefficients"),
            "The Higgs/charged Hessian is explicitly listed as an open dependency.",
        ),
        "V_eff''": ClosureObject(
            "V_eff''",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "V_eff''(Phi_H)",
            trace,
            ("effective potential V_eff", "boundary potential coefficients", "profile saddle Phi_H"),
            "Potential-curvature notation is localized but not evaluated.",
        ),
        "boundary_potential_curvature_coefficients": ClosureObject(
            "boundary_potential_curvature_coefficients",
            BLOCKED_BY_MISSING_BOUNDARY_POTENTIAL_COEFFICIENTS,
            None,
            "partial^2 U_boundary / partial Phi^2",
            trace,
            ("U_boundary", "lambda_Phi/Z_Phi convention", "curvature coefficients"),
            "No repo-fixed boundary potential coefficients are available.",
        ),
    }


def attempt_kappa_H_derivation(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_higgs_profile_action_sources(repo_root)
    return {
        **_guardrails(),
        "name": "kappa_H",
        "status": BLOCKED_BY_MISSING_EFFECTIVE_ACTION,
        "derived": False,
        "value": None,
        "formula": "kappa_H = delta^2 S_eff^(H)/delta Phi^2 |_{Phi=Phi_H} = V_eff''(Phi_H)",
        "source_trace": tuple(dict.fromkeys(item for obj in sources.values() for item in obj.source_trace)),
        "objects": {name: _asdict(obj) for name, obj in sources.items()},
        "missing_objects": (
            "S_eff^(H) Higgs/profile effective action",
            "profile saddle Phi_H",
            "H_H Higgs/profile Hessian",
            "V_eff'' value",
            "boundary potential curvature coefficients",
        ),
        "observed_Higgs_used": False,
        "kappa_H_chosen_to_set_tau": False,
        "obstruction": "kappa_H cannot be derived until the Higgs/profile effective action and Hessian data are supplied.",
    }


def _closed(value: Dict[str, object], allowed_extra_statuses: set[str] | None = None) -> bool:
    statuses = DERIVED_STATUSES | (allowed_extra_statuses or set())
    return value.get("status") in statuses and value.get("value") is not None


def attempt_sigma_tau_after_profile_scale_closure(
    overrides: Mapping[str, Dict[str, object]] | None = None,
    repo_root: Path | None = None,
) -> Dict[str, object]:
    if overrides is None:
        r = attempt_internal_profile_radius_derivation(repo_root)
        z_h = attempt_Z_H_derivation(repo_root)
        kappa = attempt_kappa_H_derivation(repo_root)
    else:
        r = dict(overrides["r_internal_profile"])
        z_h = dict(overrides["Z_H"])
        kappa = dict(overrides["kappa_H"])
    missing = [
        name
        for name, payload in (
            ("r_internal_profile", r),
            ("Z_H", z_h),
            ("kappa_H", kappa),
        )
        if not _closed(payload)
    ]
    if missing:
        return {
            **_guardrails(),
            "boundary_profile_scale_closure": BLOCKED_BY_MISSING_OBJECTS,
            "sigma_from_boundary_geometry": OPEN_LOCALIZABLE,
            "tau_from_boundary_geometry": OPEN_LOCALIZABLE,
            "sigma_derived": False,
            "tau_derived": False,
            "sigma": None,
            "tau": None,
            "missing_objects": missing,
            "charged_outputs_at_tau_exported": False,
            "sigma_formula": "sigma = (1/2) sqrt(kappa_H / Z_H)",
            "tau_formula": "tau = 1/(4 sigma r_internal_profile^2)",
        }
    sigma = 0.5 * sqrt(float(kappa["value"]) / float(z_h["value"]))
    tau = 1.0 / (4.0 * sigma * float(r["value"]) ** 2)
    return {
        **_guardrails(),
        "boundary_profile_scale_closure": DERIVED_CONDITIONAL,
        "sigma_from_boundary_geometry": DERIVED_CONDITIONAL,
        "tau_from_boundary_geometry": DERIVED_CONDITIONAL,
        "sigma_derived": True,
        "tau_derived": True,
        "sigma": sigma,
        "tau": tau,
        "missing_objects": [],
        "charged_outputs_at_tau_exported": True,
        "sigma_formula": "sigma = (1/2) sqrt(kappa_H / Z_H)",
        "tau_formula": "tau = 1/(4 sigma r_internal_profile^2)",
    }


def build_internal_profile_radius_closure_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    radius = attempt_internal_profile_radius_derivation(repo_root)
    phi = attempt_phi_normal_form(repo_root)
    z_h = attempt_Z_H_derivation(repo_root)
    kappa = attempt_kappa_H_derivation(repo_root)
    sigma_tau = attempt_sigma_tau_after_profile_scale_closure(repo_root=repo_root)
    return {
        **_guardrails(),
        "artifact": "internal_profile_radius_normalization_v1",
        "targeted_followup_to": "PR #47 boundary/profile scale closure",
        "scope": "r_internal_profile, Phi normal form, Z_H, kappa_H",
        "r_internal_profile": radius,
        "radius_disambiguation": [asdict(row) for row in disambiguate_radius_symbols(repo_root)],
        "Phi_profile": phi,
        "Z_H": z_h,
        "kappa_H": kappa,
        "profile_scale_tau_sigma_update": sigma_tau,
        "boundary_profile_scale_closure": sigma_tau["boundary_profile_scale_closure"],
        "sigma_from_boundary_geometry": sigma_tau["sigma_from_boundary_geometry"],
        "tau_from_boundary_geometry": sigma_tau["tau_from_boundary_geometry"],
        "missing_objects": sigma_tau["missing_objects"],
        "charged_outputs_at_tau_exported": sigma_tau["charged_outputs_at_tau_exported"],
        "public_status_after_gate": PUBLIC_STATUS
        if sigma_tau["tau_derived"] is False
        else DERIVED_CONDITIONAL,
    }
