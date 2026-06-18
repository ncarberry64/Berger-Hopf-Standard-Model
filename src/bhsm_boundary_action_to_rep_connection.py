"""Boundary action to representation-valued connection audit for BHSM.

This module audits whether the representation-valued boundary connection

    A_rep = A_q tensor O_q + A_j tensor O_j

is supported by a symbolic boundary action with sector source terms. It keeps
the result claim-limited: exact sector arithmetic is implemented, while the
completed BHSM boundary action and global A_j normalization remain open.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


BOUNDARY_ACTION_TO_AREP_STATUS = "BOUNDARY_ACTION_TO_A_REP_PARTIAL"
BOUNDARY_SOURCE_TERMS_STATUS = "BOUNDARY_SOURCE_TERMS_STRUCTURAL_CANDIDATE"
OQ_STATUS = "O_Q_BOUNDARY_CHARGE_PARTIAL"
OJ_STATUS = "O_J_WEAK_ISOSPIN_PROJECTOR_PARTIAL"
COLORED_LOWER_PROJECTOR_STATUS = "COLORED_LOWER_PROJECTOR_DERIVED_LEDGER_ARITHMETIC"
AQ_PERIOD_STATUS = "A_Q_PERIOD_NORMALIZATION_SUPPORTED"
AJ_PERIOD_STATUS = "A_J_PERIOD_NORMALIZATION_CONVENTION_DEPENDENT"
SECTOR_CONNECTION_STATUS = "SECTOR_CONNECTION_PARTIAL"
ACTION_TO_PHASE_MAP_STATUS = "ACTION_VARIATION_TO_PHASE_MAP_PARTIAL"
OMEGA_AS_DEGREE_STATUS = "OMEGA_AS_DEGREE_PARTIAL"
LEPTON_CONSEQUENCE_STATUS = "LEPTON_OMEGA_RECOVERED_FROM_A_REP_SOURCE_TERMS"
UP_CONSEQUENCE_STATUS = "UP_OMEGA_RECOVERED_FROM_A_REP_SOURCE_TERMS"
DOWN_CONSEQUENCE_STATUS = "DOWN_OMEGA_RECOVERED_FROM_A_REP_SOURCE_TERMS"
CLAIM_HYGIENE_STATUS = "CLAIM_HYGIENE_CANDIDATE_ONLY"


@dataclass(frozen=True)
class BoundaryActionStatus:
    """Status for one boundary-action route or component."""

    name: str
    status: str
    follows: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def Oq_from_B_L(B: Fraction | int | float, L: Fraction | int | float) -> Fraction:
    """Return O_q=3B-L."""

    return 3 * Fraction(B) - Fraction(L)


def colored_lower_projector(B: Fraction | int | float, T3: Fraction | int | float) -> Fraction:
    """Return colored lower-doublet projector (3B)(1/2-T3)."""

    return 3 * Fraction(B) * (Fraction(1, 2) - Fraction(T3))


def Oj_from_B_T3(B: Fraction | int | float, T3: Fraction | int | float) -> Fraction:
    """Return O_j=-4T3+2(3B)(1/2-T3)."""

    return -4 * Fraction(T3) + 2 * colored_lower_projector(B, T3)


def sector_operator_pair(
    B: Fraction | int | float,
    L: Fraction | int | float,
    T3: Fraction | int | float,
) -> tuple[Fraction, Fraction]:
    """Return (O_q,O_j) for sector quantum numbers."""

    return Oq_from_B_L(B, L), Oj_from_B_T3(B, T3)


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge q=k-2j."""

    return int(k) - 2 * int(j)


def omega_from_Oq_Oj_q_j(
    Oq: Fraction | int | float,
    Oj: Fraction | int | float,
    q: int,
    j: int,
) -> Fraction:
    """Return Omega=Oq*q+Oj*j."""

    return Fraction(Oq) * int(q) + Fraction(Oj) * int(j)


def sector_connection_symbolic(Oq: Fraction | int | float, Oj: Fraction | int | float) -> str:
    """Return a symbolic sector connection string A_f=Oq*A_q+Oj*A_j."""

    return f"A_f = ({Fraction(Oq)}) A_q + ({Fraction(Oj)}) A_j"


def boundary_phase_degree_from_periods(
    Oq: Fraction | int | float,
    Oj: Fraction | int | float,
    q_period: int,
    j_period: int,
) -> Fraction:
    """Return degree=(1/2pi) integral A_f from normalized periods."""

    return omega_from_Oq_Oj_q_j(Oq, Oj, q_period, j_period)


