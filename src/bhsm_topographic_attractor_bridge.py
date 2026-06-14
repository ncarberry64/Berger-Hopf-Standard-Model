"""Candidate topographic-attractor bridge for BHSM boundary-action audits.

This module is intentionally conservative.  It records a candidate bridge from
the scalar topographic operator language to the existing Hopf/Berger boundary
connection and stochastic dressing scaffolds, but it does not alter frozen
predictions or promote any candidate dressing rule to official status.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp, pi
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP


TOPOGRAPHIC_ATTRACTOR_BRIDGE_STRUCTURAL_CANDIDATE = (
    "TOPOGRAPHIC_ATTRACTOR_BRIDGE_STRUCTURAL_CANDIDATE"
)
FOURTH_ORDER_EQUATION_REPO_SUPPORTED = "FOURTH_ORDER_EQUATION_REPO_SUPPORTED"
PARTICLE_ATTRACTOR_STRUCTURAL_CANDIDATE = "PARTICLE_ATTRACTOR_STRUCTURAL_CANDIDATE"
STOCHASTIC_ATTRACTOR_DRESSING_STRUCTURAL_CANDIDATE = (
    "STOCHASTIC_ATTRACTOR_DRESSING_STRUCTURAL_CANDIDATE"
)
GEOMETRIC_INERTIA_STRUCTURAL_CANDIDATE = "GEOMETRIC_INERTIA_STRUCTURAL_CANDIDATE"
GENERATION_COUNT_GLOBAL_CURVATURE_STRUCTURAL_CANDIDATE = (
    "GENERATION_COUNT_GLOBAL_CURVATURE_STRUCTURAL_CANDIDATE"
)
ENVIRONMENTAL_MASS_SHIFT_CANDIDATE_ONLY = "ENVIRONMENTAL_MASS_SHIFT_CANDIDATE_ONLY"


@dataclass(frozen=True)
class ConnectionComponentStatus:
    """Status of the candidate A_q/A_j bridge."""

    A_q_topographic_status: str
    A_j_topographic_status: str
    representation_boundary_connection_consequence_status: str
    does_bridge_identify_A_q: bool
    does_bridge_identify_A_j: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class GenerationCountStatus:
    """Status of the global-curvature generation-count idea."""

    status: str
    ledger_generation_count: int
    derived: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ClaimSafetyStatus:
    """Claim-safety flags for topographic and environmental interpretations."""

    ordinary_environmental_mass_drift_claim: bool
    lab_mass_variation_claim: bool
    extreme_event_candidate_only: bool
    full_SM_derivation_claim: bool
    SM_replacement_claim: bool
    time_dependent_constants_official_claim: bool
    ordinary_FTL_neutrino_claim: bool


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge q=k-2j."""

    return k - 2 * j


def mode_norm_N(k: int, j: int) -> int:
    """Return the quadratic Hopf/base norm N=q^2+j^2."""

    q = q_from_kj(k, j)
    return q * q + j * j


def brownian_dressing_factor(eta: float, k: int, j: int) -> float:
    """Return the candidate Brownian damping factor exp[-eta N(k,j)]."""

    return exp(-float(eta) * mode_norm_N(k, j))


def lepton_eta_8alpha_9pi(alpha: float) -> float:
    """Return the predeclared eta_l=8 alpha/(9 pi) candidate."""

    return 8.0 * float(alpha) / (9.0 * pi)


def attractor_susceptibility_proxy(k: int, j: int, gap: float | None = None) -> float:
    """Return a monotone candidate susceptibility proxy.

    This is not a fitted prediction.  It is a diagnostic proxy in which larger
    Hopf/base norm or a larger supplied gap lowers susceptibility.
    """

    scale = 1.0 + mode_norm_N(k, j)
    if gap is not None:
        scale += max(float(gap), 0.0)
    return 1.0 / scale


def geometric_inertia_proxy(k: int, j: int, sector: str | None = None) -> float:
    """Return a candidate geometric inertia proxy.

    Quark sectors receive a color/coframe multiplicity factor as a diagnostic
    only.  This does not change frozen quark predictions.
    """

    sector_factor = 3.0 if sector in {"up", "down", "up_quarks", "down_quarks"} else 1.0
    return sector_factor * (1.0 + mode_norm_N(k, j))


