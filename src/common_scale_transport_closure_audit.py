from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
BLOCKED = "BLOCKED_BY_MISSING_TRANSPORT_OBJECTS"
OPEN_LOCALIZABLE = "OPEN_LOCALIZABLE"
EXPORTED_TEMPLATE = "EXPORTED_TEMPLATE"
MISSING = "MISSING"


@dataclass(frozen=True)
class TransportSourceObject:
    name: str
    status: str
    source_trace: str | None
    notes: str


def collect_transport_sources(repo_root: Path | None = None) -> Dict[str, TransportSourceObject]:
    root = repo_root or Path(__file__).resolve().parents[1]
    template = root / "artifacts" / "charged_transport_decomposition_template_v1.json"
    interface = root / "artifacts" / "common_scale_charged_transport_interface_v1.json"
    return {
        "T_gauge,f": TransportSourceObject(
            "T_gauge,f",
            EXPORTED_TEMPLATE if template.exists() else MISSING,
            str(template) if template.exists() else None,
            "Template exists, but no derived numerical factor is populated.",
        ),
        "T_Yukawa,self,f_i": TransportSourceObject(
            "T_Yukawa,self,f_i",
            OPEN_LOCALIZABLE,
            str(template) if template.exists() else None,
            "Self-Yukawa residual transport is named but not computed.",
        ),
        "T_threshold,f_i": TransportSourceObject(
            "T_threshold,f_i",
            OPEN_LOCALIZABLE,
            str(template) if template.exists() else None,
            "Threshold transport is named but not computed for common-scale population.",
        ),
        "T_scheme,f": TransportSourceObject(
            "T_scheme,f",
            OPEN_LOCALIZABLE,
            str(template) if template.exists() else None,
            "Scheme conversion is named but not computed.",
        ),
        "Lambda_BH": TransportSourceObject(
            "Lambda_BH",
            MISSING,
            str(interface) if interface.exists() else None,
            "Appears in the interface formula, but no derived numeric scale is present.",
        ),
        "mu_ref": TransportSourceObject(
            "mu_ref",
            MISSING,
            str(interface) if interface.exists() else None,
            "No pre-comparison common reference scale is fixed by repo derivation.",
        ),
    }


def classify_transport_source_objects(repo_root: Path | None = None) -> Dict[str, Dict[str, object]]:
    return {
        name: {
            "status": obj.status,
            "source_trace": obj.source_trace,
            "notes": obj.notes,
        }
        for name, obj in collect_transport_sources(repo_root).items()
    }


def populate_transport_if_possible(sources: Mapping[str, TransportSourceObject] | None = None) -> Dict[str, object]:
    resolved = sources or collect_transport_sources()
    required = ("T_gauge,f", "T_Yukawa,self,f_i", "T_threshold,f_i", "T_scheme,f", "Lambda_BH", "mu_ref")
    missing = [
        name
        for name in required
        if resolved[name].status not in (DERIVED_CONDITIONAL,)
    ]
    if missing:
        return {
            "status": BLOCKED,
            "populated": False,
            "missing_objects": missing,
            "transport_factors_fit_to_residuals": False,
            "mixed_pole_running_comparison_allowed": False,
        }
    return {
        "status": DERIVED_CONDITIONAL,
        "populated": True,
        "missing_objects": [],
        "transport_factors_fit_to_residuals": False,
        "mixed_pole_running_comparison_allowed": False,
    }


def build_transport_closure_or_obstruction_artifact(repo_root: Path | None = None) -> Dict[str, object]:
    sources = collect_transport_sources(repo_root)
    result = populate_transport_if_possible(sources)
    return {
        "public_status_before_gate": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_derivation_inputs_used": False,
        "observed_masses_used_as_derivation_inputs": False,
        "mixed_pole_running_comparison_allowed": False,
        "transport_factors_fit_to_residuals": False,
        "gate": "common_scale_transport",
        "status": result["status"],
        "source_objects": classify_transport_source_objects(repo_root),
        "missing_objects": result["missing_objects"],
        "obstruction": (
            "Transport interface and templates exist, but numerical/common-scale population "
            "requires derived T_gauge, self-Yukawa, threshold, scheme factors, Lambda_BH, and mu_ref."
            if result["missing_objects"]
            else None
        ),
    }
