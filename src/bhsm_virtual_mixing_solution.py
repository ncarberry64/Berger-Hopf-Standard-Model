"""BHSM mixing-dressed v1 candidate solution.

This module defines a candidate-only CKM 2-3 mixing repair. It connects the
already released middle-up virtual mass dressing ``Z_virt^{u,2}=1/2`` to a
weaker mixing-amplitude dressing, without changing the official frozen
``BHSM_BARE_V1`` or ``BHSM_DRESSED_V1_CANDIDATE`` outputs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import Path

import numpy as np

from bhsm_model import build_bhsm_model
from bhsm_v1 import compare_bhsm_v1_branches
from ckm import ckm_matrix_magnitudes
from flavor_matrix import canonical_ckm_angles, canonical_ckm_delta, jarlskog_invariant


STATUS = "CANDIDATE_NOT_OFFICIAL"
Z_VIRT_U2 = 0.5
CANDIDATE_MIXING_EXPONENT = 1.0 / 16.0
Z_MIX_23 = Z_VIRT_U2**CANDIDATE_MIXING_EXPONENT
NON_23_DAMAGE_THRESHOLD = 0.01
J_DAMAGE_THRESHOLD = 0.02

CKM_ELEMENT_ORDER = (
    ("Vud", 0, 0),
    ("Vus", 0, 1),
    ("Vub", 0, 2),
    ("Vcd", 1, 0),
    ("Vcs", 1, 1),
    ("Vcb", 1, 2),
    ("Vtd", 2, 0),
    ("Vts", 2, 1),
    ("Vtb", 2, 2),
)

PDG_STYLE_CKM_REFERENCES = {
    "Vud": 0.97367,
    "Vus": 0.22431,
    "Vub": 3.82e-3,
    "Vcd": 0.221,
    "Vcs": 0.975,
    "Vcb": 41.1e-3,
    "Vtd": 8.6e-3,
    "Vts": 41.5e-3,
    "Vtb": 1.010,
    "J_CKM": 3.0e-5,
}

REQUIRED_CANDIDATE_WORDING = (
    "This candidate is not part of the official frozen release. It is a clean "
    "repair candidate for the CKM 2-3 pressure point and requires derivation "
    "of the 1/16 exponent before promotion."
)


@dataclass(frozen=True)
class CKMResidual:
    """Residual row for a CKM matrix element or Jarlskog invariant."""

    quantity: str
    predicted: float
    reference: float
    absolute_error: float
    relative_error: float


@dataclass(frozen=True)
class CKMState:
    """CKM state generated from sine angles and the Hopf-phase delta."""

    name: str
    status: str
    sin_theta_12: float
    sin_theta_23: float
    sin_theta_13: float
    delta_cp: float
    matrix_magnitudes: list[list[float]]
    jarlskog: float
    residuals: tuple[CKMResidual, ...]


@dataclass(frozen=True)
class MixingCandidateReport:
    """Baseline-vs-candidate CKM 2-3 dressing report."""

    status: str
    rule: str
    z_virt_u2: float
    candidate_mixing_exponent: float
    z_mix_23: float
    baseline: CKMState
    candidate: CKMState
    improves_vcb: bool
    improves_vts: bool
    non_23_damage_flag: bool
    j_damage_flag: bool
    frozen_branch_check: dict[str, object]
    limitations: tuple[str, ...]


def _relative_error(predicted: float, reference: float) -> float:
    if reference == 0.0:
        return 0.0 if predicted == 0.0 else float("inf")
    return abs(predicted - reference) / abs(reference)


def _residual(quantity: str, predicted: float, reference: float) -> CKMResidual:
    return CKMResidual(
        quantity=quantity,
        predicted=float(predicted),
        reference=float(reference),
        absolute_error=float(abs(predicted - reference)),
        relative_error=float(_relative_error(predicted, reference)),
    )


def _residuals(matrix: np.ndarray, jarlskog: float) -> tuple[CKMResidual, ...]:
    rows = [
        _residual(name, float(matrix[i, j]), PDG_STYLE_CKM_REFERENCES[name])
        for name, i, j in CKM_ELEMENT_ORDER
    ]
    rows.append(_residual("J_CKM", float(jarlskog), PDG_STYLE_CKM_REFERENCES["J_CKM"]))
    return tuple(rows)


def residual_map(state: CKMState) -> dict[str, CKMResidual]:
    """Return residuals keyed by quantity."""

    return {residual.quantity: residual for residual in state.residuals}


def _ckm_state(
    name: str,
    sin_theta_12: float,
    sin_theta_23: float,
    sin_theta_13: float,
    delta_cp: float,
) -> CKMState:
    matrix = ckm_matrix_magnitudes(
        sin_theta_12,
        sin_theta_23,
        sin_theta_13,
        delta=delta_cp,
    )
    jarlskog = jarlskog_invariant(
        sin_theta_12,
        sin_theta_23,
        sin_theta_13,
        delta_cp,
    )
    if not isfinite(jarlskog):
        raise ValueError("J_CKM must be finite")
    return CKMState(
        name=name,
        status=STATUS,
        sin_theta_12=float(sin_theta_12),
        sin_theta_23=float(sin_theta_23),
        sin_theta_13=float(sin_theta_13),
        delta_cp=float(delta_cp),
        matrix_magnitudes=np.asarray(matrix, dtype=float).tolist(),
        jarlskog=float(jarlskog),
        residuals=_residuals(np.asarray(matrix, dtype=float), jarlskog),
    )


def frozen_ckm_state() -> CKMState:
    """Return the official frozen CKM state from canonical BHSM sources."""

    model = build_bhsm_model()
    angles = canonical_ckm_angles(model)
    delta = float(canonical_ckm_delta(model)["delta"])
    return _ckm_state(
        name="BHSM_FROZEN_CKM_BASELINE",
        sin_theta_12=float(angles["sin_theta_12"]),
        sin_theta_23=float(angles["sin_theta_23"]),
        sin_theta_13=float(angles["sin_theta_13"]),
        delta_cp=delta,
    )


def mixing_dressed_ckm_state() -> CKMState:
    """Return the candidate state with only CKM 2-3 mixing dressed."""

    baseline = frozen_ckm_state()
    return _ckm_state(
        name="BHSM_MIXING_DRESSED_V1_CANDIDATE",
        sin_theta_12=baseline.sin_theta_12,
        sin_theta_23=baseline.sin_theta_23 * Z_MIX_23,
        sin_theta_13=baseline.sin_theta_13,
        delta_cp=baseline.delta_cp,
    )


def official_frozen_branch_check() -> dict[str, object]:
    """Return a compact official-branch immutability check."""

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


def build_mixing_candidate_report() -> MixingCandidateReport:
    """Build the candidate report without mutating any frozen output."""

    baseline = frozen_ckm_state()
    candidate = mixing_dressed_ckm_state()
    base_residuals = residual_map(baseline)
    candidate_residuals = residual_map(candidate)
    non_23_quantities = set(candidate_residuals) - {"Vcb", "Vts"}
    non_23_damage = any(
        candidate_residuals[name].relative_error
        > base_residuals[name].relative_error + NON_23_DAMAGE_THRESHOLD
        for name in non_23_quantities
        if name != "J_CKM"
    )
    j_damage = (
        candidate_residuals["J_CKM"].relative_error
        > base_residuals["J_CKM"].relative_error + J_DAMAGE_THRESHOLD
    )
    return MixingCandidateReport(
        status=STATUS,
        rule="s23_candidate = s23_frozen * (Z_virt^{u,2})^(1/16)",
        z_virt_u2=Z_VIRT_U2,
        candidate_mixing_exponent=CANDIDATE_MIXING_EXPONENT,
        z_mix_23=Z_MIX_23,
        baseline=baseline,
        candidate=candidate,
        improves_vcb=(
            candidate_residuals["Vcb"].relative_error < base_residuals["Vcb"].relative_error
        ),
        improves_vts=(
            candidate_residuals["Vts"].relative_error < base_residuals["Vts"].relative_error
        ),
        non_23_damage_flag=non_23_damage,
        j_damage_flag=j_damage,
        frozen_branch_check=official_frozen_branch_check(),
        limitations=(
            REQUIRED_CANDIDATE_WORDING,
            "The 1/16 exponent is a CANDIDATE_EXPONENT and derivation target, not a proven BHSM result.",
            "Only CKM 2-3 mixing is changed; official frozen BHSM branches are not modified.",
        ),
    )


def _residual_table_lines(state: CKMState) -> list[str]:
    return [
        "| `{}` | `{}` | `{:.12g}` | `{:.12g}` | `{:.6g}` |".format(
            state.name,
            residual.quantity,
            residual.predicted,
            residual.reference,
            residual.relative_error,
        )
        for residual in state.residuals
    ]


def export_mixing_candidate_json(path: str | Path) -> None:
    """Export the candidate report as JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(asdict(build_mixing_candidate_report()), indent=2),
        encoding="utf-8",
    )


