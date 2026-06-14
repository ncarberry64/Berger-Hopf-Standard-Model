"""Sequential BHSM blocker-closure audit.

This sprint attempts the remaining derivation blockers in a fixed order and
records the honest result.  It does not modify frozen outputs or promote any
candidate mechanism.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bhsm_completion_manual_theory_delta import (
    CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED,
    LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED,
    NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY,
    PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED,
    SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED,
    ckm_four_projection_payload,
    frozen_sanity_payload,
    lepton_eta_delta_payload,
    neutrino_leakage_payload,
    pure_fiber_doublet_payload,
)
from bhsm_v1 import compare_bhsm_v1_branches


BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN = (
    "BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN"
)

BLOCKER_ORDER = (
    "lepton_8alpha_9pi",
    "pure_fiber_one_half",
    "boundary_action",
    "ckm_one_sixteenth",
    "neutrino_pmns",
)


@dataclass(frozen=True)
class BlockerAttempt:
    """One ordered derivation attempt."""

    blocker_id: str
    target: str
    status: str
    closed: bool
    candidate_only: bool
    evidence_found: tuple[str, ...]
    closure_requirements: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    exact_obstruction: str
    official_outputs_changed: bool


def lepton_blocker_attempt() -> BlockerAttempt:
    """Attempt Blocker 1: screened charged-lepton eta_l."""

    lepton = lepton_eta_delta_payload()
    preferred = lepton["preferred_candidate"]
    return BlockerAttempt(
        blocker_id="lepton_8alpha_9pi",
        target="eta_l=(alpha/pi)*(1-1/Omega_l^2)=8alpha/(9pi)",
        status=SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED,
        closed=False,
        candidate_only=True,
        evidence_found=(
            "Omega_l=3 is present in boundary operator and mode-selection files.",
            "The screened candidate improves mu/tau and e/tau relative to baseline.",
            f"Preferred eta_l={preferred.eta_l}.",
            f"mu/tau relative error={preferred.mu_tau_relative_error}.",
            f"e/tau relative error={preferred.e_tau_relative_error}.",
        ),
        closure_requirements=(
            "Omega_l=3 justified independently",
            "Omega_l^2 channel counting justified",
            "exactly one coherent/protected channel justified",
            "8/9 follows without residual fitting",
        ),
        missing_requirements=(
            "No repository action/spectrum argument forces Omega_l^2 as a channel count.",
            "No proof identifies exactly one coherent lepton boundary channel.",
        ),
        exact_obstruction=(
            "The 8/9 screen is structurally plausible but remains an interpretive channel-count rule."
        ),
        official_outputs_changed=False,
    )


def pure_fiber_blocker_attempt() -> BlockerAttempt:
    """Attempt Blocker 2: pure-fiber Z_virt^{u,2}=1/2."""

    payload = pure_fiber_doublet_payload()
    return BlockerAttempt(
        blocker_id="pure_fiber_one_half",
        target="Z_virt^{u,2}=1/2 for middle-up mode (6,0)",
        status=PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED,
        closed=False,
        candidate_only=True,
        evidence_found=(
            "Middle-up mode (6,0) has j=0 and is a nonzero pure-fiber mode.",
            "Existing virtual-environment notes interpret a half projection as plausible.",
            payload["rule"],
        ),
        closure_requirements=(
            "j=0, k!=0 forces two virtual fiber-orientation branches",
            "physical mass projection has rank one of two",
            "factor is not inferred from c/t residual",
        ),
        missing_requirements=(
            "No existing Berger/Hopf action or spectrum proves a two-branch doublet for every nonzero pure-fiber mode.",
            "No rank-one physical projection theorem is implemented.",
        ),
        exact_obstruction="The half factor remains a pure-fiber doublet candidate, not a forced spectral result.",
        official_outputs_changed=False,
    )


def boundary_action_blocker_attempt() -> BlockerAttempt:
    """Attempt Blocker 3: action-level origin of boundary operators."""

    return BlockerAttempt(
        blocker_id="boundary_action",
        target="action-level origin of Omega_l, Omega_u, Omega_d",
        status=BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN,
        closed=False,
        candidate_only=True,
        evidence_found=(
            "Mode-pair invariants are exact for the current charged-sector ledger.",
            "Omega_l=-q+2j=3, Omega_u=q-2j=6, Omega_d=q+4j=12 recover the non-heavy modes.",
            "Boundary scaffolds are action-linked and tested, but not uniquely varied from the full action.",
        ),
        closure_requirements=(
            "variational principle forces primitive constant boundary levels",
            "sector signs and coefficients follow from sector structure",
            "mode-pair invariance is a consequence rather than an input",
        ),
        missing_requirements=(
            "No full action variation derives the sector boundary functional.",
            "No stationarity proof fixes the signs/coefficient choices uniquely.",
        ),
        exact_obstruction=(
            "The boundary operators are strongly structured and mode-pair invariant, but their full action origin remains open."
        ),
        official_outputs_changed=False,
    )


def ckm_blocker_attempt() -> BlockerAttempt:
    """Attempt Blocker 4: CKM 1/16 exponent."""

    payload = ckm_four_projection_payload()
    return BlockerAttempt(
        blocker_id="ckm_one_sixteenth",
        target="Z_mix=Z_mass^(1/16)",
        status=CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED,
        closed=False,
        candidate_only=True,
        evidence_found=(
            "Existing CKM candidate improves Vcb and Vts without J_CKM damage.",
            "Official CKM sin_theta_13 remains unchanged.",
            "Four projection layers are documented as an interpretive chain.",
        ),
        closure_requirements=(
            "mass/probability to amplitude square-root layer independently justified",
            "internal mode to left-handed weak component square-root layer independently justified",
            "up-sector dressing to up/down mismatch square-root layer independently justified",
            "diagonal mass dressing to off-diagonal correlation square-root layer independently justified",
        ),
        missing_requirements=(
            "All four projection layers are not independently supported by action/spectrum proofs.",
            "Blocker 2 is not closed, so the Z_mass input is still candidate-level.",
        ),
        exact_obstruction=payload["layer_support"],
        official_outputs_changed=False,
    )


def neutrino_blocker_attempt() -> BlockerAttempt:
    """Attempt Blocker 5: neutrino/PMNS candidate ledger."""

    payload = neutrino_leakage_payload()
    return BlockerAttempt(
        blocker_id="neutrino_pmns",
        target="candidate-only neutrino/PMNS leakage ledger",
        status=NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY,
        closed=False,
        candidate_only=True,
        evidence_found=(
            "PMNS effective-extension screens already exist in pmns.py.",
            "Existing ledgers explicitly keep neutrino masses outside the minimal Standard Model.",
            payload["interpretation"],
        ),
        closure_requirements=(
            "derive an actual neutrino mode ledger",
            "derive PMNS structure from leakage/topological modes",
            "avoid ordinary faster-than-light interpretation",
        ),
        missing_requirements=(
            "No full neutrino leakage operator or mode spectrum is implemented.",
            "No new numerical PMNS claim is derived in this sprint.",
        ),
        exact_obstruction="The ledger can be stated safely as candidate-only, but no full neutrino/PMNS derivation is present.",
        official_outputs_changed=False,
    )


def ordered_blocker_attempts() -> tuple[BlockerAttempt, ...]:
    """Return blocker attempts in required order."""

    return (
        lepton_blocker_attempt(),
        pure_fiber_blocker_attempt(),
        boundary_action_blocker_attempt(),
        ckm_blocker_attempt(),
        neutrino_blocker_attempt(),
    )


def audit_payload() -> dict[str, Any]:
    """Return full sequential blocker closure audit payload."""

    attempts = ordered_blocker_attempts()
    blockers_closed = tuple(attempt.blocker_id for attempt in attempts if attempt.closed)
    blockers_remaining = tuple(attempt.blocker_id for attempt in attempts if not attempt.closed)
    candidate_components = tuple(attempt.blocker_id for attempt in attempts if attempt.candidate_only)
    derived_components: tuple[str, ...] = ()
    rejected_components = (
        "forced closure of lepton 8/9 without channel-count proof",
        "forced pure-fiber 1/2 without doublet/rank theorem",
        "official CKM promotion without four projection proofs",
    )
    return {
        "title": "BHSM sequential blocker closure audit",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "blocker_order": BLOCKER_ORDER,
        "attempts": attempts,
        "blockers_closed": blockers_closed,
        "blockers_remaining": blockers_remaining,
        "candidate_components": candidate_components,
        "derived_components": derived_components,
        "rejected_components": rejected_components,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "frozen_sanity": frozen_sanity_payload(),
        "official_branch_comparison": compare_bhsm_v1_branches(),
        "best_derivation_found": None,
        "best_candidate_only_strengthening": (
            "The screened lepton eta_l=8alpha/(9pi) and pure-fiber/CKM projection explanations are clearer, "
            "but remain candidate-only."
        ),
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
    """Render sequential blocker audit as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# BHSM Sequential Blocker Closure",
        "",
        "This sprint attempts the remaining derivation blockers in strict order. No official outputs are changed.",
        "",
        "## Summary",
        "",
        f"Official outputs modified: `{payload['official_outputs_modified']}`",
        f"Frozen predictions modified: `{payload['frozen_predictions_modified']}`",
        f"PRs opened: `{payload['prs_opened']}`",
        f"Safe to merge as candidate-only: `{payload['safe_to_merge_as_candidate_only']}`",
        "",
        "## Ordered Attempts",
        "",
        "| Order | Blocker | Status | Closed | Exact obstruction |",
        "| --- | --- | --- | --- | --- |",
    ]
    for index, attempt in enumerate(payload["attempts"], start=1):
        lines.append(
            f"| {index} | `{attempt.blocker_id}` | `{attempt.status}` | `{attempt.closed}` | {attempt.exact_obstruction} |"
        )
    lines.extend(["", "## Detailed Attempts", ""])
    for attempt in payload["attempts"]:
        lines.extend(
            [
                f"### {attempt.blocker_id}",
                "",
                f"Target: `{attempt.target}`",
                f"Status: `{attempt.status}`",
                f"Closed: `{attempt.closed}`",
                "",
                "Evidence found:",
            ]
        )
        lines.extend(f"- {item}" for item in attempt.evidence_found)
        lines.extend(["", "Missing requirements:"])
        lines.extend(f"- {item}" for item in attempt.missing_requirements)
        lines.append("")
    lines.extend(
        [
            "## Final Lists",
            "",
            f"Blockers closed: `{list(payload['blockers_closed'])}`",
            f"Blockers remaining: `{list(payload['blockers_remaining'])}`",
            f"Candidate components: `{list(payload['candidate_components'])}`",
            f"Derived components: `{list(payload['derived_components'])}`",
            f"Rejected components: `{list(payload['rejected_components'])}`",
            "",
            "## Claim Discipline",
            "",
            "- No ordinary faster-than-light neutrino claim is made.",
            "- No environmental mass-drift mechanism is introduced.",
            "- No claim of replacing the Standard Model or proving BHSM is made.",
            "- Candidate-only mechanisms remain non-official.",
            "",
        ]
    )
    return "\n".join(lines)


