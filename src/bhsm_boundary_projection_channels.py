"""Boundary projection-channel theorem sprint.

This module organizes several BHSM candidate mechanisms under one boundary
projection-channel framework.  It intentionally does not promote any candidate
to the frozen model: the theorem remains a structural candidate unless the
channel spaces and projection rules are independently derived.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import pi
from pathlib import Path
from typing import Any

from bhsm_completion_manual_theory_delta import (
    frozen_sanity_payload,
    lepton_eta_delta_payload,
    neutrino_leakage_payload,
)
from bhsm_sequential_blocker_closure import (
    BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN,
)
from bhsm_v1 import compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY
from mode_selection import hopf_charge, omega_down, omega_lepton, omega_up


THEOREM_STATUS = "BOUNDARY_PROJECTION_CHANNEL_STRUCTURAL_CANDIDATE"
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = (
    "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
)
PURE_FIBER_RANK_HALF_STRUCTURAL_CANDIDATE = (
    "PURE_FIBER_RANK_HALF_STRUCTURAL_CANDIDATE"
)
CKM_1_16_CHANNEL_DILUTION_STRUCTURAL_CANDIDATE = (
    "CKM_1_16_CHANNEL_DILUTION_STRUCTURAL_CANDIDATE"
)
BOUNDARY_ACTION_STRUCTURAL_CANDIDATE = "BOUNDARY_ACTION_STRUCTURAL_CANDIDATE"
NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE = "NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE"

BLOCKERS = (
    "lepton_8alpha_9pi",
    "pure_fiber_one_half",
    "ckm_one_sixteenth",
    "boundary_action",
    "neutrino_pmns",
)


@dataclass(frozen=True)
class ChannelComponentStatus:
    """Status record for one projection-channel component."""

    blocker_id: str
    status: str
    closed: bool
    candidate_only: bool
    structural_rule: str
    computed_value: float | str | dict[str, Any]
    missing_assumptions: tuple[str, ...]
    evidence: tuple[str, ...]


def active_channel_fraction(d: int) -> float:
    """Return (d^2 - 1) / d^2 for a positive channel dimension."""

    if d <= 0:
        raise ValueError("channel dimension must be positive")
    return float((d * d - 1) / (d * d))


def lepton_eta_channel_rule(alpha: float, Omega_l: int = 3) -> float:
    """Return eta_l = (alpha/pi) * active_channel_fraction(Omega_l)."""

    return float((alpha / pi) * active_channel_fraction(Omega_l))


def pure_fiber_rank_projection(dim: int = 2, rank: int = 1) -> float:
    """Return rank/dim for a candidate pure-fiber projection."""

    if dim <= 0:
        raise ValueError("projection dimension must be positive")
    if rank < 0 or rank > dim:
        raise ValueError("rank must satisfy 0 <= rank <= dim")
    return float(rank / dim)


def ckm_channel_dilution(Z_mass: float = 0.5, dim_H_mix: int = 4) -> float:
    """Return Z_mass^(1/dim(End(H_mix))) for a candidate mixing channel."""

    if Z_mass <= 0:
        raise ValueError("Z_mass must be positive")
    if dim_H_mix <= 0:
        raise ValueError("mixing channel dimension must be positive")
    return float(Z_mass ** (1.0 / (dim_H_mix * dim_H_mix)))


def boundary_operator_values() -> dict[str, dict[str, Any]]:
    """Return current charged-sector boundary values for the frozen ledger."""

    modes = {
        "lepton_middle": ("lepton", (5, 2), omega_lepton),
        "lepton_light": ("lepton", (9, 3), omega_lepton),
        "up_middle": ("up", (6, 0), omega_up),
        "up_light": ("up", (10, 1), omega_up),
        "down_middle": ("down", (6, 3), omega_down),
        "down_light": ("down", (8, 2), omega_down),
    }
    out: dict[str, dict[str, Any]] = {}
    for label, (sector, mode, omega_fn) in modes.items():
        k, j = mode
        out[label] = {
            "sector": sector,
            "mode": mode,
            "q": hopf_charge(k, j),
            "omega": omega_fn(k, j),
        }
    return out


def lepton_component(alpha: float | None = None) -> ChannelComponentStatus:
    """Return the charged-lepton 8/9 channel-rule status."""

    alpha = alpha if alpha is not None else 1.0 / ALPHA_INV_LOW_ENERGY
    manual = lepton_eta_delta_payload()
    preferred = manual["preferred_candidate"]
    return ChannelComponentStatus(
        blocker_id="lepton_8alpha_9pi",
        status=LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        closed=False,
        candidate_only=True,
        structural_rule="eta_l=(alpha/pi)*((Omega_l^2-1)/Omega_l^2), Omega_l=3",
        computed_value=lepton_eta_channel_rule(alpha, 3),
        missing_assumptions=(
            "derive H_l with dimension Omega_l from the boundary action",
            "derive End(H_l) as the stochastic covariance channel algebra",
            "derive identity/coherent-channel protection",
            "derive Brownian activity only on traceless channels",
        ),
        evidence=(
            "active_channel_fraction(3)=8/9",
            f"preferred prior eta_l={preferred.eta_l}",
            f"mu/tau relative error under prior candidate={preferred.mu_tau_relative_error}",
            f"e/tau relative error under prior candidate={preferred.e_tau_relative_error}",
        ),
    )


def pure_fiber_component() -> ChannelComponentStatus:
    """Return the pure-fiber half-projection status."""

    return ChannelComponentStatus(
        blocker_id="pure_fiber_one_half",
        status=PURE_FIBER_RANK_HALF_STRUCTURAL_CANDIDATE,
        closed=False,
        candidate_only=True,
        structural_rule="Z_virt^{u,2}=rank(P_phys)/dim(H_fiber)=1/2 for mode (6,0)",
        computed_value=pure_fiber_rank_projection(2, 1),
        missing_assumptions=(
            "derive a two-orientation virtual space for nonzero pure-fiber modes",
            "derive rank-one physical mass projection",
            "derive locality to middle-up (6,0) without touching u/t or CKM",
        ),
        evidence=(
            "middle-up mode (6,0) has j=0 and q=6",
            "official dressed branch changes only c/t",
        ),
    )


def _ckm_candidate_summary() -> dict[str, Any]:
    path = Path("audits") / "bhsm_mixing_dressed_v1_candidate_audit.json"
    if not path.exists():
        return {
            "available": False,
            "improves_vcb": None,
            "improves_vts": None,
            "j_damage_flag": None,
            "non_23_damage_flag": None,
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "available": True,
        "z_mix_23": data["z_mix_23"],
        "improves_vcb": data["improves_vcb"],
        "improves_vts": data["improves_vts"],
        "j_damage_flag": data["j_damage_flag"],
        "non_23_damage_flag": data["non_23_damage_flag"],
    }


def ckm_component() -> ChannelComponentStatus:
    """Return the CKM 1/16 channel-dilution status."""

    summary = _ckm_candidate_summary()
    return ChannelComponentStatus(
        blocker_id="ckm_one_sixteenth",
        status=CKM_1_16_CHANNEL_DILUTION_STRUCTURAL_CANDIDATE,
        closed=False,
        candidate_only=True,
        structural_rule="Z_mix=Z_mass^(1/dim(End(H_mix))), dim(H_mix)=4",
        computed_value=ckm_channel_dilution(0.5, 4),
        missing_assumptions=(
            "derive dim(H_mix)=4 from internal left-handed overlap channels",
            "derive End(H_mix) as the correct correlation algebra",
            "derive that mass dressing dilutes across all 16 channels",
            "derive Z_mass=1/2 independently before using it in CKM",
        ),
        evidence=(
            "ckm_channel_dilution(1/2,4)=(1/2)^(1/16)",
            f"existing audit summary={summary}",
        ),
    )


def boundary_action_component() -> ChannelComponentStatus:
    """Return the boundary-action channel-form status."""

    values = boundary_operator_values()
    return ChannelComponentStatus(
        blocker_id="boundary_action",
        status=BOUNDARY_ACTION_STRUCTURAL_CANDIDATE,
        closed=False,
        candidate_only=True,
        structural_rule="S_boundary contains lambda_f (Omega_f-Omega_f0)^2 |psi|^2",
        computed_value=values,
        missing_assumptions=(
            "derive the boundary penalty term by variation of the complete action",
            "derive sector signs and base/fiber coefficients rather than inserting them",
            "derive primitive constant boundary levels as stationary non-heavy modes",
            "link channel dimension d_f to Omega_f without circular use of selected modes",
        ),
        evidence=(
            "current omega values recover lepton/up/down mode pairs",
            f"previous status={BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN}",
        ),
    )


def neutrino_component() -> ChannelComponentStatus:
    """Return the candidate-only neutrino/PMNS leakage ledger status."""

    payload = neutrino_leakage_payload()
    ledger = {
        "neutrino_interpretation": "neutral leakage modes, weakly field-attached and less boundary-pinned",
        "boundary_channel_space": "candidate broad leakage channel space; dimension not derived",
        "PMNS_status": "effective-extension screen only",
        "mass_hierarchy_status": "open",
        "ordinary_FTL_claim": False,
        "candidate_only": True,
        "required_future_inputs": (
            "neutrino leakage operator",
            "neutral mode spectrum",
            "PMNS mixing derivation from channel overlap",
        ),
    }
    return ChannelComponentStatus(
        blocker_id="neutrino_pmns",
        status=NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE,
        closed=False,
        candidate_only=True,
        structural_rule="neutral leakage channels may sample broader PMNS mixing spaces than CKM",
        computed_value=ledger,
        missing_assumptions=(
            "derive neutral leakage channel space",
            "derive PMNS angles or mass splittings from the leakage operator",
            "derive mass hierarchy rather than using effective screens",
        ),
        evidence=(
            payload["interpretation"],
            "ordinary_FTL_claim=False",
            "PMNS rows remain effective-extension screens",
        ),
    )


def theorem_components() -> tuple[ChannelComponentStatus, ...]:
    """Return all boundary projection-channel components."""

    return (
        lepton_component(),
        pure_fiber_component(),
        ckm_component(),
        boundary_action_component(),
        neutrino_component(),
    )


def audit_payload() -> dict[str, Any]:
    """Return a JSON-serializable boundary projection-channel audit."""

    components = theorem_components()
    closed = tuple(component.blocker_id for component in components if component.closed)
    remaining = tuple(component.blocker_id for component in components if not component.closed)
    missing = tuple(
        f"{component.blocker_id}: {assumption}"
        for component in components
        for assumption in component.missing_assumptions
    )
    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]
    return {
        "title": "BHSM boundary projection-channel theorem sprint",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "theorem_status": THEOREM_STATUS,
        "lepton_status": LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        "pure_fiber_status": PURE_FIBER_RANK_HALF_STRUCTURAL_CANDIDATE,
        "ckm_status": CKM_1_16_CHANNEL_DILUTION_STRUCTURAL_CANDIDATE,
        "boundary_action_status": BOUNDARY_ACTION_STRUCTURAL_CANDIDATE,
        "neutrino_status": NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE,
        "components": components,
        "blockers_closed": closed,
        "blockers_remaining": remaining,
        "candidate_components": remaining,
        "derived_components": (),
        "rejected_components": (),
        "missing_assumptions": missing,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "active_fraction_d3": active_channel_fraction(3),
        "lepton_eta_8alpha_9pi": lepton_eta_channel_rule(1.0 / ALPHA_INV_LOW_ENERGY, 3),
        "pure_fiber_half": pure_fiber_rank_projection(2, 1),
        "ckm_z_one_sixteenth": ckm_channel_dilution(0.5, 4),
        "boundary_operator_values": boundary_operator_values(),
        "neutrino_ledger": neutrino_component().computed_value,
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
        "# BHSM Boundary Projection-Channel Theorem Sprint",
        "",
        "This sprint tests whether several BHSM candidate correction factors can be organized by protected versus active boundary projection-channel dimensions.",
        "The result is candidate-only: the channel dimensions and algebras are not yet derived from the complete action or spectrum.",
        "",
        "## Summary",
        "",
        f"Theorem status: `{payload['theorem_status']}`",
        f"Official outputs modified: `{payload['official_outputs_modified']}`",
        f"Frozen predictions modified: `{payload['frozen_predictions_modified']}`",
        f"PRs opened: `{payload['prs_opened']}`",
        f"Safe to merge as candidate-only: `{payload['safe_to_merge_as_candidate_only']}`",
        "",
        "## Core Channel Rule",
        "",
        "For a candidate sector boundary channel space H_f with dimension d_f:",
        "",
        "```text",
        "dim End(H_f) = d_f^2",
        "F_active(d_f) = (d_f^2 - 1) / d_f^2",
        "```",
        "",
        f"For d=3, `F_active(3)={payload['active_fraction_d3']}`.",
        "",
        "## Component Table",
        "",
        "| Blocker | Status | Closed | Structural rule | Computed value |",
        "| --- | --- | --- | --- | --- |",
    ]
    for component in payload["components"]:
        lines.append(
            f"| `{component.blocker_id}` | `{component.status}` | `{component.closed}` | {component.structural_rule} | `{component.computed_value}` |"
        )
    lines.extend(["", "## Missing Assumptions", ""])
    lines.extend(f"- {item}" for item in payload["missing_assumptions"])
    lines.extend(
        [
            "",
            "## Boundary Operator Values",
            "",
            "| Mode label | Sector | Mode | q | Omega |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    for label, row in payload["boundary_operator_values"].items():
        lines.append(
            f"| `{label}` | `{row['sector']}` | `{tuple(row['mode'])}` | {row['q']} | {row['omega']} |"
        )
    lines.extend(
        [
            "",
            "## Neutrino/PMNS Leakage Ledger",
            "",
        ]
    )
    for key, value in payload["neutrino_ledger"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Claim Discipline",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No ordinary superluminal neutrino claim is made.",
            "- No ordinary environmental mass drift claim is made.",
            "- No claim of replacing the Standard Model or proving BHSM is made.",
            "- All mechanisms remain candidate-only unless the missing assumptions are later derived.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_projection_channel_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory, audit, and optional component notes."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "boundary_projection_channel_theorem.md",
        "audit_md": base / "audits" / "boundary_projection_channel_theorem_audit.md",
        "audit_json": base / "audits" / "boundary_projection_channel_theorem_audit.json",
        "lepton": base / "theory" / "lepton_8_9_channel_rule.md",
        "fiber": base / "theory" / "pure_fiber_rank_half_rule.md",
        "ckm": base / "theory" / "ckm_1_16_channel_dilution.md",
        "boundary": base / "theory" / "boundary_action_channel_form.md",
        "neutrino": base / "theory" / "neutrino_pmns_leakage_channel_ledger.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    by_id = {component.blocker_id: component for component in payload["components"]}
    component_paths = {
        "lepton": by_id["lepton_8alpha_9pi"],
        "fiber": by_id["pure_fiber_one_half"],
        "ckm": by_id["ckm_one_sixteenth"],
        "boundary": by_id["boundary_action"],
        "neutrino": by_id["neutrino_pmns"],
    }
    for key, component in component_paths.items():
        paths[key].write_text(
            "\n".join(
                [
                    f"# {component.blocker_id}",
                    "",
                    f"Status: `{component.status}`",
                    f"Closed: `{component.closed}`",
                    f"Candidate only: `{component.candidate_only}`",
                    "",
                    f"Structural rule: `{component.structural_rule}`",
                    f"Computed value: `{component.computed_value}`",
                    "",
                    "Evidence:",
                    *[f"- {item}" for item in component.evidence],
                    "",
                    "Missing assumptions:",
                    *[f"- {item}" for item in component.missing_assumptions],
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return payload


if __name__ == "__main__":
    export_boundary_projection_channel_outputs()