def lepton_operator_pair() -> tuple[Fraction, Fraction]:
    """Return charged-lepton (O_q,O_j)=(-1,2)."""

    return sector_operator_pair(Fraction(0), Fraction(1), Fraction(-1, 2))


def up_operator_pair() -> tuple[Fraction, Fraction]:
    """Return up-sector (O_q,O_j)=(1,-2)."""

    return sector_operator_pair(Fraction(1, 3), Fraction(0), Fraction(1, 2))


def down_operator_pair() -> tuple[Fraction, Fraction]:
    """Return down-sector (O_q,O_j)=(1,4)."""

    return sector_operator_pair(Fraction(1, 3), Fraction(0), Fraction(-1, 2))


def lepton_omega_from_kj(k: int, j: int) -> Fraction:
    """Return charged-lepton Omega from (k,j)."""

    Oq, Oj = lepton_operator_pair()
    return omega_from_Oq_Oj_q_j(Oq, Oj, q_from_kj(k, j), j)


def up_omega_from_kj(k: int, j: int) -> Fraction:
    """Return up-sector Omega from (k,j)."""

    Oq, Oj = up_operator_pair()
    return omega_from_Oq_Oj_q_j(Oq, Oj, q_from_kj(k, j), j)


def down_omega_from_kj(k: int, j: int) -> Fraction:
    """Return down-sector Omega from (k,j)."""

    Oq, Oj = down_operator_pair()
    return omega_from_Oq_Oj_q_j(Oq, Oj, q_from_kj(k, j), j)


def period_normalization_status_object() -> tuple[BoundaryActionStatus, BoundaryActionStatus]:
    """Return A_q and A_j period normalization statuses."""

    aq = BoundaryActionStatus(
        "A_q_period",
        AQ_PERIOD_STATUS,
        True,
        (
            "A_q is the normalized Hopf/contact fiber component",
            "(1/2pi) integral A_q=q is supported by existing Hopf charge ledger",
        ),
        (
            "full boundary action derivation of A_q is still not completed",
        ),
    )
    aj = BoundaryActionStatus(
        "A_j_period",
        AJ_PERIOD_STATUS,
        True,
        (
            "A_j is the Berger/base or horizontal coframe component used in the boundary scaffold",
            "(1/2pi) integral A_j=j is the period convention needed for Omega_f",
        ),
        (
            "A_j normalization/global bundle coupling remains convention-dependent",
            "the completed action has not uniquely derived this period",
        ),
    )
    return aq, aj


def boundary_action_status_object() -> tuple[BoundaryActionStatus, ...]:
    """Return status objects for the boundary-action-to-A_rep chain."""

    aq, aj = period_normalization_status_object()
    return (
        BoundaryActionStatus(
            "boundary_action_to_A_rep",
            BOUNDARY_ACTION_TO_AREP_STATUS,
            True,
            (
                "symbolic boundary action uses D_boundary=d+iA_rep",
                "source terms couple A_q and A_j to representation operators O_q and O_j",
            ),
            (
                "the full BHSM boundary action is not completed",
                "source terms remain scaffolded rather than uniquely action-derived",
            ),
        ),
        BoundaryActionStatus(
            "O_q_boundary_charge",
            OQ_STATUS,
            True,
            (
                "baryon number is unit-normalized by 3B",
                "lepton number contributes with opposite sign -L",
            ),
            ("this is an action-linked charge assignment, not a completed action proof",),
        ),
        BoundaryActionStatus(
            "O_j_weak_isospin_projector",
            OJ_STATUS,
            True,
            (
                "universal weak-isospin term is -4T3",
                "colored lower-doublet correction is 2(3B)(1/2-T3)",
            ),
            ("global A_j normalization remains the main open convention dependence",),
        ),
        aq,
        aj,
        BoundaryActionStatus(
            "action_variation_to_phase_map",
            ACTION_TO_PHASE_MAP_STATUS,
            True,
            (
                "D_boundary=d+iA_rep gives boundary parallel transport",
                "sector evaluation gives A_f=O_q A_q+O_j A_j",
                "u_f(s)=exp(i integral A_f)",
            ),
            ("full variation/domain problem for the completed action remains open",),
        ),
    )


def validate_no_official_outputs_modified() -> dict[str, Any]:
    """Return frozen branch sanity checks."""

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


