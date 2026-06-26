from __future__ import annotations

from dataclasses import asdict, dataclass
from math import pi, sqrt
from pathlib import Path
from typing import Dict, Iterable


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
RADIUS_GATE_STATUS = "DERIVED_CONDITIONAL_FROM_AUTHOR_AXIOM"
RADIUS_SELECTED_BY = "AUTHOR_SUPPLIED_BHSM_OVERLAP_NORMALIZATION"

DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
DERIVED_CONDITIONAL_FROM_PROFILE_NORMALIZATION = "DERIVED_CONDITIONAL_FROM_PROFILE_NORMALIZATION"
OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH = "OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH"
BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM = "BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM"
OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H = "OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H"
BLOCKED_BY_MISSING_OBJECTS = "BLOCKED_BY_MISSING_OBJECTS"
NO_FIT_OUTPUT_BLOCKED_BY_KAPPA_H = "NO_FIT_OUTPUT_BLOCKED_BY_KAPPA_H"

CANONICAL_PROFILE_NORMALIZATION_THEOREM = "CANONICAL_INTERNAL_PROFILE_NORMALIZATION_THEOREM"
CANONICAL_PROFILE_HESSIAN_THEOREM = "CANONICAL_PROFILE_HESSIAN_THEOREM"


@dataclass(frozen=True)
class ProfileSource:
    object_id: str
    status: str
    value: float | None
    formula: str
    source_trace: tuple[str, ...]
    missing_objects: tuple[str, ...]
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
        "public_status": PUBLIC_STATUS,
        "public_status_before_gate": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "observed_masses_used": False,
        "observed_Higgs_used": False,
        "observed_gauge_values_used": False,
        "tau_fit_to_masses": False,
        "sigma_fit_to_masses": False,
        "radius_gate_status": RADIUS_GATE_STATUS,
    }


def _radius_values() -> Dict[str, object]:
    return {
        "radius_selected_by": RADIUS_SELECTED_BY,
        "r_internal_profile_status": "DERIVED_CONDITIONAL",
        "r_internal_profile_squared_formula": "1/(4*pi)",
        "r_internal_profile_squared": 1.0 / (4.0 * pi),
        "r_internal_profile_formula": "1/sqrt(4*pi)",
        "r_internal_profile": 1.0 / sqrt(4.0 * pi),
        "radius_fork_reopened": False,
    }


def collect_profile_normalization_sources(repo_root: Path | None = None) -> Dict[str, ProfileSource]:
    root = _root(repo_root)
    trace = _existing_paths(
        root,
        (
            "artifacts/internal_berger_radius_selection_theorem_v1.json",
            "artifacts/internal_profile_radius_value_v1.json",
            "theory/derived_universal_higgs_topographic_profile.md",
            "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
            "theory/theorem_discharge_scalar_topographic_level_set_boundary_embedding.md",
        ),
    )
    return {
        "canonical_profile_normalization_theorem": ProfileSource(
            CANONICAL_PROFILE_NORMALIZATION_THEOREM,
            DERIVED_CONDITIONAL_FROM_PROFILE_NORMALIZATION,
            1.0,
            "Z_H = integral_B |Phi(y)|^2 dmu_Berger = 1",
            trace,
            (),
            (
                "Author-supplied BHSM profile normalization: Phi is canonically normalized on "
                "the selected overlap-radius internal Berger profile domain."
            ),
        ),
        "Phi(y)": ProfileSource(
            "Phi(y)",
            DERIVED_CONDITIONAL,
            None,
            "Phi(y)=Phi_0 exp[-sigma d_B(y,y_0)^2]",
            trace,
            ("sigma value remains open until kappa_H closes",),
            "Universal Gaussian/topographic profile normal form is already localized.",
        ),
        "dmu_Berger": ProfileSource(
            "dmu_Berger",
            DERIVED_CONDITIONAL,
            None,
            "selected overlap-radius Berger profile measure",
            trace,
            (),
            "The author radius axiom fixes the profile radius used by the canonical normalization theorem.",
        ),
    }


def derive_Z_H_from_profile_normalization_if_possible(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_profile_normalization_sources(repo_root)
    theorem = sources["canonical_profile_normalization_theorem"]
    return {
        **_guardrails(),
        **_radius_values(),
        "name": "Z_H",
        "status": DERIVED_CONDITIONAL_FROM_PROFILE_NORMALIZATION,
        "promoted_status": DERIVED_CONDITIONAL,
        "derived": True,
        "value": 1.0,
        "formula": theorem.formula,
        "source_theorem": CANONICAL_PROFILE_NORMALIZATION_THEOREM,
        "source_trace": theorem.source_trace,
        "missing_objects": [],
        "Z_H_set_to_one_by_habit": False,
        "Z_H_set_to_one_by_theorem": True,
        "canonical_profile_normalization_encoded": True,
    }


def collect_profile_hessian_sources(repo_root: Path | None = None) -> Dict[str, ProfileSource]:
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
        "S_eff^(H)": ProfileSource(
            "S_eff^(H)",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "S_eff^(H)[Phi]",
            trace,
            ("complete Higgs/profile effective action",),
            "The effective action is localized as a dependency but not evaluated.",
        ),
        "profile_saddle": ProfileSource(
            "profile_saddle",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "delta S_eff^(H)/delta Phi |_{Phi_H}=0",
            trace,
            ("profile saddle Phi_H", "boundary conditions"),
            "The saddle equation can be stated, but the saddle is not solved.",
        ),
        "kappa_H": ProfileSource(
            "kappa_H",
            BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
            None,
            "kappa_H = delta^2 S_eff^(H)/delta Phi^2 |_{Phi=Phi_H} = V_eff''(Phi_H)",
            trace,
            (
                "profile Hessian theorem identifying a numerical curvature",
                "profile saddle Phi_H",
                "H_H Higgs/profile Hessian",
                "V_eff'' value",
                "boundary potential curvature coefficients",
            ),
            "No repo convention identifies an evaluated Hessian coefficient with kappa_H.",
        ),
        "mu_H": ProfileSource(
            "mu_H",
            OPEN_LOCALIZABLE_WITH_EXACT_SOURCE_PATH,
            None,
            "mu_H = 64*pi^5",
            _existing_paths(
                root,
                (
                    "src/spectral_bounds.py",
                    "theory/ht_bound_classification_report.md",
                    "theory/ht_no_extra_light_theorem_scaffold.md",
                ),
            ),
            ("source-traced identification mu_H == kappa_H",),
            (
                "mu_H is a heat-lift/H_T target scale in existing scaffolds, not a source-traced "
                "profile Hessian coefficient."
            ),
        ),
    }


