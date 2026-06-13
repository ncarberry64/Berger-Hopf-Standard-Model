"""BHSM full completion v1 candidate package generator.

The package created here is a candidate architecture, not an official release
and not a claim of external validation. It preserves the frozen BHSM branches
and records open derivation requirements explicitly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bhsm_model import build_bhsm_model, compute_geometric_couplings
from bhsm_v1 import compare_bhsm_v1_branches
from bhsm_virtual_mixing_solution import (
    REQUIRED_CANDIDATE_WORDING,
    build_mixing_candidate_report,
)
from prediction_ledger import CKM_REFERENCES


FULL_STATUS = "FULL_COMPLETION_CANDIDATE_NOT_OFFICIAL"
NOT_OFFICIAL = "NOT_OFFICIAL"


@dataclass(frozen=True)
class CompletionItem:
    """One full-completion candidate scorecard row."""

    item: str
    status: str
    official_or_candidate: str
    derived_status: str
    audit_result: str
    failure_risk: str
    next_action: str


def _write(path: str | Path, text: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def _write_json(path: str | Path, payload: Any) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def frozen_branch_check() -> dict[str, Any]:
    """Return the official branch preservation check."""

    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]
    return {
        "BHSM_BARE_V1_unchanged": comparison["branches"][0] == "BHSM_BARE_V1",
        "BHSM_DRESSED_V1_CANDIDATE_unchanged": comparison["branches"][1]
        == "BHSM_DRESSED_V1_CANDIDATE",
        "dressed_branch_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
        "u_over_t_unchanged": next(row for row in comparison["rows"] if row["quantity"] == "u/t")[
            "changed"
        ]
        is False,
        "ckm_sin_theta_13_unchanged": next(
            row for row in comparison["rows"] if row["quantity"] == "sin_theta_13"
        )["changed"]
        is False,
        "changed_rows": changed,
    }


def z_virt_derivation_payload() -> dict[str, Any]:
    """Attempt summary for Z_virt^{u,2}=1/2."""

    routes = [
        {
            "route": "middle-up mode parity",
            "result": "supports a special pure-fiber middle-up channel but does not force 1/2",
        },
        {
            "route": "Hopf fiber projection",
            "result": "structurally compatible with a half-projection interpretation",
        },
        {
            "route": "boundary operator Omega_u = 6",
            "result": "identifies the mode channel but does not uniquely determine the amplitude factor",
        },
        {
            "route": "two-state virtual dressing / half-occupation",
            "result": "best current structural motivation for 1/2",
        },
        {
            "route": "internal action or H_T proxy",
            "result": "insufficient for an action-level derivation in this branch",
        },
    ]
    return {
        "factor": 0.5,
        "classification": "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
        "fitted_from_residual": False,
        "routes": routes,
        "conclusion": (
            "Z_virt^{u,2}=1/2 is preserved as the released candidate factor, "
            "but this audit does not derive it uniquely from the internal action."
        ),
        "next_action": "derive the half-projection rule from the Berger-Hopf internal action or reject promotion",
    }


def ckm_exponent_derivation_payload() -> dict[str, Any]:
    """Attempt summary for the 1/16 CKM mixing exponent."""

    routes = [
        "mass eigenvalue dressing versus mixing amplitude dressing",
        "overlap amplitude as a fractional projection of mass dressing",
        "2-to-3 family bridge order",
        "Hopf projection depth",
        "boundary operator ratio Omega_l:Omega_u:Omega_d",
        "internal mode overlap order",
        "16-fold phase or covering structure if independently found",
    ]
    return {
        "exponent": 1.0 / 16.0,
        "classification": "OPEN_DERIVATION_REQUIRED",
        "candidate_label": "CANDIDATE_EXPONENT_NOT_DERIVED",
        "selected_by_residual": True,
        "routes_examined": routes,
        "conclusion": (
            "The 1/16 exponent is the best predeclared CKM 2-3 audit candidate, "
            "but this branch does not derive it independently of residual comparison."
        ),
        "next_action": "derive or reject the exponent before any promotion",
    }


def full_ckm_payload() -> dict[str, Any]:
    """Return full CKM candidate audit payload."""

    report = build_mixing_candidate_report()
    ckm_exponent = ckm_exponent_derivation_payload()
    return {
        "status": "CANDIDATE_SURVIVAL",
        "derivation_status": ckm_exponent["classification"],
        "best_candidate": "Z^(1/16)",
        "baseline": asdict(report.baseline),
        "candidate": asdict(report.candidate),
        "improves_vcb": report.improves_vcb,
        "improves_vts": report.improves_vts,
        "non_2_3_damage_flag": report.non_23_damage_flag,
        "j_damage_flag": report.j_damage_flag,
        "candidate_is_official": False,
        "references": {
            "Vcb": 0.0411,
            "Vts": 0.0415,
            "Vub": CKM_REFERENCES["sin_theta_13"],
            "J_CKM": CKM_REFERENCES["jarlskog"],
        },
    }


def charged_lepton_payload() -> dict[str, Any]:
    """Return charged-lepton candidate status."""

    return {
        "classification": "OPEN_LEPTON_PRECISION_WARNING",
        "candidate_status": "LEPTON_DRESSING_REJECTED",
        "official_status": "NOT_OFFICIAL",
        "rule": None,
        "reason": (
            "No single pre-registered lepton virtual dressing rule is derived or "
            "cleanly motivated in this branch without fitting separate factors."
        ),
        "official_lepton_predictions_changed": False,
        "next_action": "derive a mode-structured lepton dressing rule or leave the lepton precision gap open",
    }


def quark_rg_payload() -> dict[str, Any]:
    """Return common-scale quark RG status."""

    return {
        "classification": "EXTERNAL_INPUT_REQUIRED",
        "rough_pdg_screen": "available but scheme-sensitive",
        "common_scale_rg_screen": "not validated from external precision inputs in this branch",
        "precision_verdict": "not issued",
        "next_action": "supply validated common-scale running quark masses with uncertainties",
    }


def gauge_payload() -> dict[str, Any]:
    """Return gauge coupling completion audit."""

    values = compute_geometric_couplings(build_bhsm_model())["values"]
    return {
        "classification": "GAUGE_COARSE_SURVIVAL",
        "normalization": "repository electroweak matching convention; alpha_1 is GUT-normalized where RG modules require it",
        "values": values,
        "alpha3_reference": "alpha_s(M_Z) comparison screen only",
        "alpha1_issue": "convention and scale matching must remain explicit",
        "retuned": False,
        "next_action": "complete precision threshold/RG convention audit",
    }


def boundary_payload() -> dict[str, Any]:
    """Return boundary operator completion status."""

    return {
        "classification": "ACTION_LINKED",
        "operators": {
            "Omega_l": "-q + 2j = 3",
            "Omega_u": "q - 2j = 6",
            "Omega_d": "q + 4j = 12",
        },
        "status": "structural scaffold exists, full action derivation still required",
        "overstated": False,
        "next_action": "derive the sector boundary functional from the complete internal action",
    }


def scalar_higgs_gap_payload() -> dict[str, Any]:
    """Return scalar/Higgs/gap safety status."""

    return {
        "classification": "STRONG_PROXY_SURVIVAL",
        "gap_status": "proxy/scaffold audited",
        "dangerous_light_scalar": False,
        "proof_status": "OPEN_FULL_SPECTRUM_REQUIRED",
        "next_action": "replace proxy/scaffold gap checks with full spectral proof inputs",
    }


def scorecard_rows() -> tuple[CompletionItem, ...]:
    """Return the full completion candidate scorecard."""

    return (
        CompletionItem(
            "release integrity",
            "CLEAN_SURVIVAL",
            "official",
            "verified by tests",
            "frozen branches preserved",
            "low",
            "keep freeze guards active",
        ),
        CompletionItem(
            "c/t mass dressing",
            "CAVEATED_SURVIVAL",
            "official candidate",
            "STRUCTURALLY_MOTIVATED_NOT_DERIVED",
            "Z=1/2 preserved; no residual fit performed here",
            "derivation gap",
            "derive half-projection rule",
        ),
        CompletionItem(
            "CKM 2-3 mixing dressing",
            "CANDIDATE_SURVIVAL",
            "candidate",
            "OPEN_DERIVATION_REQUIRED",
            "Z^(1/16) improves Vcb/Vts with no damage flags",
            "candidate exponent not derived",
            "derive or reject 1/16",
        ),
        CompletionItem(
            "full CKM matrix",
            "CANDIDATE_SURVIVAL",
            "candidate",
            "OPEN_DERIVATION_REQUIRED",
            "matrix reconstructed and residuals reported",
            "future input drift",
            "freeze rule before future comparisons",
        ),
        CompletionItem(
            "charged leptons",
            "OPEN_DERIVATION_REQUIRED",
            "not official",
            "OPEN_LEPTON_PRECISION_WARNING",
            "no clean lepton dressing adopted",
            "precision residuals remain",
            "derive single mode-structured rule",
        ),
        CompletionItem(
            "quark RG/common-scale",
            "OPEN_DERIVATION_REQUIRED",
            "audit",
            "EXTERNAL_INPUT_REQUIRED",
            "mixed-scale screens not precision verdicts",
            "scheme dependence",
            "supply validated common-scale inputs",
        ),
        CompletionItem(
            "gauge couplings",
            "CAVEATED_SURVIVAL",
            "audit",
            "GAUGE_COARSE_SURVIVAL",
            "matching convention recorded; no retuning",
            "precision convention/scale",
            "complete threshold/RG convention audit",
        ),
        CompletionItem(
            "boundary operators",
            "OPEN_DERIVATION_REQUIRED",
            "audit",
            "ACTION_LINKED",
            "operators recover ledger but full action derivation remains",
            "action-origin gap",
            "derive boundary functional from full action",
        ),
        CompletionItem(
            "scalar/Higgs/gap",
            "CAVEATED_SURVIVAL",
            "audit",
            "STRONG_PROXY_SURVIVAL",
            "no dangerous light scalar in scaffold audit",
            "full spectrum open",
            "complete spectral proof inputs",
        ),
        CompletionItem(
            "claim discipline",
            "CLEAN_SURVIVAL",
            "official guardrail",
            "verified by tests",
            "candidate package denies confirmation/replacement claims",
            "low",
            "keep candidate labels visible",
        ),
    )


def full_manifest_payload() -> dict[str, Any]:
    """Return the full completion candidate manifest."""

    return {
        "status": FULL_STATUS,
        "official_frozen_branches_preserved": True,
        "confirmation_status": "BHSM is not confirmed. This package is a completion candidate and falsification target.",
        "candidate_scope": [
            "bare Berger-Hopf geometry",
            "released c/t virtual mass dressing",
            "candidate CKM 2-3 mixing dressing",
            "charged-lepton precision warning",
            "gauge coupling comparison",
            "quark RG audit",
            "boundary operator derivation status",
        ],
        "officially_unchanged": [
            "BHSM_BARE_V1",
            "BHSM_DRESSED_V1_CANDIDATE",
            "docs/frozen_predictions.md",
            "docs/frozen_predictions.json",
            "released c/t dressed branch",
            "u/t",
            "d/b",
            "s/b",
            "charged-lepton ratios unless a separate candidate is created",
            "gauge couplings",
            "s12",
            "s13",
            "delta_cp",
        ],
        "candidate_additions": [
            "BHSM_MIXING_DRESSED_V1_CANDIDATE",
            "BHSM_LEPTON_DRESSED_V1_CANDIDATE status file",
            "derivation-attempt notes",
            "completion audits",
            "completion scorecard",
        ],
        "unresolved_derivations": [
            "derive Z_virt^{u,2}=1/2",
            "derive or reject CKM exponent 1/16",
            "charged-lepton precision rule",
            "validated common-scale quark RG inputs",
            "boundary operator full action derivation",
            "full scalar/Higgs/gap spectral proof inputs",
        ],
        "frozen_branch_check": frozen_branch_check(),
    }


def markdown_table(rows: tuple[CompletionItem, ...]) -> str:
    """Render scorecard rows as Markdown."""

    lines = [
        "| Item | Status | Official/Candidate | Derived Status | Audit Result | Failure Risk | Next Action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.item} | `{row.status}` | {row.official_or_candidate} | "
            f"`{row.derived_status}` | {row.audit_result} | {row.failure_risk} | {row.next_action} |"
        )
    return "\n".join(lines)


def render_manifest_markdown() -> str:
    """Render the full completion candidate manifest."""

    payload = full_manifest_payload()
    return "\n".join(
        [
            "# BHSM_FULL_COMPLETION_V1_CANDIDATE",
            "",
            f"Status: `{FULL_STATUS}`",
            "",
            "BHSM is not confirmed. This package is a completion candidate and falsification target.",
            "",
            "## Candidate Scope",
            "",
            "This candidate attempts to unify bare Berger-Hopf geometry, the released "
            "`c/t` virtual mass dressing, the candidate CKM 2-3 mixing dressing, "
            "gauge comparison, quark RG audit, scalar/gap status, and boundary "
            "operator derivation status without changing official frozen outputs.",
            "",
            "## Officially Unchanged",
            "",
            *[f"- {item}" for item in payload["officially_unchanged"]],
            "",
            "## Candidate Additions",
            "",
            *[f"- {item}" for item in payload["candidate_additions"]],
            "",
            "## Unresolved Derivations",
            "",
            *[f"- {item}" for item in payload["unresolved_derivations"]],
            "",
            "## Confirmation Status",
            "",
            "BHSM is not confirmed. This package is a completion candidate and falsification target.",
        ]
    ) + "\n"


def render_payload_markdown(title: str, payload: dict[str, Any]) -> str:
    """Render a simple payload note."""

    lines = [f"# {title}", "", "```json", json.dumps(payload, indent=2), "```", ""]
    return "\n".join(lines)


def render_scorecard_markdown() -> str:
    """Render the full completion scorecard."""

    return "\n".join(
        [
            "# BHSM Completion Scorecard",
            "",
            "Status rows are candidate/audit classifications, not official release changes.",
            "",
            markdown_table(scorecard_rows()),
            "",
            "BHSM is not confirmed. This scorecard is a falsification and completion-candidate target.",
        ]
    ) + "\n"


def generate_all_completion_outputs() -> None:
    """Generate the full completion candidate package."""

    payloads = {
        "z_virt_u2_derivation": z_virt_derivation_payload(),
        "ckm_mixing_exponent_derivation": ckm_exponent_derivation_payload(),
        "full_ckm_completion_candidate": full_ckm_payload(),
        "charged_lepton_dressing_candidate": charged_lepton_payload(),
        "common_scale_quark_rg": quark_rg_payload(),
        "gauge_coupling_completion": gauge_payload(),
        "boundary_operator_derivation": boundary_payload(),
        "scalar_higgs_gap_completion": scalar_higgs_gap_payload(),
    }

    _write("candidates/BHSM_FULL_COMPLETION_V1_CANDIDATE.md", render_manifest_markdown())
    _write_json("candidates/BHSM_FULL_COMPLETION_V1_CANDIDATE.json", full_manifest_payload())

    _write("theory/derive_z_virt_u2_candidate.md", render_payload_markdown("Derive Z_virt u2 Candidate", payloads["z_virt_u2_derivation"]))
    _write_json("audits/z_virt_u2_derivation_audit.json", payloads["z_virt_u2_derivation"])
    _write("audits/z_virt_u2_derivation_audit.md", render_payload_markdown("Z_virt u2 Derivation Audit", payloads["z_virt_u2_derivation"]))

    _write("theory/derive_ckm_mixing_exponent_candidate.md", render_payload_markdown("Derive CKM Mixing Exponent Candidate", payloads["ckm_mixing_exponent_derivation"]))
    _write_json("audits/ckm_mixing_exponent_derivation_audit.json", payloads["ckm_mixing_exponent_derivation"])
    _write("audits/ckm_mixing_exponent_derivation_audit.md", render_payload_markdown("CKM Mixing Exponent Derivation Audit", payloads["ckm_mixing_exponent_derivation"]))

    _write_json("audits/full_ckm_completion_candidate_audit.json", payloads["full_ckm_completion_candidate"])
    _write("audits/full_ckm_completion_candidate_audit.md", render_payload_markdown("Full CKM Completion Candidate Audit", payloads["full_ckm_completion_candidate"]))

    _write("theory/charged_lepton_virtual_dressing_candidate.md", render_payload_markdown("Charged Lepton Virtual Dressing Candidate", payloads["charged_lepton_dressing_candidate"]))
    _write_json("audits/charged_lepton_dressing_candidate_audit.json", payloads["charged_lepton_dressing_candidate"])
    _write("audits/charged_lepton_dressing_candidate_audit.md", render_payload_markdown("Charged Lepton Dressing Candidate Audit", payloads["charged_lepton_dressing_candidate"]))
    _write_json("candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.json", payloads["charged_lepton_dressing_candidate"])
    _write("candidates/BHSM_LEPTON_DRESSED_V1_CANDIDATE.md", render_payload_markdown("BHSM_LEPTON_DRESSED_V1_CANDIDATE", payloads["charged_lepton_dressing_candidate"]))

    _write("theory/quark_rg_scheme_note.md", render_payload_markdown("Quark RG Scheme Note", payloads["common_scale_quark_rg"]))
    _write_json("audits/common_scale_quark_rg_audit.json", payloads["common_scale_quark_rg"])
    _write("audits/common_scale_quark_rg_audit.md", render_payload_markdown("Common-Scale Quark RG Audit", payloads["common_scale_quark_rg"]))

    _write("theory/gauge_normalization_note.md", render_payload_markdown("Gauge Normalization Note", payloads["gauge_coupling_completion"]))
    _write_json("audits/gauge_coupling_completion_audit.json", payloads["gauge_coupling_completion"])
    _write("audits/gauge_coupling_completion_audit.md", render_payload_markdown("Gauge Coupling Completion Audit", payloads["gauge_coupling_completion"]))

    _write("theory/boundary_operator_completion_attempt.md", render_payload_markdown("Boundary Operator Completion Attempt", payloads["boundary_operator_derivation"]))
    _write_json("audits/boundary_operator_derivation_audit.json", payloads["boundary_operator_derivation"])
    _write("audits/boundary_operator_derivation_audit.md", render_payload_markdown("Boundary Operator Derivation Audit", payloads["boundary_operator_derivation"]))

    _write("theory/scalar_higgs_gap_completion_note.md", render_payload_markdown("Scalar Higgs Gap Completion Note", payloads["scalar_higgs_gap_completion"]))
    _write_json("audits/scalar_higgs_gap_completion_audit.json", payloads["scalar_higgs_gap_completion"])
    _write("audits/scalar_higgs_gap_completion_audit.md", render_payload_markdown("Scalar Higgs Gap Completion Audit", payloads["scalar_higgs_gap_completion"]))

    scorecard_payload = [asdict(row) for row in scorecard_rows()]
    _write("docs/bhsm_completion_scorecard.md", render_scorecard_markdown())
    _write_json("docs/bhsm_completion_scorecard.json", scorecard_payload)


if __name__ == "__main__":
    generate_all_completion_outputs()