def threshold_gate(intensity: float, threshold: float, power: float) -> float:
    """Return I^p/(I^p+I_*^p), with zero response at zero intensity."""

    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if power <= 0:
        raise ValueError("power must be positive")
    if intensity <= 0:
        return 0.0
    numerator = float(intensity) ** float(power)
    denominator = numerator + float(threshold) ** float(power)
    return numerator / denominator


def environmental_shift_candidate(delta_T: float, susceptibility: float, gate: float) -> float:
    """Return candidate fractional shift delta_T * susceptibility * gate."""

    return float(delta_T) * float(susceptibility) * float(gate)


def generation_count_status_object(ledger_generation_count: int = 3) -> GenerationCountStatus:
    """Return conservative generation-count status."""

    return GenerationCountStatus(
        status=GENERATION_COUNT_GLOBAL_CURVATURE_STRUCTURAL_CANDIDATE,
        ledger_generation_count=ledger_generation_count,
        derived=False,
        limitations=(
            "The frozen mode ledger uses three generations.",
            "A global-curvature or cosmic-hypersphere derivation is not implemented.",
        ),
    )


def connection_component_status_object() -> ConnectionComponentStatus:
    """Return conservative A_q/A_j topographic connection status."""

    return ConnectionComponentStatus(
        A_q_topographic_status="A_Q_HOPF_FIBER_COMPONENT_SUPPORTED_NOT_DERIVED",
        A_j_topographic_status="A_J_BERGER_BASE_COMPONENT_STRUCTURAL_CANDIDATE",
        representation_boundary_connection_consequence_status=(
            "REPRESENTATION_BOUNDARY_CONNECTION_PARTIAL"
        ),
        does_bridge_identify_A_q=True,
        does_bridge_identify_A_j=False,
        limitations=(
            "A_q is supported by the Hopf/fiber charge component but no explicit contact one-form is constructed here.",
            "A_j remains a Berger/base/coframe structural candidate without a derived boundary one-form.",
            "The full boundary action coupling of A_rep is still open.",
        ),
    )


def claim_safety_status_object() -> ClaimSafetyStatus:
    """Return required safety flags."""

    return ClaimSafetyStatus(
        ordinary_environmental_mass_drift_claim=False,
        lab_mass_variation_claim=False,
        extreme_event_candidate_only=True,
        full_SM_derivation_claim=False,
        SM_replacement_claim=False,
        time_dependent_constants_official_claim=False,
        ordinary_FTL_neutrino_claim=False,
    )


def _frozen_sanity() -> dict[str, Any]:
    comparison = compare_bhsm_v1_branches()
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    canonical_a = canonical_geometry_config().a
    sanity = dict(frozen_sanity_payload())
    sanity.update(
        {
            "a_unchanged": bare.version.geometry_a == canonical_a
            and dressed.version.geometry_a == canonical_a,
            "S_unchanged": bare.version.overlap_s == S_OVERLAP
            and dressed.version.overlap_s == S_OVERLAP,
            "official_branch_comparison": comparison,
        }
    )
    return sanity


def _lepton_rows(alpha: float) -> list[dict[str, Any]]:
    eta = lepton_eta_8alpha_9pi(alpha)
    rows = []
    for label, mode in {
        "tau_reference": (0, 0),
        "muon": (5, 2),
        "electron": (9, 3),
    }.items():
        rows.append(
            {
                "label": label,
                "mode": mode,
                "q": q_from_kj(*mode),
                "N": mode_norm_N(*mode),
                "dressing_factor": brownian_dressing_factor(eta, *mode),
                "susceptibility_proxy": attractor_susceptibility_proxy(*mode),
                "geometric_inertia_proxy": geometric_inertia_proxy(*mode, sector="lepton"),
            }
        )
    return rows