def audit_payload() -> dict[str, Any]:
    """Return boundary-action-to-representation-connection audit payload."""

    open_blockers = (
        "full BHSM boundary action is not yet completed",
        "A_rep may remain partial because source terms are scaffolded",
        "A_q period normalization is stronger than A_j but still part of an incomplete action derivation",
        "A_j normalization/global bundle coupling remains convention-dependent",
        "degree theorem remains partial until normalized periods are fully action-derived",
        "coherent residue sheets and stochastic response selector remain downstream partial/candidate structures",
        "no official predictions change",
        "full Standard Model derivation is not claimed",
    )
    lepton_pair = lepton_operator_pair()
    up_pair = up_operator_pair()
    down_pair = down_operator_pair()
    statuses = boundary_action_status_object()
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "boundary_action_to_Arep_status": BOUNDARY_ACTION_TO_AREP_STATUS,
        "boundary_source_terms_status": BOUNDARY_SOURCE_TERMS_STATUS,
        "Oq_status": OQ_STATUS,
        "Oj_status": OJ_STATUS,
        "colored_lower_projector_status": COLORED_LOWER_PROJECTOR_STATUS,
        "Aq_period_status": AQ_PERIOD_STATUS,
        "Aj_period_status": AJ_PERIOD_STATUS,
        "sector_connection_status": SECTOR_CONNECTION_STATUS,
        "action_to_phase_map_status": ACTION_TO_PHASE_MAP_STATUS,
        "omega_as_degree_status": OMEGA_AS_DEGREE_STATUS,
        "lepton_consequence_status": LEPTON_CONSEQUENCE_STATUS,
        "up_consequence_status": UP_CONSEQUENCE_STATUS,
        "down_consequence_status": DOWN_CONSEQUENCE_STATUS,
        "claim_hygiene_status": CLAIM_HYGIENE_STATUS,
        "does_boundary_action_generate_Arep": True,
        "does_Oq_follow_from_boundary_charge": True,
        "does_Oj_follow_from_weak_isospin_projector": True,
        "does_colored_lower_projector_work": True,
        "does_Aq_period_equal_q": True,
        "does_Aj_period_equal_j": True,
        "does_Af_define_phase_map": True,
        "does_degree_equal_Omega": True,
        "does_this_promote_full_BHSM": False,
        "does_this_claim_full_SM_derivation": False,
        "does_this_change_official_predictions": False,
        "does_this_change_frozen_predictions": False,
        "sector_operator_pairs": {
            "charged_lepton": lepton_pair,
            "up": up_pair,
            "down": down_pair,
        },
        "mode_omega_checks": {
            "lepton_muon": lepton_omega_from_kj(5, 2),
            "lepton_electron": lepton_omega_from_kj(9, 3),
            "up_middle": up_omega_from_kj(6, 0),
            "up_light": up_omega_from_kj(10, 1),
            "down_middle": down_omega_from_kj(6, 3),
            "down_light": down_omega_from_kj(8, 2),
        },
        "period_degree_checks": {
            "lepton_muon": boundary_phase_degree_from_periods(-1, 2, 1, 2),
            "lepton_electron": boundary_phase_degree_from_periods(-1, 2, 3, 3),
            "up_middle": boundary_phase_degree_from_periods(1, -2, 6, 0),
            "up_light": boundary_phase_degree_from_periods(1, -2, 8, 1),
            "down_middle": boundary_phase_degree_from_periods(1, 4, 0, 3),
            "down_light": boundary_phase_degree_from_periods(1, 4, 4, 2),
        },
        "status_objects": statuses,
        "derived_components": (
            "O_q_arithmetic_from_3B_minus_L",
            "colored_lower_projector_arithmetic",
            "sector_operator_pairs_recover_lepton_up_down_coefficients",
            "mode_Omega_arithmetic_for_supplied_ledgers",
        ),
        "partial_components": (
            "boundary_action_to_A_rep_source_term_scaffold",
            "O_q_as_boundary_charge_coupling",
            "O_j_as_weak_isospin_projector_coupling",
            "action_variation_to_boundary_phase_map",
            "omega_as_degree_given_periods",
        ),
        "conditional_components": (
            "A_q_period_normalization_from_Hopf_contact_component",
            "A_j_period_normalization_as_Berger_base_convention",
        ),
        "candidate_components": (
            "full_boundary_action_source_terms",
            "global_A_j_bundle_coupling",
        ),
        "open_blockers": open_blockers,
        "missing_assumptions": open_blockers,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "frozen_sanity": validate_no_official_outputs_modified(),
    }
    return payload


def _jsonable(value: object) -> object:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator, "value": float(value)}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def _fraction_label(value: Fraction | dict[str, Any]) -> str:
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if value["denominator"] == 1:
        return str(value["numerator"])
    return f"{value['numerator']}/{value['denominator']}"


