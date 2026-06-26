from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Dict, List, Mapping


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

DERIVED_FIXED = "DERIVED_FIXED"
DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
OPEN_LOCALIZABLE = "OPEN_LOCALIZABLE"
EMPIRICAL_COMPARISON_INPUT = "EMPIRICAL_COMPARISON_INPUT"
FORBIDDEN_FIT_INPUT = "FORBIDDEN_FIT_INPUT"
MISSING = "MISSING"


@dataclass(frozen=True)
class SourceObject:
    name: str
    status: str
    source_trace: str | None
    notes: str


def collect_tau_sigma_sources(repo_root: Path | None = None) -> Dict[str, SourceObject]:
    root = repo_root or Path(__file__).resolve().parents[1]
    profile = root / "theory" / "derived_universal_higgs_topographic_profile.md"
    guardrail = root / "theory" / "derived_universal_profile_width_guardrail.md"
    blockers = root / "docs" / "open_blockers_backlog.md"
    return {
        "a": SourceObject(
            "a",
            DERIVED_FIXED,
            "constants: alpha^{-1}/(12*pi^2) / charged artifacts",
            "Frozen alpha-anchored Berger anisotropy is available.",
        ),
        "r": SourceObject(
            "r",
            MISSING,
            None,
            "No repo-derived numerical Berger/internal radius for tau=1/(4 sigma r^2).",
        ),
        "sigma": SourceObject(
            "sigma",
            OPEN_LOCALIZABLE,
            str(guardrail) if guardrail.exists() else None,
            "Universal width is guarded against fitting, but its value is not derived.",
        ),
        "tau": SourceObject(
            "tau",
            OPEN_LOCALIZABLE,
            "artifacts/universal_tau_sigma_response_scaffold_v1.json",
            "Tau is defined as universal branch variable, not numerically derived.",
        ),
        "kappa_H": SourceObject(
            "kappa_H",
            MISSING,
            None,
            "Required by sigma=(1/2)sqrt(kappa_H/Z_H), but no source object was found.",
        ),
        "Z_H": SourceObject(
            "Z_H",
            MISSING,
            None,
            "Required by sigma=(1/2)sqrt(kappa_H/Z_H), but no source object was found.",
        ),
        "Phi(y)": SourceObject(
            "Phi(y)",
            DERIVED_CONDITIONAL if profile.exists() else MISSING,
            str(profile) if profile.exists() else None,
            "Universal topographic profile form is recorded, but width value remains open.",
        ),
        "Phi_0": SourceObject(
            "Phi_0",
            OPEN_LOCALIZABLE,
            str(profile) if profile.exists() else None,
            "Profile symbol appears in the universal profile, but normalization is not numeric.",
        ),
        "y_0": SourceObject(
            "y_0",
            OPEN_LOCALIZABLE,
            str(profile) if profile.exists() else None,
            "Profile center appears in the universal profile, but coordinate value is not fixed.",
        ),
        "profile second variation": SourceObject(
            "profile second variation",
            OPEN_LOCALIZABLE,
            str(blockers) if blockers.exists() else None,
            "Profile EOM/source and Hessian data remain open-localizable.",
        ),
        "boundary embedding X": SourceObject(
            "boundary embedding X",
            OPEN_LOCALIZABLE,
            str(blockers) if blockers.exists() else None,
            "Boundary embedding is localized in backlog but not evaluable.",
        ),
        "shape operator S": SourceObject(
            "shape operator S",
            OPEN_LOCALIZABLE,
            str(blockers) if blockers.exists() else None,
            "Shape-operator formulas are conditional; values require embedding/profile data.",
        ),
        "collar Jacobian J": SourceObject(
            "collar Jacobian J",
            OPEN_LOCALIZABLE,
            str(blockers) if blockers.exists() else None,
            "Collar Jacobian depends on open shape/operator inputs.",
        ),
        "Higgs/profile normalization": SourceObject(
            "Higgs/profile normalization",
            OPEN_LOCALIZABLE,
            str(profile) if profile.exists() else None,
            "Profile normalization is symbolic, not a derived numerical normalization.",
        ),
    }


def classify_tau_sigma_source_objects(repo_root: Path | None = None) -> Dict[str, Dict[str, object]]:
    return {
        name: {
            "status": source.status,
            "source_trace": source.source_trace,
            "notes": source.notes,
        }
        for name, source in collect_tau_sigma_sources(repo_root).items()
    }