def _quark_rows() -> list[dict[str, Any]]:
    rows = []
    for label, mode, sector in (
        ("charm_middle_up", (6, 0), "up"),
        ("light_up", (10, 1), "up"),
        ("strange_middle_down", (6, 3), "down"),
        ("light_down", (8, 2), "down"),
    ):
        rows.append(
            {
                "label": label,
                "mode": mode,
                "sector": sector,
                "q": q_from_kj(*mode),
                "N": mode_norm_N(*mode),
                "pure_fiber": mode[1] == 0 and q_from_kj(*mode) != 0,
                "susceptibility_proxy": attractor_susceptibility_proxy(*mode),
                "geometric_inertia_proxy": geometric_inertia_proxy(*mode, sector=sector),
            }
        )
    return rows


def audit_payload(alpha: float | None = None) -> dict[str, Any]:
    """Return the structured topographic-attractor bridge audit payload."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    connection = connection_component_status_object()
    generation = generation_count_status_object()
    safety = claim_safety_status_object()
    blockers_remaining = (
        "construct explicit Hopf/fiber boundary one-form A_q",
        "construct explicit Berger/base/coframe boundary one-form A_j",
        "derive A_rep coupling from the full boundary action",
        "derive attractor energy Hessian from a complete BHSM action",
        "derive Brownian/traceless stochastic generator from the full action",
        "derive eta_l=8alpha/(9pi) rather than treating it as structural candidate",
        "derive global-curvature generation count rather than using ledger count",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "topographic_attractor_bridge_status": TOPOGRAPHIC_ATTRACTOR_BRIDGE_STRUCTURAL_CANDIDATE,
        "fourth_order_equation_status": FOURTH_ORDER_EQUATION_REPO_SUPPORTED,
        "particle_attractor_status": PARTICLE_ATTRACTOR_STRUCTURAL_CANDIDATE,
        "A_q_topographic_status": connection.A_q_topographic_status,
        "A_j_topographic_status": connection.A_j_topographic_status,
        "representation_boundary_connection_consequence_status": (
            connection.representation_boundary_connection_consequence_status
        ),
        "stochastic_dressing_status": STOCHASTIC_ATTRACTOR_DRESSING_STRUCTURAL_CANDIDATE,
        "quadratic_norm_status": "QUADRATIC_HOPF_BASE_NORM_STRUCTURAL_CANDIDATE",
        "geometric_inertia_status": GEOMETRIC_INERTIA_STRUCTURAL_CANDIDATE,
        "lepton_hierarchy_consequence_status": "LEPTON_ATTRACTOR_HIERARCHY_STRUCTURAL_CANDIDATE",
        "hadronic_hierarchy_consequence_status": (
            "HADRONIC_ATTRACTOR_HIERARCHY_STRUCTURAL_CANDIDATE"
        ),
        "generation_count_status": generation.status,
        "environmental_mass_shift_status": ENVIRONMENTAL_MASS_SHIFT_CANDIDATE_ONLY,
        "does_bridge_identify_A_q": connection.does_bridge_identify_A_q,
        "does_bridge_identify_A_j": connection.does_bridge_identify_A_j,
        "does_bridge_derive_exponential_dressing": False,
        "does_bridge_derive_lepton_8_9": False,
        "does_bridge_change_official_predictions": False,
        "ordinary_environmental_mass_drift_claim": safety.ordinary_environmental_mass_drift_claim,
        "lab_mass_variation_claim": safety.lab_mass_variation_claim,
        "extreme_event_candidate_only": safety.extreme_event_candidate_only,
        "full_SM_derivation_claim": safety.full_SM_derivation_claim,
        "SM_replacement_claim": safety.SM_replacement_claim,
        "time_dependent_constants_official_claim": safety.time_dependent_constants_official_claim,
        "ordinary_FTL_neutrino_claim": safety.ordinary_FTL_neutrino_claim,
        "blockers_closed": (
            "topographic_attractor_bridge_scaffold",
            "environmental_mass_shift_safety_gate",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (),
        "candidate_components": (
            "particle_attractor_states",
            "A_q_topographic_fiber_component",
            "A_j_topographic_base_component",
            "Brownian_exponential_dressing",
            "geometric_inertia_susceptibility",
            "global_curvature_generation_count",
            "extreme_event_environmental_susceptibility",
        ),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "eta_l_8alpha_9pi": lepton_eta_8alpha_9pi(resolved_alpha),
        "lepton_attractor_rows": _lepton_rows(resolved_alpha),
        "quark_attractor_rows": _quark_rows(),
        "generation_count": asdict(generation),
        "connection_component": asdict(connection),
        "claim_safety": asdict(safety),
        "environmental_shift_example_gate_zero": environmental_shift_candidate(
            delta_T=1.0,
            susceptibility=attractor_susceptibility_proxy(5, 2),
            gate=threshold_gate(0.0, threshold=1.0, power=2.0),
        ),
        "frozen_sanity": _frozen_sanity(),
    }
    return payload


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def render_markdown(payload: dict[str, Any] | None = None, title: str | None = None) -> str:
    """Render the audit payload as Markdown."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Topographic Attractor Boundary-Action Bridge"
    lines = [
        f"# {heading}",
        "",
        "This note records a candidate bridge from a fourth-order topographic field scaffold to the existing Hopf-Berger boundary connection and stochastic dressing language.",
        "It does not change frozen predictions and does not promote candidate dressing rules.",
        "",
        "## Problem",
        "",
        "The representation-valued boundary connection reproduces the charged-sector omega operators, but explicit boundary one-forms and the full boundary action remain open.",
        "",
        "## Candidate Bridge",
        "",
        "```text",
        "L_T T = S",
        "L_T = Laplacian - B Laplacian^2",
        "E[T, psi_f] = ||L_T T - S_f[psi_f]||^2 + lambda_BHSM ||D_BH psi_f||^2 + boundary terms",
        "```",
        "",
        f"Topographic bridge status: `{p['topographic_attractor_bridge_status']}`",
        f"Fourth-order equation status: `{p['fourth_order_equation_status']}`",
        f"Particle attractor status: `{p['particle_attractor_status']}`",
        f"A_q status: `{p['A_q_topographic_status']}`",
        f"A_j status: `{p['A_j_topographic_status']}`",
        f"Stochastic dressing status: `{p['stochastic_dressing_status']}`",
        f"Geometric inertia status: `{p['geometric_inertia_status']}`",
        "",
        "## Charged-Lepton Attractor Hierarchy",
        "",
        "The candidate quadratic norm is `N(k,j)=q^2+j^2`, with `q=k-2j`. Brownian damping is treated as `Z=exp[-eta N]`.",
        "",
        "| Label | Mode | q | N | Susceptibility Proxy | Inertia Proxy |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in p["lepton_attractor_rows"]:
        lines.append(
            f"| `{row['label']}` | `{tuple(row['mode'])}` | `{row['q']}` | `{row['N']}` | `{row['susceptibility_proxy']:.6g}` | `{row['geometric_inertia_proxy']:.6g}` |"
        )
    lines.extend(
        [
            "",
            "## Hadronic / Quark Hierarchy",
            "",
            "| Label | Mode | Sector | q | N | Pure Fiber | Inertia Proxy |",
            "| --- | --- | --- | ---: | ---: | --- | ---: |",
        ]
    )
    for row in p["quark_attractor_rows"]:
        lines.append(
            f"| `{row['label']}` | `{tuple(row['mode'])}` | `{row['sector']}` | `{row['q']}` | `{row['N']}` | `{row['pure_fiber']}` | `{row['geometric_inertia_proxy']:.6g}` |"
        )
    lines.extend(
        [
            "",
            "## Environmental Safety",
            "",
            f"Environmental mass-shift status: `{p['environmental_mass_shift_status']}`",
            f"Ordinary environmental mass drift claim: `{p['ordinary_environmental_mass_drift_claim']}`",
            f"Lab mass variation claim: `{p['lab_mass_variation_claim']}`",
            f"Extreme-event candidate only: `{p['extreme_event_candidate_only']}`",
            "",
            "## Generation Count",
            "",
            f"Generation count status: `{p['generation_count_status']}`",
            "The current audit treats global-curvature generation count as a structural candidate or ledger assumption, not a proof.",
            "",
            "## Blockers Remaining",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in p["blockers_remaining"])
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- Lab-scale mass variation is not asserted.",
            "- No official time-dependent constants claim is made.",
            "- No neutrino speed anomaly claim is made.",
            "- No Standard Model replacement or full derivation claim is made.",
            "- Lepton 8/9 remains unpromoted.",
            "",
        ]
    )
    return "\n".join(lines)