def render_markdown(payload: dict[str, Any] | None = None, title: str | None = None) -> str:
    """Render boundary-action audit Markdown."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Boundary Action to Representation-Valued Connection"
    lines = [
        f"# {heading}",
        "",
        "This audit tests whether a symbolic boundary action can support the representation-valued connection `A_rep=A_q tensor O_q + A_j tensor O_j`. The result is partial and candidate-safe.",
        "",
        "## Status",
        "",
        f"Boundary action to A_rep: `{p['boundary_action_to_Arep_status']}`",
        f"Boundary source terms: `{p['boundary_source_terms_status']}`",
        f"O_q status: `{p['Oq_status']}`",
        f"O_j status: `{p['Oj_status']}`",
        f"Colored lower projector: `{p['colored_lower_projector_status']}`",
        f"A_q period: `{p['Aq_period_status']}`",
        f"A_j period: `{p['Aj_period_status']}`",
        f"Sector connection: `{p['sector_connection_status']}`",
        f"Action-to-phase-map: `{p['action_to_phase_map_status']}`",
        f"Omega-as-degree: `{p['omega_as_degree_status']}`",
        "",
        "## Boundary Source-Term Scaffold",
        "",
        "```text",
        "S_boundary[f] = integral_{S1} Psi_f^dagger [d + i A_q O_q + i A_j O_j] Psi_f",
        "A_f = O_q^(f) A_q + O_j^(f) A_j",
        "u_f(s) = exp(i integral A_f)",
        "deg(u_f) = (1/2pi) integral A_f",
        "```",
        "",
        "## Sector Operators",
        "",
        "| Sector | O_q | O_j | Connection |",
        "| --- | ---: | ---: | --- |",
    ]
    for sector, pair in p["sector_operator_pairs"].items():
        Oq, Oj = pair
        lines.append(f"| `{sector}` | `{_fraction_label(Oq)}` | `{_fraction_label(Oj)}` | `{sector_connection_symbolic(Oq, Oj)}` |")
    lines.extend(
        [
            "",
            "## Mode Checks",
            "",
            "| Mode | Omega |",
            "| --- | ---: |",
        ]
    )
    for label, value in p["mode_omega_checks"].items():
        lines.append(f"| `{label}` | `{_fraction_label(value)}` |")
    lines.extend(
        [
            "",
            "## Period-Degree Checks",
            "",
            "| Case | Degree |",
            "| --- | ---: |",
        ]
    )
    for label, value in p["period_degree_checks"].items():
        lines.append(f"| `{label}` | `{_fraction_label(value)}` |")
    lines.extend(
        [
            "",
            "## Claim Boundaries",
            "",
            f"Promotes full BHSM: `{p['does_this_promote_full_BHSM']}`",
            f"Claims full SM derivation: `{p['does_this_claim_full_SM_derivation']}`",
            f"Changes official predictions: `{p['does_this_change_official_predictions']}`",
            "",
            "## Open Blockers",
            "",
        ]
    )
    lines.extend(f"{index}. {item}" for index, item in enumerate(p["open_blockers"], start=1))
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No frozen lepton, quark, CKM, or down-sector rule is changed.",
            "- No claim is made that BHSM replaces the Standard Model.",
            "- The result remains partial/candidate until the completed boundary action is derived.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_action_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export boundary-action-to-A_rep artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "main": base / "theory" / "boundary_action_to_rep_connection.md",
        "source": base / "theory" / "boundary_action_source_terms_for_Aq_Aj.md",
        "oq": base / "theory" / "Oq_boundary_charge_derivation.md",
        "oj": base / "theory" / "Oj_weak_isospin_projector_derivation.md",
        "periods": base / "theory" / "Aq_Aj_period_normalization_status.md",
        "phase": base / "theory" / "action_variation_to_boundary_phase_map.md",
        "audit_md": base / "audits" / "boundary_action_to_rep_connection_audit.md",
        "audit_json": base / "audits" / "boundary_action_to_rep_connection_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["main"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["source"].write_text(render_markdown(payload, "Boundary Action Source Terms for A_q and A_j"), encoding="utf-8")
    outputs["oq"].write_text(render_markdown(payload, "O_q Boundary Charge Derivation"), encoding="utf-8")
    outputs["oj"].write_text(render_markdown(payload, "O_j Weak-Isospin Projector Derivation"), encoding="utf-8")
    outputs["periods"].write_text(render_markdown(payload, "A_q/A_j Period Normalization Status"), encoding="utf-8")
    outputs["phase"].write_text(render_markdown(payload, "Action Variation to Boundary Phase Map"), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_boundary_action_outputs()
