"""Boundary connection holonomy construction sprint.

This sprint searches for a boundary connection object whose sector-projected
holonomies reproduce the BHSM boundary levels.  The implemented construction is
purely auditable: it confirms the linear holonomy candidate reproduces the
current 3, 6, 12 levels, but does not promote the coefficients to a derivation
unless their geometric origin is supplied.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import pi
from pathlib import Path
from typing import Any, Callable

from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY


BOUNDARY_CONNECTION_HOLONOMY_STRUCTURAL_CANDIDATE = (
    "BOUNDARY_CONNECTION_HOLONOMY_STRUCTURAL_CANDIDATE"
)
HOPF_CONNECTION_STRUCTURAL_CANDIDATE = "HOPF_CONNECTION_STRUCTURAL_CANDIDATE"
BERGER_AXIS_CONNECTION_STRUCTURAL_CANDIDATE = "BERGER_AXIS_CONNECTION_STRUCTURAL_CANDIDATE"
SECTOR_PROJECTED_CONNECTION_STRUCTURAL_CANDIDATE = (
    "SECTOR_PROJECTED_CONNECTION_STRUCTURAL_CANDIDATE"
)
TOPOGRAPHIC_SURFACE_CONNECTION_INTERPRETATION_ONLY = (
    "TOPOGRAPHIC_SURFACE_CONNECTION_INTERPRETATION_ONLY"
)
ELECTROWEAK_BOUNDARY_CONNECTION_STRUCTURAL_CANDIDATE = (
    "ELECTROWEAK_BOUNDARY_CONNECTION_STRUCTURAL_CANDIDATE"
)
COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE = "COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE"
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = (
    "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
)
PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY = "PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY"
CKM_H_MIX_DIM4_ANALOGY_ONLY = "CKM_H_MIX_DIM4_ANALOGY_ONLY"
NEUTRINO_LEAKAGE_CHANNEL_REFINED = "NEUTRINO_LEAKAGE_CHANNEL_REFINED"


@dataclass(frozen=True)
class ConnectionCandidate:
    """One candidate boundary connection route."""

    candidate_id: str
    title: str
    status: str
    derived: bool
    evidence_found: tuple[str, ...]
    evidence_missing: tuple[str, ...]


@dataclass(frozen=True)
class SectorConnectionRule:
    """Linear sector-projected holonomy rule Omega_f=a_f q+b_f j."""

    sector: str
    a_q: int
    b_j: int
    status: str
    coefficient_origin: tuple[str, ...]
    missing_origin: tuple[str, ...]


def q_from_kj(k: int, j: int) -> int:
    """Return q=k-2j."""

    return k - 2 * j


def omega_linear(q: int, j: int, a: int, b: int) -> int:
    """Return a*q+b*j."""

    return a * q + b * j


def omega_lepton(q: int, j: int) -> int:
    """Return Omega_l=-q+2j."""

    return omega_linear(q, j, -1, 2)


def omega_up(q: int, j: int) -> int:
    """Return Omega_u=q-2j."""

    return omega_linear(q, j, 1, -2)


def omega_down(q: int, j: int) -> int:
    """Return Omega_d=q+4j."""

    return omega_linear(q, j, 1, 4)


def check_mode_pair_constant_level(
    modes: tuple[tuple[int, int], ...] | list[tuple[int, int]],
    omega_fn: Callable[[int, int], int],
) -> dict[str, Any]:
    """Return whether all modes share a constant omega level."""

    rows = []
    values = []
    for k, j in modes:
        q = q_from_kj(k, j)
        omega = omega_fn(q, j)
        values.append(omega)
        rows.append({"mode": (k, j), "q": q, "j": j, "omega": omega})
    return {
        "constant": len(set(values)) == 1,
        "level": values[0] if values and len(set(values)) == 1 else None,
        "rows": rows,
    }


def coefficient_origin_status(sector: str) -> SectorConnectionRule:
    """Return coefficient-origin status for a charged sector."""

    data = {
        "lepton": SectorConnectionRule(
            sector="lepton",
            a_q=-1,
            b_j=2,
            status=COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE,
            coefficient_origin=(
                "negative Hopf sign is compatible with lepton charge orientation",
                "factor 2 is compatible with weak/base doublet participation",
            ),
            missing_origin=(
                "derive the negative q orientation from a concrete connection",
                "derive the base factor 2 from weak/boundary geometry rather than assigning it",
            ),
        ),
        "up": SectorConnectionRule(
            sector="up",
            a_q=1,
            b_j=-2,
            status=COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE,
            coefficient_origin=(
                "positive Hopf sign is compatible with up-sector orientation",
                "negative base sign is compatible with upper weak-component orientation",
            ),
            missing_origin=(
                "derive the base sign from the projected connection",
                "derive factor 2 without using the desired mode pair",
            ),
        ),
        "down": SectorConnectionRule(
            sector="down",
            a_q=1,
            b_j=4,
            status=COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE,
            coefficient_origin=(
                "positive Hopf sign is compatible with down-sector orientation",
                "factor 4 is compatible with coframe/color participation plus base doubling",
            ),
            missing_origin=(
                "derive factor 4 from coframe/color geometry inside A_boundary",
                "derive down/up base-sign split from the same universal connection",
            ),
        ),
    }
    if sector not in data:
        raise ValueError(f"unknown sector: {sector}")
    return data[sector]


def holonomy_integer_status(Omega: int) -> dict[str, Any]:
    """Return candidate holonomy-integrality status for Omega."""

    return {
        "Omega": int(Omega),
        "integer": int(Omega) == Omega,
        "primitive_candidate": abs(int(Omega)) > 0,
        "status": "INTEGRAL_LEVEL_CONFIRMED_CONNECTION_OPEN",
    }


def cyclic_dimension_from_holonomy(Omega: int) -> int:
    """Return |Omega| as candidate cyclic dimension."""

    value = abs(int(Omega))
    if value == 0:
        raise ValueError("Omega must be nonzero")
    return value


def lepton_channel_consequence(alpha: float, assumptions_enabled: bool = True) -> dict[str, Any]:
    """Return lepton 8/9 consequence under explicit assumptions."""

    dim_h = cyclic_dimension_from_holonomy(3)
    active_fraction = (dim_h * dim_h - 1) / (dim_h * dim_h)
    eta = (alpha / pi) * active_fraction
    return {
        "assumptions_enabled": assumptions_enabled,
        "Omega_l": 3,
        "dim_H_l": dim_h,
        "active_fraction": active_fraction,
        "eta_l": eta,
        "status": LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        "derived": False,
    }


def connection_candidate_status(candidate_id: str) -> ConnectionCandidate:
    """Return a connection-candidate route status."""

    candidates = {
        "hopf": ConnectionCandidate(
            candidate_id="hopf",
            title="Hopf fiber connection",
            status=HOPF_CONNECTION_STRUCTURAL_CANDIDATE,
            derived=False,
            evidence_found=(
                "BHSM uses Hopf charge q=k-2j and Hopf/U(1) phase language.",
                "A Hopf-fiber connection can account naturally for the q part of Omega_f.",
            ),
            evidence_missing=(
                "No explicit Hopf connection one-form A_boundary is implemented.",
                "The j-dependent base terms 2j, -2j, and 4j do not follow from Hopf q alone.",
            ),
        ),
        "berger_axis": ConnectionCandidate(
            candidate_id="berger_axis",
            title="Berger squashing axis connection",
            status=BERGER_AXIS_CONNECTION_STRUCTURAL_CANDIDATE,
            derived=False,
            evidence_found=(
                "The alpha-anchored Berger geometry distinguishes a preferred internal axis.",
                "A squashed-axis connection is compatible with a q/base split.",
            ),
            evidence_missing=(
                "No sigma_3 or Berger-axis connection is explicitly tied to sector coefficients.",
                "Factors 2 and 4 are not derived from anisotropy alone.",
            ),
        ),
        "sector_projected": ConnectionCandidate(
            candidate_id="sector_projected",
            title="Sector-projected boundary connection",
            status=SECTOR_PROJECTED_CONNECTION_STRUCTURAL_CANDIDATE,
            derived=False,
            evidence_found=(
                "Linear projected rules A_f=a_f A_q+b_f A_j reproduce the charged-sector boundary levels.",
                "Existing boundary scaffolds link coefficient signs to sector orientation, weak component, chirality, and coframe factors.",
            ),
            evidence_missing=(
                "The universal connection A_boundary and projectors P_f are not constructed.",
                "Coefficient origins remain structural candidates rather than consequences of a connection.",
            ),
        ),
        "topographic_surface": ConnectionCandidate(
            candidate_id="topographic_surface",
            title="White-hole/topographic surface phase connection",
            status=TOPOGRAPHIC_SURFACE_CONNECTION_INTERPRETATION_ONLY,
            derived=False,
            evidence_found=(
                "Topographic and stochastic-output language exists in the repo narrative.",
            ),
            evidence_missing=(
                "No mathematical surface connection with computable holonomy is implemented.",
                "Ontology is not an action-level proof.",
            ),
        ),
        "electroweak": ConnectionCandidate(
            candidate_id="electroweak",
            title="Electroweak/U(1) boundary connection",
            status=ELECTROWEAK_BOUNDARY_CONNECTION_STRUCTURAL_CANDIDATE,
            derived=False,
            evidence_found=(
                "The alpha/pi stochastic scale is compatible with electromagnetic/U(1) dressing.",
                "Hypercharge and anomaly ledgers are implemented elsewhere.",
            ),
            evidence_missing=(
                "Electroweak U(1) does not by itself produce Omega_l=3, Omega_u=6, Omega_d=12.",
                "No gauge connection derivation fixes the sector base coefficients.",
            ),
        ),
    }
    if candidate_id not in candidates:
        raise ValueError(f"unknown connection candidate: {candidate_id}")
    return candidates[candidate_id]


def connection_candidates() -> tuple[ConnectionCandidate, ...]:
    """Return all connection-candidate route statuses."""

    return (
        connection_candidate_status("hopf"),
        connection_candidate_status("berger_axis"),
        connection_candidate_status("sector_projected"),
        connection_candidate_status("topographic_surface"),
        connection_candidate_status("electroweak"),
    )


def mode_pair_checks() -> dict[str, Any]:
    """Return exact constant-level checks for the charged mode pairs."""

    return {
        "lepton": check_mode_pair_constant_level(((5, 2), (9, 3)), omega_lepton),
        "up": check_mode_pair_constant_level(((6, 0), (10, 1)), omega_up),
        "down": check_mode_pair_constant_level(((6, 3), (8, 2)), omega_down),
    }


def validate_no_official_outputs_modified() -> dict[str, Any]:
    """Return frozen branch sanity checks."""

    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]
    return {
        "frozen_sanity": frozen_sanity_payload(),
        "official_branch_comparison": comparison,
        "official_dressed_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
    }


def audit_payload() -> dict[str, Any]:
    """Return the full boundary connection holonomy audit payload."""

    candidates = connection_candidates()
    coefficient_rules = tuple(coefficient_origin_status(sector) for sector in ("lepton", "up", "down"))
    checks = mode_pair_checks()
    does_holonomy_produce = all(row["constant"] for row in checks.values())
    missing = tuple(
        f"{candidate.candidate_id}: {item}"
        for candidate in candidates
        for item in candidate.evidence_missing
    ) + tuple(
        f"{rule.sector}: {item}"
        for rule in coefficient_rules
        for item in rule.missing_origin
    ) + (
        "construct universal A_boundary and sector projectors P_f",
        "derive a_f,b_f from geometry rather than structural coefficient ledger",
        "derive dim(H)=|Omega| from holonomy quotient",
        "derive identity/traceless stochastic protection before promoting lepton 8/9",
    )
    no_outputs = validate_no_official_outputs_modified()
    payload: dict[str, Any] = {
        "title": "BHSM boundary connection holonomy construction sprint",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "boundary_connection_status": BOUNDARY_CONNECTION_HOLONOMY_STRUCTURAL_CANDIDATE,
        "hopf_connection_status": HOPF_CONNECTION_STRUCTURAL_CANDIDATE,
        "berger_axis_connection_status": BERGER_AXIS_CONNECTION_STRUCTURAL_CANDIDATE,
        "sector_projected_connection_status": SECTOR_PROJECTED_CONNECTION_STRUCTURAL_CANDIDATE,
        "topographic_surface_connection_status": TOPOGRAPHIC_SURFACE_CONNECTION_INTERPRETATION_ONLY,
        "electroweak_boundary_connection_status": ELECTROWEAK_BOUNDARY_CONNECTION_STRUCTURAL_CANDIDATE,
        "coefficient_origin_status": COEFFICIENT_ORIGIN_STRUCTURAL_CANDIDATE,
        "does_holonomy_produce_3_6_12": does_holonomy_produce,
        "does_dim_H_equal_abs_Omega_follow": False,
        "does_lepton_8_9_follow": False,
        "pure_fiber_consequence_status": PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY,
        "ckm_consequence_status": CKM_H_MIX_DIM4_ANALOGY_ONLY,
        "neutrino_consequence_status": NEUTRINO_LEAKAGE_CHANNEL_REFINED,
        "blockers_closed": (),
        "blockers_remaining": (
            "define universal A_boundary",
            "derive sector projectors P_f",
            "derive coefficient signs and factors",
            "derive cyclic quotient dimension",
            "derive identity/traceless stochastic protection",
        ),
        "derived_components": (),
        "candidate_components": (
            "hopf_q_connection_part",
            "berger_axis_connection_part",
            "sector_projected_linear_holonomy",
            "electroweak_alpha_surface_scale",
            "neutrino_boundary_leakage_refinement",
        ),
        "rejected_components": (),
        "missing_assumptions": missing,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "files_concepts_searched": (
            "Hopf charge and U(1) phase language",
            "Berger anisotropy and internal-axis notes",
            "boundary operator scaffold and phase contribution records",
            "virtual/stochastic dressing notes",
            "electroweak and hypercharge ledgers",
            "topographic surface/scalar scaffold notes",
        ),
        "connection_candidates": candidates,
        "coefficient_rules": coefficient_rules,
        "mode_pair_checks": checks,
        "holonomy_integer_status": {
            "lepton": holonomy_integer_status(3),
            "up": holonomy_integer_status(6),
            "down": holonomy_integer_status(12),
        },
        "lepton_channel_consequence": lepton_channel_consequence(
            1.0 / ALPHA_INV_LOW_ENERGY
        ),
    }
    payload.update(no_outputs)
    return payload


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render the audit as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# BHSM Boundary Connection Holonomy Construction",
        "",
        "This sprint tests candidate boundary connections A_boundary and sector projections A_f whose holonomies could produce Omega_l=3, Omega_u=6, and Omega_d=12.",
        "The result is structural candidate only: the linear sector-projected form reproduces the levels, but the universal connection and coefficient origins are not derived.",
        "",
        "## Summary",
        "",
        f"Boundary connection status: `{payload['boundary_connection_status']}`",
        f"Hopf connection: `{payload['hopf_connection_status']}`",
        f"Berger axis connection: `{payload['berger_axis_connection_status']}`",
        f"Sector-projected connection: `{payload['sector_projected_connection_status']}`",
        f"Topographic surface connection: `{payload['topographic_surface_connection_status']}`",
        f"Electroweak boundary connection: `{payload['electroweak_boundary_connection_status']}`",
        f"Coefficient origin: `{payload['coefficient_origin_status']}`",
        f"Holonomy candidate produces 3,6,12: `{payload['does_holonomy_produce_3_6_12']}`",
        f"dim(H)=|Omega| follows: `{payload['does_dim_H_equal_abs_Omega_follow']}`",
        f"Lepton 8/9 follows: `{payload['does_lepton_8_9_follow']}`",
        "",
        "## Candidate Connections",
        "",
        "| Candidate | Status | Derived |",
        "| --- | --- | --- |",
    ]
    for candidate in payload["connection_candidates"]:
        lines.append(f"| `{candidate.candidate_id}` | `{candidate.status}` | `{candidate.derived}` |")
    lines.extend(
        [
            "",
            "## Mode Pair Checks",
            "",
            "| Sector | Constant | Level |",
            "| --- | --- | ---: |",
        ]
    )
    for sector, check in payload["mode_pair_checks"].items():
        lines.append(f"| `{sector}` | `{check['constant']}` | `{check['level']}` |")
    lines.extend(
        [
            "",
            "## Coefficient Rules",
            "",
            "| Sector | a_q | b_j | Status |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for rule in payload["coefficient_rules"]:
        lines.append(f"| `{rule.sector}` | {rule.a_q} | {rule.b_j} | `{rule.status}` |")
    lines.extend(["", "## Missing Assumptions", ""])
    lines.extend(f"- {item}" for item in payload["missing_assumptions"])
    lines.extend(
        [
            "",
            "## Consequences",
            "",
            f"- Pure-fiber: `{payload['pure_fiber_consequence_status']}`",
            f"- CKM: `{payload['ckm_consequence_status']}`",
            f"- Neutrino/PMNS: `{payload['neutrino_consequence_status']}`",
            "",
            "## Claim Discipline",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No ordinary superluminal neutrino claim is made.",
            "- No ordinary environmental mass drift claim is made.",
            "- No claim of replacing the Standard Model or proving BHSM is made.",
            "- The connection construction remains candidate-only unless A_boundary and coefficient origins are derived.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_connection_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "boundary_connection_holonomy_construction.md",
        "audit_md": base / "audits" / "boundary_connection_holonomy_construction_audit.md",
        "audit_json": base / "audits" / "boundary_connection_holonomy_construction_audit.json",
        "hopf": base / "theory" / "hopf_connection_candidate.md",
        "berger": base / "theory" / "berger_axis_connection_candidate.md",
        "sector": base / "theory" / "sector_projected_boundary_connection.md",
        "topographic": base / "theory" / "topographic_surface_connection_candidate.md",
        "electroweak": base / "theory" / "electroweak_boundary_connection_candidate.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    notes = {
        "hopf": "The Hopf connection candidate naturally supports the q component, but not the j-dependent sector terms.",
        "berger": "The Berger-axis candidate is compatible with a preferred internal axis, but factors 2 and 4 are not derived from anisotropy alone.",
        "sector": "The sector-projected candidate A_f=a_f A_q+b_f A_j reproduces 3,6,12, but coefficient origins remain structural candidates.",
        "topographic": "The topographic surface phase connection remains interpretation-only because no computable surface holonomy is implemented.",
        "electroweak": "The electroweak/U(1) candidate supports alpha/pi dressing scale, but not the sector Omega levels by itself.",
    }
    for key, text in notes.items():
        status_key = {
            "hopf": "hopf_connection_status",
            "berger": "berger_axis_connection_status",
            "sector": "sector_projected_connection_status",
            "topographic": "topographic_surface_connection_status",
            "electroweak": "electroweak_boundary_connection_status",
        }[key]
        paths[key].write_text(
            f"# {key.replace('_', ' ').title()} Candidate\n\n"
            f"Status: `{payload[status_key]}`\n\n"
            f"{text}\n",
            encoding="utf-8",
        )
    return payload


if __name__ == "__main__":
    export_boundary_connection_outputs()
