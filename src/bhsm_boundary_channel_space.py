"""Boundary channel-space construction sprint.

This module tests whether a primitive BHSM boundary level Omega_f can define a
finite channel space H_f with dim(H_f)=|Omega_f|.  The arithmetic consequences
are implemented directly; the theorem status remains candidate-level unless
the cyclic boundary quotient and identity-channel protection are independently
derived from the full action or spectrum.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import pi
from pathlib import Path
from typing import Any

from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY
from mode_selection import hopf_charge, omega_down, omega_lepton, omega_up


BOUNDARY_CHANNEL_SPACE_STRUCTURAL_CANDIDATE = (
    "BOUNDARY_CHANNEL_SPACE_STRUCTURAL_CANDIDATE"
)
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = (
    "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
)
PURE_FIBER_DOUBLE_CHANNEL_SUPPORTED_BY_ANALOGY = (
    "PURE_FIBER_DOUBLE_CHANNEL_SUPPORTED_BY_ANALOGY"
)
CKM_MIX_CHANNEL_SPACE_SUPPORTED_BY_ANALOGY = (
    "CKM_MIX_CHANNEL_SPACE_SUPPORTED_BY_ANALOGY"
)
NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE = "NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE"


@dataclass(frozen=True)
class ChannelRoute:
    """One tested route for dim(H_f)=|Omega_f|."""

    route_id: str
    title: str
    status: str
    supports_dimension_rule: bool
    derived: bool
    evidence: tuple[str, ...]
    missing_assumptions: tuple[str, ...]


@dataclass(frozen=True)
class ChannelSpaceReport:
    """Compact theorem status report."""

    theorem_status: str
    lepton_status: str
    pure_fiber_consequence_status: str
    ckm_consequence_status: str
    neutrino_consequence_status: str
    does_dim_H_equal_abs_Omega_follow: bool
    does_identity_channel_protection_follow: bool
    does_active_traceless_fraction_follow: bool
    blockers_closed: tuple[str, ...]
    blockers_remaining: tuple[str, ...]


def boundary_level_abs(Omega: int) -> int:
    """Return |Omega|, rejecting the zero level as a non-channel target."""

    value = abs(int(Omega))
    if value == 0:
        raise ValueError("primitive boundary channel level must be nonzero")
    return value


def cyclic_channel_dimension(Omega: int) -> int:
    """Return the candidate cyclic channel dimension |Omega|."""

    return boundary_level_abs(Omega)


def end_channel_count(dim_H: int) -> int:
    """Return dim End(H) = dim(H)^2."""

    if dim_H <= 0:
        raise ValueError("dim_H must be positive")
    return dim_H * dim_H


def active_traceless_count(dim_H: int) -> int:
    """Return dim End(H)-1 for candidate traceless active channels."""

    return end_channel_count(dim_H) - 1


def active_fraction_from_dim(dim_H: int) -> float:
    """Return the candidate active traceless fraction."""

    return float(active_traceless_count(dim_H) / end_channel_count(dim_H))


def active_fraction_from_Omega(Omega: int) -> float:
    """Return active fraction using dim(H)=|Omega|."""

    return active_fraction_from_dim(cyclic_channel_dimension(Omega))


def lepton_eta_from_channel_space(alpha: float, Omega_l: int = 3) -> float:
    """Return eta_l=(alpha/pi)*active_fraction_from_Omega(Omega_l)."""

    return float((alpha / pi) * active_fraction_from_Omega(Omega_l))


def charged_sector_boundary_levels() -> dict[str, dict[str, Any]]:
    """Return frozen charged-sector mode-pair boundary levels."""

    rows = {
        "lepton_middle": ("lepton", (5, 2), omega_lepton),
        "lepton_light": ("lepton", (9, 3), omega_lepton),
        "up_middle": ("up", (6, 0), omega_up),
        "up_light": ("up", (10, 1), omega_up),
        "down_middle": ("down", (6, 3), omega_down),
        "down_light": ("down", (8, 2), omega_down),
    }
    out: dict[str, dict[str, Any]] = {}
    for label, (sector, mode, omega_fn) in rows.items():
        k, j = mode
        omega = omega_fn(k, j)
        out[label] = {
            "sector": sector,
            "mode": mode,
            "q": hopf_charge(k, j),
            "omega": omega,
            "candidate_dim_H": cyclic_channel_dimension(omega),
            "end_channels": end_channel_count(cyclic_channel_dimension(omega)),
        }
    return out


def route_a_boundary_winding() -> ChannelRoute:
    """Test Route A: primitive boundary winding quantization."""

    return ChannelRoute(
        route_id="A",
        title="Boundary winding quantization",
        status="STRUCTURAL_CANDIDATE",
        supports_dimension_rule=True,
        derived=False,
        evidence=(
            "Omega_f values are integer primitive boundary levels on the supplied charged-sector ledger.",
            "A cyclic residue basis |r>, r=0,...,|Omega_f|-1 would give dim(H_f)=|Omega_f|.",
        ),
        missing_assumptions=(
            "derive boundary equivalence modulo Omega_f",
            "derive exactly |Omega_f| inequivalent channel residues",
            "derive primitive winding interpretation from the complete boundary action",
        ),
    )


def route_b_holonomy_phase() -> ChannelRoute:
    """Test Route B: cyclic holonomy or phase quantization."""

    return ChannelRoute(
        route_id="B",
        title="Holonomy phase quantization",
        status="STRUCTURAL_CANDIDATE",
        supports_dimension_rule=True,
        derived=False,
        evidence=(
            "A Z_Omega phase basis exp(2*pi*i*n/Omega_f) would naturally have |Omega_f| states.",
            "Existing BHSM notes use Hopf and boundary-phase language.",
        ),
        missing_assumptions=(
            "derive that Omega_f sets the phase denominator",
            "derive the cyclic phase representation without choosing it post hoc",
            "derive compatibility with sector boundary signs and cofactors",
        ),
    )


def route_c_boundary_algebra() -> ChannelRoute:
    """Test Route C: finite cyclic boundary algebra."""

    return ChannelRoute(
        route_id="C",
        title="Finite boundary algebra representation",
        status="STRUCTURAL_CANDIDATE",
        supports_dimension_rule=True,
        derived=False,
        evidence=(
            "The regular representation of C[Z_|Omega_f|] has dimension |Omega_f|.",
            "The identity element of the algebra suggests a coherent protected channel candidate.",
        ),
        missing_assumptions=(
            "derive the quotient algebra A_f=C[Z_|Omega_f|] from the boundary operator",
            "derive that the regular representation is the stochastic channel space",
            "derive identity-channel protection rather than assuming it",
        ),
    )


def route_d_stationary_boundary_action() -> ChannelRoute:
    """Test Route D: stationary boundary action."""

    return ChannelRoute(
        route_id="D",
        title="Stationary boundary action",
        status="STRUCTURAL_CANDIDATE",
        supports_dimension_rule=True,
        derived=False,
        evidence=(
            "A penalty lambda_f*(Omega_f-Omega_f0)^2 would make non-heavy stationary modes sit on Omega_f0.",
            "The current mode-pair invariants already sit on constant levels 3, 6, and 12.",
        ),
        missing_assumptions=(
            "derive the boundary penalty term by variation of the full action",
            "derive residual |Omega_f0| channels after stationarity",
            "derive sector coefficients and signs before selecting the modes",
        ),
    )


def channel_routes() -> tuple[ChannelRoute, ...]:
    """Return all tested channel-space derivation routes."""

    return (
        route_a_boundary_winding(),
        route_b_holonomy_phase(),
        route_c_boundary_algebra(),
        route_d_stationary_boundary_action(),
    )


def theorem_report() -> ChannelSpaceReport:
    """Return the honest theorem-status report."""

    return ChannelSpaceReport(
        theorem_status=BOUNDARY_CHANNEL_SPACE_STRUCTURAL_CANDIDATE,
        lepton_status=LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        pure_fiber_consequence_status=PURE_FIBER_DOUBLE_CHANNEL_SUPPORTED_BY_ANALOGY,
        ckm_consequence_status=CKM_MIX_CHANNEL_SPACE_SUPPORTED_BY_ANALOGY,
        neutrino_consequence_status=NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE,
        does_dim_H_equal_abs_Omega_follow=False,
        does_identity_channel_protection_follow=False,
        does_active_traceless_fraction_follow=False,
        blockers_closed=(),
        blockers_remaining=(
            "derive dim(H_f)=|Omega_f| from boundary quotient/holonomy/action",
            "derive identity-channel protection",
            "derive traceless-channel Brownian activity",
            "derive pure-fiber doublet rather than analogy",
            "derive CKM dim(H_mix)=4 rather than analogy",
        ),
    )


def audit_payload() -> dict[str, Any]:
    """Return a JSON-serializable channel-space audit payload."""

    report = theorem_report()
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]
    routes = channel_routes()
    missing = tuple(
        f"Route {route.route_id}: {item}"
        for route in routes
        for item in route.missing_assumptions
    ) + report.blockers_remaining
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    return {
        "title": "BHSM boundary channel-space construction sprint",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "theorem_status": report.theorem_status,
        "lepton_status": report.lepton_status,
        "pure_fiber_consequence_status": report.pure_fiber_consequence_status,
        "ckm_consequence_status": report.ckm_consequence_status,
        "neutrino_consequence_status": report.neutrino_consequence_status,
        "derived_components": (),
        "candidate_components": (
            "boundary_channel_space",
            "lepton_8_9",
            "pure_fiber_analogy",
            "ckm_mix_analogy",
            "neutrino_leakage",
        ),
        "rejected_components": (),
        "missing_assumptions": missing,
        "does_dim_H_equal_abs_Omega_follow": report.does_dim_H_equal_abs_Omega_follow,
        "does_identity_channel_protection_follow": report.does_identity_channel_protection_follow,
        "does_active_traceless_fraction_follow": report.does_active_traceless_fraction_follow,
        "blockers_closed": report.blockers_closed,
        "blockers_remaining": report.blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "routes": routes,
        "boundary_levels": charged_sector_boundary_levels(),
        "calculations": {
            "cyclic_channel_dimension_3": cyclic_channel_dimension(3),
            "end_channel_count_3": end_channel_count(3),
            "active_traceless_count_3": active_traceless_count(3),
            "active_fraction_from_dim_3": active_fraction_from_dim(3),
            "lepton_eta_8alpha_9pi": lepton_eta_from_channel_space(alpha, 3),
        },
        "pure_fiber_consequence": (
            "The cyclic-channel language is compatible by analogy with a two-orientation pure-fiber space, "
            "but it does not derive that doublet."
        ),
        "ckm_consequence": (
            "The End-space channel language is compatible by analogy with a 16-channel CKM 2-3 correlation space, "
            "but it does not derive dim(H_mix)=4."
        ),
        "neutrino_consequence": {
            "ordinary_FTL_claim": False,
            "candidate_only": True,
            "no_numerical_PMNS_claims": True,
            "note": (
                "Neutral leakage modes may occupy weakly field-attached residual boundary channels rather than "
                "charged EM-dressed channels."
            ),
        },
        "frozen_sanity": frozen_sanity_payload(),
        "official_branch_comparison": comparison,
        "official_dressed_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
    }


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
    """Render the audit payload as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# BHSM Boundary Channel-Space Construction",
        "",
        "This sprint tests whether a primitive boundary level Omega_f constructs a finite channel space H_f with dim(H_f)=|Omega_f|.",
        "The result remains structural and candidate-only: the quotient, holonomy, or action derivation is not yet complete.",
        "",
        "## Summary",
        "",
        f"Theorem status: `{payload['theorem_status']}`",
        f"Lepton status: `{payload['lepton_status']}`",
        f"Pure-fiber consequence: `{payload['pure_fiber_consequence_status']}`",
        f"CKM consequence: `{payload['ckm_consequence_status']}`",
        f"Neutrino consequence: `{payload['neutrino_consequence_status']}`",
        f"dim(H)=|Omega| follows: `{payload['does_dim_H_equal_abs_Omega_follow']}`",
        f"Identity-channel protection follows: `{payload['does_identity_channel_protection_follow']}`",
        f"Active traceless fraction follows: `{payload['does_active_traceless_fraction_follow']}`",
        "",
        "## Calculations",
        "",
        "| Quantity | Value |",
        "| --- | ---: |",
    ]
    for key, value in payload["calculations"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Tested Routes",
            "",
            "| Route | Title | Status | Supports rule | Derived |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for route in payload["routes"]:
        lines.append(
            f"| `{route.route_id}` | {route.title} | `{route.status}` | `{route.supports_dimension_rule}` | `{route.derived}` |"
        )
    lines.extend(["", "## Boundary Levels", ""])
    lines.extend(
        [
            "| Mode label | Sector | Mode | q | Omega | Candidate dim(H) | End channels |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for label, row in payload["boundary_levels"].items():
        lines.append(
            f"| `{label}` | `{row['sector']}` | `{tuple(row['mode'])}` | {row['q']} | {row['omega']} | {row['candidate_dim_H']} | {row['end_channels']} |"
        )
    lines.extend(["", "## Missing Assumptions", ""])
    lines.extend(f"- {item}" for item in payload["missing_assumptions"])
    lines.extend(
        [
            "",
            "## Consequences",
            "",
            f"- Pure-fiber: {payload['pure_fiber_consequence']}",
            f"- CKM: {payload['ckm_consequence']}",
            f"- Neutrino: {payload['neutrino_consequence']['note']}",
            "",
            "## Claim Discipline",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No ordinary superluminal neutrino claim is made.",
            "- No ordinary environmental mass drift claim is made.",
            "- No claim of replacing the Standard Model or proving BHSM is made.",
            "- The 8/9 lepton factor remains candidate-only until identity protection and traceless activity are derived.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_channel_space_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "boundary_channel_space_construction.md",
        "audit_md": base / "audits" / "boundary_channel_space_construction_audit.md",
        "audit_json": base / "audits" / "boundary_channel_space_construction_audit.json",
        "lepton": base / "theory" / "lepton_channel_space_8_9_consequence.md",
        "holonomy": base / "theory" / "boundary_cyclic_holonomy_candidate.md",
        "algebra": base / "theory" / "boundary_algebra_representation_candidate.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["lepton"].write_text(
        "\n".join(
            [
                "# Lepton Channel-Space 8/9 Consequence",
                "",
                f"Status: `{payload['lepton_status']}`",
                "",
                "If dim(H_l)=Omega_l=3 and if the identity channel is protected while traceless channels are active, then:",
                "",
                "```text",
                "dim End(H_l)=9",
                "active traceless channels=8",
                "eta_l=(alpha/pi)*(8/9)",
                "```",
                "",
                "This sprint does not derive the identity protection or Brownian traceless-channel rule, so the result remains candidate-only.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["holonomy"].write_text(
        "\n".join(
            [
                "# Boundary Cyclic Holonomy Candidate",
                "",
                "A boundary phase basis exp(2*pi*i*n/Omega_f) would produce |Omega_f| channel states.",
                "The remaining task is to derive Omega_f as the phase denominator from the complete boundary action.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["algebra"].write_text(
        "\n".join(
            [
                "# Boundary Algebra Representation Candidate",
                "",
                "The regular representation of C[Z_|Omega_f|] has dimension |Omega_f|.",
                "The remaining task is to derive this quotient algebra and show that its regular representation is the stochastic channel space.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_boundary_channel_space_outputs()