def export_sequential_blocker_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export docs and audit files."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "doc_md": base / "docs" / "BHSM_SEQUENTIAL_BLOCKER_CLOSURE.md",
        "doc_json": base / "docs" / "BHSM_SEQUENTIAL_BLOCKER_CLOSURE.json",
        "audit_md": base / "audits" / "bhsm_sequential_blocker_closure_audit.md",
        "audit_json": base / "audits" / "bhsm_sequential_blocker_closure_audit.json",
        "lepton_note": base / "theory" / "lepton_screened_alpha_pi_derivation_attempt.md",
        "fiber_note": base / "theory" / "pure_fiber_doublet_derivation_attempt.md",
        "boundary_note": base / "theory" / "boundary_action_derivation_attempt.md",
        "ckm_note": base / "theory" / "ckm_four_projection_derivation_attempt.md",
        "neutrino_note": base / "theory" / "neutrino_leakage_pmns_candidate_ledger.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["doc_md"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    json_text = json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n"
    paths["doc_json"].write_text(json_text, encoding="utf-8")
    paths["audit_json"].write_text(json_text, encoding="utf-8")
    attempts = {attempt.blocker_id: attempt for attempt in payload["attempts"]}
    note_map = {
        "lepton_note": attempts["lepton_8alpha_9pi"],
        "fiber_note": attempts["pure_fiber_one_half"],
        "boundary_note": attempts["boundary_action"],
        "ckm_note": attempts["ckm_one_sixteenth"],
        "neutrino_note": attempts["neutrino_pmns"],
    }
    for key, attempt in note_map.items():
        paths[key].write_text(
            "\n".join(
                [
                    f"# {attempt.blocker_id}",
                    "",
                    f"Status: `{attempt.status}`",
                    f"Closed: `{attempt.closed}`",
                    "",
                    "Evidence:",
                    *[f"- {item}" for item in attempt.evidence_found],
                    "",
                    "Missing requirements:",
                    *[f"- {item}" for item in attempt.missing_requirements],
                    "",
                    f"Exact obstruction: {attempt.exact_obstruction}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return payload


if __name__ == "__main__":
    export_sequential_blocker_outputs()