def derive_sigma_if_possible(sources: Mapping[str, SourceObject] | None = None) -> Dict[str, object]:
    resolved = sources or collect_tau_sigma_sources()
    required = ("kappa_H", "Z_H")
    missing = [name for name in required if resolved[name].status not in (DERIVED_FIXED, DERIVED_CONDITIONAL)]
    if missing:
        return {
            "status": OPEN_LOCALIZABLE,
            "derived": False,
            "value": None,
            "missing_objects": missing,
            "formula": "sigma = (1/2) sqrt(kappa_H / Z_H)",
        }
    # This branch is intentionally unreachable with current repo sources, but
    # remains executable if future artifacts provide numeric values.
    kappa_h = float(getattr(resolved["kappa_H"], "value"))  # type: ignore[arg-type]
    z_h = float(getattr(resolved["Z_H"], "value"))  # type: ignore[arg-type]
    return {
        "status": DERIVED_CONDITIONAL,
        "derived": True,
        "value": 0.5 * sqrt(kappa_h / z_h),
        "missing_objects": [],
        "formula": "sigma = (1/2) sqrt(kappa_H / Z_H)",
    }


def derive_tau_if_possible(sources: Mapping[str, SourceObject] | None = None) -> Dict[str, object]:
    resolved = sources or collect_tau_sigma_sources()
    sigma_result = derive_sigma_if_possible(resolved)
    missing = list(sigma_result["missing_objects"])
    if resolved["r"].status not in (DERIVED_FIXED, DERIVED_CONDITIONAL):
        missing.append("r")
    if missing:
        return {
            "status": OPEN_LOCALIZABLE,
            "derived": False,
            "value": None,
            "missing_objects": sorted(set(missing), key=missing.index),
            "formula": "tau = 1 / (4 sigma r^2)",
        }
    sigma = float(sigma_result["value"])
    r_value = float(getattr(resolved["r"], "value"))  # type: ignore[arg-type]
    return {
        "status": DERIVED_CONDITIONAL,
        "derived": True,
        "value": 1.0 / (4.0 * sigma * r_value**2),
        "missing_objects": [],
        "formula": "tau = 1 / (4 sigma r^2)",
    }


def compute_charged_outputs_at_tau_if_possible() -> Dict[str, object]:
    tau_result = derive_tau_if_possible()
    if not tau_result["derived"]:
        return {
            "status": "BLOCKED_BY_TAU_SIGMA_BOUNDARY_DERIVATION",
            "derived": False,
            "missing_objects": tau_result["missing_objects"],
            "artifacts_exported": [],
        }
    return {
        "status": "NO_FIT_OUTPUT_CANDIDATE",
        "derived": True,
        "tau": tau_result["value"],
        "artifacts_exported": [
            "artifacts/charged_outputs_at_boundary_tau_A_local_v1.json",
            "artifacts/charged_outputs_at_boundary_tau_A_background_identity_v1.json",
        ],
    }


def build_tau_sigma_closure_or_obstruction_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_tau_sigma_sources(repo_root)
    sigma_result = derive_sigma_if_possible(sources)
    tau_result = derive_tau_if_possible(sources)
    status = DERIVED_CONDITIONAL if tau_result["derived"] else OPEN_LOCALIZABLE
    missing: List[str] = []
    for item in list(sigma_result["missing_objects"]) + list(tau_result["missing_objects"]):
        if item not in missing:
            missing.append(item)
    return {
        "public_status_before_gate": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "observed_masses_used": False,
        "target_ratios_used": False,
        "gate": "tau_sigma",
        "status": status,
        "sigma_from_boundary_geometry": sigma_result["status"],
        "tau_from_boundary_geometry": tau_result["status"],
        "sigma_result": sigma_result,
        "tau_result": tau_result,
        "source_objects": classify_tau_sigma_source_objects(repo_root),
        "missing_objects": missing,
        "obstruction": (
            "Cannot compute sigma=(1/2)sqrt(kappa_H/Z_H) and tau=1/(4 sigma r^2) "
            "until kappa_H, Z_H, and r are repo-derived."
            if missing
            else None
        ),
    }