def export_mixing_candidate_markdown(path: str | Path) -> None:
    """Export the candidate report as Markdown."""

    report = build_mixing_candidate_report()
    baseline_residuals = residual_map(report.baseline)
    candidate_residuals = residual_map(report.candidate)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# BHSM_MIXING_DRESSED_V1_CANDIDATE",
        "",
        "Status: `CANDIDATE_NOT_OFFICIAL`",
        "",
        REQUIRED_CANDIDATE_WORDING,
        "",
        "## Rule",
        "",
        "`s23_candidate = s23_frozen * (Z_virt^{u,2})^(1/16)`",
        "",
        f"- `Z_virt^{{u,2}} = {report.z_virt_u2}`",
        f"- `CANDIDATE_MIXING_EXPONENT = {report.candidate_mixing_exponent}`",
        f"- `Z_MIX_23 = {report.z_mix_23}`",
        "",
        "## Scope",
        "",
        "Only CKM 2-3 mixing is changed.",
        "",
        "## Unchanged",
        "",
        "- `BHSM_BARE_V1`",
        "- `BHSM_DRESSED_V1_CANDIDATE`",
        "- `c/t` dressed value",
        "- `u/t`",
        "- `d/b`",
        "- `s/b`",
        "- charged-lepton ratios",
        "- gauge couplings",
        "- `s12`",
        "- `s13`",
        "- `delta_cp`",
        "",
        "## Baseline vs Candidate",
        "",
        "| Quantity | Baseline rel. err. | Candidate rel. err. | Improved |",
        "| --- | ---: | ---: | --- |",
    ]
    for name in ("Vcb", "Vts", "J_CKM"):
        lines.append(
            "| `{}` | `{:.6g}` | `{:.6g}` | `{}` |".format(
                name,
                baseline_residuals[name].relative_error,
                candidate_residuals[name].relative_error,
                candidate_residuals[name].relative_error
                < baseline_residuals[name].relative_error,
            )
        )
    lines.extend(
        [
            "",
            "## Full Residual Table",
            "",
            "| State | Quantity | Predicted | Reference | Relative Error |",
            "| --- | --- | ---: | ---: | ---: |",
            *_residual_table_lines(report.baseline),
            *_residual_table_lines(report.candidate),
            "",
            "## Flags",
            "",
            f"- Improves `Vcb`: `{report.improves_vcb}`",
            f"- Improves `Vts`: `{report.improves_vts}`",
            f"- Non-2-3 damage flag: `{report.non_23_damage_flag}`",
            f"- `J_CKM` damage flag: `{report.j_damage_flag}`",
            "",
            "## Promotion Status",
            "",
            "This candidate is not promoted. Promotion requires derivation of the "
            "1/16 exponent from BHSM geometry, boundary operators, mode overlap "
            "order, or internal action before any future external comparison.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_audit_markdown(path: str | Path) -> None:
    """Export the audit report as Markdown."""

    report = build_mixing_candidate_report()
    baseline_residuals = residual_map(report.baseline)
    candidate_residuals = residual_map(report.candidate)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# BHSM Mixing-Dressed v1 Candidate Audit",
        "",
        "Status: `CANDIDATE_NOT_OFFICIAL` / `CANDIDATE_EXPONENT`",
        "",
        REQUIRED_CANDIDATE_WORDING,
        "",
        "This audit compares the official frozen CKM baseline to the candidate "
        "CKM 2-3 mixing dressing. It does not change the official released "
        "`BHSM_BARE_V1` or `BHSM_DRESSED_V1_CANDIDATE` outputs.",
        "",
        "## Candidate Check",
        "",
        "| Check | Result |",
        "| --- | --- |",
        f"| Improves `Vcb` | `{report.improves_vcb}` |",
        f"| Improves `Vts` | `{report.improves_vts}` |",
        f"| Non-2-3 damage flag | `{report.non_23_damage_flag}` |",
        f"| `J_CKM` damage flag | `{report.j_damage_flag}` |",
        "",
        "## Pressure-Point Residuals",
        "",
        "| Quantity | Baseline | Candidate | Reference | Baseline rel. err. | Candidate rel. err. |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("Vcb", "Vts", "J_CKM"):
        base = baseline_residuals[name]
        candidate = candidate_residuals[name]
        lines.append(
            "| `{}` | `{:.12g}` | `{:.12g}` | `{:.12g}` | `{:.6g}` | `{:.6g}` |".format(
                name,
                base.predicted,
                candidate.predicted,
                base.reference,
                base.relative_error,
                candidate.relative_error,
            )
        )
    lines.extend(
        [
            "",
            "## Full Residual Table",
            "",
            "| State | Quantity | Predicted | Reference | Relative Error |",
            "| --- | --- | ---: | ---: | ---: |",
            *_residual_table_lines(report.baseline),
            *_residual_table_lines(report.candidate),
            "",
            "## Frozen Branch Check",
            "",
            "```json",
            json.dumps(report.frozen_branch_check, indent=2),
            "```",
            "",
            "## Limitations",
            "",
            "- `1/16` is not proven and remains a derivation target.",
            "- The candidate is not part of the official frozen release.",
            "- Future adoption requires freezing the rule before future external comparisons.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_audit_json(path: str | Path) -> None:
    """Export the audit report as JSON."""

    export_mixing_candidate_json(path)


def generate_all_outputs() -> None:
    """Generate candidate and audit artifacts."""

    export_audit_markdown("audits/bhsm_mixing_dressed_v1_candidate_audit.md")
    export_audit_json("audits/bhsm_mixing_dressed_v1_candidate_audit.json")
    export_mixing_candidate_markdown("candidates/BHSM_MIXING_DRESSED_V1_CANDIDATE.md")
    export_mixing_candidate_json("candidates/BHSM_MIXING_DRESSED_V1_CANDIDATE.json")


if __name__ == "__main__":
    generate_all_outputs()