def derive_kappa_H_from_profile_hessian_if_possible(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_profile_hessian_sources(repo_root)
    source = sources["kappa_H"]
    return {
        **_guardrails(),
        **_radius_values(),
        "name": "kappa_H",
        "status": BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
        "derived": False,
        "value": None,
        "formula": source.formula,
        "source_theorem": CANONICAL_PROFILE_HESSIAN_THEOREM,
        "source_trace": source.source_trace,
        "objects": {name: asdict(obj) for name, obj in sources.items()},
        "missing_objects": source.missing_objects,
        "observed_Higgs_used": False,
        "kappa_H_chosen_to_set_tau": False,
        "mu_H_identified_with_kappa_H": False,
        "mu_H_identification_status": "NOT_IDENTIFIED_WITH_KAPPA_H_WITHOUT_SOURCE_TRACE",
        "obstruction": (
            "kappa_H remains blocked until a profile Hessian theorem evaluates "
            "delta^2 S_eff^(H) at Phi_H or source-traces an existing stiffness object to kappa_H."
        ),
    }


def derive_sigma_tau_if_possible(repo_root: Path | None = None) -> Dict[str, object]:
    z_h = derive_Z_H_from_profile_normalization_if_possible(repo_root)
    kappa_h = derive_kappa_H_from_profile_hessian_if_possible(repo_root)
    if z_h["derived"] and kappa_h["derived"]:
        kappa_value = float(kappa_h["value"])
        z_value = float(z_h["value"])
        sigma = 0.5 * sqrt(kappa_value / z_value)
        tau = 2.0 * pi * sqrt(z_value / kappa_value)
        return {
            **_guardrails(),
            **_radius_values(),
            "profile_scale_closure": DERIVED_CONDITIONAL,
            "sigma_from_boundary_geometry": DERIVED_CONDITIONAL,
            "tau_from_boundary_geometry": DERIVED_CONDITIONAL,
            "sigma_derived": True,
            "tau_derived": True,
            "sigma": sigma,
            "tau": tau,
            "sigma_formula": "sigma = (1/2)*sqrt(kappa_H/Z_H)",
            "tau_formula": "tau = 2*pi*sqrt(Z_H/kappa_H)",
            "missing_objects": [],
            "charged_outputs_at_tau_exported": False,
        }
    return {
        **_guardrails(),
        **_radius_values(),
        "profile_scale_closure": BLOCKED_BY_MISSING_OBJECTS,
        "sigma_from_boundary_geometry": OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H,
        "tau_from_boundary_geometry": OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H,
        "sigma_derived": False,
        "tau_derived": False,
        "sigma": None,
        "tau": None,
        "Z_H_status": DERIVED_CONDITIONAL,
        "Z_H_value": 1.0,
        "kappa_H_status": BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
        "missing_objects": ["kappa_H"],
        "sigma_formula": "sigma(kappa_H) = (1/2)*sqrt(kappa_H)",
        "tau_formula": "tau(kappa_H) = 2*pi/sqrt(kappa_H)",
        "tau_numeric_computed": False,
        "charged_outputs_at_tau_exported": False,
    }


def compute_charged_outputs_at_tau_if_possible(repo_root: Path | None = None) -> Dict[str, object]:
    sigma_tau = derive_sigma_tau_if_possible(repo_root)
    return {
        **_guardrails(),
        **_radius_values(),
        "status": NO_FIT_OUTPUT_BLOCKED_BY_KAPPA_H,
        "exported": False,
        "reason": "Charged outputs at boundary tau are exported only after tau is numeric/derived.",
        "tau_derived": sigma_tau["tau_derived"],
        "missing_objects": sigma_tau["missing_objects"],
        "output_files": [],
    }


def build_profile_normalization_hessian_closure_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    z_h = derive_Z_H_from_profile_normalization_if_possible(repo_root)
    kappa_h = derive_kappa_H_from_profile_hessian_if_possible(repo_root)
    sigma_tau = derive_sigma_tau_if_possible(repo_root)
    charged = compute_charged_outputs_at_tau_if_possible(repo_root)
    return {
        **_guardrails(),
        **_radius_values(),
        "artifact": "profile_normalization_hessian_closure_v1",
        "targeted_followup_to": "PR #50 author internal Berger radius selection theorem",
        "Z_H": z_h,
        "kappa_H": kappa_h,
        "sigma_tau": sigma_tau,
        "charged_outputs_at_tau": charged,
        "Z_H_profile_normalization": DERIVED_CONDITIONAL,
        "kappa_H_profile_hessian": BLOCKED_BY_MISSING_PROFILE_HESSIAN_THEOREM,
        "profile_scale_closure": sigma_tau["profile_scale_closure"],
        "remaining_blockers": sigma_tau["missing_objects"],
        "public_status_after_gate": PUBLIC_STATUS,
    }
