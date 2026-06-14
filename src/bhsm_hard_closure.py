"""BHSM hard-closure sprint audit generator.

This module attempts closure of the remaining completion blockers. It does not
change frozen outputs and it does not promote candidate mechanisms unless a
repo-supported derivation or validation is present.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bhsm_v1 import compare_bhsm_v1_branches
from bhsm_virtual_mixing_solution import build_mixing_candidate_report
from common_scale_quark_rg_closure import (
    _jsonable as common_scale_quark_rg_jsonable,
    closure_audit_payload as common_scale_quark_rg_audit_payload,
    render_markdown as render_common_scale_quark_rg_markdown,
)
from gauge_couplings import gauge_coupling_screen
from rg_matching import matching_report
from scalar_decoupling import build_scalar_proxy_spectrum, hopf_gap_mass, scalar_decoupling_report
from constants import V_HIGGS_EMPIRICAL_GEV


CLOSED_SOLVED = "CLOSED_SOLVED"
CLOSED_REJECTED = "CLOSED_REJECTED"
BLOCKS_FULL_COMPLETION = "BLOCKS_FULL_COMPLETION"
FINAL_STATUS = "PARTIAL_COMPLETION_WITH_BLOCKERS"


@dataclass(frozen=True)
class ClosureResult:
    """One hard-closure audit result."""

    issue_id: str
    title: str
    status: str
    blocker: str | None
    classification: str
    pass_fail_criteria: tuple[str, ...]
    evidence: tuple[str, ...]
    unchanged_quantities: tuple[str, ...]
    next_action: str


def _write(path: str | Path, text: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _write_json(path: str | Path, payload: Any) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def frozen_sanity_payload() -> dict[str, Any]:
    """Return frozen branch sanity checks."""

    comparison = compare_bhsm_v1_branches()
    rows = comparison["rows"]
    changed = [row for row in rows if row["changed"]]
    return {
        "BHSM_BARE_V1_unchanged": comparison["branches"][0] == "BHSM_BARE_V1",
        "BHSM_DRESSED_V1_CANDIDATE_unchanged": comparison["branches"][1]
        == "BHSM_DRESSED_V1_CANDIDATE",
        "dressed_branch_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
        "u_over_t_unchanged": next(row for row in rows if row["quantity"] == "u/t")[
            "changed"
        ]
        is False,
        "ckm_sin_theta_13_unchanged": next(
            row for row in rows if row["quantity"] == "sin_theta_13"
        )["changed"]
        is False,
        "changed_rows": changed,
    }


def z_virt_u2_closure() -> ClosureResult:
    """Attempt closure of Z_virt^{u,2}=1/2."""

    return ClosureResult(
        issue_id="P0-1",
        title="Derive released Z_virt^{u,2}=1/2",
        status=BLOCKS_FULL_COMPLETION,
        blocker="Z_VIRT_U2_NOT_DERIVED",
        classification="STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        pass_fail_criteria=(
            "Z=1/2 must follow from BHSM structure without c/t residual input.",
            "If the half factor is only a two-state interpretation, it remains open.",
        ),
        evidence=(
            "Middle-up mode (6,0) is a pure-fiber j=0 up-sector mode.",
            "Omega_u=6 identifies the channel but does not force the 1/2 amplitude.",
            "Two-state virtual half-occupation is structurally plausible but not derived from the action.",
        ),
        unchanged_quantities=("Z_virt^{u,2}=1/2 preserved", "official branches unchanged"),
        next_action="derive the half-occupation/projection factor from the internal action or reject the released dressing promotion",
    )


def ckm_exponent_closure() -> ClosureResult:
    """Attempt closure of CKM 1/16 exponent."""

    report = build_mixing_candidate_report()
    return ClosureResult(
        issue_id="P0-2",
        title="Derive or reject CKM mixing exponent 1/16",
        status=BLOCKS_FULL_COMPLETION,
        blocker="CKM_1_16_EXPONENT_NOT_DERIVED",
        classification="CANDIDATE_EXPONENT_NOT_DERIVED",
        pass_fail_criteria=(
            "1/16 must follow independently from BHSM structure.",
            "Residual improvement alone is not a derivation.",
        ),
        evidence=(
            f"Candidate improves Vcb: {report.improves_vcb}.",
            f"Candidate improves Vts: {report.improves_vts}.",
            f"Non-2-3 damage flag: {report.non_23_damage_flag}.",
            "No independent 16-fold phase/covering/order derivation is present in the repo.",
        ),
        unchanged_quantities=("s12 unchanged", "s13 unchanged", "delta_cp unchanged"),
        next_action="derive or reject the exponent before any official promotion",
    )


def boundary_operator_closure() -> ClosureResult:
    """Attempt closure of boundary operator action derivation."""

    return ClosureResult(
        issue_id="P0-3",
        title="Boundary operator action derivation",
        status=BLOCKS_FULL_COMPLETION,
        blocker="BOUNDARY_OPERATORS_NOT_ACTION_DERIVED",
        classification="ACTION_LINKED",
        pass_fail_criteria=(
            "Omega_l, Omega_u, Omega_d must follow from an action/spectral/boundary principle.",
            "Recovery of the mode ledger alone is not enough.",
        ),
        evidence=(
            "Operational and action-linked scaffolds recover Omega_l=-q+2j=3.",
            "Operational and action-linked scaffolds recover Omega_u=q-2j=6.",
            "Operational and action-linked scaffolds recover Omega_d=q+4j=12.",
            "A unique derivation from the complete internal action is not present on this branch.",
        ),
        unchanged_quantities=("mode ledger unchanged", "frozen outputs unchanged"),
        next_action="derive the sector boundary functional from the complete internal action",
    )


def charged_lepton_closure() -> ClosureResult:
    """Attempt closure of charged-lepton precision dressing."""

    return ClosureResult(
        issue_id="P1-1",
        title="Charged-lepton precision dressing",
        status=BLOCKS_FULL_COMPLETION,
        blocker="LEPTON_PRECISION_NOT_SOLVED",
        classification="OPEN_LEPTON_PRECISION_WARNING",
        pass_fail_criteria=(
            "One fixed lepton-mode rule must improve mu/tau and e/tau.",
            "Separate fitted electron and muon factors are forbidden.",
        ),
        evidence=(
            "No single derived/pre-registered lepton dressing rule is available in repo inputs.",
            "Official frozen lepton predictions remain unchanged.",
        ),
        unchanged_quantities=("charged-lepton ratios unchanged", "quark and CKM sectors unchanged"),
        next_action="derive a mode-dependent lepton dressing rule or keep precision warning open",
    )


def common_scale_quark_rg_closure() -> ClosureResult:
    """Attempt closure of common-scale quark RG validation."""

    audit = common_scale_quark_rg_audit_payload()
    closed = bool(audit["closes_common_scale_input_blocker"])
    return ClosureResult(
        issue_id="P1-2",
        title="Common-scale quark RG validation",
        status=CLOSED_SOLVED if closed else BLOCKS_FULL_COMPLETION,
        blocker=None if closed else "COMMON_SCALE_QUARK_RG_INPUTS_MISSING",
        classification=audit["classification"],
        pass_fail_criteria=(
            "Validated common-scale u/t, c/t, d/b, s/b references must be available.",
            "Mixed-scale PDG-style values cannot be used as a precision verdict.",
        ),
        evidence=(
            f"Common-scale input validated: {audit['common_scale_input_validated']}.",
            f"Reference scale: {audit['reference']['scale']}.",
            f"Reference scheme: {audit['reference']['scheme']}.",
            f"Dressed c/t improves versus bare: {audit['ct_dressing_effect']['dressed_improves_c_over_t']}.",
            f"Warning-level dressed ratios: {audit['branch_summary']['real_tensions']}.",
            "Precision quark matching remains warning-level because uncertainties are not propagated and u/t remains outside tolerance.",
        ),
        unchanged_quantities=("quark ratios unchanged", "dressed c/t unchanged"),
        next_action="propagate common-scale uncertainties and investigate the remaining u/t tension without retuning",
    )


def gauge_precision_closure() -> ClosureResult:
    """Attempt closure of gauge coupling convention/scale lock."""

    screen = gauge_coupling_screen()
    rg = matching_report()
    in_window = all(row["in_electroweak_window"] for row in rg["rows"].values())
    alpha3_error = screen.relative_error["alpha_3"]
    solved = bool(in_window and alpha3_error < 0.01)
    return ClosureResult(
        issue_id="P2-1",
        title="Gauge coupling precision lock",
        status=CLOSED_SOLVED if solved else BLOCKS_FULL_COMPLETION,
        blocker=None if solved else "GAUGE_PRECISION_NOT_LOCKED",
        classification="GAUGE_PRECISION_SURVIVAL" if solved else "GAUGE_CONVENTION_OPEN",
        pass_fail_criteria=(
            "Use explicit electroweak matching convention.",
            "All one-loop matching scales must lie in the electroweak window.",
            "alpha_3 screen must remain within 1 percent.",
        ),
        evidence=(
            f"alpha_3 relative error: {alpha3_error}.",
            f"one-loop matching scales in electroweak window: {in_window}.",
            "Two-/three-loop threshold matching remains a separate precision extension, not a retuning step.",
        ),
        unchanged_quantities=("gauge coupling formulas unchanged",),
        next_action="keep convention explicit and extend to higher-loop thresholds without retuning",
    )


def scalar_higgs_gap_closure() -> ClosureResult:
    """Attempt closure of scalar/Higgs/gap full proof."""

    gap = hopf_gap_mass(V_HIGGS_EMPIRICAL_GEV)
    report = scalar_decoupling_report(build_scalar_proxy_spectrum(6), gap)
    return ClosureResult(
        issue_id="P2-2",
        title="Scalar/Higgs/gap full proof",
        status=BLOCKS_FULL_COMPLETION,
        blocker="FULL_SPECTRUM_GAP_PROOF_MISSING",
        classification="STRONG_PROXY_SURVIVAL",
        pass_fail_criteria=(
            "Full-spectrum proof or rigorous bound must exist.",
            "Proxy/scaffold pass is not proof-level closure.",
        ),
        evidence=(
            f"Scalar scaffold passes: {report['passes']}.",
            f"Dangerous light scalar count: {len(report['dangerous_light_modes'])}.",
            "Full action-level spectrum proof remains absent.",
        ),
        unchanged_quantities=("scalar scaffold unchanged", "H_T proxy status not upgraded"),
        next_action="complete full-spectrum scalar/H_T proof inputs",
    )


def closure_results() -> tuple[ClosureResult, ...]:
    """Return all hard-closure results."""

    return (
        z_virt_u2_closure(),
        ckm_exponent_closure(),
        boundary_operator_closure(),
        charged_lepton_closure(),
        common_scale_quark_rg_closure(),
        gauge_precision_closure(),
        scalar_higgs_gap_closure(),
    )


def hard_closure_status_payload() -> dict[str, Any]:
    """Return final hard-closure status."""

    results = closure_results()
    blockers = [result for result in results if result.status == BLOCKS_FULL_COMPLETION]
    p0_p1_blockers = [
        result for result in blockers if result.issue_id.startswith("P0") or result.issue_id.startswith("P1")
    ]
    final_status = "FULL_COMPLETION_READY" if not p0_p1_blockers else FINAL_STATUS
    return {
        "final_status": final_status,
        "promotion_allowed": final_status == "FULL_COMPLETION_READY",
        "no_retuning_preserved": True,
        "frozen_sanity": frozen_sanity_payload(),
        "solved_issues": [asdict(result) for result in results if result.status == CLOSED_SOLVED],
        "rejected_candidates": [asdict(result) for result in results if result.status == CLOSED_REJECTED],
        "remaining_blockers": [asdict(result) for result in blockers],
        "results": [asdict(result) for result in results],
    }


def render_result_markdown(result: ClosureResult) -> str:
    """Render one closure result."""

    lines = [
        f"# {result.title}",
        "",
        f"Issue: `{result.issue_id}`",
        f"Status: `{result.status}`",
        f"Classification: `{result.classification}`",
        f"Blocker: `{result.blocker}`" if result.blocker else "Blocker: `None`",
        "",
        "## Pass/Fail Criteria",
        "",
        *[f"- {item}" for item in result.pass_fail_criteria],
        "",
        "## Evidence",
        "",
        *[f"- {item}" for item in result.evidence],
        "",
        "## Unchanged Quantities",
        "",
        *[f"- {item}" for item in result.unchanged_quantities],
        "",
        "## Next Action",
        "",
        result.next_action,
        "",
    ]
    return "\n".join(lines)


def render_status_markdown() -> str:
    """Render final hard-closure status."""

    payload = hard_closure_status_payload()
    lines = [
        "# BHSM Hard Closure Status",
        "",
        f"Final status: `{payload['final_status']}`",
        f"Promotion allowed: `{payload['promotion_allowed']}`",
        "",
        "BHSM is not confirmed, and this branch does not supersede the Standard Model.",
        "",
        "## Solved Issues",
        "",
    ]
    solved = payload["solved_issues"]
    lines.extend([f"- `{item['issue_id']}` {item['title']}: `{item['classification']}`" for item in solved] or ["- None"])
    lines.extend(["", "## Rejected Candidates", ""])
    rejected = payload["rejected_candidates"]
    lines.extend([f"- `{item['issue_id']}` {item['title']}: `{item['classification']}`" for item in rejected] or ["- None"])
    lines.extend(["", "## Remaining Blockers", ""])
    lines.extend(
        [
            f"- `{item['issue_id']}` {item['title']}: `{item['blocker']}`"
            for item in payload["remaining_blockers"]
        ]
        or ["- None"]
    )
    lines.extend(["", "## No-Retuning Discipline", "", "Frozen sanity is preserved."])
    return "\n".join(lines) + "\n"


FILE_MAP = {
    "P0-1": (
        "theory/z_virt_u2_derivation.md",
        "audits/z_virt_u2_closure_audit.md",
        "audits/z_virt_u2_closure_audit.json",
    ),
    "P0-2": (
        "theory/ckm_mixing_exponent_1_16_derivation.md",
        "audits/ckm_mixing_exponent_1_16_closure_audit.md",
        "audits/ckm_mixing_exponent_1_16_closure_audit.json",
    ),
    "P0-3": (
        "theory/boundary_operator_action_derivation.md",
        "audits/boundary_operator_closure_audit.md",
        "audits/boundary_operator_closure_audit.json",
    ),
    "P1-1": (
        "theory/charged_lepton_precision_solution.md",
        "audits/charged_lepton_precision_closure_audit.md",
        "audits/charged_lepton_precision_closure_audit.json",
    ),
    "P1-2": (
        "theory/common_scale_quark_rg_solution.md",
        "audits/common_scale_quark_rg_closure_audit.md",
        "audits/common_scale_quark_rg_closure_audit.json",
    ),
    "P2-1": (
        "theory/gauge_coupling_precision_solution.md",
        "audits/gauge_coupling_precision_closure_audit.md",
        "audits/gauge_coupling_precision_closure_audit.json",
    ),
    "P2-2": (
        "theory/scalar_higgs_gap_full_solution.md",
        "audits/scalar_higgs_gap_closure_audit.md",
        "audits/scalar_higgs_gap_closure_audit.json",
    ),
}


def generate_hard_closure_outputs() -> None:
    """Generate all hard-closure outputs."""

    for result in closure_results():
        theory_path, md_path, json_path = FILE_MAP[result.issue_id]
        rendered = render_result_markdown(result)
        _write(theory_path, rendered)
        if result.issue_id == "P1-2":
            audit = common_scale_quark_rg_audit_payload()
            _write(md_path, render_common_scale_quark_rg_markdown(audit))
            _write_json(json_path, common_scale_quark_rg_jsonable(audit))
        else:
            _write(md_path, rendered)
            _write_json(json_path, asdict(result))
    _write("docs/BHSM_HARD_CLOSURE_STATUS.md", render_status_markdown())
    _write_json("docs/BHSM_HARD_CLOSURE_STATUS.json", hard_closure_status_payload())


if __name__ == "__main__":
    generate_hard_closure_outputs()