def export_topographic_attractor_bridge_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export the topographic-attractor bridge audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "theory_main": base / "theory" / "topographic_attractor_boundary_action_bridge.md",
        "stochastic": base / "theory" / "stochastic_attractor_dressing_candidate.md",
        "inertia": base / "theory" / "geometric_inertia_susceptibility_candidate.md",
        "generation": base / "theory" / "generation_count_global_curvature_candidate.md",
        "environment": base / "theory" / "environmental_mass_shift_safety_note.md",
        "AqAj": base / "theory" / "Aq_Aj_topographic_connection_candidate.md",
        "lepton": base / "theory" / "lepton_attractor_hierarchy_candidate.md",
        "quark": base / "theory" / "quark_attractor_hierarchy_candidate.md",
        "audit_py": base / "audits" / "topographic_attractor_boundary_action_bridge_audit.py",
        "audit_md": base / "audits" / "topographic_attractor_boundary_action_bridge_audit.md",
        "audit_json": base / "audits" / "topographic_attractor_boundary_action_bridge_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["theory_main"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    outputs["stochastic"].write_text(
        "# Stochastic Attractor Dressing Candidate\n\n"
        f"Status: `{payload['stochastic_dressing_status']}`\n\n"
        "`Z=exp[-eta N]` is consistent with a Brownian/Hessian damping analogy, with `N=q^2+j^2`. The exponential form and `eta_l=8alpha/(9pi)` remain candidate-only.\n",
        encoding="utf-8",
    )
    outputs["inertia"].write_text(
        "# Geometric Inertia Susceptibility Candidate\n\n"
        f"Status: `{payload['geometric_inertia_status']}`\n\n"
        "The proxy uses larger `1+N` as larger geometric inertia and smaller susceptibility. Quark coframe multiplicity is diagnostic only.\n",
        encoding="utf-8",
    )
    outputs["generation"].write_text(
        "# Generation Count Global Curvature Candidate\n\n"
        f"Status: `{payload['generation_count_status']}`\n\n"
        "The three-generation ledger is preserved. A cosmic/global-curvature explanation is candidate-only and not derived here.\n",
        encoding="utf-8",
    )
    outputs["environment"].write_text(
        "# Environmental Mass-Shift Safety Note\n\n"
        f"Status: `{payload['environmental_mass_shift_status']}`\n\n"
        "This file records only a threshold-gated extreme-event candidate. It makes no ordinary lab mass-drift or time-dependent-constant claim.\n",
        encoding="utf-8",
    )
    outputs["AqAj"].write_text(
        "# A_q / A_j Topographic Connection Candidate\n\n"
        f"A_q status: `{payload['A_q_topographic_status']}`\n\n"
        f"A_j status: `{payload['A_j_topographic_status']}`\n\n"
        "`A_q` is supported as a Hopf/fiber charge component. `A_j` remains a Berger/base structural candidate until an explicit one-form and action coupling are constructed.\n",
        encoding="utf-8",
    )
    outputs["lepton"].write_text(
        "# Lepton Attractor Hierarchy Candidate\n\n"
        "Tau has `N=0`, muon has `N=5`, and electron has `N=18`. This supports the qualitative susceptibility ordering but does not alter official lepton ratios.\n",
        encoding="utf-8",
    )
    outputs["quark"].write_text(
        "# Quark Attractor Hierarchy Candidate\n\n"
        f"Status: `{payload['hadronic_hierarchy_consequence_status']}`\n\n"
        "The pure-fiber middle-up half factor and light-up coframe ideas remain candidate-only. No quark or CKM output is changed.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_topographic_attractor_bridge_outputs()
